from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def classify_guard(row: Any, rc: int, label: str) -> str:
    if not isinstance(row, dict):
        raise ValueError(f"budget_guard_output_invalid:{label}:object_required")
    status = row.get("status")
    errors = row.get("cost_evidence_errors")
    remaining = row.get("remaining_usd")
    reserve = row.get("reserve_usd")
    if status == "PASS":
        if rc != 0 or errors:
            raise ValueError(f"budget_guard_pass_inconsistent:{label}")
        return "PASS"
    clean_hold = (
        status == "BLOCKED"
        and rc != 0
        and errors == []
        and isinstance(remaining, (int, float))
        and not isinstance(remaining, bool)
        and isinstance(reserve, (int, float))
        and not isinstance(reserve, bool)
        and remaining <= reserve
    )
    if not clean_hold:
        raise ValueError(f"budget_guard_block_not_clean:{label}")
    return "HOLD"


def decide(
    decision_row: Any,
    decision_rc: int,
    validation_row: Any,
    validation_rc: int,
    monthly_row: Any,
    monthly_rc: int,
) -> dict[str, str]:
    decision_state = classify_guard(decision_row, decision_rc, "DECISION_MISS_AUDIT")
    validation_state = classify_guard(validation_row, validation_rc, "EVIDENCE_GAP_VALIDATION")
    monthly_state = classify_guard(monthly_row, monthly_rc, "MONTHLY_API_COST")

    monthly_pass = monthly_state == "PASS"
    decision_eligible = monthly_pass and decision_state == "PASS"
    validation_eligible = monthly_pass and validation_state == "PASS"

    def reason(lane: str, lane_state: str) -> str:
        if monthly_state != "PASS":
            return "MONTHLY_API_COST"
        if lane_state != "PASS":
            return lane
        return "NONE"

    return {
        "decision_eligible": "true" if decision_eligible else "false",
        "validation_eligible": "true" if validation_eligible else "false",
        "decision_hold_reason": reason("DECISION_MISS_AUDIT", decision_state),
        "validation_hold_reason": reason("EVIDENCE_GAP_VALIDATION", validation_state),
        "monthly_state": monthly_state,
    }


def read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"budget_guard_output_invalid:{label}:{exc}") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-json", type=Path, required=True)
    parser.add_argument("--decision-rc", type=int, required=True)
    parser.add_argument("--validation-json", type=Path, required=True)
    parser.add_argument("--validation-rc", type=int, required=True)
    parser.add_argument("--monthly-json", type=Path, required=True)
    parser.add_argument("--monthly-rc", type=int, required=True)
    parser.add_argument("--github-output", type=Path, required=True)
    args = parser.parse_args()

    result = decide(
        read_json(args.decision_json, "DECISION_MISS_AUDIT"),
        args.decision_rc,
        read_json(args.validation_json, "EVIDENCE_GAP_VALIDATION"),
        args.validation_rc,
        read_json(args.monthly_json, "MONTHLY_API_COST"),
        args.monthly_rc,
    )
    with args.github_output.open("a", encoding="utf-8") as handle:
        for key, value in result.items():
            handle.write(f"{key}={value}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
