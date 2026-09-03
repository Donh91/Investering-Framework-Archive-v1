from __future__ import annotations

import hashlib
from datetime import timedelta
from typing import Any

from forecast_study_common_v1_3_2 import (
    ACTIVATION, ADMISSION, EXACT_SETTLEMENT, OWNER_CLASS, REVALIDATION, STUDY_ID,
    canon, digest, digest_bytes, is_hex_sha256, iso, parse_dt, validate_activation,
    verify_self_hash, with_self_hash,
)

def admission_for(
    forecast: dict[str, Any],
    evidence_class: str,
    activation: dict[str, Any],
    prereg_bytes: bytes,
    erratum_bytes: bytes,
    b1: dict[str, Any],
    recorded_at_utc: str,
) -> dict[str, Any]:
    start, end = validate_activation(activation, prereg_bytes, erratum_bytes)
    if forecast.get("contract") != "FROZEN_FORECAST_v1":
        raise ValueError("NOT_FROZEN_FORECAST")
    if evidence_class != OWNER_CLASS:
        raise ValueError("WRONG_EVIDENCE_CLASS")
    if forecast.get("direction") not in {"UP", "DOWN"}:
        raise ValueError("F1_DIRECTIONAL_ONLY")
    if forecast.get("settlement_contract_version") != EXACT_SETTLEMENT:
        raise ValueError("EXACT_SETTLEMENT_REQUIRED")
    if forecast.get("ratification_outcome_blind") is not True:
        raise ValueError("OUTCOME_BLIND_RATIFICATION_REQUIRED")
    if forecast.get("ratification_contract") != "FORECAST_RATIFICATION_PACKET_v2":
        raise ValueError("OWNER_RATIFICATION_CONTRACT_REQUIRED")
    for field in ("candidate_sha256", "ratification_sha256", "source_output_sha256"):
        if not is_hex_sha256(forecast.get(field)):
            raise ValueError(f"{field.upper()}_REQUIRED")

    frozen = parse_dt(str(forecast["frozen_at_utc"]))
    due = parse_dt(str(forecast["outcome_due_utc"]))
    recorded = parse_dt(recorded_at_utc)
    if not (start <= frozen < end):
        raise ValueError("OUTSIDE_COHORT_FREEZE_WINDOW")
    if not (frozen <= recorded < due):
        raise ValueError("ADMISSION_NOT_RECORDED_BETWEEN_FREEZE_AND_OUTCOME_DUE")
    horizon = int(forecast["horizon_days"])
    if due != frozen + timedelta(days=horizon):
        raise ValueError("DUE_TIME_HORIZON_MISMATCH")

    if b1.get("contract") != "B1_CLIMATOLOGY_FREEZE_v1" or b1.get("no_lookahead") is not True:
        raise ValueError("B1_INVALID")
    if parse_dt(str(b1["freeze_utc"])) != frozen or int(b1["horizon_days"]) != horizon or b1["direction"] != forecast["direction"]:
        raise ValueError("B1_FORECAST_MISMATCH")
    if abs(float(b1["threshold_pct"]) - float(forecast["threshold_pct"])) > 1e-12:
        raise ValueError("B1_THRESHOLD_MISMATCH")
    if int(b1.get("admissible_event_count") or 0) < 20:
        raise ValueError("B1_MIN_EVENTS_NOT_MET")
    if parse_dt(str(b1["last_event_end_close_utc"])) >= frozen:
        raise ValueError("B1_LOOKAHEAD")

    row: dict[str, Any] = {
        "contract": ADMISSION,
        "status": "ADMITTED",
        "study_id": STUDY_ID,
        "forecast_id": forecast["forecast_id"],
        "forecast_sha256": digest(forecast),
        "evidence_class": evidence_class,
        "forecast_family": "F1_DIRECTIONAL_ONLY",
        "study_admission_basis_utc": iso(frozen),
        "study_admission_recorded_at_utc": iso(recorded),
        "freeze_day_utc": frozen.date().isoformat(),
        "outcome_due_utc": iso(due),
        "outcome_due_day_utc": due.date().isoformat(),
        "horizon_days": horizon,
        "direction": forecast["direction"],
        "metric_path": forecast["metric_path"],
        "threshold_pct": float(forecast["threshold_pct"]),
        "candidate_id": forecast.get("candidate_id"),
        "candidate_sha256": forecast.get("candidate_sha256"),
        "ratification_sha256": forecast.get("ratification_sha256"),
        "prompt_sha256": forecast.get("prompt_sha256"),
        "context_sha256": forecast.get("context_sha256"),
        "source_output_sha256": forecast.get("source_output_sha256"),
        "baseline_evidence_path": forecast.get("baseline_evidence_path"),
        "baseline_evidence_sha256": forecast.get("baseline_evidence_sha256"),
        "baseline_evidence_observed_at_utc": forecast.get("baseline_evidence_observed_at_utc"),
        "p_clim": float(b1["p_clim"]),
        "b1_climatology_sha256": digest(b1),
        "preregistration_sha256": digest_bytes(prereg_bytes),
        "endpoint_erratum_sha256": digest_bytes(erratum_bytes),
        "activation_receipt_sha256": digest(activation),
        "outcome_data_read": False,
        "authority": {
            "forecast_skill_claim": False,
            "portfolio_action": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        },
    }
    row["admission_id"] = "t13_" + hashlib.sha256(
        canon({"forecast": row["forecast_sha256"], "activation": row["activation_receipt_sha256"]})
    ).hexdigest()[:24]
    return with_self_hash(row, "admission_sha256")


