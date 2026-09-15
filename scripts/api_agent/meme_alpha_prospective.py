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
SHADOW_CUTOFF_MINUTES = {1, 5, 15, 30}
FEATURE_MUTABILITY_CLASSES = {
    "IMMUTABLE_EVENT",
    "SNAPSHOT_PINNED",
    "DERIVED_FROM_PINNED_EVENTS",
    "MUTABLE_LIVE_FIELD",
    "UNKNOWN",
}
WALLET_ROLE_CLASSES = {
    "SELF_INITIATED_TRADE",
    "ROUTER_ATTRIBUTED_TRADE",
    "DIRECT_TRANSFER",
    "SEEDED_DUST",
    "CONSOLIDATION_EXIT_WALLET",
    "CREATOR_OR_FUNDER_LINKED",
    "UNKNOWN",
}


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _is_unknown(value: Any) -> bool:
    return value is None or value == "UNKNOWN"


def validate_shadow_feature(feature: dict[str, Any], cutoff_utc: str) -> list[str]:
    """Validate one point-in-time feature without assigning alpha meaning.

    A mutable live field is deliberately not accepted as historical evidence.  A
    snapshot-pinned field must have been observed no later than the decision
    cutoff.  Immutable events and deterministic derivatives may be reconstructed
    later, but their effective timestamp still has to pre-date the cutoff.
    """

    required = (
        "feature_name",
        "feature_value_at_cutoff",
        "feature_effective_at_utc",
        "source_observed_at_utc",
        "source_or_schema_version",
        "source_record_or_event_identity",
        "mutability_class",
    )
    errors: list[str] = []
    for key in required:
        if key not in feature or feature[key] in {"", []}:
            errors.append(f"FEATURE_PROVENANCE_MISSING:{key}")
    if errors:
        return errors

    mutability = str(feature["mutability_class"])
    if mutability not in FEATURE_MUTABILITY_CLASSES:
        errors.append("INVALID_MUTABILITY_CLASS")
        return errors
    if mutability == "MUTABLE_LIVE_FIELD":
        errors.append("MUTABLE_LIVE_FIELD_NOT_HISTORICAL_EVIDENCE")
    if mutability == "UNKNOWN" and not _is_unknown(feature["feature_value_at_cutoff"]):
        errors.append("UNKNOWN_MUTABILITY_CANNOT_CARRY_POSITIVE_VALUE")

    cutoff = _parse_utc(cutoff_utc)
    effective = _parse_utc(str(feature["feature_effective_at_utc"]))
    observed = _parse_utc(str(feature["source_observed_at_utc"]))
    if effective > cutoff:
        errors.append("FEATURE_EFFECTIVE_AFTER_CUTOFF")
    if mutability == "SNAPSHOT_PINNED" and observed > cutoff:
        errors.append("SNAPSHOT_OBSERVED_AFTER_CUTOFF")
    return errors


