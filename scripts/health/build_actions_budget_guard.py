from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
STATE_ORDER = {"NORMAL": 0, "ELEVATED": 1, "CONSERVE": 2, "CRITICAL": 3, "UNKNOWN": 4}


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def parse_date(value: Any):
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def unknown_state(now: datetime, reason: str, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "contract": "GITHUB_ACTIONS_BUDGET_STATE_v1",
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "state": "UNKNOWN",
        "snapshot_status": reason,
        "usage_snapshot": snapshot or {},
        "usage_pct": None,
        "projected_cycle_minutes": None,
        "projected_cycle_pct": None,
        "reset_eta_days": None,
        "burn_risk": "HIGH",
        "deferred_class_c": None,
        "protected_a_blocked": None,
        "recommended_behavior": [
            "Do not invent billing usage.",
            "Refresh the external/manual GitHub Actions usage snapshot.",
            "Preserve protected Class A duties and avoid blind reruns until capacity is known.",
        ],
        "authority": {
            "budget_self_increase": False,
            "workflow_disable": False,
            "market_semantics": False,
            "portfolio_action": False,
        },
    }


def evaluate(snapshot: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    now = (now or datetime.now(UTC)).astimezone(UTC)
    if snapshot.get("contract") != "GITHUB_ACTIONS_USAGE_SNAPSHOT_v1":
        return unknown_state(now, "INVALID_CONTRACT", snapshot)

    observed = parse_ts(snapshot.get("observed_at_utc"))
    cycle_start = parse_date(snapshot.get("cycle_start_date_utc"))
    reset_date = parse_date(snapshot.get("reset_date_utc"))
    try:
        used = float(snapshot.get("used_minutes"))
        allowance = float(snapshot.get("included_minutes"))
        freshness_max_hours = float(snapshot.get("freshness_max_hours", 72))
    except (TypeError, ValueError):
        return unknown_state(now, "INVALID_NUMERIC_FIELDS", snapshot)

    if not observed or not cycle_start or not reset_date or used < 0 or allowance <= 0:
        return unknown_state(now, "INVALID_SNAPSHOT_FIELDS", snapshot)

    reset_dt = datetime.combine(reset_date, time.min, tzinfo=UTC)
    cycle_start_dt = datetime.combine(cycle_start, time.min, tzinfo=UTC)
    if reset_dt <= cycle_start_dt:
        return unknown_state(now, "INVALID_CYCLE_WINDOW", snapshot)

    if observed < cycle_start_dt or observed >= reset_dt:
        return unknown_state(now, "SNAPSHOT_OUTSIDE_CYCLE", snapshot)

    if now >= reset_dt and observed < reset_dt:
        return unknown_state(now, "SNAPSHOT_PRE_RESET", snapshot)

    age_hours = max(0.0, (now - observed).total_seconds() / 3600.0)
    if age_hours > freshness_max_hours:
        state = unknown_state(now, "STALE_USAGE_SNAPSHOT", snapshot)
        state["snapshot_age_hours"] = round(age_hours, 3)
        return state

    usage_pct = used / allowance * 100.0
    cycle_seconds = (reset_dt - cycle_start_dt).total_seconds()
    elapsed_seconds = max(1.0, min((observed - cycle_start_dt).total_seconds(), cycle_seconds))
    elapsed_fraction = elapsed_seconds / cycle_seconds
    projected_minutes = used / elapsed_fraction if elapsed_fraction > 0 else None
    projected_pct = projected_minutes / allowance * 100.0 if projected_minutes is not None else None
    reset_eta_days = max(0, math.ceil((reset_dt - now).total_seconds() / 86400.0))

    state = "NORMAL"
    if usage_pct >= 90.0 or (projected_pct is not None and projected_pct >= 110.0):
        state = "CRITICAL"
    elif usage_pct >= 80.0 or (projected_pct is not None and projected_pct >= 100.0):
        state = "CONSERVE"
    elif usage_pct >= 65.0 or (projected_pct is not None and projected_pct >= 85.0):
        state = "ELEVATED"

    stop_usage = bool(snapshot.get("stop_usage"))
    protected_blocked = bool(stop_usage and used >= allowance)
    if protected_blocked:
        state = "CRITICAL"

    behavior = {
        "NORMAL": [
            "Keep current cadence.",
            "Continue normal targeted validation and evidence refresh.",
        ],
        "ELEVATED": [
            "Deduplicate equivalent work and prefer cached/current artifacts.",
            "Prefer targeted failed-job reruns over full-workflow reruns.",
            "Avoid new recurring workflows when an existing owner can absorb the duty.",
        ],
        "CONSERVE": [
            "Permit protected Class A duties.",
            "Reduce or event-drive routine Class B work where semantics are unchanged.",
            "Defer Class C backfills, exploratory sweeps and duplicate audits by default.",
            "Do not use broad reruns when targeted verification is sufficient.",
        ],
        "CRITICAL": [
            "Reserve remaining capacity for protected Class A duties.",
            "Block/defer Class C work and run Class B only when materially necessary.",
            "Do not blind-rerun deterministic failures.",
            "Escalate if protected duties are blocked by the account hard stop.",
        ],
    }[state]

    return {
        "contract": "GITHUB_ACTIONS_BUDGET_STATE_v1",
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "state": state,
        "snapshot_status": "FRESH",
        "snapshot_age_hours": round(age_hours, 3),
        "usage_snapshot": {
            "source_type": snapshot.get("source_type"),
            "source_ref": snapshot.get("source_ref"),
            "observed_at_utc": snapshot.get("observed_at_utc"),
            "cycle_start_date_utc": snapshot.get("cycle_start_date_utc"),
            "reset_date_utc": snapshot.get("reset_date_utc"),
            "used_minutes": used,
            "included_minutes": allowance,
            "stop_usage": stop_usage,
        },
        "usage_pct": round(usage_pct, 3),
        "projected_cycle_minutes": round(projected_minutes, 3) if projected_minutes is not None else None,
        "projected_cycle_pct": round(projected_pct, 3) if projected_pct is not None else None,
        "reset_eta_days": reset_eta_days,
        "burn_risk": {"NORMAL": "LOW", "ELEVATED": "MODERATE", "CONSERVE": "HIGH", "CRITICAL": "CRITICAL"}[state],
        "deferred_class_c": None,
        "protected_a_blocked": protected_blocked,
        "recommended_behavior": behavior,
        "authority": {
            "budget_self_increase": False,
            "workflow_disable": False,
            "market_semantics": False,
            "portfolio_action": False,
        },
    }


def render_markdown(state: dict[str, Any]) -> str:
    snap = state.get("usage_snapshot") or {}
    used = snap.get("used_minutes")
    allowance = snap.get("included_minutes")
    usage = "UNKNOWN" if used is None or allowance is None else f"{used:g}/{allowance:g}"
    lines = [
        "# GitHub Actions Budget Guard",
        "",
        f"- ACTIONS_BUDGET: **{state.get('state', 'UNKNOWN')}**",
        f"- USAGE_SNAPSHOT: {usage}",
        f"- SNAPSHOT_STATUS: {state.get('snapshot_status', 'UNKNOWN')}",
        f"- RESET_ETA_DAYS: {state.get('reset_eta_days') if state.get('reset_eta_days') is not None else 'UNKNOWN'}",
        f"- BURN_RISK: {state.get('burn_risk', 'HIGH')}",
        f"- DEFERRED_CLASS_C: {state.get('deferred_class_c') if state.get('deferred_class_c') is not None else 'UNKNOWN'}",
        f"- PROTECTED_A_BLOCKED: {'YES' if state.get('protected_a_blocked') is True else 'NO' if state.get('protected_a_blocked') is False else 'UNKNOWN'}",
        "",
        "## Required behavior",
    ]
    lines.extend(f"- {item}" for item in state.get("recommended_behavior", []))
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", type=Path, required=True)
    ap.add_argument("--json-output", type=Path, required=True)
    ap.add_argument("--md-output", type=Path, required=True)
    ap.add_argument("--now")
    args = ap.parse_args()
    now = parse_ts(args.now) if args.now else datetime.now(UTC)
    if now is None:
        raise SystemExit("invalid --now timestamp")
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        snapshot = {}
    state = evaluate(snapshot, now)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.md_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_output.write_text(render_markdown(state), encoding="utf-8")
    print(f"ACTIONS_BUDGET={state['state']}")
    print(f"SNAPSHOT_STATUS={state['snapshot_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
