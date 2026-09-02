from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

UTC = timezone.utc

RATIFICATION_PACKET_V2 = "FORECAST_RATIFICATION_PACKET_v2"
RATIFICATION_QUEUE_V1 = "FORECAST_RATIFICATION_QUEUE_v1"
RATIFICATION_TERMINAL_V1 = "FORECAST_RATIFICATION_TERMINAL_v1"

CUTOVER_COMMIT_SHA = "4057fde279ed0d8eea2df07da10543bda38ee8f8"
CUTOVER_UTC = "2026-09-02T09:56:53Z"
DECISION_SLA_MINUTES = 60
PACKET_RECORDING_TOLERANCE_MINUTES = 15

ALLOWED_AUTHORITIES = frozenset({"CHATGPT_FRAMEWORK_OWNER", "EXPLICIT_USER_MANDATE"})
ALLOWED_DECISIONS = frozenset({"RATIFY", "REJECT"})


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def cutover_dt() -> datetime:
    return parse_dt(CUTOVER_UTC)


def decision_deadline(candidate_created_at_utc: str) -> datetime:
    return parse_dt(candidate_created_at_utc) + timedelta(minutes=DECISION_SLA_MINUTES)


def is_post_cutover_candidate(candidate: dict[str, Any]) -> bool:
    created = candidate.get("created_at_utc")
    return bool(created) and parse_dt(str(created)) >= cutover_dt()


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
