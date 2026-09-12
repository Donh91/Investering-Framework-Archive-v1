"""Pre-call budget checks for the existing text-only API gateway.

Reservations survive process failure within a checkout. Cross-run crash safety
still requires the workflow to publish/reconcile them before another paid run.
"""
from __future__ import annotations

import json
import subprocess
import sys
import uuid
import fcntl
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.api_agent.resource_budget import amount, monthly_allowance
except ModuleNotFoundError:
    from resource_budget import amount, monthly_allowance

ROOT = Path(__file__).resolve().parents[2]


def retry_output_limit(initial):
    return min(max(int(initial) * 2, 2400), 5000)


def request_ceiling(payload, estimate_cost):
    if payload.get("tools") or payload.get("previous_response_id") or payload.get("conversation"):
        raise ValueError("unbounded_tool_or_conversation_cost")
    if payload.get("service_tier", "default") not in {"default", "flex"}:
        raise ValueError("premium_service_tier_not_budgeted")
    output = payload.get("max_output_tokens")
    if type(output) is not int or not 1 <= output <= 128000:
        raise ValueError("bounded_output_tokens_required")
    # Conservative UTF-8 byte bound plus framing/schema overhead. This gateway
    # accepts text-only input, without hidden history or server tool loops.
    wire = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    input_bound = len(wire) + 8192
    return estimate_cost(payload["model"], input_bound, output)


def _guard(script, args):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/api_agent" / script), *args], cwd=ROOT, capture_output=True, text=True)
    try:
        result = json.loads(proc.stdout)
    except (ValueError, TypeError):
        raise ValueError("budget_evidence_unavailable") from None
    if proc.returncode or result.get("status") != "PASS":
        raise ValueError("budget_evidence_or_remaining_balance_blocked")
    return result


def reserve(task, payload, registry, estimate_cost):
    lock_root = ROOT / "runtime/api-cost-ledger"
    lock_root.mkdir(parents=True, exist_ok=True)
    with (lock_root / ".reservation.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _reserve_locked(task, payload, registry, estimate_cost)


def _reserve_locked(task, payload, registry, estimate_cost):
    policy = json.loads((ROOT / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json").read_text())
    first = request_ceiling(payload, estimate_cost)
    retry_limit = min(retry_output_limit(payload["max_output_tokens"]), registry["tasks"][task].get("retry_max_output_tokens", 128000))
    retry = dict(payload, max_output_tokens=retry_limit)
    maximum = first + request_ceiling(retry, estimate_cost)
    if maximum > amount(registry["single_run_hard_stop_usd"], "single_run_cap"):
        raise ValueError("single_run_budget_would_be_exceeded")
    hard = min(amount(registry["monthly_hard_stop_usd"], "registry_monthly_cap"), amount(policy["monthly_hard_stop_usd"], "monthly_cap"))
    state = _guard("check_monthly_cost_guard.py", ["--receipt-root", "research/api_agent/outputs", "--pending-ledger-root", "runtime/api-cost-ledger", "--hard-stop-usd", str(hard), "--reserve-usd", str(policy["global_reserve_usd"])])
    policy = dict(policy, monthly_hard_stop_usd=hard)
    available = monthly_allowance(policy, state["spent_usd"])
    lane = policy.get("task_lanes", {}).get(task, task)
    if lane not in policy["lane_caps_usd"]:
        raise ValueError("task_budget_lane_not_contracted")
    lane_args = ["--receipt-root", "research/api_agent/outputs", "--task", lane, "--cap-usd", str(policy["lane_caps_usd"][lane]), "--reserve-usd", "0"]
    for alias, owner in policy.get("task_lanes", {}).items():
        if owner == lane:
            lane_args.extend(["--include-task", alias])
    lane_state = _guard("check_api_lane_budget.py", lane_args)
    # Pending calls are conservatively charged to the selected lane as well.
    pending_root = ROOT / "runtime/api-cost-ledger"
    pending_cost = 0.0
    if pending_root.exists():
        for path in pending_root.glob("*.json"):
            item = json.loads(path.read_text())
            if item.get("budget_lane") == lane and item.get("budget_month") == state["month"]:
                pending_cost += amount(item.get("estimated_cost_usd"), "pending_cost")
    available = min(available, lane_state["remaining_usd"] - pending_cost)
    if maximum > available:
        raise ValueError("monthly_or_lane_pacing_deferred")
    pending_root.mkdir(parents=True, exist_ok=True)
    path = pending_root / (uuid.uuid4().hex + ".json")
    value = {"contract": "API_COST_RESERVATION_v1", "task": task, "budget_lane": lane, "budget_month": state["month"], "created_at_utc": datetime.now(timezone.utc).isoformat(), "estimated_cost_usd": maximum, "status": "RESERVED_OR_UNKNOWN", "maximum_cost_usd": maximum}
    # Exclusive creation. Paid calls occur only after the reservation is written.
    with path.open("x") as handle:
        json.dump(value, handle, sort_keys=True, allow_nan=False)
        handle.flush()
        import os
        os.fsync(handle.fileno())
    return path, value


def settle(path, reservation, receipt):
    value = {**reservation, "status": "SETTLED", "estimated_cost_usd": receipt["estimated_cost_usd"], "response_id": receipt.get("response_id"), "response_ids": receipt.get("response_ids"), "created_unix": receipt["created_unix"]}
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, sort_keys=True, allow_nan=False) + "\n")
    temp.replace(path)
