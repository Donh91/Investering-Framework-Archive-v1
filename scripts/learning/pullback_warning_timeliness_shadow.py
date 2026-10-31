"""Bounded post-issuance pullback warning accountability, research ONLY.

Do not confuse sustained market-risk state (ELEVATED) with a new time-bound
predictive warning. No live alerts, calibrated likelihoods, model reweights,
portfolio decisions, first-known/edge claims or source-authority upgrades.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
import math
from typing import Any

CONTRACT = "PULLBACK_RADAR_TIMEBOX_SHADOW_v1"
HOUR = timedelta(hours=1)
# Research hypotheses fixed for FORWARD evaluation. This historical replay
# is DEVELOPMENT_ONLY; thresholds are NOT official pullback classifications.
HORIZONS = {"12h": (12, -1.5), "24h": (24, -2.5), "72h": (72, -4.0)}
RANK = {"NORMAL": 0, "BUILDING": 1, "ELEVATED": 2, "HIGH": 3, "CONFIRMED": 4}
TRUST_GAP_HOURS = 24
EXPIRY_HOURS = 72


def iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def target_close_after(issued: datetime) -> datetime:
    """First completed UTC hourly candle STRICTLY after issuance."""
    utc = issued.astimezone(timezone.utc)
    start = utc.replace(minute=0, second=0, microsecond=0)
    if utc != start:
        start += HOUR
    # Entire bar must open at or after issue. Do not use the straddling bar.
    return start + HOUR


def evaluate_path(issued: datetime, asof: datetime, market: dict, horizon_hours: int,
                  barrier_pct: float) -> dict[str, Any]:
    """Post-alert close-only downside: no intrahour lookahead, no retro credit."""
    target = issued + timedelta(hours=horizon_hours)
    base = {
        "target_at_utc": iso(target), "maturity": "PENDING",
        "hit_within_window": None, "first_touch_at_utc": None,
        "lead_hours": None, "observed_worst_btc_close_drawdown_pct": None,
        "barrier_pct": barrier_pct, "definition": "FIRST_POST_ISSUE_CLOSE_TO_SUBSEQUENT_HOURLY_CLOSES",
        "authority": "EXPOST_DEVELOPMENT_ONLY",
    }
    if asof < target:
        return base
    anchor = target_close_after(issued)
    # A forecast issued between hourly boundaries cannot claim the
    # price movement in the partially observed first hour.
    if anchor > target:
        return {**base, "maturity": "UNKNOWN_NO_POST_ISSUE_ANCHOR"}
    closes = []
    t = anchor
    while t <= target:
        item = market.get(t)
        if not item or not isinstance(item.get("btc"), (float, int)) or item["btc"] <= 0:
            return {**base, "maturity": "UNKNOWN_MISSING_COMPLETED_HOUR"}
        closes.append((t, float(item["btc"])))
        t += HOUR
    if len(closes) < 2:
        return {**base, "maturity": "UNKNOWN_INSUFFICIENT_POST_ISSUE_PATH"}
    start = closes[0][1]
    downs = [(when, 100*(p/start-1)) for when,p in closes[1:]]
    first = next(((when, ret) for when,ret in downs if ret <= barrier_pct), None)
    worst = min(ret for _,ret in downs)
    return {
        **base, "maturity": "MATURED_EXPOST_ONLY",
        "hit_within_window": first is not None,
        "first_touch_at_utc": iso(first[0]) if first else None,
        "lead_hours": round((first[0]-issued).total_seconds()/3600, 5) if first else None,
        "observed_worst_btc_close_drawdown_pct": round(worst, 6),
        "anchor_close_utc": iso(anchor), "anchor_price_source": "FIRST_FULLY_POST_ISSUE_HOURLY_CLOSE",
        "candle_count": len(closes),
    }


def reference_clock_valid(f: dict, issued: datetime) -> bool:
    """Do not admit a warning using a future, ambiguous or missing reference."""
    ref = f.get("market_reference") or {}
    opened = ref.get("observation_open_utc")
    if not isinstance(opened, str):
        return False
    try:
        t = datetime.fromisoformat(opened.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return False
    if t.utcoffset() is None:
        return False
    t = t.astimezone(timezone.utc)
    if t.minute or t.second or t.microsecond or t + HOUR > issued:
        return False
    for asset in ("btc_usdt", "eth_usdt"):
        v = ref.get(asset)
        if isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) or v <= 0:
            return False
    return True


def evaluate(freezes: list[dict], market: dict, asof: datetime) -> dict[str, Any]:
    """No new warning without a real fresh state transition. No aging credit."""
    previous = None
    active_since = None
    # One correlated market-risk episode can contain transient NORMAL ticks and
    # legitimate severity escalation. Neither resets the 72h episode clock.
    episode_at = None
    episode_peak = -1
    counts = Counter()
    rows = []
    for e in sorted(freezes, key=lambda x: (x["issued"], x["path"])):
        f = e["data"]
        issued = e["issued"]
        if issued > asof:
            continue
        tracker = f.get("protection_tracker") or {}
        risk = str(tracker.get("pullback_risk_state") or "UNAVAILABLE")
        good = (risk in RANK and tracker.get("data_quality") == "OK" and
                tracker.get("contract") == "COMPASS_PROTECTION_TRACKER_v1" and
                f.get("contract") == "OFFICIAL_DAILY_COMPASS_v1")
        if not good or not reference_clock_valid(f, issued):
            counts["SOURCE_UNAVAILABLE_OR_UNQUALIFIED" if not good else
                   "INVALID_REFERENCE_CLOCK_OR_PRICE"] += 1
            previous = None
            active_since = None
            continue
        status = None
        if previous is None or not (timedelta(0) <= issued - previous[0] <= timedelta(hours=TRUST_GAP_HOURS)):
            status = "LEFT_CENSORED_NO_TRANSITION_PROOF" if RANK[risk] >= 2 else "NO_WARNING"
            active_since = None
        elif RANK[risk] >= 2 and RANK[previous[1]] < 2:
            status = "NEW_WARNING"
            active_since = issued
        elif RANK[risk] >= 3 and RANK[risk] > RANK[previous[1]]:
            status = "ESCALATION"
            active_since = issued
        elif RANK[risk] >= 2:
            if active_since is not None and issued - active_since > timedelta(hours=EXPIRY_HOURS):
                status = "EXPIRED_NO_FRESH_WARNING"
            else:
                status = "REPEAT_STATE_NOT_NEW_WARNING"
        else:
            status = "NO_WARNING"
            active_since = None
        if status in {"NEW_WARNING", "ESCALATION"}:
            open_episode = (episode_at is not None and
                            timedelta(0) <= issued - episode_at < timedelta(hours=EXPIRY_HOURS))
            if open_episode and RANK[risk] <= episode_peak:
                # Risk flapping is not a fresh forecast. Suppression must not
                # re-arm the countdown or grant later market drops extra credit.
                status = "RETRIGGER_WITHIN_OPEN_WINDOW_NOT_SCORED"
                active_since = episode_at
            else:
                if not open_episode:
                    episode_at, episode_peak = issued, -1
                episode_peak = max(episode_peak, RANK[risk])
        previous = (issued, risk)
        counts[status] += 1
        # A persistent ELEVATED flag is neither repeated warning coverage nor
        # proof of a correct downside forecast.
        if status not in {"NEW_WARNING", "ESCALATION"}:
            continue
        horizons = {
            name: evaluate_path(issued, asof, market, hours, barrier)
            for name, (hours, barrier) in HORIZONS.items()
        }
        rows.append({
            "source_path": e["path"], "source_sha256": e["sha256"],
            "issued_at_utc": iso(issued), "risk_state": risk,
            "new_alert_class": status, "outcomes": horizons,
            "first_known_source_verified": False,
            "portfolio_action": False,
        })
    horizon_summary = {}
    for name in HORIZONS:
        mature = [row["outcomes"][name] for row in rows
                  if row["outcomes"][name]["maturity"] == "MATURED_EXPOST_ONLY"]
        hits = sum(v["hit_within_window"] is True for v in mature)
        horizon_summary[name] = {
            "new_warning_or_escalation_n": len(rows),
            "matured_n": len(mature),
            "hit_n": hits,
            "false_alarm_n": len(mature)-hits,
            "pending_n": sum(row["outcomes"][name]["maturity"] == "PENDING" for row in rows),
            "unknown_n": sum(row["outcomes"][name]["maturity"].startswith("UNKNOWN") for row in rows),
            "hit_rate_descriptive": round(hits/len(mature), 5) if mature else None,
            "warning_skill_or_edge": None,
        }
    return {
        "contract": CONTRACT, "asof_utc": iso(asof),
        "status": "EXPOST_RESEARCH_NOT_ALERTING",
        "thresholds": {k: {"horizon_hours": h, "btc_close_decline_pct": p}
                       for k,(h,p) in HORIZONS.items()},
        "warning_state_counts": dict(sorted(counts.items())),
        "new_warning_or_escalation_events": len(rows),
        "horizons": horizon_summary, "alerts": rows,
        "repeated_elevated_count_is_not_warning_success": True,
        "expired_alert_cannot_be_credited_from_later_drop": True,
        "false_negative_recall_unknown_without_matched_no_alert_grid": True,
        "first_known_publication_verified": False,
        "prospective_holdout_completed": False,
        "independent_event_clustering_verified": False,
        "calibrated_probability": None, "economically_executable_edge": None,
        "automatic_model_reweighting": False,
        "trade_permission": "NONE",
    }
