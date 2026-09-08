"""Deterministic admission for two separate resource pools. Never grants spend."""
from __future__ import annotations

import calendar
import math
from datetime import datetime, timedelta, timezone


def amount(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"invalid_resource_amount:{name}")
    return float(value)


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("resource_timestamp_required")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.utcoffset() is None:
        raise ValueError("resource_timezone_required")
    return dt.astimezone(timezone.utc)


def monthly_allowance(policy, spent, *, now=None):
    now = now or datetime.now(timezone.utc)
    spent = amount(spent, "spent")
    hard = amount(policy["monthly_hard_stop_usd"], "hard_stop")
    reserve = amount(policy["global_reserve_usd"], "reserve")
    if reserve > hard:
        raise ValueError("reserve_exceeds_monthly_cap")
    pacing = policy["resource_pacing"]
    days = calendar.monthrange(now.year, now.month)[1]
    # Two days of bounded headroom; unspent headroom accumulates through the month.
    fraction = min(1.0, (now.day + amount(pacing["monthly_headroom_days"], "headroom_days")) / days)
    ceiling = (hard - reserve) * fraction
    return max(0.0, min(hard - reserve - spent, ceiling - spent))


def api_admission(policy, snapshot, cost, *, now=None):
    now = now or datetime.now(timezone.utc)
    cost = amount(cost, "request_cost")
    if snapshot.get("contract") != "API_BUDGET_SNAPSHOT_v1" or snapshot.get("status") != "PASS":
        raise ValueError("verified_api_budget_snapshot_required")
    observed = timestamp(snapshot.get("generated_at_utc"))
    if not 0 <= (now - observed).total_seconds() <= 900 or snapshot.get("month") != now.strftime("%Y-%m"):
        raise ValueError("api_budget_snapshot_stale")
    available = monthly_allowance(policy, snapshot["spent_usd"], now=now)
    available = min(available, amount(snapshot["lane_remaining_usd"], "lane_remaining"))
    return {"status": "PASS" if cost <= available else "DEFER_BUDGET", "available_usd": round(available, 8), "reserved_cost_usd": cost}


def codex_admission(policy, snapshot, effort, estimated_usage_percent, *, now=None):
    """Telemetry is host supplied, never inferred from API dollars or weekday."""
    now = now or datetime.now(timezone.utc)
    pacing = policy["codex_usage"]
    if not isinstance(snapshot, dict) or snapshot.get("contract") != "CODEX_USAGE_SNAPSHOT_v1":
        return {"status": "WAITING_FOR_USAGE", "reason": "CODEX_QUOTA_UNAVAILABLE", "max_effort_allowed": False}
    try:
        observed = timestamp(snapshot.get("observed_at_utc"))
        start = timestamp(snapshot.get("weekly_window_start_utc"))
        reset = timestamp(snapshot.get("weekly_reset_at_utc"))
        if snapshot.get("source") != "CODEX_HOST_USAGE" or not 0 <= (now - observed).total_seconds() <= pacing["telemetry_max_age_seconds"]:
            raise ValueError("codex_usage_stale_or_unverified")
        if reset - start != timedelta(days=7) or not start <= now < reset:
            raise ValueError("codex_reset_window_invalid")
        used = amount(snapshot["weekly_used_percent"], "weekly_used")
        daily = amount(snapshot["rolling_24h_used_percent"], "rolling_daily_used")
        pending = amount(snapshot["reserved_percent"], "reserved")
        estimate = amount(estimated_usage_percent, "estimated_usage")
        short_remaining = amount(snapshot["short_window_remaining_percent"], "short_remaining")
        short_estimate = amount(snapshot["estimated_short_window_usage_percent"], "short_estimate")
        if any(v > 100 for v in (used, daily, pending, estimate, short_remaining, short_estimate)) or estimate == 0 or short_estimate == 0:
            raise ValueError("codex_usage_out_of_range")
        reserve = amount(pacing["weekly_reserve_percent"], "weekly_reserve")
        daily_cap = amount(pacing["rolling_24h_cap_percent"], "daily_cap")
        elapsed_days = (now - start).total_seconds() / 86400
        paced_ceiling = (100 - reserve) * min(1.0, (elapsed_days + 1) / 7)
        allowance = max(0.0, min(100 - reserve - used - pending, paced_ceiling - used - pending, daily_cap - daily - pending))
        if effort == "max" and elapsed_days < pacing["max_effort_minimum_elapsed_days"]:
            return {"status": "DEFER_USAGE", "reason": "MAX_EFFORT_RESET_DAY_PROTECTION", "max_effort_allowed": False}
        allowed = estimate <= allowance and short_estimate <= short_remaining
        return {"status": "PASS" if allowed else "DEFER_USAGE", "reason": "WITHIN_PACING" if allowed else "CODEX_USAGE_PACING", "available_percent": round(allowance, 4), "max_effort_allowed": allowed and elapsed_days >= pacing["max_effort_minimum_elapsed_days"]}
    except (KeyError, TypeError, ValueError, OverflowError):
        return {"status": "WAITING_FOR_USAGE", "reason": "CODEX_QUOTA_INVALID_OR_STALE", "max_effort_allowed": False}
