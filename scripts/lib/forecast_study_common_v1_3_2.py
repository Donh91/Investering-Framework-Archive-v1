from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

UTC = timezone.utc
PREREG_V131 = "FORECAST_SKILL_PREREGISTRATION_v1_3_1"
ERRATUM_V132 = "FORECAST_SKILL_PREREGISTRATION_v1_3_2_ERRATUM"
ACTIVATION = "FORECAST_SKILL_COHORT_ACTIVATION_v1"
ADMISSION = "STUDY_ADMISSION_LEDGER_v1"
REVALIDATION = "OUTCOME_BLIND_TECHNICAL_REVALIDATION_v1"
OWNER_CLASS = "API_AGENT_OWNER_RATIFIED_PROSPECTIVE_v1"
EXACT_SETTLEMENT = "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1"
SOURCE_FRESHNESS_CONTRACT = "FORECAST_SOURCE_TEMPORAL_PROVENANCE_v1"
SOURCE_FRESHNESS_CUTOVER_SHA = "a64d2770e5a81549c86c8c14a4a6ca2f3e6c577b"
SOURCE_OUTPUT_MAX_AGE_MINUTES = 60
BLOCK_DAYS = 28
ALPHA = 0.025
STUDY_ID = "FORECAST_SKILL_CONFIRMATORY_V1_3_1"

def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def is_hex_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def with_self_hash(value: dict[str, Any], field: str) -> dict[str, Any]:
    out = dict(value)
    out[field] = digest(out)
    return out


def verify_self_hash(value: dict[str, Any], field: str) -> None:
    expected = value.get(field)
    material = dict(value)
    material.pop(field, None)
    if expected != digest(material):
        raise ValueError(f"{field.upper()}_MISMATCH")


def validate_source_candidate_binding(candidate_record: dict[str, Any], forecast: dict[str, Any]) -> dict[str, Any]:
    if candidate_record.get("contract") != "FORECAST_CANDIDATE_v1":
        raise ValueError("SOURCE_CANDIDATE_CONTRACT_REQUIRED")
    if candidate_record.get("candidate_id") != forecast.get("candidate_id"):
        raise ValueError("SOURCE_CANDIDATE_ID_MISMATCH")
    candidate_hash = digest(candidate_record)
    if forecast.get("candidate_sha256") != candidate_hash:
        raise ValueError("SOURCE_CANDIDATE_HASH_MISMATCH")
    if candidate_record.get("source_output_sha256") != forecast.get("source_output_sha256"):
        raise ValueError("SOURCE_OUTPUT_HASH_BINDING_MISMATCH")
    if candidate_record.get("source_freshness_contract") != SOURCE_FRESHNESS_CONTRACT:
        raise ValueError("SOURCE_TEMPORAL_PROVENANCE_CONTRACT_REQUIRED")
    if candidate_record.get("source_freshness_cutover_commit_sha") != SOURCE_FRESHNESS_CUTOVER_SHA:
        raise ValueError("SOURCE_TEMPORAL_PROVENANCE_CUTOVER_MISMATCH")
    source_at = parse_dt(str(candidate_record.get("source_output_created_at_utc") or ""))
    created_at = parse_dt(str(candidate_record.get("created_at_utc") or ""))
    age = (created_at - source_at).total_seconds()
    if age < 0 or age > SOURCE_OUTPUT_MAX_AGE_MINUTES * 60:
        raise ValueError("SOURCE_OUTPUT_STALE_OR_FUTURE_AT_MATERIALIZATION")
    recorded_age = candidate_record.get("source_output_age_at_materialization_seconds")
    if not isinstance(recorded_age, (int, float)) or isinstance(recorded_age, bool) or abs(float(recorded_age) - age) > 1.0:
        raise ValueError("SOURCE_OUTPUT_AGE_BINDING_MISMATCH")
    receipt_sha = candidate_record.get("source_receipt_sha256")
    if not is_hex_sha256(receipt_sha):
        raise ValueError("SOURCE_RECEIPT_SHA256_REQUIRED")
    return {
        "candidate_record_sha256": candidate_hash,
        "source_freshness_contract": SOURCE_FRESHNESS_CONTRACT,
        "source_freshness_cutover_commit_sha": SOURCE_FRESHNESS_CUTOVER_SHA,
        "source_output_created_at_utc": iso(source_at),
        "source_output_age_at_materialization_seconds": float(recorded_age),
        "source_output_max_age_minutes": SOURCE_OUTPUT_MAX_AGE_MINUTES,
        "source_receipt_sha256": receipt_sha,
    }


def validate_candidate_cohort_eligibility(candidate_record: dict[str, Any], cohort_start: datetime, cohort_end: datetime) -> datetime:
    """Require the immutable source candidate itself, not only later ratification, to originate inside the fixed cohort."""
    created_at = parse_dt(str(candidate_record.get("created_at_utc") or ""))
    if not (cohort_start <= created_at < cohort_end):
        raise ValueError("SOURCE_CANDIDATE_OUTSIDE_COHORT")
    return created_at


def validate_activation(
    activation: dict[str, Any], prereg_bytes: bytes, erratum_bytes: bytes
) -> tuple[datetime, datetime]:
    if activation.get("contract") != ACTIVATION:
        raise ValueError("WRONG_ACTIVATION_CONTRACT")
    if activation.get("status") != "ACTIVE":
        raise ValueError("COHORT_NOT_ACTIVE")
    verify_self_hash(activation, "activation_payload_sha256")
    if activation.get("study_id") != STUDY_ID:
        raise ValueError("ACTIVATION_STUDY_ID_MISMATCH")
    if activation.get("preregistration_sha256") != digest_bytes(prereg_bytes):
        raise ValueError("PREREGISTRATION_HASH_MISMATCH")
    if activation.get("endpoint_erratum_sha256") != digest_bytes(erratum_bytes):
        raise ValueError("ERRATUM_HASH_MISMATCH")
    if not isinstance(activation.get("implementation_main_sha"), str) or len(activation["implementation_main_sha"]) != 40:
        raise ValueError("IMPLEMENTATION_MAIN_SHA_INVALID")
    start = parse_dt(str(activation["cohort_start_utc"]))
    end = parse_dt(str(activation["cohort_end_utc_exclusive"]))
    recorded = parse_dt(str(activation["activation_recorded_at_utc"]))
    readback = parse_dt(str(activation["implementation_readback_at_utc"]))
    if end - start != timedelta(days=240):
        raise ValueError("COHORT_NOT_EXACTLY_240_DAYS")
    if start.time().isoformat() != "00:00:00" or end.time().isoformat() != "00:00:00":
        raise ValueError("COHORT_BOUNDARY_NOT_UTC_MIDNIGHT")
    if not (readback <= recorded < start):
        raise ValueError("ACTIVATION_NOT_PROSPECTIVELY_RECORDED_BEFORE_START")
    if activation.get("outcome_data_read") is not False:
        raise ValueError("ACTIVATION_OUTCOME_DATA_READ_MUST_BE_FALSE")
    return start, end
