#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from research_governance_common import ROOT, GOV, digest, load_json, persist_json

BASE = GOV / "compounding_learning_v1"
POLICY = BASE / "POLICY.json"
STATE = BASE / "STATE.json"
NEXT = BASE / "NEXT_BEST_EXPERIMENT.json"

EXPERIMENT_ROOT = ROOT / "research" / "experiment_lifecycle"
REGISTRY = EXPERIMENT_ROOT / "LATEST_EXPERIMENT_REGISTRY.json"
ADMISSION = EXPERIMENT_ROOT / "LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"
ADJUDICATION = EXPERIMENT_ROOT / "weekly_adjudication" / "LATEST.json"

T13_ACTIVATION = ROOT / "research/api_agent/forecast_skill/COHORT_ACTIVATION_v1.json"
T13_STATUS = ROOT / "research/api_agent/forecast_skill/LATEST_STUDY_STATUS.json"

PROFILE_DEFAULTS = {
    "FAST": {"day_checkpoints": [7, 14, 30], "matured_checkpoints": [5, 10, 20]},
    "STANDARD": {"day_checkpoints": [7, 14, 30, 60, 90], "matured_checkpoints": [5, 10, 20, 40]},
    "LONG": {"day_checkpoints": [30, 60, 90, 120, 180, 240], "matured_checkpoints": [10, 25, 50, 100]},
    "CONFIRMATORY": {"day_checkpoints": [30, 60, 90, 120, 180], "matured_checkpoints": []},
}

ADJUDICATION_ESCALATIONS = {
    "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW",
    "RUN_FAILURE_AND_RETIREMENT_REVIEW",
}

LEARNING_PRIORITY = {
    "SUPPORTED_NEEDS_INCREMENTAL_VALUE": 0,
    "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW": 1,
    "INCONCLUSIVE_KEEP_FROZEN": 2,
    "WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE": 3,
    "ARCHIVE_DUPLICATE": 4,
    "WAIT_FOR_MAPPING": 5,
    "KEEP_QUARANTINED": 6,
    "WAIT_FOR_REFRESHED_UNIFIED_ADJUDICATION": 7,
}


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


def _admission_map(admission: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(row.get("candidate_id")): row
        for row in admission.get("candidates", [])
        if isinstance(row, dict) and row.get("candidate_id")
    }


def _adjudication_map(adjudication: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        str(row.get("candidate_id")): row
        for row in adjudication.get("candidate_actions", [])
        if isinstance(row, dict) and row.get("candidate_id")
    }


def _profile(candidate: Dict[str, Any], policy: Dict[str, Any]) -> str:
    profiles = policy.get("profiles") or PROFILE_DEFAULTS
    explicit = str(candidate.get("learning_profile") or "").upper()
    if explicit in profiles:
        return explicit
    test_id = str(candidate.get("test_id") or "").upper()
    title = str(candidate.get("title") or "").upper()
    kind = str(candidate.get("kind") or "").upper()
    if "CONFIRMATORY" in title or test_id.startswith("FORECAST_SKILL_CONFIRMATORY"):
        return "CONFIRMATORY"
    if "INTRADAY" in title or "INTRADAY" in kind:
        return "FAST"
    if any(token in kind for token in ("FORECAST_TEST", "SENSOR_COMBINATION", "SEQUENCE_TEST")):
        return "STANDARD"
    return str(policy.get("default_profile") or "STANDARD").upper()


