from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Sequence

from .models import Authority, DatasetIdentity, MarketType, TemporalPoint


class ContractViolation(ValueError):
    """Raised when a frozen backtest contract is violated."""


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ContractViolation(f"timestamp is not timezone-aware: {value}")
    return parsed


def validate_temporal(point: TemporalPoint) -> None:
    knowledge = parse_timestamp(point.knowledge_at_utc)
    decision = parse_timestamp(point.decision_at_utc)
    execution = parse_timestamp(point.execution_at_utc)
    label_end = parse_timestamp(point.label_end_utc)
    if not (knowledge <= decision <= execution < label_end):
        raise ContractViolation(
            "point-in-time violation: required knowledge_at <= decision_at <= execution_at < label_end"
        )


def validate_direct_gate_source(identity: DatasetIdentity, gate_name: str) -> None:
    if identity.authority is not Authority.DIRECT:
        raise ContractViolation(f"{gate_name}: direct gate requires DIRECT authority, got {identity.authority.value}")
    if identity.market_type is not MarketType.SPOT:
        raise ContractViolation(f"{gate_name}: direct spot gate requires SPOT market type, got {identity.market_type.value}")


def validate_no_silent_substitution(owner: DatasetIdentity, candidate: DatasetIdentity) -> None:
    if owner.venue != candidate.venue:
        raise ContractViolation(f"venue substitution forbidden: {owner.venue} -> {candidate.venue}")
    if owner.market_type is not candidate.market_type:
        raise ContractViolation(
            f"market-type substitution forbidden: {owner.market_type.value} -> {candidate.market_type.value}"
        )
    if owner.timezone_basis != candidate.timezone_basis:
        raise ContractViolation(
            f"timezone-basis substitution forbidden: {owner.timezone_basis} -> {candidate.timezone_basis}"
        )


def duplicate_keys(rows: Iterable[dict[str, Any]], key_fields: Sequence[str]) -> list[tuple[Any, ...]]:
    if not key_fields:
        raise ContractViolation("composite key must contain at least one field")
    keys: list[tuple[Any, ...]] = []
    for row_number, row in enumerate(rows, start=1):
        try:
            key = tuple(row[field] for field in key_fields)
        except KeyError as exc:
            raise ContractViolation(f"row {row_number}: missing key field {exc.args[0]}") from exc
        keys.append(key)
    counts = Counter(keys)
    return sorted([key for key, count in counts.items() if count > 1], key=repr)


def validate_composite_key(rows: Iterable[dict[str, Any]], key_fields: Sequence[str]) -> None:
    duplicates = duplicate_keys(rows, key_fields)
    if duplicates:
        raise ContractViolation(f"duplicate composite keys: {duplicates[:10]}")


def validate_etf_sessions(rows: Iterable[dict[str, Any]]) -> None:
    seen_dates: set[str] = set()
    for row in rows:
        date_text = str(row["date"])
        date_value = datetime.fromisoformat(date_text).date()
        if date_value.weekday() >= 5:
            raise ContractViolation(f"weekend ETF row forbidden: {date_text}")
        if date_text in seen_dates:
            raise ContractViolation(f"duplicate ETF session: {date_text}")
        seen_dates.add(date_text)
        if row.get("synthetic_zero") in {True, "True", "true", "1", 1}:
            raise ContractViolation(f"synthetic ETF zero forbidden: {date_text}")
        knowledge = row.get("feature_knowledge_available_at_utc") or row.get("not_before_session_close_utc")
        if not knowledge:
            raise ContractViolation(f"ETF session lacks knowledge time: {date_text}")
        knowledge_time = parse_timestamp(str(knowledge))
        if knowledge_time.date() < date_value:
            raise ContractViolation(f"ETF knowledge time before session date: {date_text}")


@dataclass(frozen=True)
class ContinuationPage:
    timestamps_ms: tuple[int, ...]
    next_after_ms: int | None


def validate_backward_continuation(current: ContinuationPage, older: ContinuationPage) -> None:
    if not current.timestamps_ms or not older.timestamps_ms:
        raise ContractViolation("continuation pages must not be empty")
    if tuple(sorted(current.timestamps_ms, reverse=True)) != current.timestamps_ms:
        raise ContractViolation("current page timestamps must be descending")
    if tuple(sorted(older.timestamps_ms, reverse=True)) != older.timestamps_ms:
        raise ContractViolation("older page timestamps must be descending")
    current_oldest = min(current.timestamps_ms)
    if current.next_after_ms != current_oldest:
        raise ContractViolation(
            f"resume cursor mismatch: expected oldest {current_oldest}, got {current.next_after_ms}"
        )
    overlap = set(current.timestamps_ms).intersection(older.timestamps_ms)
    if overlap:
        raise ContractViolation(f"continuation overlap detected: {sorted(overlap)[:5]}")
    if max(older.timestamps_ms) >= current_oldest:
        raise ContractViolation("older continuation page does not precede current page")
