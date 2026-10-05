#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE = Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/hourly_features.csv.gz")
METHOD = "06_RESEARCH_LAB/m6_methods/2026-10-05__gap-sensitive-episode-power-method-v1.md"
WINDOWS = ("ALTSEASON_2020_2021", "MODERN_ANALOGUE_2025_2026")
THRESHOLDS = (0.20, 0.30, 0.40)
FAMILY_GAPS_DAYS = (7, 14, 30)


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_rows(path: Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError("empty_source")
    required = {
        "timestamp_utc",
        "research_window_id",
        "continuity_segment_id",
        "ew_return_1h_pct",
        "ew_index",
        "btc_usdt",
    }
    missing = sorted(required - set(rows[0]))
    if missing:
        raise ValueError(f"missing_columns:{missing}")
    return rows


def build_window(rows: list[dict[str, str]], window: str) -> tuple[list[dict[str, Any]], list[datetime]]:
    selected = [r for r in rows if r.get("research_window_id") == window]
    if not selected:
        raise ValueError(f"empty_window:{window}")
    selected.sort(key=lambda r: parse_ts(r["timestamp_utc"]))

    idx = 100.0
    prev_seg = None
    out = []
    gaps = []
    for i, row in enumerate(selected):
        t = parse_ts(row["timestamp_utc"])
        seg = row["continuity_segment_id"]
        if i == 0:
            idx = 100.0
        elif seg == prev_seg:
            ret = float(row["ew_return_1h_pct"] or 0.0)
            idx *= 1.0 + ret / 100.0
        else:
            gaps.append(t)
            # Carry the last observed level to the next observed endpoint.
            # This explicitly does NOT fabricate a return inside the missing interval.
        out.append(
            {
                "t": t,
                "ew": idx,
                "btc": float(row["btc_usdt"]),
                "segment": seg,
                "raw_ew_index": float(row["ew_index"]),
            }
        )
        prev_seg = seg
    return out, gaps


def crosses_gap(start: datetime, end: datetime | None, gaps: list[datetime]) -> bool | None:
    if end is None:
        return None
    return any(start < g <= end for g in gaps)


def episodes(series: list[tuple[datetime, float]], threshold: float, gaps: list[datetime]) -> list[dict[str, Any]]:
    if not series:
        return []
    peak_i = 0
    peak_v = series[0][1]
    state = "UP"
    threshold_cross_i = None
    trough_i = None
    trough_v = None
    out = []

    def finish(rebound_i: int | None, open_right_censored: bool) -> None:
        nonlocal peak_i, peak_v, threshold_cross_i, trough_i, trough_v
        if trough_i is None or trough_v is None:
            return
        peak_t = series[peak_i][0]
        cross_t = series[threshold_cross_i][0] if threshold_cross_i is not None else None
        trough_t = series[trough_i][0]
        rebound_t = series[rebound_i][0] if rebound_i is not None else None
        out.append(
            {
                "peak_timestamp_utc": peak_t.isoformat().replace("+00:00", "Z"),
                "threshold_cross_timestamp_utc": cross_t.isoformat().replace("+00:00", "Z") if cross_t else None,
                "trough_timestamp_utc": trough_t.isoformat().replace("+00:00", "Z"),
                "rebound_confirm_timestamp_utc": rebound_t.isoformat().replace("+00:00", "Z") if rebound_t else None,
                "peak_value": peak_v,
                "trough_value": trough_v,
                "drawdown_pct": (trough_v / peak_v - 1.0) * 100.0,
                "peak_to_trough_hours": (trough_t - peak_t).total_seconds() / 3600.0,
                "peak_to_rebound_hours": (rebound_t - peak_t).total_seconds() / 3600.0 if rebound_t else None,
                "crosses_gap_peak_to_trough": crosses_gap(peak_t, trough_t, gaps),
                "crosses_gap_peak_to_rebound": crosses_gap(peak_t, rebound_t, gaps),
                "open_right_censored": open_right_censored,
            }
        )

    for i, (_, value) in enumerate(series):
        if state == "UP":
            if value > peak_v:
                peak_i, peak_v = i, value
            elif value <= peak_v * (1.0 - threshold):
                state = "DOWN"
                threshold_cross_i = i
                trough_i, trough_v = i, value
        else:
            assert trough_v is not None and trough_i is not None
            if value < trough_v:
                trough_i, trough_v = i, value
            elif value >= trough_v * (1.0 + threshold):
                finish(i, False)
                state = "UP"
                peak_i, peak_v = i, value
                threshold_cross_i = None
                trough_i = None
                trough_v = None

    if state == "DOWN":
        finish(None, True)
    return out


def family_summary(rows: list[dict[str, Any]], gap_days: int) -> dict[str, Any]:
    if not rows:
        return {"family_count": 0, "families": []}
    ordered = sorted(rows, key=lambda x: x["peak_timestamp_utc"])
    families = []
    current = [ordered[0]]
    prev_peak = parse_ts(ordered[0]["peak_timestamp_utc"])
    for row in ordered[1:]:
        peak = parse_ts(row["peak_timestamp_utc"])
        if (peak - prev_peak).total_seconds() < gap_days * 86400:
            current.append(row)
        else:
            families.append(current)
            current = [row]
        prev_peak = peak
    families.append(current)
    return {
        "family_count": len(families),
        "families": [
            {
                "family_id": f"F{i+1:02d}",
                "episode_count": len(group),
                "first_peak_utc": group[0]["peak_timestamp_utc"],
                "last_peak_utc": group[-1]["peak_timestamp_utc"],
                "max_drawdown_pct": min(float(x["drawdown_pct"]) for x in group),
                "contains_gap_crossing_episode": any(bool(x["crosses_gap_peak_to_trough"]) for x in group),
            }
            for i, group in enumerate(families)
        ],
    }


def summarize_episode_set(rows: list[dict[str, Any]]) -> dict[str, Any]:
    no_gap = [x for x in rows if not x["crosses_gap_peak_to_trough"]]
    return {
        "episode_count_all_observed_endpoints": len(rows),
        "episode_count_peak_to_trough_no_gap": len(no_gap),
        "gap_crossing_episode_count": len(rows) - len(no_gap),
        "right_censored_episode_count": sum(bool(x["open_right_censored"]) for x in rows),
        "families_all": {str(g): family_summary(rows, g) for g in FAMILY_GAPS_DAYS},
        "families_no_gap": {str(g): family_summary(no_gap, g) for g in FAMILY_GAPS_DAYS},
        "episodes": rows,
    }


def naive_raw_ew_signature(points: list[dict[str, Any]]) -> dict[str, Any]:
    raw = [(x["t"], x["raw_ew_index"]) for x in points]
    eps = episodes(raw, 0.30, [])
    return {
        "naive_raw_ew_30pct_count": len(eps),
        "largest_drawdown_pct": min((float(x["drawdown_pct"]) for x in eps), default=None),
        "largest_examples": sorted(eps, key=lambda x: x["drawdown_pct"])[:3],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    source = args.repo_root / SOURCE
    rows = load_rows(source)
    result: dict[str, Any] = {
        "contract": "M6_GAP_SENSITIVE_EPISODE_POWER_CENSUS_v1",
        "mission_id": "RL-DISTRIBUTION-SURVIVAL-META-006",
        "status": "RESEARCH_ONLY_POWER_CENSUS",
        "method_path": METHOD,
        "source_path": str(SOURCE),
        "threshold_grid_pct": [20, 30, 40],
        "family_gap_grid_days": list(FAMILY_GAPS_DAYS),
        "windows": {},
        "authority": {
            "market_rule_change": False,
            "portfolio_action": False,
            "exit_rule": False,
            "canonical_promotion": False,
        },
    }

    for window in WINDOWS:
        points, gaps = build_window(rows, window)
        wout: dict[str, Any] = {
            "row_count": len(points),
            "first_timestamp_utc": points[0]["t"].isoformat().replace("+00:00", "Z"),
            "last_timestamp_utc": points[-1]["t"].isoformat().replace("+00:00", "Z"),
            "continuity_gap_count": len(gaps),
            "continuity_gap_timestamps_utc": [x.isoformat().replace("+00:00", "Z") for x in gaps],
            "rebase_trap_signature": naive_raw_ew_signature(points),
            "assets": {},
        }
        for asset, key in (("EW_ALT_CHAINED", "ew"), ("BTCUSDT", "btc")):
            series = [(x["t"], float(x[key])) for x in points]
            asset_out = {}
            for threshold in THRESHOLDS:
                eps = episodes(series, threshold, gaps)
                asset_out[str(int(threshold * 100))] = summarize_episode_set(eps)
            wout["assets"][asset] = asset_out
        result["windows"][window] = wout

    result["interpretation_boundary"] = [
        "Counts are an observable episode inventory, not evidence of framework warning skill.",
        "All 20/30/40 drawdown thresholds and 7/14/30-day family-gap rules are reported; none is selected post hoc as the true definition.",
        "Gap-crossing peak-to-trough paths remain visible but are separated from fully observed no-gap paths.",
        "No terminal-distribution label is inferred from drawdown magnitude alone.",
        "The 2020-2021 and 2025-2026 research windows are never stitched across the missing 2022-2024 period.",
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    compact = {}
    for w, wo in result["windows"].items():
        compact[w] = {}
        for asset, ao in wo["assets"].items():
            compact[w][asset] = {
                th: {
                    "episodes_all": x["episode_count_all_observed_endpoints"],
                    "episodes_no_gap": x["episode_count_peak_to_trough_no_gap"],
                    "families_no_gap": {g: v["family_count"] for g, v in x["families_no_gap"].items()},
                }
                for th, x in ao.items()
            }
    print(json.dumps({"status": "PASS", "summary": compact}, sort_keys=True))


if __name__ == "__main__":
    main()
