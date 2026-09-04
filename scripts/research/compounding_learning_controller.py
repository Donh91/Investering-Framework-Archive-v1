#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from research_governance_common import ROOT, GOV, digest, load_json, persist_json

BASE = GOV / "compounding_learning_v1"
POLICY = BASE / "POLICY.json"
STATE = BASE / "STATE.json"
NEXT = BASE / "NEXT_BEST_EXPERIMENT.json"

EXPERIMENT_ROOT = ROOT / "research" / "experiment_lifecycle"
REGISTRY = EXPERIMENT_ROOT / "LATEST_EXPERIMENT_REGISTRY.json"
ADMISSION = EXPERIMENT_ROOT / "LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"

T13_ACTIVATION = ROOT / "research/api_agent/forecast_skill/COHORT_ACTIVATION_v1.json"
T13_STATUS = ROOT / "research/api_agent/forecast_skill/LATEST_STUDY_STATUS.json"

PROFILE_DEFAULTS = {
    "FAST": {"day_checkpoints": [7, 14, 30], "matured_checkpoints": [5, 10, 20]},
    "STANDARD": {"day_checkpoints": [30, 60, 90], "matured_checkpoints": [10, 20, 40]},
    "LONG": {"day_checkpoints": [60, 120, 180, 240], "matured_checkpoints": [10, 25, 50, 100]},
    "CONFIRMATORY": {"day_checkpoints": [30, 60, 90, 120, 180], "matured_checkpoints": []},
}

VERDICT_PRIORITY = {
    "DATA_DEFECT": 0,
    "REPLICATION_REQUIRED": 1,
    "REDUNDANT": 2,
    "NO_EDGE": 3,
    "INCONCLUSIVE": 4,
    "INSUFFICIENT_EVIDENCE": 5,
}

ACTION_PRIORITY = {
    "RECOVER_EVALUATOR": 0,
    "RUN_INCREMENTAL_VALUE_TEST": 1,
    "RUN_REDUNDANCY_CONFIRMATION": 2,
    "DEPRIORITIZE": 3,
    "CONTINUE_PROSPECTIVE_TEST": 4,
    "CONTINUE_OBSERVING": 5,
}

TERMINAL_NO_EDGE_STATES = {"MATURED_FAILED", "NO_EDGE", "MATURED_NO_EDGE", "FAILED"}
SUPPORTED_STATES = {"MATURED_SUPPORTED", "SUPPORTED", "PROMISING"}
INCONCLUSIVE_STATES = {"MATURED_INCONCLUSIVE", "INCONCLUSIVE"}


def _parse_utc(value: Any) -> Optional[datetime]:
    if not value:
        return None
    text = str(value).strip()
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            return None
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def _now_utc(value: Optional[str] = None) -> datetime:
    if value:
        dt = _parse_utc(value)
        if not dt:
            raise ValueError("invalid --as-of-utc timestamp")
        return dt
    return datetime.now(timezone.utc)


