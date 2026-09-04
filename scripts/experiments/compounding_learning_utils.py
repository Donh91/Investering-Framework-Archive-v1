#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc

ALLOWED_VERDICTS = {
    "PROMISING",
    "INSUFFICIENT_EVIDENCE",
    "REDUNDANT",
    "DATA_DEFECT",
    "FAILED",
    "REPLICATION_REQUIRED",
}

ALLOWED_ACTIONS = {
    "CONTINUE_OBSERVING",
    "RECOVER_EVIDENCE_PATH",
    "RUN_INCREMENTAL_VALUE_TEST",
    "RUN_REDUNDANCY_CONFIRMATION",
    "DEPRIORITIZE",
    "FREEZE_NEW_CHALLENGER",
    "OPEN_PROSPECTIVE_FORWARD_TEST",
}

BLOCKED_ADMISSION = {
    "TARGET_UNIT_QUARANTINED",
    "BLOCKED_INVALID_TARGET",
    "KEEP_SHADOW_INSUFFICIENT_COMBINATION",
}


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def parse_utc(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        result = datetime.fromisoformat(text)
        if result.tzinfo is None:
            return None
        return result.astimezone(UTC)
    except (TypeError, ValueError):
        return None


def iso(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def candidate_spec_map(candidate_root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not candidate_root.exists():
        return out
    for path in candidate_root.rglob("*.json"):
        value = read_json(path, {})
        if not isinstance(value, dict) or value.get("contract") != "EXPERIMENT_CANDIDATE_v1":
            continue
        cid = str(value.get("candidate_id") or "")
        spec = value.get("spec") if isinstance(value.get("spec"), dict) else {}
        if cid:
            out[cid] = {
                "horizon_days": spec.get("horizon_days"),
                "regime_dependency": spec.get("regime_dependency"),
                "target_direction": spec.get("target_direction"),
            }
    return out


def enrich_registry_with_candidate_specs(registry: dict[str, Any], candidate_root: Path) -> dict[str, Any]:
    specs = candidate_spec_map(candidate_root)
    out = dict(registry)
    rows = []
    for row in registry.get("candidates", []):
        if not isinstance(row, dict):
            continue
        value = dict(row)
        value.update({k: v for k, v in specs.get(str(row.get("candidate_id") or ""), {}).items() if v is not None})
        rows.append(value)
    out["candidates"] = rows
    return out


def validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("contract") != "COMPOUNDING_LEARNING_POLICY_v1":
        raise ValueError("invalid compounding learning policy contract")
    if policy.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise ValueError("invalid compounding learning authority")
    for key in (
        "canonical_effect",
        "portfolio_execution",
        "automatic_promotion",
        "automatic_canonical_write",
        "automatic_market_rule_change",
        "automatic_threshold_change",
        "automatic_weight_change",
        "automatic_child_registration",
    ):
        if policy.get(key) is not False:
            raise ValueError(f"compounding learning firewall invalid: {key}")
    profiles = policy.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("learning profiles missing")
    for name, cfg in profiles.items():
        if name not in {"FAST", "MEDIUM", "LONG", "CONFIRMATORY"} or not isinstance(cfg, dict):
            raise ValueError("invalid learning profile")
        if name == "CONFIRMATORY" and cfg.get("interim_performance_inference_allowed") is not False:
            raise ValueError("confirmatory interim inference must be disabled")


def profile_for(candidate: dict[str, Any], policy: dict[str, Any]) -> str:
    protected = {str(x) for x in policy.get("confirmatory_candidate_ids", [])}
    candidate_id = str(candidate.get("candidate_id") or "")
    if candidate_id in protected:
        return "CONFIRMATORY"
    horizon = as_int(candidate.get("horizon_days"), 0)
    if horizon and horizon <= as_int(policy.get("fast_horizon_days_max"), 7):
        return "FAST"
    if horizon and horizon <= as_int(policy.get("medium_horizon_days_max"), 30):
        return "MEDIUM"
    if horizon:
        return "LONG"
    kind = str(candidate.get("kind") or "").upper()
    if kind in {"FORECAST_TEST", "SENSOR_COMBINATION", "SEQUENCE_TEST"}:
        return "MEDIUM"
    return "LONG"


def thresholds(cfg: dict[str, Any], key: str, current: int) -> list[int]:
    fixed = sorted({as_int(x) for x in cfg.get(key, []) if as_int(x) > 0})
    if not fixed:
        return []
    recurring_key = "recurring_day_step_after_max" if key == "day_checkpoints" else "recurring_matured_step_after_max"
    recurring = as_int(cfg.get(recurring_key), 0)
    values = list(fixed)
    if recurring > 0 and current > fixed[-1]:
        nxt = fixed[-1] + recurring
        while nxt <= current:
            values.append(nxt)
            nxt += recurring
    return values


def candidate_age_days(candidate: dict[str, Any], as_of: datetime) -> int | None:
    created = parse_utc(candidate.get("created_at_utc"))
    if not created or created > as_of:
        return None
    return max(0, int((as_of - created).total_seconds() // 86400))


def admission_map(admissions: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("candidate_id")): row
        for row in admissions.get("candidates", [])
        if isinstance(row, dict) and row.get("candidate_id")
    }


def adjudication_map(adjudication: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("candidate_id")): row
        for row in adjudication.get("candidate_actions", [])
        if isinstance(row, dict) and row.get("candidate_id")
    }


def monthly_claim_map(monthly: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("candidate_id")): row
        for row in monthly.get("learning_claims", [])
        if isinstance(row, dict) and row.get("candidate_id")
    }


def classify(
    candidate: dict[str, Any],
    admission: dict[str, Any],
    adjudication: dict[str, Any],
    monthly_claim: dict[str, Any],
) -> tuple[str, str, str, str]:
    admission_status = str(admission.get("status") or candidate.get("scientific_admission_status") or "UNAVAILABLE").upper()
    state = str(candidate.get("state") or "UNKNOWN").upper()
    adjudication_action = str(adjudication.get("selected_action") or "").upper()

    if "DUPLICATE" in admission_status or adjudication_action == "ARCHIVE_ONLY_DUPLICATE":
        return (
            "REDUNDANT",
            "DEPRIORITIZE",
            "NO_CHILD",
            "semantic duplicate is preserved for audit but must not consume a new forward-test lane",
        )
    if admission_status == "WAITING_FOR_MAPPING" or state == "WAITING_FOR_MAPPING":
        return (
            "DATA_DEFECT",
            "RECOVER_EVIDENCE_PATH",
            "EVIDENCE_REPAIR",
            "the hypothesis is not yet machine-mappable; recover the evidence/mapping path before further learning claims",
        )
    if admission_status in BLOCKED_ADMISSION or adjudication_action == "KEEP_QUARANTINED" or state == "TARGET_UNIT_QUARANTINED":
        return (
            "DATA_DEFECT",
            "RECOVER_EVIDENCE_PATH",
            "EVIDENCE_REPAIR",
            "scientific admission or lifecycle state is quarantined; repair the exact evidence contract before scoring",
        )
    if adjudication_action == "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW":
        return (
            "PROMISING",
            "RUN_INCREMENTAL_VALUE_TEST",
            "INCREMENTAL_VALUE_CHILD",
            "mature supportive evidence exists, but incremental value versus the frozen baseline and controls is still unproven",
        )
    if adjudication_action == "RUN_FAILURE_AND_RETIREMENT_REVIEW":
        return (
            "FAILED",
            "DEPRIORITIZE",
            "FAILURE_REVIEW",
            "negative prospective evidence exists; preserve the parent and route to evidence-aware failure/retirement review",
        )
    if adjudication_action == "KEEP_SHADOW_INCONCLUSIVE":
        return (
            "INSUFFICIENT_EVIDENCE",
            "CONTINUE_OBSERVING",
            "NO_CHILD",
            "mature evidence remains inconclusive under the existing adjudication owner",
        )
    if monthly_claim and str(monthly_claim.get("state") or "").upper() == "MATURED_SUPPORTED":
        return (
            "REPLICATION_REQUIRED",
            "RUN_INCREMENTAL_VALUE_TEST",
            "INCREMENTAL_VALUE_CHILD",
            "monthly learning owner reports supportive evidence; independent incremental-value review is required before any stronger claim",
        )
    if state.startswith("MATURED_"):
        return (
            "INSUFFICIENT_EVIDENCE",
            "CONTINUE_OBSERVING",
            "NO_CHILD",
            "a matured lifecycle state exists but no current unified adjudication authorizes a stronger learning verdict",
        )
    return (
        "INSUFFICIENT_EVIDENCE",
        "CONTINUE_OBSERVING",
        "NO_CHILD",
        "no owner-produced mature adjudication supports escalation at this checkpoint",
    )


def checkpoint_key(candidate_id: str, axis: str, threshold: int) -> str:
    return f"{candidate_id}:{axis}:{threshold}"


def crossed_keys(candidate: dict[str, Any], profile: str, policy: dict[str, Any], as_of: datetime) -> list[dict[str, Any]]:
    cfg = policy["profiles"][profile]
    age = candidate_age_days(candidate, as_of)
    matured = as_int(candidate.get("matured_outcome_count"), 0)
    out: list[dict[str, Any]] = []
    if age is not None:
        for threshold in thresholds(cfg, "day_checkpoints", age):
            if age >= threshold:
                out.append({"axis": "DAY", "threshold": threshold, "key": checkpoint_key(str(candidate["candidate_id"]), "DAY", threshold)})
    if profile != "CONFIRMATORY":
        for threshold in thresholds(cfg, "matured_outcome_checkpoints", matured):
            if matured >= threshold:
                out.append({"axis": "MATURED_OUTCOMES", "threshold": threshold, "key": checkpoint_key(str(candidate["candidate_id"]), "MATURED_OUTCOMES", threshold)})
    return out
