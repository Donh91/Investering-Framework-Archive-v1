"""Classify the existing routine API guards without granting new paid authority.

Draft integration only: the caller must gate every paid/producer step on PASS.
HOLD is a non-execution disposition, not a completed analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LANES = {
    "research": ("RESEARCH_AUTOMATION", 10.0, 0.25, False),
    "director": ("DAILY_DIRECTOR_SHADOW", 4.0, 0.05, True),
}


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate key")
        value[key] = item
    return value


def classify(kind, result, lane):
    """Only exact clean reserve denials may become a neutral HOLD."""
    if lane not in LANES or kind not in {"lane", "monthly"}:
        return "ERROR", "UNKNOWN_GUARD"
    task, cap, reserve, _ = LANES[lane]
    try:
        row = json.loads(result.stdout, object_pairs_hook=_object,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
    except (TypeError, ValueError):
        return "ERROR", "GUARD_OUTPUT_INVALID"
    if not isinstance(row, dict) or row.get("fail_closed") is not True or row.get("cost_evidence_errors") != []:
        return "ERROR", "GUARD_EVIDENCE_UNVERIFIED"
    remaining = row.get("remaining_usd")
    actual_reserve = row.get("reserve_usd")
    if not _number(remaining) or not _number(actual_reserve):
        return "ERROR", "GUARD_BUDGET_INVALID"
    if kind == "lane":
        if row.get("task") != task or row.get("cap_usd") != cap or actual_reserve != reserve:
            return "ERROR", "LANE_CONTRACT_MISMATCH"
        exhausted = remaining <= reserve
        expected_error = "api_lane_budget_blocked"
    else:
        owner_remaining = row.get("owner_global_remaining_usd_after_risk")
        owner_reserve = row.get("owner_global_reserve_usd")
        if (row.get("requested_hard_stop_usd") != 40 or row.get("effective_hard_stop_usd") != 40
                or actual_reserve != 4.0 or row.get("historical_pr_audit_only") is not False
                or row.get("paid_authority") is not False or row.get("malformed_cost_receipts") != []
                or not _number(owner_remaining) or not _number(owner_reserve) or owner_reserve != 4.0):
            return "ERROR", "MONTHLY_CONTRACT_MISMATCH"
        exhausted = remaining <= actual_reserve or owner_remaining < owner_reserve
        expected_error = "monthly_api_cost_guard_blocked"
    if result.returncode == 0 and row.get("status") == "PASS" and not result.stderr.strip() and not exhausted:
        return "PASS", "GUARD_PASS"
    if (result.returncode == 1 and row.get("status") == "BLOCKED"
            and result.stderr.strip() == expected_error and exhausted):
        return "HOLD", "API_RESERVE_GUARD_BLOCKED"
    return "ERROR", "UNCLASSIFIED_GUARD_RESULT"


def run_guards(lane, runner=subprocess.run):
    task, cap, reserve, pending = LANES[lane]
    base = ["--receipt-root", "research/api_agent/outputs"]
    commands = [
        ("lane", [sys.executable, "scripts/api_agent/check_api_lane_budget.py", *base,
                  "--task", task, "--cap-usd", str(cap), "--reserve-usd", str(reserve)]),
        ("monthly", [sys.executable, "scripts/api_agent/check_monthly_cost_guard.py", *base,
                     *(["--pending-ledger-root", "runtime/api-cost-ledger"] if pending else []),
                     "--hard-stop-usd", "40", "--reserve-usd", "4.0"]),
    ]
    observations = []
    for kind, command in commands:
        result = runner(command, cwd=ROOT, capture_output=True, text=True, check=False)
        disposition, reason = classify(kind, result, lane)
        observations.append({
            "guard": kind, "returncode": result.returncode,
            "disposition": disposition, "reason": reason,
            "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
        })
        if disposition != "PASS":
            return disposition, reason, observations
    return "PASS", "BOTH_EXISTING_GUARDS_PASS", observations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", choices=sorted(LANES), required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    disposition, reason, observations = run_guards(args.lane)
    receipt = {
        "contract": "ROUTINE_API_BUDGET_DISPOSITION_v1",
        "lane": args.lane, "disposition": disposition, "reason": reason,
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "head_sha": os.environ.get("GITHUB_SHA"),
        "guard_observations": observations,
        "paid_call_executed_here": False, "analysis_completed_here": False,
        "paid_authority": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    # On ERROR no success output is issued. HOLD never grants a paid call.
    if disposition == "ERROR":
        raise SystemExit(reason)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a") as out:
            out.write(f"Routine API guard: {disposition} ({reason})\n")
    print(f"disposition={disposition}")


if __name__ == "__main__":
    main()
