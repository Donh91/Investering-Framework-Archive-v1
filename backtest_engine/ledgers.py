from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


LINEAGE_CLASSES = {
    "FULL_POINT_IN_TIME",
    "PARTIAL_POINT_IN_TIME",
    "RETROSPECTIVE_RECONSTRUCTION",
    "UNUSABLE_FOR_BT10",
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp is not timezone-aware: {value}")
    return parsed


@dataclass(frozen=True)
class DecisionLineageRow:
    record_id: str
    record_type: str
    event_time_utc: str
    knowledge_at_utc: str | None
    decision_at_utc: str | None
    rule_version: str | None
    input_artifact_ids: tuple[str, ...]
    input_hashes: tuple[str, ...]
    state_before: str | None
    state_after: str | None
    action_permission: str | None
    lineage_class: str
    exclusion_reason: str | None = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.record_id:
            errors.append("record_id is required")
        if self.lineage_class not in LINEAGE_CLASSES:
            errors.append(f"unsupported lineage_class: {self.lineage_class}")
        if len(self.input_artifact_ids) != len(self.input_hashes):
            errors.append("input_artifact_ids and input_hashes must have equal length")

        _parse_utc(self.event_time_utc)
        knowledge = _parse_utc(self.knowledge_at_utc) if self.knowledge_at_utc else None
        decision = _parse_utc(self.decision_at_utc) if self.decision_at_utc else None

        if self.lineage_class == "FULL_POINT_IN_TIME":
            if knowledge is None or decision is None:
                errors.append("FULL_POINT_IN_TIME requires knowledge_at_utc and decision_at_utc")
            if not self.rule_version:
                errors.append("FULL_POINT_IN_TIME requires rule_version")
            if not self.input_artifact_ids:
                errors.append("FULL_POINT_IN_TIME requires input artifacts")
            if knowledge is not None and decision is not None and knowledge > decision:
                errors.append("knowledge_at_utc cannot be after decision_at_utc")

        if self.lineage_class == "UNUSABLE_FOR_BT10" and not self.exclusion_reason:
            errors.append("UNUSABLE_FOR_BT10 requires exclusion_reason")
        return errors


@dataclass(frozen=True)
class CounterfactualDeploymentRow:
    event_id: str
    policy_id: str
    event_knowledge_at_utc: str
    decision_at_utc: str
    execution_at_utc: str
    label_end_utc: str
    entry_price: float
    horizon_price: float
    realized_delta: float
    foregone_delta: float
    maximum_adverse_excursion: float
    maximum_favorable_excursion: float
    drawdown_avoided: float
    opportunity_cost: float
    regret_sign: str
    source_hashes: tuple[str, ...]

    def validate(self) -> list[str]:
        errors: list[str] = []
        knowledge = _parse_utc(self.event_knowledge_at_utc)
        decision = _parse_utc(self.decision_at_utc)
        execution = _parse_utc(self.execution_at_utc)
        label_end = _parse_utc(self.label_end_utc)
        if not knowledge <= decision <= execution < label_end:
            errors.append("temporal order must satisfy knowledge <= decision <= execution < label_end")
        if self.entry_price <= 0.0 or self.horizon_price <= 0.0:
            errors.append("prices must be positive")
        if self.regret_sign not in {"POSITIVE", "NEGATIVE", "ZERO"}:
            errors.append("regret_sign must be POSITIVE, NEGATIVE or ZERO")
        if not self.source_hashes:
            errors.append("at least one source hash is required")
        return errors


def validate_decision_lineage(rows: Iterable[DecisionLineageRow]) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    seen: set[str] = set()
    counts = {lineage_class: 0 for lineage_class in sorted(LINEAGE_CLASSES)}

    for row in rows:
        if row.record_id in seen:
            errors.append({"record_id": row.record_id, "errors": ["duplicate record_id"]})
        seen.add(row.record_id)
        counts[row.lineage_class] = counts.get(row.lineage_class, 0) + 1
        row_errors = row.validate()
        if row_errors:
            errors.append({"record_id": row.record_id, "errors": row_errors})

    return {
        "status": "PASS" if not errors else "FAIL",
        "row_count": len(seen),
        "lineage_counts": counts,
        "errors": errors,
        "bt10_eligible_rows": counts.get("FULL_POINT_IN_TIME", 0),
    }