def _age_days(candidate: Dict[str, Any], admission_row: Dict[str, Any], as_of: datetime) -> Tuple[Optional[int], str]:
    """Operational checkpoint clock only; never retroactively age historical requalifications."""
    if bool(admission_row.get("historical_candidate_requalification")):
        start = _parse_utc(candidate.get("forward_test_started_at_utc"))
        if start is None:
            return None, "DISABLED_HISTORICAL_REQUALIFICATION_WITHOUT_FORWARD_START"
        basis = "FORWARD_TEST_STARTED_AT_UTC"
    else:
        start = _parse_utc(candidate.get("forward_test_started_at_utc") or candidate.get("created_at_utc"))
        basis = "FORWARD_TEST_STARTED_AT_UTC" if candidate.get("forward_test_started_at_utc") else "CANDIDATE_CREATED_AT_UTC_OPERATIONAL_ONLY"
    if start is None or start > as_of:
        return None, "UNAVAILABLE"
    return int((as_of - start).total_seconds() // 86400), basis


def _crossed(values: Iterable[int], current: Optional[int]) -> List[int]:
    if current is None:
        return []
    return [int(value) for value in values if current >= int(value)]


def _checkpoint_key(candidate_id: str, axis: str, threshold: int) -> str:
    return f"{candidate_id}:CHECKPOINT:{axis}:{int(threshold)}"


def _escalation_key(candidate_id: str, action: str, matured_count: int) -> str:
    return f"{candidate_id}:ADJUDICATION:{action}:{int(matured_count)}"


def _adjudication_is_current(candidate: Dict[str, Any], admission_row: Dict[str, Any], row: Optional[Dict[str, Any]]) -> Tuple[bool, str]:
    if not row:
        return False, "MISSING_CANDIDATE_ADJUDICATION"
    if str(row.get("lifecycle_state") or "") != str(candidate.get("state") or ""):
        return False, "LIFECYCLE_STATE_DRIFT"
    if int(row.get("matured_outcome_count") or 0) != int(candidate.get("matured_outcome_count") or 0):
        return False, "MATURED_COUNT_DRIFT"
    current_admission = str(admission_row.get("status") or candidate.get("scientific_admission_status") or "")
    row_admission = str(row.get("scientific_admission_status") or "")
    if current_admission and row_admission and current_admission != row_admission:
        return False, "SCIENTIFIC_ADMISSION_DRIFT"
    if row.get("canonical_effect") is not False or row.get("portfolio_execution") is not False:
        return False, "ADJUDICATION_AUTHORITY_BREACH"
    return True, "CURRENT"


def _learning_from_adjudication(row: Optional[Dict[str, Any]], current: bool) -> Tuple[str, str, str, bool, str]:
    if not current or not row:
        return (
            "WAIT_FOR_REFRESHED_UNIFIED_ADJUDICATION",
            "CONTINUE_OBSERVING",
            "do not reinterpret evidence until Unified Experimental Adjudication matches the current lifecycle state",
            False,
            "NONE",
        )
    action = str(row.get("selected_action") or "")
    reason = str(row.get("reason") or "")
    if action == "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW":
        return (
            "SUPPORTED_NEEDS_INCREMENTAL_VALUE",
            "RUN_INCREMENTAL_VALUE_TEST",
            "supportive prospective evidence may justify a child test only after incremental-value and adversarial review; the frozen parent remains immutable",
            True,
            "DOES_THE_SIGNAL_ADD_INCREMENTAL_PROSPECTIVE_VALUE_BEYOND_ITS_FROZEN_BASELINE_AND_CONTROLS",
        )
    if action == "RUN_FAILURE_AND_RETIREMENT_REVIEW":
        return (
            "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW",
            "STRESS_TEST_REGIME_SPECIFICITY",
            "negative prospective evidence warrants bounded failure review; any salvage hypothesis must be a new preregistered child rather than a rewrite of the failed parent",
            True,
            "IS_THE_FAILURE_ROBUST_ACROSS_REGIMES_OR_IS_A_NEW_PROSPECTIVE_REGIME_SPECIFIC_CHILD_TEST_JUSTIFIED",
        )
    mapping = {
        "KEEP_SHADOW_INCONCLUSIVE": ("INCONCLUSIVE_KEEP_FROZEN", reason or "matured evidence remains inconclusive"),
        "ARCHIVE_ONLY_DUPLICATE": ("ARCHIVE_DUPLICATE", reason or "semantic duplicate remains archive-only"),
        "WAIT_FOR_MAPPING": ("WAIT_FOR_MAPPING", reason or "candidate is not yet machine-mappable"),
        "KEEP_QUARANTINED": ("KEEP_QUARANTINED", reason or "scientific admission does not permit forward execution"),
    }
    state, why = mapping.get(action, ("WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE", reason or "insufficient mature prospective evidence for escalation"))
    return state, "CONTINUE_OBSERVING", why, False, "NONE"


def _make_packet(candidate: Dict[str, Any], admission_row: Dict[str, Any], row: Optional[Dict[str, Any]], current: bool, freshness: str, profile: str, age_days: Optional[int], age_basis: str, event_keys: List[str]) -> Dict[str, Any]:
    learning_state, action, reason, proposal_eligible, question = _learning_from_adjudication(row, current)
    return {
        "contract": "COMPOUNDING_LEARNING_CHECKPOINT_PACKET_v1",
        "candidate_id": str(candidate.get("candidate_id") or ""),
        "parent_candidate_id": str(candidate.get("candidate_id") or ""),
        "title": str(candidate.get("title") or ""),
        "kind": str(candidate.get("kind") or ""),
        "learning_profile": profile,
        "candidate_state": str(candidate.get("state") or ""),
        "scientific_admission_status": str(admission_row.get("status") or candidate.get("scientific_admission_status") or ""),
        "historical_candidate_requalification": bool(admission_row.get("historical_candidate_requalification")),
        "age_days": age_days,
        "age_basis": age_basis,
        "observation_count": int(candidate.get("observation_count") or 0),
        "matured_outcome_count": int(candidate.get("matured_outcome_count") or 0),
        "semantic_fingerprint": str(admission_row.get("semantic_fingerprint") or candidate.get("semantic_fingerprint") or ""),
        "trigger_event_keys": sorted(event_keys),
        "unified_adjudication_action": row.get("selected_action") if current and row else None,
        "unified_adjudication_reason": row.get("reason") if current and row else None,
        "adjudication_freshness": freshness,
        "learning_state": learning_state,
        "recommended_action": action,
        "reason": reason,
        "proposal_eligible": proposal_eligible,
        "next_falsifiable_question": question,
        "scientific_interpretation_owner": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1",
        "controller_role": "NEXT_LEARNING_STRATEGY_ONLY",
        "frozen_parent_preserved": True,
        "retrospective_rescore_allowed": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "automatic_promotion": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
    }


def evaluate_candidates(registry: Dict[str, Any], admission: Dict[str, Any], adjudication: Dict[str, Any], policy: Dict[str, Any], previous_state: Dict[str, Any], as_of: datetime) -> Tuple[List[Dict[str, Any]], List[str]]:
    profiles = policy.get("profiles") or PROFILE_DEFAULTS
    admitted = _admission_map(admission)
    adjudicated = _adjudication_map(adjudication)
    prior_keys = set(previous_state.get("emitted_event_keys") or [])
    packets: List[Dict[str, Any]] = []

    for candidate in registry.get("candidates", []) if isinstance(registry, dict) else []:
        if not isinstance(candidate, dict) or not candidate.get("candidate_id"):
            continue
        cid = str(candidate["candidate_id"])
        admission_row = admitted.get(cid, {})
        profile = _profile(candidate, policy)
        cfg = profiles.get(profile) or profiles.get("STANDARD") or PROFILE_DEFAULTS["STANDARD"]
        age, age_basis = _age_days(candidate, admission_row, as_of)
        matured = int(candidate.get("matured_outcome_count") or 0)
        new_keys: List[str] = []
        for threshold in _crossed(cfg.get("day_checkpoints", []), age):
            key = _checkpoint_key(cid, "DAY", threshold)
            if key not in prior_keys:
                new_keys.append(key)
        for threshold in _crossed(cfg.get("matured_checkpoints", []), matured):
            key = _checkpoint_key(cid, "MATURED", threshold)
            if key not in prior_keys:
                new_keys.append(key)

        row = adjudicated.get(cid)
        is_current, freshness = _adjudication_is_current(candidate, admission_row, row)
        if is_current and str(row.get("selected_action") or "") in ADJUDICATION_ESCALATIONS:
            key = _escalation_key(cid, str(row.get("selected_action")), matured)
            if key not in prior_keys:
                new_keys.append(key)
        if new_keys:
            packets.append(_make_packet(candidate, admission_row, row, is_current, freshness, profile, age, age_basis, new_keys))

    packets.sort(key=lambda item: (
        0 if item.get("proposal_eligible") else 1,
        LEARNING_PRIORITY.get(str(item.get("learning_state")), 99),
        -int(item.get("matured_outcome_count") or 0),
        -int(item.get("observation_count") or 0),
        str(item.get("candidate_id")),
    ))
    selected = packets[: int(policy.get("max_checkpoint_candidates_per_run", 25))]
    selected_keys = sorted({key for packet in selected for key in packet.get("trigger_event_keys", [])})
    return selected, selected_keys


def _proposal_from_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "proposal_status": "PROPOSAL_ONLY_ROUTE_THROUGH_EXISTING_RESEARCH_GOVERNANCE_AND_SCIENTIFIC_ADMISSION",
        "source": "COMPOUNDING_LEARNING",
        "parent_candidate_id": packet["candidate_id"],
        "target": packet["candidate_id"],
        "action": packet["recommended_action"],
        "learning_state": packet["learning_state"],
        "learning_profile": packet["learning_profile"],
        "reason": packet["reason"],
        "next_falsifiable_question": packet["next_falsifiable_question"],
        "unified_adjudication_action": packet["unified_adjudication_action"],
        "frozen_parent_preserved": True,
        "child_may_mutate_parent": False,
        "new_test_automatically_admitted": False,
        "retrospective_rescore_allowed": False,
        "automatic_parameter_search": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "model_weight_change": False,
        "automatic_threshold_change": False,
        "automatic_market_rule_change": False,
        "automatic_promotion": False,
        "next_route": [
            "RESEARCH_MEMORY_NOVELTY",
            "DECISION_IMPACT_VOI",
            "INDEPENDENT_ADVERSARIAL_SENTINEL",
            "META_ORCHESTRATOR",
            "SCIENTIFIC_ADMISSION_OR_EXISTING_OWNER",
            "PROSPECTIVE_FREEZE_IF_AUTHORIZED",
            "EXPERIMENT_EXECUTION_PLANE",
        ],
    }


