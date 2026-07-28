from __future__ import annotations

from datetime import datetime


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone-aware timestamp required")
    return parsed


def validate_prospective_receipt(row: dict) -> list[str]:
    required = {
        "event_id",
        "policy_family",
        "rule_version",
        "knowledge_at_utc",
        "decision_at_utc",
        "execution_at_utc",
        "label_end_utc",
        "action_permission",
        "source_hashes",
        "transaction_cost_contract",
    }
    errors: list[str] = []
    missing = required - set(row)
    if missing:
        errors.append(f"missing required fields: {sorted(missing)}")
        return errors

    knowledge, decision, execution, label_end = map(
        _parse_utc,
        [
            row["knowledge_at_utc"],
            row["decision_at_utc"],
            row["execution_at_utc"],
            row["label_end_utc"],
        ],
    )
    if not knowledge <= decision <= execution < label_end:
        errors.append("temporal order violation")
    if not row["source_hashes"]:
        errors.append("source hashes required")
    if row["action_permission"] == "NONE" and not row.get("no_action_reason"):
        errors.append("NONE action requires no_action_reason")
    return errors


def retrospective_policy_quarantine(horizon_end_utc: str, created_at_utc: str) -> bool:
    return _parse_utc(created_at_utc) > _parse_utc(horizon_end_utc)
