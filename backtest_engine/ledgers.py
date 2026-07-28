from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


LEGACY_LINEAGE_CLASSES = {
    "FULL_POINT_IN_TIME",
    "PARTIAL_POINT_IN_TIME",
    "RETROSPECTIVE_RECONSTRUCTION",
    "UNUSABLE_FOR_BT10",
}

REPAIR_CLASSES = {
    "A_FULLY_REPLAYABLE",
    "B_PARTIALLY_RECONSTRUCTABLE",
    "C_QUARANTINED",
}

TIME_PRECISIONS = {"EXACT", "UPPER_BOUND", "DATE_ONLY", "RANGE", "UNKNOWN"}


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
        if self.lineage_class not in LEGACY_LINEAGE_CLASSES:
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
class DecisionLineageRepairRow:
    record_id: str
    record_type: str
    repair_class: str
    event_at_utc: str | None
    event_time_precision: str
    knowledge_at_utc: str | None
    knowledge_time_precision: str
    decision_at_utc: str | None
    execution_at_utc: str | None
    label_end_utc: str | None
    policy_version: str | None
    state_before: str | None
    state_after: str | None
    action_permission: str | None
    transaction_cost_contract: str | None
    source_artifact_ids: tuple[str, ...]
    source_hashes: tuple[str, ...]
    missing_required_fields: tuple[str, ...]
    exclusion_reason: str | None = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.record_id:
            errors.append("record_id is required")
        if self.repair_class not in REPAIR_CLASSES:
            errors.append(f"unsupported repair_class: {self.repair_class}")
        if self.event_time_precision not in TIME_PRECISIONS:
            errors.append("unsupported event_time_precision")
        if self.knowledge_time_precision not in TIME_PRECISIONS:
            errors.append("unsupported knowledge_time_precision")
        if len(self.source_artifact_ids) != len(self.source_hashes):
            errors.append("source artifact and hash counts differ")
        if not self.source_artifact_ids:
            errors.append("at least one source artifact is required")

        parsed: dict[str, datetime] = {}
        for field, value in {
            "event_at_utc": self.event_at_utc,
            "knowledge_at_utc": self.knowledge_at_utc,
            "decision_at_utc": self.decision_at_utc,
            "execution_at_utc": self.execution_at_utc,
            "label_end_utc": self.label_end_utc,
        }.items():
            if value:
                try:
                    parsed[field] = _parse_utc(value)
                except ValueError as exc:
                    errors.append(str(exc))

        if self.repair_class == "A_FULLY_REPLAYABLE":
            required = {
                "event_at_utc": self.event_at_utc,
                "knowledge_at_utc": self.knowledge_at_utc,
                "decision_at_utc": self.decision_at_utc,
                "execution_at_utc": self.execution_at_utc,
                "label_end_utc": self.label_end_utc,
                "policy_version": self.policy_version,
                "transaction_cost_contract": self.transaction_cost_contract,
            }
            absent = [field for field, value in required.items() if not value]
            if absent:
                errors.append(f"A_FULLY_REPLAYABLE missing: {','.join(absent)}")
            if self.missing_required_fields:
                errors.append("A_FULLY_REPLAYABLE cannot declare missing required fields")
            if self.event_time_precision != "EXACT" or self.knowledge_time_precision != "EXACT":
                errors.append("A_FULLY_REPLAYABLE requires exact event and knowledge times")
        if self.repair_class == "B_PARTIALLY_RECONSTRUCTABLE" and not self.missing_required_fields:
            errors.append("B_PARTIALLY_RECONSTRUCTABLE must list missing required fields")
        if self.repair_class == "C_QUARANTINED" and not self.exclusion_reason:
            errors.append("C_QUARANTINED requires exclusion_reason")

        knowledge = parsed.get("knowledge_at_utc")
        decision = parsed.get("decision_at_utc")
        execution = parsed.get("execution_at_utc")
        label_end = parsed.get("label_end_utc")
        if knowledge and decision and knowledge > decision:
            errors.append("knowledge_at_utc cannot be after decision_at_utc")
        if decision and execution and decision > execution:
            errors.append("decision_at_utc cannot be after execution_at_utc")
        if execution and label_end and execution >= label_end:
            errors.append("execution_at_utc must be before label_end_utc")
        return errors

    @property
    def policy_replay_eligible(self) -> bool:
        return self.repair_class == "A_FULLY_REPLAYABLE" and not self.validate()


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
    counts = {lineage_class: 0 for lineage_class in sorted(LEGACY_LINEAGE_CLASSES)}
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


def validate_repair_ledger(rows: Iterable[DecisionLineageRepairRow]) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    seen: set[str] = set()
    counts = {repair_class: 0 for repair_class in sorted(REPAIR_CLASSES)}
    replayable = 0
    for row in rows:
        if row.record_id in seen:
            errors.append({"record_id": row.record_id, "errors": ["duplicate record_id"]})
        seen.add(row.record_id)
        counts[row.repair_class] = counts.get(row.repair_class, 0) + 1
        row_errors = row.validate()
        if row_errors:
            errors.append({"record_id": row.record_id, "errors": row_errors})
        elif row.policy_replay_eligible:
            replayable += 1
    return {
        "status": "PASS" if not errors else "FAIL",
        "row_count": len(seen),
        "repair_class_counts": counts,
        "policy_replay_eligible_rows": replayable,
        "actual_policy_replay_unlocked": replayable > 0,
        "errors": errors,
    }