def _t13_status(as_of: datetime) -> Dict[str, Any]:
    activation = load_json(T13_ACTIVATION, {})
    status = load_json(T13_STATUS, {})
    if not isinstance(activation, dict) or not activation:
        return {
            "contract": "COMPOUNDING_LEARNING_T13_FIREWALL_v1",
            "phase": "ACTIVATION_NOT_AVAILABLE",
            "interim_performance_inference_allowed": False,
            "scientific_method_change_allowed": False,
            "automatic_child_experiment_allowed": False,
        }
    start = _parse_utc(activation.get("cohort_start_utc"))
    end = _parse_utc(activation.get("cohort_end_utc_exclusive"))
    if start and as_of < start:
        phase, day = "PRE_START", 0
    elif start and end and start <= as_of < end:
        phase, day = "ACCRUING", int((as_of - start).total_seconds() // 86400) + 1
    elif end and as_of >= end:
        phase, day = "ACCRUAL_CLOSED", int(activation.get("freeze_accrual_window_days") or 240)
    else:
        phase, day = "UNKNOWN", None
    return {
        "contract": "COMPOUNDING_LEARNING_T13_FIREWALL_v1",
        "study_id": activation.get("study_id"),
        "phase": phase,
        "cohort_start_utc": activation.get("cohort_start_utc"),
        "cohort_end_utc_exclusive": activation.get("cohort_end_utc_exclusive"),
        "accrual_day": day,
        "operational_checkpoint_days_reached": [d for d in [30, 60, 90, 120, 180] if day is not None and day >= d],
        "forecast_skill_status": activation.get("forecast_skill_status") or (status.get("forecast_skill_status") if isinstance(status, dict) else None) or "UNPROVEN",
        "study_status": status.get("status") if isinstance(status, dict) else None,
        "outcome_data_read_flag": bool(activation.get("outcome_data_read", status.get("outcome_data_read", False) if isinstance(status, dict) else False)),
        "interim_performance_inference_allowed": False,
        "scientific_method_change_allowed": False,
        "automatic_child_experiment_allowed": False,
        "checkpoint_scope": "ACCRUAL_HEALTH_DATA_QUALITY_CONCENTRATION_AND_MATURITY_READINESS_ONLY",
        "checkpoint_may_not_emit_skill_verdict": True,
        "final_confirmatory_test_owner": "FORECAST_SKILL_CONFIRMATORY_V1_3_1_PLUS_BINDING_V1_3_2_ERRATUM",
    }


def build_state(registry: Dict[str, Any], admission: Dict[str, Any], adjudication: Dict[str, Any], policy: Dict[str, Any], previous_state: Dict[str, Any], as_of: datetime) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    packets, new_keys = evaluate_candidates(registry, admission, adjudication, policy, previous_state, as_of)
    all_keys = sorted(set(previous_state.get("emitted_event_keys") or []) | set(new_keys))
    eligible = [packet for packet in packets if packet.get("proposal_eligible")]
    if eligible:
        primary = eligible[0]
        proposal = _proposal_from_packet(primary)
        action, target, reason = str(primary["recommended_action"]), str(primary["candidate_id"]), str(primary["reason"])
    else:
        proposal = {
            "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "proposal_status": "NO_NEW_SCIENTIFICALLY_ELIGIBLE_CHILD_TEST",
            "source": "COMPOUNDING_LEARNING",
            "canonical_effect": False,
            "portfolio_execution": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        }
        action, target = "CONTINUE_OBSERVING", "EXPERIMENT_LIFECYCLE"
        reason = "descriptive checkpoints may exist, but fresh Unified Experimental Adjudication has not justified a child-test proposal"

    t13 = _t13_status(as_of)
    fingerprint_input = {
        "registry_candidate_count": registry.get("candidate_count", len(registry.get("candidates", []))),
        "admission_candidate_count": admission.get("candidate_count", len(admission.get("candidates", []))),
        "adjudication_generated_at_utc": adjudication.get("generated_at_utc"),
        "packets": packets,
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
        "family": "EXPERIMENT_LEARNING_AND_CALIBRATION",
        "learning_loop": "OBSERVE_FREEZE_TEST_MATURE_ADJUDICATE_LEARN_CHALLENGE_RETEST_IMPROVE",
        "scientific_interpretation_owner": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1",
        "controller_role": "NEXT_LEARNING_STRATEGY_ONLY",
        "registry_candidate_count": int(registry.get("candidate_count") or len(registry.get("candidates", []))),
        "scientific_admission_candidate_count": int(admission.get("candidate_count") or len(admission.get("candidates", []))),
        "adjudication_generated_at_utc": adjudication.get("generated_at_utc"),
        "new_learning_event_count": len(packets),
        "learning_packets": packets,
        "emitted_event_keys": all_keys,
        "next_best_experiment": proposal,
        "t13_confirmatory_firewall": t13,
        "frozen_parent_rewrite_allowed": False,
        "retrospective_rescore_allowed": False,
        "canonical_effect": False,
        "portfolio_execution": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
        "external_provider_calls_authorized": False,
        "automatic_promotion": False,
        "automatic_canonical_write": False,
        "automatic_threshold_change": False,
        "automatic_weight_change": False,
        "automatic_market_rule_change": False,
        "model_weight_change": False,
    }
    state["evidence_fingerprint"] = digest(fingerprint_input)
    proposal = dict(proposal)
    proposal["evidence_fingerprint"] = state["evidence_fingerprint"]
    state["next_best_experiment"] = proposal
    return state, proposal


def _validate_policy(policy: Dict[str, Any]) -> None:
    if policy.get("contract") != "COMPOUNDING_LEARNING_CONTROLLER_POLICY_v1":
        raise RuntimeError("compounding learning policy contract invalid")
    if policy.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise RuntimeError("compounding learning policy authority invalid")
    forbidden = (
        "canonical_effect", "automatic_promotion", "automatic_canonical_write", "portfolio_execution",
        "model_weight_change", "automatic_threshold_change", "automatic_weight_change",
        "automatic_market_rule_change", "retrospective_rescore_allowed", "frozen_parent_rewrite_allowed",
    )
    if any(policy.get(key) is not False for key in forbidden):
        raise RuntimeError("compounding learning policy firewall invalid")


def _validate_inputs(registry: Dict[str, Any], admission: Dict[str, Any], adjudication: Dict[str, Any]) -> None:
    if registry.get("contract") != "EXPERIMENT_LIFECYCLE_REGISTRY_v1":
        raise RuntimeError("experiment registry contract unavailable or invalid")
    if admission.get("contract") != "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1":
        raise RuntimeError("scientific admission registry contract unavailable or invalid")
    if adjudication.get("contract") != "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1":
        raise RuntimeError("unified adjudication contract unavailable or invalid")
    if adjudication.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise RuntimeError("unified adjudication authority invalid")
    for key in ("canonical_effect", "portfolio_execution", "automatic_threshold_change", "automatic_weight_change", "automatic_market_rule_change"):
        if adjudication.get(key) is not False:
            raise RuntimeError(f"unified adjudication firewall invalid: {key}")


def run_controller(*, dry_run: bool = False, as_of_utc: Optional[str] = None) -> Dict[str, Any]:
    policy = load_json(POLICY, {})
    _validate_policy(policy)
    registry, admission, adjudication = load_json(REGISTRY, {}), load_json(ADMISSION, {}), load_json(ADJUDICATION, {})
    if not all(isinstance(obj, dict) for obj in (registry, admission, adjudication)):
        raise RuntimeError("required experiment inputs unavailable")
    _validate_inputs(registry, admission, adjudication)
    previous = load_json(STATE, {})
    state, proposal = build_state(registry, admission, adjudication, policy, previous if isinstance(previous, dict) else {}, _now_utc(as_of_utc))
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
    print({
        "contract": state["contract"],
        "new_learning_event_count": state["new_learning_event_count"],
        "primary_action": state["primary_action"],
        "target": state["target"],
        "t13_phase": state["t13_confirmatory_firewall"].get("phase"),
    })


if __name__ == "__main__":
    main()