def _age_days(candidate: Dict[str, Any], as_of: datetime) -> Optional[int]:
    created = _parse_utc(candidate.get("created_at_utc"))
    if not created or created > as_of:
        return None
    return int((as_of - created).total_seconds() // 86400)


def _profile(candidate: Dict[str, Any], policy: Dict[str, Any]) -> str:
    explicit = str(candidate.get("learning_profile") or "").upper()
    profiles = policy.get("profiles") or PROFILE_DEFAULTS
    if explicit in profiles:
        return explicit
    kind = str(candidate.get("kind") or "").upper()
    title = str(candidate.get("title") or "").upper()
    if "CONFIRMATORY" in title or str(candidate.get("test_id") or "").startswith("FORECAST_SKILL_CONFIRMATORY"):
        return "CONFIRMATORY"
    if "INTRADAY" in kind or "INTRADAY" in title:
        return "FAST"
    if any(token in kind for token in ("SENSOR", "FORECAST_TEST")):
        return "STANDARD"
    return str(policy.get("default_profile") or "STANDARD").upper()


def _admission_map(admission: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in admission.get("candidates", []) if isinstance(admission, dict) else []:
        cid = str(row.get("candidate_id") or "")
        if cid:
            out[cid] = row
    return out


def _classify(candidate: Dict[str, Any], admission_row: Dict[str, Any]) -> Tuple[str, str, str]:
    state = str(candidate.get("state") or "").upper()
    admission_status = str(
        admission_row.get("status") or candidate.get("scientific_admission_status") or ""
    ).upper()

    if "DUPLICATE" in admission_status:
        return (
            "REDUNDANT",
            "RUN_REDUNDANCY_CONFIRMATION",
            "scientific admission marks the candidate as a semantic duplicate; confirm redundancy before retirement",
        )
    if any(token in state for token in ("QUARANTINED", "DATA_DEFECT", "SOURCE_DEFECT", "EVALUATOR_MISSING")):
        return (
            "DATA_DEFECT",
            "RECOVER_EVALUATOR",
            "candidate is quarantined or has an explicit data/evaluator defect; repair evidence machinery before learning from outcomes",
        )
    if state in SUPPORTED_STATES:
        return (
            "REPLICATION_REQUIRED",
            "RUN_INCREMENTAL_VALUE_TEST",
            "owner state is supportive; require incremental-value or replication evidence before any promotion claim",
        )
    if state in TERMINAL_NO_EDGE_STATES:
        return (
            "NO_EDGE",
            "DEPRIORITIZE",
            "owner state explicitly reports no edge or failure; deprioritize without rewriting the historical parent",
        )
    if state in INCONCLUSIVE_STATES:
        return (
            "INCONCLUSIVE",
            "CONTINUE_PROSPECTIVE_TEST",
            "matured evidence is inconclusive; continue only under the frozen owner contract",
        )
    return (
        "INSUFFICIENT_EVIDENCE",
        "CONTINUE_PROSPECTIVE_TEST",
        "no owner-produced performance verdict is mature enough for escalation",
    )


def _crossed(values: Iterable[int], current: Optional[int]) -> List[int]:
    if current is None:
        return []
    return [int(v) for v in values if current >= int(v)]


def _checkpoint_key(candidate_id: str, axis: str, threshold: int) -> str:
    return f"{candidate_id}:{axis}:{int(threshold)}"


def evaluate_candidates(
    registry: Dict[str, Any],
    admission: Dict[str, Any],
    policy: Dict[str, Any],
    previous_state: Dict[str, Any],
    as_of: datetime,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    profiles = policy.get("profiles") or PROFILE_DEFAULTS
    admitted = _admission_map(admission)
    prior_keys = set(previous_state.get("emitted_checkpoint_keys") or [])
    due: List[Dict[str, Any]] = []

    candidates = registry.get("candidates", []) if isinstance(registry, dict) else []
    for candidate in candidates:
        cid = str(candidate.get("candidate_id") or "")
        if not cid:
            continue
        profile = _profile(candidate, policy)
        cfg = profiles.get(profile) or profiles.get("STANDARD") or PROFILE_DEFAULTS["STANDARD"]
        age = _age_days(candidate, as_of)
        matured = int(candidate.get("matured_outcome_count") or 0)
        candidate_keys: List[Tuple[str, int, str]] = []

        for threshold in _crossed(cfg.get("day_checkpoints", []), age):
            key = _checkpoint_key(cid, "DAY", threshold)
            if key not in prior_keys:
                candidate_keys.append(("DAY", threshold, key))
        for threshold in _crossed(cfg.get("matured_checkpoints", []), matured):
            key = _checkpoint_key(cid, "MATURED", threshold)
            if key not in prior_keys:
                candidate_keys.append(("MATURED", threshold, key))

        if not candidate_keys:
            continue

        verdict, action, reason = _classify(candidate, admitted.get(cid, {}))
        by_axis: Dict[str, Tuple[str, int, str]] = {}
        for axis, threshold, key in candidate_keys:
            current = by_axis.get(axis)
            if current is None or threshold > current[1]:
                by_axis[axis] = (axis, threshold, key)
        keys = sorted(row[2] for row in by_axis.values())

        due.append({
            "candidate_id": cid,
            "parent_id": cid,
            "title": str(candidate.get("title") or ""),
            "kind": str(candidate.get("kind") or ""),
            "learning_profile": profile,
            "age_days": age,
            "observation_count": int(candidate.get("observation_count") or 0),
            "matured_outcome_count": matured,
            "candidate_state": str(candidate.get("state") or ""),
            "scientific_admission_status": str(
                admitted.get(cid, {}).get("status") or candidate.get("scientific_admission_status") or ""
            ),
            "checkpoint_keys": keys,
            "learning_verdict": verdict,
            "recommended_action": action,
            "reason": reason,
            "semantic_fingerprint": str(candidate.get("semantic_fingerprint") or ""),
            "canonical_effect": False,
            "portfolio_execution": False,
            "automatic_promotion": False,
        })

    due.sort(key=lambda item: (
        VERDICT_PRIORITY.get(item["learning_verdict"], 99),
        ACTION_PRIORITY.get(item["recommended_action"], 99),
        -int(item.get("matured_outcome_count") or 0),
        -int(item.get("observation_count") or 0),
        item["candidate_id"],
    ))
    max_due = int(policy.get("max_checkpoint_candidates_per_run", 25))
    selected = due[:max_due]
    selected_keys = sorted({key for item in selected for key in item["checkpoint_keys"]})
    return selected, selected_keys


def _t13_status(as_of: datetime) -> Dict[str, Any]:
    activation = load_json(T13_ACTIVATION, {})
    status = load_json(T13_STATUS, {})
    if not isinstance(activation, dict) or not activation:
        return {
            "contract": "COMPOUNDING_LEARNING_T13_FIREWALL_v1",
            "status": "ACTIVATION_NOT_AVAILABLE",
            "interim_performance_inference_allowed": False,
            "scientific_method_change_allowed": False,
        }

    start = _parse_utc(activation.get("cohort_start_utc"))
    end = _parse_utc(activation.get("cohort_end_utc_exclusive"))
    if start and as_of < start:
        phase, day = "PRE_START", 0
    elif start and end and start <= as_of < end:
        phase = "ACCRUING"
        day = int((as_of - start).total_seconds() // 86400) + 1
    elif end and as_of >= end:
        phase = "ACCRUAL_CLOSED"
        day = int(activation.get("freeze_accrual_window_days") or 240)
    else:
        phase, day = "UNKNOWN", None

    operational_due = [d for d in [30, 60, 90, 120, 180] if day is not None and day >= d]
    return {
        "contract": "COMPOUNDING_LEARNING_T13_FIREWALL_v1",
        "study_id": activation.get("study_id"),
        "phase": phase,
        "cohort_start_utc": activation.get("cohort_start_utc"),
        "cohort_end_utc_exclusive": activation.get("cohort_end_utc_exclusive"),
        "accrual_day": day,
        "operational_checkpoint_days_reached": operational_due,
        "forecast_skill_status": activation.get("forecast_skill_status") or status.get("forecast_skill_status") or "UNPROVEN",
        "outcome_data_read_flag": bool(activation.get("outcome_data_read", status.get("outcome_data_read", False))),
        "interim_performance_inference_allowed": False,
        "scientific_method_change_allowed": False,
        "checkpoint_scope": "ACCRUAL_DATA_QUALITY_CONCENTRATION_AND_MATURITY_READINESS_ONLY",
        "final_confirmatory_test_owner": "FORECAST_SKILL_CONFIRMATORY_V1_3_1_PLUS_BINDING_V1_3_2_ERRATUM",
    }


def _proposal_from_checkpoint(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "proposal_status": "PROPOSAL_ONLY_REQUIRES_EXISTING_NOVELTY_VOI_AND_SCIENTIFIC_ADMISSION",
        "parent_candidate_id": item["candidate_id"],
        "target": item["candidate_id"],
        "action": item["recommended_action"],
        "learning_verdict": item["learning_verdict"],
        "learning_profile": item["learning_profile"],
        "reason": item["reason"],
        "frozen_parent_preserved": True,
        "child_may_mutate_parent": False,
        "new_test_automatically_admitted": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "model_weight_change": False,
        "automatic_promotion": False,
        "next_route": [
            "RESEARCH_MEMORY_NOVELTY_GATE",
            "DECISION_IMPACT_VOI",
            "SCIENTIFIC_ADMISSION_OR_EXISTING_OWNER",
            "PROSPECTIVE_FREEZE_IF_AUTHORIZED",
            "EXPERIMENT_EXECUTION_PLANE",
        ],
    }


def build_state(
    registry: Dict[str, Any],
    admission: Dict[str, Any],
    policy: Dict[str, Any],
    previous_state: Dict[str, Any],
    as_of: datetime,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    due, new_keys = evaluate_candidates(registry, admission, policy, previous_state, as_of)
    all_keys = sorted(set(previous_state.get("emitted_checkpoint_keys") or []) | set(new_keys))

    if due:
        primary = due[0]
        proposal = _proposal_from_checkpoint(primary)
        action = primary["recommended_action"]
        target = primary["candidate_id"]
        reason = primary["reason"]
    else:
        proposal = {
            "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "proposal_status": "NO_NEW_CHECKPOINT_DUE",
            "canonical_effect": False,
            "portfolio_execution": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        }
        action = "CONTINUE_OBSERVING"
        target = "EXPERIMENT_LIFECYCLE"
        reason = "no new time-or-evidence checkpoint crossed since the previous controller state"

    t13 = _t13_status(as_of)
    fingerprint_input = {
        "registry_authority": registry.get("authority"),
        "registry_candidate_count": registry.get("candidate_count", len(registry.get("candidates", []))),
        "admission_candidate_count": admission.get("candidate_count", len(admission.get("candidates", []))),
        "due": due,
        "proposal": proposal,
        "t13": t13,
    }
    state = {
        "contract": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1",
        "status": "ACTIVE",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "generated_at_utc": as_of.isoformat().replace("+00:00", "Z"),
        "primary_action": action,
        "target": target,
        "reason": reason,
        "learning_loop": "OBSERVE_FREEZE_TEST_MATURE_LEARN_CHALLENGE_RETEST_IMPROVE",
        "registry_candidate_count": int(registry.get("candidate_count") or len(registry.get("candidates", []))),
        "scientific_admission_candidate_count": int(admission.get("candidate_count") or len(admission.get("candidates", []))),
        "new_checkpoint_candidate_count": len(due),
        "checkpoint_queue": due,
        "emitted_checkpoint_keys": all_keys,
        "next_best_experiment": proposal,
        "t13_confirmatory_firewall": t13,
        "canonical_effect": False,
        "portfolio_execution": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
        "external_provider_calls_authorized": False,
        "automatic_promotion": False,
        "automatic_canonical_write": False,
        "model_weight_change": False,
    }
    state["evidence_fingerprint"] = digest(fingerprint_input)
    proposal = dict(proposal)
    proposal["evidence_fingerprint"] = state["evidence_fingerprint"]
    return state, proposal


def run_controller(*, dry_run: bool = False, as_of_utc: Optional[str] = None) -> Dict[str, Any]:
    policy = load_json(POLICY, {})
    if policy.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise RuntimeError("compounding learning policy authority invalid")
    forbidden = (
        "canonical_effect",
        "automatic_promotion",
        "automatic_canonical_write",
        "portfolio_execution",
        "model_weight_change",
    )
    if any(policy.get(key) is not False for key in forbidden):
        raise RuntimeError("compounding learning policy firewall invalid")

    registry = load_json(REGISTRY, {})
    admission = load_json(ADMISSION, {})
    if not isinstance(registry, dict) or not registry.get("candidates"):
        raise RuntimeError("experiment registry unavailable or empty")
    if not isinstance(admission, dict) or "candidates" not in admission:
        raise RuntimeError("scientific admission registry unavailable")

    previous = load_json(STATE, {})
    state, proposal = build_state(registry, admission, policy, previous, _now_utc(as_of_utc))
    if not dry_run:
        persist_json(STATE, state)
        persist_json(NEXT, proposal)
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--as-of-utc")
    args = parser.parse_args()
    state = run_controller(dry_run=args.dry_run, as_of_utc=args.as_of_utc)
    print(json.dumps(state, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
