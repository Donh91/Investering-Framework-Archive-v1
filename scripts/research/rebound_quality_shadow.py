#!/usr/bin/env python3
"""RQS v0: non-binding, PIT-conservative rebound evidence diagnostic.

Consumes only existing PUBLIC Hourly owner rows. No signal, forecast, probability,
portfolio permission, private-source access, remote fetch, model or scheduler.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "REBOUND_QUALITY_SHADOW_DIAGNOSTIC_v0"
PUBLIC_OWNER_ROOT = Path("03_DAILY_CAPTURE_LOGS/hourly")
CANDIDATE_DRAWDOWN_PCT = -1.5  # research-only, fixed before outcome review
CANDIDATE_RECOVERY_PCT = 0.75   # research-only, fixed before outcome review
MAX_OWNER_AGE_HOURS = 3


def utc(s: str) -> datetime:
    if not isinstance(s, str) or not s:
        raise ValueError("missing_utc_timestamp")
    t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if t.tzinfo is None or t.utcoffset() != timedelta(0):
        raise ValueError("timestamp_must_be_utc")
    return t.astimezone(timezone.utc)


def number(row: Mapping[str, str], name: str) -> float | None:
    raw = row.get(name)
    if raw is None or raw == "":
        return None
    try:
        x = float(raw)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def pct(a: float, b: float) -> float:
    return (b / a - 1.0) * 100.0


def maximum_close_drawdown(values: list[float]) -> float:
    peak = values[0]
    result = 0.0
    for value in values:
        peak = max(peak, value)
        result = min(result, pct(peak, value))
    return result


def assess(rows: list[Mapping[str, str]], asof: str) -> dict[str, Any]:
    """One fixed-cutoff replay, never a registered prospective forecast."""
    cutoff = utc(asof)
    seen: dict[str, Mapping[str, str]] = {}
    for r in rows:
        start = utc(r["timestamp_utc"])  # Binance spot candle OPEN
        candle_end = start + timedelta(hours=1)  # completed 1h candle CLOSE
        # source_window_end_utc is the whole collection RUN coverage end,
        # NOT the individual candle end. Repeated values are normal across rows.
        run_coverage_end = utc(r["source_window_end_utc"])
        if run_coverage_end < candle_end:
            raise ValueError("source_coverage_ends_before_candle")
        if candle_end > cutoff or run_coverage_end > cutoff:
            # No future candle AND no later collection window in an as-of replay.
            # This still does not establish true first-known availability.
            continue
        key = candle_end.isoformat()
        if key in seen:
            if dict(seen[key]) != dict(r):
                raise ValueError("conflicting_duplicate_candle")
            continue  # byte-equivalent overlap across daily files
        seen[key] = r
    ordered = sorted(seen.items())
    base: dict[str, Any] = {
        "contract": CONTRACT,
        "status": "INSUFFICIENT_EVIDENCE",
        "asof_utc": cutoff.isoformat().replace("+00:00", "Z"),
        "research_only": True,
        "first_known_verified": False,
        "prospective_forecast_issued": False,
        "score_0_100": None,
        "score_status": "BLOCKED_UNVALIDATED_AND_NO_INDEPENDENT_BREADTH",
        "bull_trap_probability": None,
        "short_covering_proven": False,
        "trade_permission": "NONE",
        "family_independence": {"SPOT_PRICE_FLOW": False, "DERIVATIVES_OI": False, "BREADTH": False},
        "evidence": {},
        "limitations": ["Historical first-known/ingestion clock not established; no PIT-admitted results.",
                        "Spot price, taker volume and ETH/BTC share the same spot family, not three independent votes.",
                        "OI direction does not uniquely identify short-covering or position side.",
                        "No independent same-clock breadth owner joined; score and BUY/SELL remain unavailable."],
    }
    if len(ordered) < 16:
        base["reason"] = "NEEDS_16_CONTIGUOUS_COMPLETED_HOURS"
        return base
    tail = ordered[-16:]
    timestamps = [utc(ts) for ts, _ in tail]
    if any((b - a) != timedelta(hours=1) for a, b in zip(timestamps, timestamps[1:])):
        base["reason"] = "HOURLY_GAP_NO_FORWARD_FILL"
        return base
    if cutoff - timestamps[-1] > timedelta(hours=MAX_OWNER_AGE_HOURS):
        base["reason"] = "OWNER_DATA_STALE"
        return base
    candles = [r for _, r in tail]
    if any(r.get("spot_status") != "PASS" for r in candles):
        base["reason"] = "SPOT_SOURCE_NOT_PASS"
        return base
    closes = [number(r, "btc_close") for r in candles]
    if any(v is None or v <= 0 for v in closes):
        base["reason"] = "BTC_CLOSE_INVALID"
        return base
    prior_dd = maximum_close_drawdown(closes[:-3])
    current_return = pct(closes[-4], closes[-1])
    candidate = prior_dd <= CANDIDATE_DRAWDOWN_PCT and current_return >= CANDIDATE_RECOVERY_PCT
    spot_tail = candles[-3:]
    buys = [number(r, "btc_taker_buy_quote_volume") for r in spot_tail]
    totals = [number(r, "btc_quote_volume") for r in spot_tail]
    share = None
    if all(v is not None and v >= 0 for v in buys) and all(v is not None and v > 0 for v in totals) and all(b <= t for b, t in zip(buys, totals)):
        share = sum(buys) / sum(totals)
    ethbtc0 = number(candles[-4], "ethbtc_close")
    ethbtc1 = number(candles[-1], "ethbtc_close")
    relative = pct(ethbtc0, ethbtc1) if ethbtc0 is not None and ethbtc1 is not None and min(ethbtc0, ethbtc1) > 0 else None
    prior_vol = [number(r, "btc_quote_volume") for r in candles[-16:-4]]
    vol_ratio = None
    if all(v is not None and v > 0 for v in prior_vol) and all(v is not None and v > 0 for v in totals):
        median_prior = statistics.median(prior_vol)
        vol_ratio = (sum(totals) / 3.0) / median_prior
    oi0 = number(candles[-4], "btc_open_interest")
    oi1 = number(candles[-1], "btc_open_interest")
    oi_ok = all(r.get("derivatives_status") == "PASS" for r in candles[-4:]) and oi0 is not None and oi1 is not None and min(oi0, oi1) > 0
    oi_delta = pct(oi0, oi1) if oi_ok else None
    oi_pattern = "UNAVAILABLE"
    if oi_delta is not None and current_return > 0:
        oi_pattern = "PRICE_UP_OI_DOWN_SIDE_UNIDENTIFIED" if oi_delta < 0 else (
            "PRICE_UP_OI_UP_LEVERAGE_POSSIBLE" if oi_delta > 0 else "PRICE_UP_OI_FLAT")
    base["family_independence"] = {"SPOT_PRICE_FLOW": share is not None and vol_ratio is not None and relative is not None,
                                    "DERIVATIVES_OI": oi_delta is not None, "BREADTH": False}
    base["evidence"] = {
        "window_end_utc": timestamps[-1].isoformat().replace("+00:00", "Z"),
        "candidate": candidate,
        "candidate_definition": {"previous_13h_max_close_drawdown_pct_lte": CANDIDATE_DRAWDOWN_PCT,
                                 "last_3h_btc_return_pct_gte": CANDIDATE_RECOVERY_PCT},
        "prior_max_close_drawdown_pct": round(prior_dd, 6),
        "btc_last_3h_return_pct": round(current_return, 6),
        "btc_last_3h_taker_buy_quote_share": round(share, 6) if share is not None else None,
        "btc_last_3h_quote_volume_vs_prior_12h_median": round(vol_ratio, 6) if vol_ratio is not None else None,
        "ethbtc_last_3h_return_pct": round(relative, 6) if relative is not None else None,
        "btc_open_interest_last_3h_change_pct": round(oi_delta, 6) if oi_delta is not None else None,
        "oi_pattern": oi_pattern,
        "breadth_state": "UNAVAILABLE_NO_SAME_CLOCK_INDEPENDENT_JOIN",
    }
    base["status"] = "REPLAY_CANDIDATE_RESEARCH_ONLY" if candidate else "NO_CANDIDATE_RESEARCH_ONLY"
    base["reason"] = "EXPLORATORY_DIAGNOSTICS_NOT_CALIBRATED"
    return base



def replay_census(rows: list[Mapping[str, str]], asof: str) -> dict[str, Any]:
    """Bounded exploratory census, not first-known evidence or skill backtest."""
    cutoff = utc(asof)
    # Form a complete CLOSED-hour UTC grid, including missing owner hours. Building
    # clocks only from observed rows hides gaps from the coverage denominator.
    last_complete = cutoff.replace(minute=0, second=0, microsecond=0)
    # Always score the same 168 completed UTC-hour cutoffs regardless of
    # whether the owner collected the first, last or ANY source hour.
    # Source rows before the grid may still serve as lookback warmup; they
    # never alter the denominator. Both endpoints are inclusive (168 total).
    first = last_complete - timedelta(hours=167)
    if first.minute or first.second or first.microsecond:
        raise ValueError("hourly_candle_not_utc_aligned")
    cutoffs = []
    hour = first
    while hour <= last_complete:
        cutoffs.append(hour)
        hour += timedelta(hours=1)
    results = [assess(rows, t.isoformat()) for t in cutoffs]
    eligible_statuses = {"REPLAY_CANDIDATE_RESEARCH_ONLY", "NO_CANDIDATE_RESEARCH_ONLY"}
    candidates = []
    eligible_count = 0
    exclusions: dict[str, int] = {}
    for r in results:
        if r["status"] not in eligible_statuses:
            reason = r.get("reason", r["status"])
            exclusions[reason] = exclusions.get(reason, 0) + 1
            continue
        eligible_count += 1
        if r["evidence"].get("candidate") is True:
            candidates.append(utc(r["evidence"]["window_end_utc"]))
    cluster_sensitivity = {}
    for cooldown in (6, 12, 24):
        groups: list[list[datetime]] = []
        for stamp in candidates:
            if not groups or stamp - groups[-1][-1] > timedelta(hours=cooldown):
                groups.append([stamp])
            else:
                groups[-1].append(stamp)
        cluster_sensitivity[str(cooldown) + "h"] = {
            "cluster_count": len(groups),
            "groups": [
                {"first_utc": group[0].isoformat().replace("+00:00", "Z"),
                 "last_utc": group[-1].isoformat().replace("+00:00", "Z"),
                 "raw_candidates": len(group)} for group in groups
            ],
        }
    return {
        "contract": "REBOUND_QUALITY_EXPLORATORY_REPLAY_CENSUS_v0",
        "asof_utc": cutoff.isoformat().replace("+00:00", "Z"),
        "evaluated_cutoffs": len(results),
        "eligible_complete_cutoffs": eligible_count,
        "excluded_cutoffs_by_reason": exclusions,
        "raw_rebound_candidate_cutoffs": len(candidates),
        "cluster_sensitivity_NOT_CHOSEN_OR_CALIBRATED": cluster_sensitivity,
        "first_known_verified": False,
        "performance_backtest": False,
        "directional_accuracy": None,
        "after_cost_edge": None,
        "official_action_permission": "NONE",
        "warning": "Exploratory retrospective census only. No first-known, holdout, causal or performance proof.",
    }



def due_only_outcome_preview(rows: list[Mapping[str, str]], event_end_utc: str,
                             review_asof_utc: str) -> dict[str, Any]:
    """EX-POST price path description, never a scored or issued forecast.

    A candidate can only be assessed for a due horizon when every intermediate
    source candle is present, PASS and covered by an as-of-eligible owner run.
    """
    event_end, review_time = utc(event_end_utc), utc(review_asof_utc)
    if review_time < event_end:
        raise ValueError("review_before_event")
    known: dict[datetime, Mapping[str, str]] = {}
    for row in rows:
        close = utc(row["timestamp_utc"]) + timedelta(hours=1)
        coverage_end = utc(row["source_window_end_utc"])
        if coverage_end < close:
            raise ValueError("source_coverage_ends_before_candle")
        if close > review_time or coverage_end > review_time:
            continue
        if close in known and dict(known[close]) != dict(row):
            raise ValueError("conflicting_duplicate_candle")
        known[close] = row
    event = known.get(event_end)
    ref_close = number(event, "btc_close") if event is not None else None
    if event is None or event.get("spot_status") != "PASS" or ref_close is None or ref_close <= 0:
        status = "MISSING_ELIGIBLE_EVENT_REFERENCE"
    else:
        status = "DESCRIPTIVE_EXPOST_REFERENCE_AVAILABLE"
    horizons: dict[str, dict[str, Any]] = {}
    for h in (6, 24, 72):
        due = event_end + timedelta(hours=h)
        key = f"{h}h"
        if due > review_time:
            horizons[key] = {"status": "PENDING_NOT_MATURE", "due_utc": due.isoformat().replace("+00:00", "Z"),
                             "btc_close_return_pct": None}
            continue
        window = [known.get(event_end + timedelta(hours=i)) for i in range(1, h + 1)]
        if (status != "DESCRIPTIVE_EXPOST_REFERENCE_AVAILABLE"
                or any(row is None or row.get("spot_status") != "PASS"
                       or number(row, "btc_close") is None
                       or number(row, "btc_close") <= 0 for row in window)):
            horizons[key] = {"status": "UNAVAILABLE_MISSING_OR_INVALID_HOURLY_SOURCE",
                             "due_utc": due.isoformat().replace("+00:00", "Z"),
                             "btc_close_return_pct": None}
            continue
        finish = number(window[-1], "btc_close")
        horizons[key] = {
            "status": "DESCRIPTIVE_EXPOST_ONLY",
            "due_utc": due.isoformat().replace("+00:00", "Z"),
            "btc_close_return_pct": round(pct(ref_close, finish), 6),
        }
    return {
        "contract": "REBOUND_QUALITY_DUE_ONLY_OUTCOME_PREVIEW_v0",
        "event_end_utc": event_end.isoformat().replace("+00:00", "Z"),
        "review_asof_utc": review_time.isoformat().replace("+00:00", "Z"),
        "reference_status": status,
        "horizons": horizons,
        "original_prospective_registration_verified": False,
        "first_known_verified": False,
        "prediction_or_skill_scored": False,
        "trade_permission": "NONE",
        "warning": "Historical descriptive follow-up only; no registered forecast, causal attribution, calibrated precision or profitable edge.",
    }


def read_public_owner(repo: Path, files: list[Path]) -> list[dict[str, str]]:
    root = (repo / PUBLIC_OWNER_ROOT).resolve()
    out: list[dict[str, str]] = []
    for file in files:
        target = (repo / file).resolve()
        if not target.is_relative_to(root) or target.suffix != ".csv":
            raise ValueError("outside_public_hourly_owner")
        with target.open(newline="", encoding="utf-8") as handle:
            out.extend(csv.DictReader(handle))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--csv", type=Path, required=True, action="append")
    ap.add_argument("--asof", required=True, help="UTC snapshot cutoff, not retrospective issuance proof")
    ap.add_argument("--scan", action="store_true", help="exploratory last-168h census, not a performance test")
    ap.add_argument("--event-end", default=None, help="UTC event-close for due-only descriptive outcome preview")
    args = ap.parse_args()
    rows = read_public_owner(args.repo, args.csv)
    result = (due_only_outcome_preview(rows, args.event_end, args.asof) if args.event_end
              else replay_census(rows, args.asof) if args.scan else assess(rows, args.asof))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
