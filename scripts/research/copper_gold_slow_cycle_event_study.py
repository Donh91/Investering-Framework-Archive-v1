#!/usr/bin/env python3
"""Descriptive, point-in-time Copper/Gold and BTC event study.

BTC peak labels use future outcomes and are audit labels, not deployable
signals. Copper/Gold is joined only from settled bars known by the event date.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


AUTHORITY = {
    "binding": False,
    "canonical_acceptance": False,
    "framework_state_change": False,
    "portfolio_action": False,
    "execution_authority": False,
}
HORIZONS = (60, 120, 240, 365)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def load_btc(path: Path) -> list[tuple[date, float]]:
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            raw_date = row.get("time") or row.get("date") or row.get("Date")
            raw_price = row.get("PriceUSD") or row.get("close") or row.get("Close")
            if raw_date and raw_price not in (None, ""):
                value = float(raw_price)
                if value > 0:
                    rows.append((date.fromisoformat(raw_date[:10]), value))
    rows.sort()
    if not rows:
        raise ValueError("btc_price_series_empty")
    if len({day for day, _ in rows}) != len(rows):
        raise ValueError("btc_duplicate_date")
    return rows


def load_features(path: Path) -> dict[str, list[dict[str, Any]]]:
    anchors: dict[str, list[dict[str, Any]]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("settled") != "True":
                continue
            parsed: dict[str, Any] = dict(row)
            parsed["bar_end_day"] = date.fromisoformat(row["bar_end_timestamp"][:10])
            for field in ("ratio_close_proxy", "macd_histogram", "rsi_14_wilder"):
                parsed[field] = float(row[field]) if row.get(field) else None
            anchors.setdefault(row["anchor_id"], []).append(parsed)
    if set(anchors) != {"JAN_FEB", "FEB_MAR"}:
        raise ValueError("both_anchor_variants_required")
    for rows in anchors.values():
        rows.sort(key=lambda row: row["bar_end_day"])
    return anchors


def index_on_or_after(days: list[date], target: date) -> int | None:
    index = bisect.bisect_left(days, target)
    return index if index < len(days) else None


def forward_metrics(series: list[tuple[date, float]], start_index: int) -> dict[str, float | None]:
    start_day, start_price = series[start_index]
    days = [row[0] for row in series]
    output: dict[str, float | None] = {}
    for horizon in HORIZONS:
        end_index = index_on_or_after(days, start_day + timedelta(days=horizon))
        if end_index is None:
            output[f"return_{horizon}d_pct"] = None
            output[f"max_drawdown_{horizon}d_pct"] = None
            continue
        window = series[start_index : end_index + 1]
        output[f"return_{horizon}d_pct"] = round((series[end_index][1] / start_price - 1) * 100, 6)
        output[f"max_drawdown_{horizon}d_pct"] = round((min(price for _, price in window) / start_price - 1) * 100, 6)
    return output


def objective_peak_episodes(series: list[tuple[date, float]]) -> list[dict[str, Any]]:
    days = [row[0] for row in series]
    candidates = []
    for index, (event_day, price) in enumerate(series):
        future_index = index_on_or_after(days, event_day + timedelta(days=365))
        if future_index is None:
            break
        prior_start = bisect.bisect_left(days, event_day - timedelta(days=365))
        if price < max(value for _, value in series[prior_start : index + 1]):
            continue
        metrics = forward_metrics(series, index)
        if metrics["max_drawdown_365d_pct"] is None or metrics["max_drawdown_365d_pct"] > -20:
            continue
        future = series[index + 1 : future_index + 1]
        reclaim_day = next((day for day, future_price in future if future_price > price), None)
        candidates.append({
            "event_day": event_day,
            "btc_price": price,
            "reclaimed_within_365d": reclaim_day is not None,
            "first_reclaim_date": reclaim_day,
            **metrics,
        })
    clusters: list[list[dict[str, Any]]] = []
    for candidate in candidates:
        if not clusters or (candidate["event_day"] - clusters[-1][-1]["event_day"]).days > 180:
            clusters.append([candidate])
        else:
            clusters[-1].append(candidate)
    episodes = [max(cluster, key=lambda row: row["btc_price"]) for cluster in clusters]
    for row in episodes:
        if row["reclaimed_within_365d"]:
            row["outcome_label"] = "MID_CYCLE_RECLAIMED_WITHIN_365D"
        elif row["max_drawdown_365d_pct"] <= -50:
            row["outcome_label"] = "TERMINAL_PROXY_50_PLUS_NO_365D_RECLAIM"
        else:
            row["outcome_label"] = "DEEP_PULLBACK_20_TO_50_NO_365D_RECLAIM"
    return episodes


def latest_settled_state(rows: list[dict[str, Any]], event_day: date) -> dict[str, Any] | None:
    eligible = [row for row in rows if row["bar_end_day"] <= event_day]
    if not eligible:
        return None
    row = eligible[-1]
    return {
        "bar_end_period": row["bar_end_period"],
        "bar_end_timestamp": row["bar_end_timestamp"],
        "regime_state": row["regime_state"],
        "macd_histogram": row["macd_histogram"],
        "rsi_14_wilder": row["rsi_14_wilder"],
        "lookahead_guard": "BAR_END_ON_OR_BEFORE_EVENT",
    }


def signal_events(rows: list[dict[str, Any]], state: str, btc: list[tuple[date, float]], shift_days: int = 0) -> list[dict[str, Any]]:
    days = [row[0] for row in btc]
    output = []
    for row in rows:
        if row["regime_state"] != state:
            continue
        event_day = row["bar_end_day"] + timedelta(days=shift_days)
        if event_day < days[0]:
            continue
        index = index_on_or_after(days, event_day)
        if index is None:
            continue
        metrics = forward_metrics(btc, index)
        if metrics["return_240d_pct"] is None:
            continue
        output.append({
            "source_bar_end_period": row["bar_end_period"],
            "event_date": btc[index][0].isoformat(),
            "btc_price": btc[index][1],
            "regime_state": state,
            "shift_days": shift_days,
            **metrics,
        })
    return output


def median(values: list[float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    middle = len(values) // 2
    return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {"event_count": len(events)}
    for field in ("return_60d_pct", "return_120d_pct", "return_240d_pct", "max_drawdown_240d_pct"):
        value = median([float(row[field]) for row in events if row.get(field) is not None])
        output[field + "_median"] = round(value, 6) if value is not None else None
    return output


def build_study(features_path: Path, btc_path: Path, btc_source: dict[str, Any] | None = None) -> dict[str, Any]:
    btc = load_btc(btc_path)
    anchors = load_features(features_path)
    peaks = []
    for peak in objective_peak_episodes(btc):
        peaks.append({
            **{key: value.isoformat() if isinstance(value, date) else value for key, value in peak.items()},
            "copper_gold_state_by_anchor": {
                anchor: latest_settled_state(rows, peak["event_day"])
                for anchor, rows in sorted(anchors.items())
            },
        })
    anchor_results = {}
    for anchor, rows in sorted(anchors.items()):
        negative = signal_events(rows, "TURNING_NEGATIVE", btc)
        positive = signal_events(rows, "TURNING_POSITIVE", btc)
        shifted = signal_events(rows, "TURNING_NEGATIVE", btc, 91)
        anchor_results[anchor] = {
            "turning_negative": {"events": negative, "summary": summarize(negative)},
            "control_turning_positive": {"events": positive, "summary": summarize(positive)},
            "control_turning_negative_shifted_91d": {"events": shifted, "summary": summarize(shifted)},
        }
    return {
        "contract": "COPPER_GOLD_SLOW_CYCLE_EVENT_STUDY_v2",
        "status": "EXPLORATORY_SMALL_N_NOT_VALIDATION",
        "source_lineage": {
            "features_path": features_path.as_posix(),
            "features_sha256": sha256_file(features_path),
            "btc_sha256": sha256_file(btc_path),
            "btc_first_observation": btc[0][0].isoformat(),
            "btc_last_observation": btc[-1][0].isoformat(),
            **(btc_source or {}),
        },
        "method": {
            "objective_peak_label": "Trailing-365d high followed by at least 20% drawdown inside 365d; candidates within 180d clustered at highest price.",
            "terminal_proxy": "At least 50% drawdown and no reclaim of event price inside 365d.",
            "state_join": "Latest settled 2M bar ending on or before BTC event date.",
            "negative_controls": ["TURNING_POSITIVE", "TURNING_NEGATIVE shifted 91 calendar days"],
            "threshold_optimization": False,
            "interpolation": False,
            "forward_fill": False,
        },
        "objective_btc_peak_episodes": peaks,
        "anchor_results": anchor_results,
        "limitations": [
            "Crypto has too few independent market cycles for reliable statistical inference.",
            "Peak labels use future outcomes and cannot be used as live signals.",
            "The study does not prove incremental value against the full framework baseline.",
            "World Bank monthly period averages are a macro proxy, not TechDev's exact futures series.",
        ],
        "incremental_value_verdict": "NOT_VALIDATED_REQUIRES_PROSPECTIVE_BASELINE_COMPARISON",
        "authority": AUTHORITY,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settled-features", type=Path, required=True)
    parser.add_argument("--btc-csv", type=Path, required=True)
    parser.add_argument("--btc-source-repository")
    parser.add_argument("--btc-source-revision")
    parser.add_argument("--btc-source-path")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = {
        key: value for key, value in {
            "btc_source_repository": args.btc_source_repository,
            "btc_source_revision": args.btc_source_revision,
            "btc_source_path": args.btc_source_path,
        }.items() if value
    }
    study = build_study(args.settled_features, args.btc_csv, source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(study, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": study["status"], "objective_peak_count": len(study["objective_btc_peak_episodes"]), "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
