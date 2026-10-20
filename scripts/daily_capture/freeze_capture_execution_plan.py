#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "DAILY_LIVE_ANCHOR_EXECUTION_PLAN_v2"
OWNER_IDS = {
    "fred_macro", "binance_spot", "binance_microstructure",
    "okx_swap", "top100_breadth", "cfgi_sentiment",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def build_plan(
    *,
    run_id: str,
    trigger: str,
    schedule_id: str,
    slow_macro_planned: bool,
    slow_macro_reason: str,
    planned_at_utc: str | None = None,
) -> dict[str, Any]:
    if not run_id.strip() or not trigger.strip():
        raise ValueError("run_identity_required")
    planned = planned_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    expected = {
        "fred_macro": "PASS" if slow_macro_planned else "DISABLED",
        "binance_spot": "DISABLED",
        "binance_microstructure": "PASS",
        "okx_swap": "PASS",
        "top100_breadth": "PASS",
        "cfgi_sentiment": "PASS",
    }
    plan = {
        "contract": CONTRACT,
        "run_id": run_id,
        "planned_at_utc": planned,
        "trigger": trigger,
        "schedule_id": schedule_id or None,
        "slow_macro_planned": slow_macro_planned,
        "slow_macro_reason": slow_macro_reason,
        "expected_owner_statuses": expected,
        "intent_basis": "WORKFLOW_TRIGGER_AND_SLOW_MACRO_DECISION_ONLY",
        "frozen_before_owner_execution": True,
        "outcome_independent": True,
    }
    plan["plan_sha256"] = digest({k: v for k, v in plan.items() if k != "plan_sha256"})
    return plan


def validate_plan(plan: Any) -> dict[str, Any]:
    if not isinstance(plan, dict) or plan.get("contract") != CONTRACT:
        raise ValueError("execution_plan_contract_invalid")
    expected = plan.get("expected_owner_statuses")
    if not isinstance(expected, dict) or set(expected) != OWNER_IDS:
        raise ValueError("execution_plan_owner_set_invalid")
    if any(value not in {"PASS", "DISABLED"} for value in expected.values()):
        raise ValueError("execution_plan_owner_status_invalid")
    if plan.get("intent_basis") != "WORKFLOW_TRIGGER_AND_SLOW_MACRO_DECISION_ONLY":
        raise ValueError("execution_plan_intent_basis_invalid")
    if plan.get("frozen_before_owner_execution") is not True or plan.get("outcome_independent") is not True:
        raise ValueError("execution_plan_not_pre_frozen")
    declared = plan.get("plan_sha256")
    actual = digest({k: v for k, v in plan.items() if k != "plan_sha256"})
    if not isinstance(declared, str) or declared != actual:
        raise ValueError("execution_plan_hash_invalid")
    return plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--schedule-id", default="")
    parser.add_argument("--slow-macro-planned", choices=("true", "false"), required=True)
    parser.add_argument("--slow-macro-reason", required=True)
    parser.add_argument("--planned-at-utc")
    args = parser.parse_args()
    plan = build_plan(
        run_id=args.run_id,
        trigger=args.trigger,
        schedule_id=args.schedule_id,
        slow_macro_planned=args.slow_macro_planned == "true",
        slow_macro_reason=args.slow_macro_reason,
        planned_at_utc=args.planned_at_utc,
    )
    validate_plan(plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(plan))
    print(json.dumps({"status": "PASS", "contract": CONTRACT, "run_id": plan["run_id"], "plan_sha256": plan["plan_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