def freeze_shadow_observation(
    *,
    identity: dict[str, Any],
    cutoff_minutes: int,
    cutoff_utc: str,
    features: list[dict[str, Any]],
    wallet_roles: list[str] | None = None,
    collector_status: str = "ACTIVE",
) -> dict[str, Any]:
    """Freeze a deterministic G2/G3 research observation envelope.

    This function does not score, recommend, alert or execute.  Its job is to
    make later retrospective analysis incapable of silently rewriting the
    observation that was actually available at the decision cutoff.
    """

    if int(cutoff_minutes) not in SHADOW_CUTOFF_MINUTES:
        raise ValueError("UNSUPPORTED_SHADOW_CUTOFF")
    for key in ("chain", "token_id", "token_origin_utc"):
        if identity.get(key) in {None, ""}:
            raise ValueError(f"IDENTITY_MISSING:{key}")
    cutoff_dt = _parse_utc(cutoff_utc)
    if _parse_utc(str(identity["token_origin_utc"])) > cutoff_dt:
        raise ValueError("TOKEN_ORIGIN_AFTER_CUTOFF")

    normalized_features: list[dict[str, Any]] = []
    validation_errors: list[str] = []
    seen_names: set[str] = set()
    for feature in features:
        item = dict(feature)
        name = str(item.get("feature_name", ""))
        if name in seen_names:
            validation_errors.append(f"DUPLICATE_FEATURE:{name}")
        seen_names.add(name)
        for error in validate_shadow_feature(item, cutoff_utc):
            validation_errors.append(f"{name or 'UNKNOWN_FEATURE'}:{error}")
        normalized_features.append(item)

    roles = list(wallet_roles or [])
    invalid_roles = sorted({role for role in roles if role not in WALLET_ROLE_CLASSES})
    if invalid_roles:
        validation_errors.extend(f"INVALID_WALLET_ROLE:{role}" for role in invalid_roles)

    if validation_errors:
        raise ValueError(";".join(sorted(validation_errors)))

    normalized_features.sort(key=lambda item: str(item["feature_name"]))
    normalized_roles = sorted(roles)
    data_state = "READY" if collector_status == "ACTIVE" else "DEGRADED_DATA"
    packet: dict[str, Any] = {
        "contract": "MEME_ALPHA_G2_G3_SHADOW_OBSERVATION_v1",
        "identity": {
            "chain": str(identity["chain"]),
            "token_id": str(identity["token_id"]),
            "token_origin_utc": str(identity["token_origin_utc"]),
        },
        "cutoff_minutes": int(cutoff_minutes),
        "cutoff_utc": str(cutoff_utc),
        "collector_status": str(collector_status),
        "data_state": data_state,
        "features": normalized_features,
        "wallet_roles": normalized_roles,
        "authority": {
            "portfolio_action": False,
            "automatic_trading": False,
            "position_size_output": False,
            "live_alert_change": False,
        },
    }
    packet["observation_sha256"] = stable_hash(packet)
    return packet


def binary_prevalence_canary(
    retrospective_values: list[bool | int | None | str],
    shadow_values: list[bool | int | None | str],
    *,
    max_allowed_abs_delta: float | None = None,
) -> dict[str, Any]:
    """Compare a binary feature's retrospective and live-shadow prevalence.

    The function is an integrity canary only.  It never interprets a prevalence
    shift as market alpha or as a bearish/bullish signal.
    """

    def summarize(values: list[bool | int | None | str]) -> dict[str, Any]:
        known: list[int] = []
        unknown = 0
        for value in values:
            if _is_unknown(value):
                unknown += 1
                continue
            if value in {True, 1}:
                known.append(1)
            elif value in {False, 0}:
                known.append(0)
            else:
                raise ValueError("BINARY_CANARY_NON_BINARY_VALUE")
        total = len(values)
        return {
            "count": total,
            "known_count": len(known),
            "unknown_count": unknown,
            "unknown_rate": round(unknown / total, 6) if total else None,
            "positive_rate": round(sum(known) / len(known), 6) if known else None,
        }

    retro = summarize(retrospective_values)
    shadow = summarize(shadow_values)
    if retro["positive_rate"] is None or shadow["positive_rate"] is None:
        delta = None
        status = "INSUFFICIENT_DATA"
    else:
        delta = round(float(shadow["positive_rate"]) - float(retro["positive_rate"]), 6)
        if max_allowed_abs_delta is None:
            status = "MEASURED_NO_AUTOMATIC_GATE"
        else:
            status = "PASS" if abs(delta) <= float(max_allowed_abs_delta) else "REVIEW_REQUIRED"
    return {
        "contract": "MEME_ALPHA_SHADOW_PREVALENCE_CANARY_v1",
        "retrospective": retro,
        "shadow": shadow,
        "positive_rate_delta": delta,
        "max_allowed_abs_delta": max_allowed_abs_delta,
        "status": status,
        "market_interpretation_allowed": False,
    }


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
