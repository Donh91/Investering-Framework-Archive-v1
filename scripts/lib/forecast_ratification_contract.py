from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

UTC = timezone.utc

RATIFICATION_PACKET_V2 = "FORECAST_RATIFICATION_PACKET_v2"
RATIFICATION_QUEUE_V1 = "FORECAST_RATIFICATION_QUEUE_v1"
RATIFICATION_TERMINAL_V1 = "FORECAST_RATIFICATION_TERMINAL_v1"
SOURCE_FRESHNESS_CONTRACT_V1 = "FORECAST_SOURCE_TEMPORAL_PROVENANCE_v1"

CUTOVER_COMMIT_SHA = "4057fde279ed0d8eea2df07da10543bda38ee8f8"
CUTOVER_UTC = "2026-09-02T09:56:53Z"
SOURCE_FRESHNESS_CUTOVER_COMMIT_SHA = "a64d2770e5a81549c86c8c14a4a6ca2f3e6c577b"
SOURCE_FRESHNESS_CUTOVER_UTC = "2026-09-02T17:21:49Z"
DECISION_SLA_MINUTES = 60
PACKET_RECORDING_TOLERANCE_MINUTES = 15
CANDIDATE_RECORDING_TOLERANCE_MINUTES = 15
SOURCE_OUTPUT_MAX_AGE_MINUTES = 60

ALLOWED_AUTHORITIES = frozenset({"CHATGPT_FRAMEWORK_OWNER", "EXPLICIT_USER_MANDATE"})
ALLOWED_DECISIONS = frozenset({"RATIFY", "REJECT"})
REQUIRED_DECISION_BASIS_SCOPE = frozenset({"RATIFICATION_QUEUE", "CANDIDATE_RECORD"})


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def cutover_dt() -> datetime:
    return parse_dt(CUTOVER_UTC)


def source_freshness_cutover_dt() -> datetime:
    return parse_dt(SOURCE_FRESHNESS_CUTOVER_UTC)


def decision_deadline(candidate_created_at_utc: str) -> datetime:
    return parse_dt(candidate_created_at_utc) + timedelta(minutes=DECISION_SLA_MINUTES)


def is_post_cutover_candidate(candidate: dict[str, Any]) -> bool:
    created = candidate.get("created_at_utc")
    return bool(created) and parse_dt(str(created)) >= cutover_dt()


def is_post_source_freshness_cutover_candidate(candidate: dict[str, Any]) -> bool:
    created = candidate.get("created_at_utc")
    return bool(created) and parse_dt(str(created)) >= source_freshness_cutover_dt()


def validate_source_temporal_provenance(candidate: dict[str, Any]) -> float:
    """Validate recent model-output provenance for newly hardened candidates.

    Candidate creation is materialization time. The source-freshness cutover is
    separately pinned so older records retain their historical contract while
    candidates created after the hardening boundary must bind the Director
    receipt time, receipt hash and exact age at materialization.
    """
    if not is_post_source_freshness_cutover_candidate(candidate):
        return 0.0
    if candidate.get("source_freshness_contract") != SOURCE_FRESHNESS_CONTRACT_V1:
        raise ValueError("SOURCE_TEMPORAL_PROVENANCE_CONTRACT_REQUIRED")
    if candidate.get("source_freshness_cutover_commit_sha") != SOURCE_FRESHNESS_CUTOVER_COMMIT_SHA:
        raise ValueError("SOURCE_TEMPORAL_PROVENANCE_CUTOVER_MISMATCH")
    source_raw = candidate.get("source_output_created_at_utc")
    if not source_raw:
        raise ValueError("SOURCE_OUTPUT_CREATED_AT_REQUIRED")
    created_raw = candidate.get("created_at_utc")
    if not created_raw:
        raise ValueError("CANDIDATE_CREATED_AT_REQUIRED")
    source_at = parse_dt(str(source_raw))
    created_at = parse_dt(str(created_raw))
    age_seconds = (created_at - source_at).total_seconds()
    if age_seconds < 0:
        raise ValueError("SOURCE_OUTPUT_TIMESTAMP_AFTER_CANDIDATE_CREATION")
    if age_seconds > SOURCE_OUTPUT_MAX_AGE_MINUTES * 60:
        raise ValueError("SOURCE_OUTPUT_STALE_AT_CANDIDATE_MATERIALIZATION")
    recorded_age = candidate.get("source_output_age_at_materialization_seconds")
    if not isinstance(recorded_age, (int, float)) or isinstance(recorded_age, bool):
        raise ValueError("SOURCE_OUTPUT_AGE_BINDING_REQUIRED")
    if abs(float(recorded_age) - age_seconds) > 1.0:
        raise ValueError("SOURCE_OUTPUT_AGE_BINDING_MISMATCH")
    receipt_sha = candidate.get("source_receipt_sha256")
    if not isinstance(receipt_sha, str) or len(receipt_sha) != 64 or any(ch not in "0123456789abcdef" for ch in receipt_sha):
        raise ValueError("SOURCE_RECEIPT_SHA256_REQUIRED")
    return age_seconds


def validate_packet_shape(packet: dict[str, Any]) -> None:
    if packet.get("contract") != RATIFICATION_PACKET_V2:
        raise ValueError("WRONG_RATIFICATION_PACKET_CONTRACT")
    if packet.get("decision") not in ALLOWED_DECISIONS:
        raise ValueError("INVALID_RATIFICATION_DECISION")
    if packet.get("authority") not in ALLOWED_AUTHORITIES:
        raise ValueError("INVALID_RATIFICATION_AUTHORITY")
    if packet.get("outcome_blind") is not True:
        raise ValueError("RATIFICATION_MUST_BE_OUTCOME_BLIND")
    if packet.get("self_promotion_allowed") is not False:
        raise ValueError("SELF_PROMOTION_MUST_REMAIN_FALSE")
    if packet.get("prospective_cutover_commit_sha") != CUTOVER_COMMIT_SHA:
        raise ValueError("RATIFICATION_CUTOVER_COMMIT_MISMATCH")
    candidate_sha = packet.get("candidate_sha256")
    if not isinstance(candidate_sha, str) or len(candidate_sha) != 64:
        raise ValueError("INVALID_CANDIDATE_SHA256")
    if not packet.get("candidate_id"):
        raise ValueError("RATIFICATION_CANDIDATE_ID_REQUIRED")
    if not packet.get("decision_at_utc"):
        raise ValueError("RATIFICATION_DECISION_TIME_REQUIRED")
    if not isinstance(packet.get("owner_actor"), str) or not packet.get("owner_actor", "").strip():
        raise ValueError("RATIFICATION_OWNER_ACTOR_REQUIRED")
    if not isinstance(packet.get("decision_rationale"), str) or not packet.get("decision_rationale", "").strip():
        raise ValueError("RATIFICATION_DECISION_RATIONALE_REQUIRED")
    scope = packet.get("decision_basis_scope")
    if not isinstance(scope, list) or frozenset(scope) != REQUIRED_DECISION_BASIS_SCOPE or len(scope) != 2:
        raise ValueError("RATIFICATION_DECISION_BASIS_SCOPE_INVALID")
    if packet.get("outcome_paths_read") != []:
        raise ValueError("RATIFICATION_OUTCOME_PATHS_MUST_BE_EMPTY")