def technical_revalidation(
    admission: dict[str, Any],
    forecast: dict[str, Any],
    activation: dict[str, Any],
    prereg_bytes: bytes,
    erratum_bytes: bytes,
    now_utc: str,
) -> dict[str, Any]:
    validate_activation(activation, prereg_bytes, erratum_bytes)
    if admission.get("contract") != ADMISSION:
        raise ValueError("WRONG_ADMISSION_CONTRACT")
    verify_self_hash(admission, "admission_sha256")
    if admission.get("forecast_sha256") != digest(forecast):
        raise ValueError("FORECAST_HASH_DRIFT")
    now = parse_dt(now_utc)
    due = parse_dt(str(admission["outcome_due_utc"]))
    if now < due:
        raise ValueError("OUTCOME_DUE_NOT_REACHED")
    checks = {
        "evidence_class": admission.get("evidence_class") == OWNER_CLASS,
        "direction": forecast.get("direction") in {"UP", "DOWN"},
        "exact_settlement": forecast.get("settlement_contract_version") == EXACT_SETTLEMENT,
        "outcome_blind_ratification": forecast.get("ratification_outcome_blind") is True,
        "forecast_hash": admission.get("forecast_sha256") == digest(forecast),
        "due_time": admission.get("outcome_due_utc") == forecast.get("outcome_due_utc"),
        "prereg_hash": admission.get("preregistration_sha256") == digest_bytes(prereg_bytes),
        "erratum_hash": admission.get("endpoint_erratum_sha256") == digest_bytes(erratum_bytes),
        "activation_hash": admission.get("activation_receipt_sha256") == digest(activation),
        "admission_outcome_blind": admission.get("outcome_data_read") is False,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    row = {
        "contract": REVALIDATION,
        "forecast_id": forecast["forecast_id"],
        "admission_id": admission["admission_id"],
        "revalidated_at_utc": iso(now),
        "status": status,
        "checks": checks,
        "outcome_data_read": False,
        "technical_failure_effect": "OUTCOME_UNAVAILABLE" if status != "PASS" else None,
        "authority": {
            "forecast_skill_claim": False,
            "portfolio_action": False,
            "model_weight_change": False,
        },
    }
    return with_self_hash(row, "revalidation_sha256")
