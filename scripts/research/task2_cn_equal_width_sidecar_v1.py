#!/usr/bin/env python3
"""Non-promotional, source-clock-censored equal-width controls for Task2 CN replay.

Consumes the existing Task2 historical replay CSV, not private data or live markets.
This is descriptive retrospective arithmetic. It cannot establish original PIT
issuance, first consumer delivery, range skill, or trading advantage.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

CONTRACT = "TASK2_CN_EQUAL_WIDTH_RESEARCH_SIDECAR_v1"
FIELDS = ("week", "asset", "target_mature", "forecast_available",
          "prior_week_available", "forecast_low", "forecast_high", "prior_close",
          "actual_low", "actual_high", "actual_close", "source_clock_class")


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        x = float(value)
    except (ValueError, TypeError, OverflowError):
        return None
    return x if math.isfinite(x) and x > 0 else None


def _yes(value):
    if value is True or value == "True" or value == "true" or value == "1":
        return True
    if value is False or value == "False" or value == "false" or value == "0":
        return False
    return None


def interval_score_close(low, high, actual_close, alpha):
    """Central 1-alpha interval score; merely an assumed-alpha sensitivity here."""
    if not 0 < alpha < 1 or not 0 < low < high or actual_close <= 0:
        raise ValueError("invalid interval/alpha")
    penalty = 2 / alpha
    return (high - low) + penalty * max(0.0, low - actual_close) + penalty * max(0.0, actual_close - high)


def _scores(low, high, observed_low, observed_high, close, reference, alpha):
    return {
        "full_range_covered": int(low <= observed_low and observed_high <= high),
        "close_covered": int(low <= close <= high),
        "width_fraction": (high - low) / reference,
        "boundary_breach_fraction": (max(0.0, low - observed_low) + max(0.0, observed_high - high)) / reference,
        "assumed_alpha_interval_score_close_fraction": interval_score_close(low, high, close, alpha) / reference,
    }


def compute(input_rows, alpha=0.2):
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float)) or not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between zero and one")
    seen, comparisons, excluded = set(), [], []
    for index, source in enumerate(input_rows, 1):
        if not isinstance(source, dict):
            raise ValueError("input row is not an object")
        raw_week = str(source.get("week", ""))
        asset = str(source.get("asset", ""))
        if asset not in ("BTC", "ETH") or not raw_week.isascii() or not raw_week.isdecimal() or not 1 <= int(raw_week) <= 53:
            raise ValueError(f"unsupported week/asset: {(raw_week, asset)}")
        # Normalize accepted numeric spellings BEFORE dedupe, e.g. 39 == 039.
        key = (int(raw_week), asset)
        if key in seen:
            raise ValueError(f"duplicate independent week/asset: {key}")
        seen.add(key)
        eligible = [_yes(source.get(k)) for k in ("target_mature", "forecast_available", "prior_week_available")]
        if eligible != [True, True, True]:
            excluded.append({"week": int(key[0]), "asset": key[1], "reason": "NOT_MATURE_OR_MISSING_MATCHED_BASELINE"})
            continue
        prices = {k: _number(source.get(k)) for k in FIELDS[5:11]}
        if any(value is None for value in prices.values()):
            excluded.append({"week": int(key[0]), "asset": key[1], "reason": "INVALID_OR_MISSING_PRICE"})
            continue
        lo, hi, pc = (prices[k] for k in ("forecast_low", "forecast_high", "prior_close"))
        alo, ahi, close = (prices[k] for k in ("actual_low", "actual_high", "actual_close"))
        if lo >= hi or alo > ahi or not alo <= close <= ahi:
            excluded.append({"week": int(key[0]), "asset": key[1], "reason": "INCONSISTENT_RANGE_OR_OUTCOME"})
            continue
        width = hi - lo
        eq_low, eq_high = pc - width / 2, pc + width / 2
        if eq_low <= 0:
            excluded.append({"week": int(key[0]), "asset": key[1], "reason": "EQUAL_WIDTH_PRIOR_INTERVAL_NONPOSITIVE"})
            continue
        forecast = _scores(lo, hi, alo, ahi, close, pc, alpha)
        eq_prior = _scores(eq_low, eq_high, alo, ahi, close, pc, alpha)
        comparisons.append({
            "iso_year": 2026, "week": int(key[0]), "asset": key[1],
            "forecast_low": lo, "forecast_high": hi,
            "equal_width_prior_low": eq_low, "equal_width_prior_high": eq_high,
            "reference_prior_close": pc,
            "forecast": forecast, "equal_width_prior": eq_prior,
            "first_in_main_price_control": "SOURCE_BLOCKED_NO_VERIFIED_ANCHOR_PRICE",
            "post_issue_actual_window": "SOURCE_BLOCKED_NO_VERIFIED_HOURLY_CENSOR",
            "information_time_class": "RETROSPECTIVE_ONLY_NOT_FIRST_KNOWN_OR_DELIVERY",
            "historical_source_clock_class": source.get("source_clock_class") or "UNKNOWN",
            "source_version_adjudication": "NOT_PERFORMED_IN_NUMERIC_SIDECAR",
            "model_promotion": False,
        })
    by_asset = {}
    for asset in ("BTC", "ETH"):
        selected = [x for x in comparisons if x["asset"] == asset]
        count = len(selected)
        def avg(side, metric):
            return mean(x[side][metric] for x in selected) if count else None
        by_asset[asset] = {
            "independent_week_count": count,
            "forecast_full_range_cover_count": sum(x["forecast"]["full_range_covered"] for x in selected),
            "equal_width_prior_full_range_cover_count": sum(x["equal_width_prior"]["full_range_covered"] for x in selected),
            "forecast_close_cover_count": sum(x["forecast"]["close_covered"] for x in selected),
            "equal_width_prior_close_cover_count": sum(x["equal_width_prior"]["close_covered"] for x in selected),
            "forecast_mean_boundary_breach_fraction": avg("forecast", "boundary_breach_fraction"),
            "equal_width_prior_mean_boundary_breach_fraction": avg("equal_width_prior", "boundary_breach_fraction"),
            "forecast_mean_assumed_alpha_interval_score_close_fraction": avg("forecast", "assumed_alpha_interval_score_close_fraction"),
            "equal_width_prior_mean_assumed_alpha_interval_score_close_fraction": avg("equal_width_prior", "assumed_alpha_interval_score_close_fraction"),
        }
    return {
        "contract": CONTRACT,
        "science_status": "RETROSPECTIVE_DESCRIPTION_ONLY_NO_MODEL_PROMOTION",
        "alpha_assumption": alpha,
        "alpha_meaning": "SENSITIVITY_ONLY; CN bands have no verified 1-alpha nominal coverage contract",
        "baseline": "EXACT_CN_WIDTH_CENTERED_ON_PRIOR_WEEK_CLOSE",
        "clock_limitation": "First-in-main price, true first-known, consumer delivery, post-freeze OHLC UNKNOWN",
        "scored_sample_semantics": "One 2026 ISO week per asset; not 14 independent observations pooled across assets",
        "historical_rewrite_note": "W40 structural/internal claim revisions require original-vs-scored blob sidecar; not admitted here",
        "compared_rows": comparisons,
        "excluded_rows": excluded,
        "summary_by_asset": by_asset,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path, help="existing replay weekly CSV")
    ap.add_argument("--out", required=True, type=Path, help="new output directory")
    ap.add_argument("--assumed-alpha", type=float, default=0.2)
    args = ap.parse_args(argv)
    data = args.input.read_bytes()
    rows = list(csv.DictReader(data.decode("utf-8-sig").splitlines()))
    missing = set(FIELDS) - set(rows[0] if rows else [])
    if missing:
        raise ValueError(f"required replay columns absent: {sorted(missing)}")
    result = compute(rows, args.assumed_alpha)
    result["source_csv_sha256"] = hashlib.sha256(data).hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "equal_width_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"contract": CONTRACT, "rows": len(result["compared_rows"]),
                      "status": result["science_status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
