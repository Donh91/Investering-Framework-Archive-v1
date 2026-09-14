from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

TRIAL_ROOT_RE = re.compile(r"^EE-\d{3}-[A-Z0-9_-]+-\d{8}$")
ARTIFACT_RE = re.compile(r"^(EE-\d{3}-[A-Z0-9_-]+-\d{8})::A-\d{3}$")
TOKEN_RE = re.compile(r"^(EE-\d{3}-[A-Z0-9_-]+-\d{8}::A-\d{3})::T-\d{3}$")
TRIAL_STATES = {
    "DISCOVERY_OPEN",
    "DISCOVERY_COMPLETE",
    "OUTCOME_MATURING",
    "OUTCOME_MATURED",
    "INVALIDATED",
}


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def root_trial_id(identifier: str) -> str:
    if TRIAL_ROOT_RE.fullmatch(identifier):
        return identifier
    match = ARTIFACT_RE.fullmatch(identifier)
    if match:
        return match.group(1)
    match = TOKEN_RE.fullmatch(identifier)
    if match:
        return match.group(1).split("::", 1)[0]
    raise ValueError(f"invalid prospective identifier: {identifier}")


def validate_lineage(record: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    grandfathered = set(policy.get("grandfathered_trials", []))
    trial_id = root_trial_id(str(record.get("trial_id", "")))
    if trial_id in grandfathered:
        return []
    missing = []
    for key in policy.get("required_lineage", []):
        value = record.get(key)
        if value is None or value == "" or value == []:
            missing.append(str(key))
    return missing


def validate_trial_record(record: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        root_trial_id(str(record.get("trial_id", "")))
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    state = str(record.get("trial_state", ""))
    if state not in TRIAL_STATES:
        errors.append("INVALID_TRIAL_STATE")
        return errors

    lineage_missing = validate_lineage(record, policy)
    if lineage_missing:
        errors.append("LINEAGE_MISSING:" + ",".join(sorted(lineage_missing)))

    if state == "OUTCOME_MATURED":
        if record.get("falsifier_result") in {None, "", "NOT_YET_MATURED"}:
            errors.append("MATURED_REQUIRES_FINAL_FALSIFIER")
        missed_winner_audit = record.get("missed_winner_audit")
        if missed_winner_audit is None or missed_winner_audit == {}:
            errors.append("MATURED_REQUIRES_MISSED_WINNER_AUDIT")
        outcome = str(record.get("outcome_class", ""))
        if outcome == "PROSPECTIVE_SIGNAL_SURVIVED":
            for key in ("mfe_after_discovery", "mae_after_discovery", "realizable_return_after_slippage", "exit_feasibility"):
                if record.get(key) is None:
                    errors.append(f"POSITIVE_OUTCOME_REQUIRES_{key.upper()}")
    elif record.get("falsifier_result") not in {None, "", "NOT_YET_MATURED"}:
        errors.append("NON_MATURED_TRIAL_CANNOT_HAVE_FINAL_FALSIFIER")

    return errors


def method_review_eligibility(records: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    required = int(policy["trial_state_machine"]["minimum_unique_ecosystem_trials_for_review"])
    matured_roots: set[str] = set()
    invalid: list[str] = []
    for record in records:
        if record.get("trial_state") != "OUTCOME_MATURED":
            continue
        errors = validate_trial_record(record, policy)
        if errors:
            invalid.append(str(record.get("trial_id", "UNKNOWN")))
            continue
        matured_roots.add(root_trial_id(str(record["trial_id"])))
    return {
        "matured_unique_ecosystem_trials": len(matured_roots),
        "minimum_required": required,
        "eligible_for_method_review": len(matured_roots) >= required and not invalid,
        "invalid_matured_trials": sorted(invalid),
    }


def queue_slo_status(priority: str, enqueued_at_utc: str, now_utc: str, policy: dict[str, Any]) -> dict[str, Any]:
    key = {
        "P0": "P0_event_driven_max_queue_age_minutes",
        "P1": "P1_max_queue_age_minutes",
        "P2": "P2_max_queue_age_minutes",
    }.get(priority)
    if key is None:
        raise ValueError(f"unsupported priority: {priority}")
    start = datetime.fromisoformat(enqueued_at_utc.replace("Z", "+00:00"))
    end = datetime.fromisoformat(now_utc.replace("Z", "+00:00"))
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    age_minutes = max(0.0, (end - start).total_seconds() / 60.0)
    limit = float(policy["queue_slo"][key])
    return {
        "priority": priority,
        "queue_age_minutes": round(age_minutes, 3),
        "slo_minutes": limit,
        "status": "BREACH" if age_minutes > limit else "PASS",
    }


def kill_or_redraft(summary: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    minimum = int(policy["kill_criteria"]["evaluate_only_after_minimum_matured_trials"])
    matured = int(summary.get("matured_unique_ecosystem_trials", 0))
    reasons: list[str] = []
    if matured < minimum:
        return {"eligible": False, "decision": "CONTINUE_COHORT", "reasons": []}
    if int(summary.get("sellable_signal_survived_count", 0)) == 0:
        reasons.append("ZERO_SELLABLE_PROSPECTIVE_SIGNAL_SURVIVED")
    precision = summary.get("actionable_precision")
    control = summary.get("matched_control_precision")
    if precision is not None and control is not None and float(precision) <= float(control):
        reasons.append("ACTIONABLE_PRECISION_NOT_ABOVE_MATCHED_CONTROL")
    if summary.get("cohort_selection_integrity") is False:
        reasons.append("COHORT_SELECTION_INTEGRITY_BROKEN")
    if int(summary.get("non_grandfathered_lineage_failures", 0)) > 0:
        reasons.append("LINEAGE_INCOMPLETE_FOR_ANY_NON_GRANDFATHERED_TRIAL")
    if summary.get("missed_winner_recall_unacceptably_low") is True and summary.get("compensating_precision_edge") is not True:
        reasons.append("MISSED_WINNER_RECALL_UNACCEPTABLY_LOW_WITH_NO_COMPENSATING_PRECISION_EDGE")
    return {
        "eligible": True,
        "decision": "KILL_OR_REDRAFT" if reasons else "METHOD_REVIEW_ALLOWED",
        "reasons": sorted(set(reasons)),
    }
