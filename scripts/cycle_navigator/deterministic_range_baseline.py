#!/usr/bin/env python3
"""Deterministic weekly BTC/ETH range baseline for Cycle Navigator accountability.

The baseline is intentionally simple and independent from the LLM forecast:
- anchor on the last completed ISO-week close;
- estimate asymmetric upside/downside excursions from the median of the last
  four complete weekly high/open and low/open excursions;
- publish one prospective weekly envelope per asset.

It is a benchmark, not a market rule and not portfolio authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "CN_DETERMINISTIC_RANGE_BASELINE_v1"
SCORE_CONTRACT = "CN_DETERMINISTIC_RANGE_BASELINE_SCORE_v1"
METHOD = "MEDIAN_4W_ASYMMETRIC_WEEKLY_EXCURSION_FROM_PRIOR_CLOSE_v1"
LOOKBACK_WEEKS = 4


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _finite(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if value == value and value not in (float("inf"), float("-inf")) else None


def _week_key(value: Mapping[str, Any]) -> tuple[int, int] | None:
    year = value.get("iso_year")
    week = value.get("iso_week")
    if isinstance(year, int) and isinstance(week, int):
        return year, week
    return None


def _asset_week_range(pack: Mapping[str, Any], asset: str) -> dict[str, float] | None:
    row = (((pack.get("hourly_sequence") or {}).get(asset.lower()) or {}).get("week_range") or {})
    if not isinstance(row, Mapping):
        return None
    open_v, high, low, close = (_finite(row.get(k)) for k in ("open", "high", "low", "close"))
    if None in (open_v, high, low, close) or open_v <= 0 or low <= 0 or high < low:
        return None
    return {"open": open_v, "high": high, "low": low, "close": close}


def eligible_weekly_packs(repo: Path, *, before: tuple[int, int] | None = None) -> list[tuple[tuple[int, int], Path, dict[str, Any]]]:
    root = repo / "03_DAILY_CAPTURE_LOGS/weekly"
    rows: list[tuple[tuple[int, int], Path, dict[str, Any]]] = []
    if not root.exists():
        return rows
    for path in sorted(root.glob("*/*.json")):
        try:
            value = read_json(path)
        except Exception:
            continue
        key = _week_key(value)
        if key is None or (before is not None and key >= before):
            continue
        if value.get("contract") != "WEEKLY_RAW_CALIBRATION_PACK_v3" or value.get("readiness") != "READY":
            continue
        observed = ((value.get("hourly_gap_diagnostics") or {}).get("observed_hours"))
        if observed != 168:
            continue
        if _asset_week_range(value, "BTC") is None or _asset_week_range(value, "ETH") is None:
            continue
        rows.append((key, path.relative_to(repo), value))
    rows.sort(key=lambda x: x[0])
    return rows


def _asset_baseline(packs: list[tuple[tuple[int, int], Path, dict[str, Any]]], asset: str) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    for key, path, pack in packs:
        r = _asset_week_range(pack, asset)
        if r is None:
            continue
        up = max(0.0, r["high"] / r["open"] - 1.0)
        down = max(0.0, 1.0 - r["low"] / r["open"])
        samples.append({
            "iso_year": key[0],
            "iso_week": key[1],
            "source_path": path.as_posix(),
            "open": r["open"],
            "close": r["close"],
            "up_excursion_pct": up * 100.0,
            "down_excursion_pct": down * 100.0,
        })
    if not samples:
        return {"status": "UNAVAILABLE", "reason": "NO_ELIGIBLE_WEEKLY_SAMPLES"}
    anchor = samples[-1]["close"]
    up_pct = float(statistics.median(row["up_excursion_pct"] for row in samples))
    down_pct = float(statistics.median(row["down_excursion_pct"] for row in samples))
    low = anchor * (1.0 - down_pct / 100.0)
    high = anchor * (1.0 + up_pct / 100.0)
    return {
        "status": "READY",
        "anchor_price": anchor,
        "median_up_excursion_pct": up_pct,
        "median_down_excursion_pct": down_pct,
        "low": low,
        "high": high,
        "predicted_width_pct_of_anchor": (high - low) / anchor * 100.0,
        "samples": samples,
    }


def build_baseline(repo: Path, *, target_year: int, target_week: int, lookback_weeks: int = LOOKBACK_WEEKS) -> dict[str, Any]:
    target = (target_year, target_week)
    eligible = eligible_weekly_packs(repo, before=target)
    selected = eligible[-lookback_weeks:]
    source_keys = [f"{year}-W{week:02d}" for (year, week), _, _ in selected]
    value = {
        "contract": CONTRACT,
        "method": METHOD,
        "target_iso_year": target_year,
        "target_iso_week": target_week,
        "lookback_weeks_requested": lookback_weeks,
        "lookback_weeks_used": len(selected),
        "source_weeks": source_keys,
        "assets": {
            "BTC": _asset_baseline(selected, "BTC"),
            "ETH": _asset_baseline(selected, "ETH"),
        },
        "independence": {
            "llm_forecast_input": False,
            "generated_without_cycle_navigator_model_output": True,
            "purpose": "SIMPLE_RANGE_BENCHMARK",
        },
        "authority": {
            "portfolio_execution": False,
            "market_threshold_change": False,
            "model_weight_change": False,
            "official_range_override": False,
            "automatic_promotion": False,
        },
    }
    value["baseline_sha256"] = digest({k: v for k, v in value.items() if k != "baseline_sha256"})
    return value


def score_baseline(baseline: Mapping[str, Any], actual_pack: Mapping[str, Any]) -> dict[str, Any]:
    target = (baseline.get("target_iso_year"), baseline.get("target_iso_week"))
    actual_key = _week_key(actual_pack)
    if actual_key != target:
        raise ValueError("baseline_actual_week_mismatch")
    result: dict[str, Any] = {
        "contract": SCORE_CONTRACT,
        "baseline_contract": baseline.get("contract"),
        "baseline_sha256": baseline.get("baseline_sha256"),
        "target_iso_year": target[0],
        "target_iso_week": target[1],
        "assets": {},
        "authority": {
            "portfolio_execution": False,
            "market_threshold_change": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        },
    }
    for asset in ("BTC", "ETH"):
        pred = ((baseline.get("assets") or {}).get(asset) or {})
        actual = _asset_week_range(actual_pack, asset)
        if pred.get("status") != "READY" or actual is None:
            result["assets"][asset] = {"status": "UNAVAILABLE"}
            continue
        low, high = _finite(pred.get("low")), _finite(pred.get("high"))
        if low is None or high is None:
            result["assets"][asset] = {"status": "UNAVAILABLE"}
            continue
        lower_miss = max(0.0, low - actual["low"])
        upper_miss = max(0.0, actual["high"] - high)
        result["assets"][asset] = {
            "status": "SCORED",
            "predicted_low": low,
            "predicted_high": high,
            "actual_low": actual["low"],
            "actual_high": actual["high"],
            "full_range_contained": low <= actual["low"] and high >= actual["high"],
            "lower_miss_pct_of_actual_open": lower_miss / actual["open"] * 100.0,
            "upper_miss_pct_of_actual_open": upper_miss / actual["open"] * 100.0,
            "predicted_width_pct_of_actual_open": (high - low) / actual["open"] * 100.0,
            "actual_width_pct_of_actual_open": (actual["high"] - actual["low"]) / actual["open"] * 100.0,
            "midpoint_error_pct_of_actual_open": abs(((high + low) / 2.0) - ((actual["high"] + actual["low"]) / 2.0)) / actual["open"] * 100.0,
        }
    result["score_sha256"] = digest({k: v for k, v in result.items() if k != "score_sha256"})
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--target-year", type=int, required=True)
    ap.add_argument("--target-week", type=int, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    value = build_baseline(args.repo_root.resolve(), target_year=args.target_year, target_week=args.target_week)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(value))
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
