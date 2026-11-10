"""Task2 read-only original CN daily-close evidence, not Official score authority.

Requires the immutable original freeze and site first-known receipt.  Scores only
fully completed UTC days after the original post-freeze window, with explicit
SOURCE_GAP/UNMATURED and abstention accounting. Never emits trading signals.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CONTRACT = "TASK2_CN_DAILY_PATH_DESCRIPTIVE_SCORE_v1"
ROOT = "05_CYCLE_NAVIGATOR/weekly"
RECEIPT = "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json"
FORECAST = "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
ASSETS = ("BTC", "ETH")


def utc(s: str) -> datetime:
    if not isinstance(s, str) or not s.endswith("Z"):
        raise ValueError("UTC_Z_TIMESTAMP_REQUIRED")
    v = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if v.utcoffset() != timedelta(0):
        raise ValueError("UTC_Z_TIMESTAMP_REQUIRED")
    return v.astimezone(timezone.utc)


def iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("SOURCE_JSON_OBJECT_REQUIRED")
    return data


def number(x: Any) -> float:
    if isinstance(x, bool):
        raise ValueError("INVALID_NUMERIC_POINT")
    v = float(x)
    if not math.isfinite(v) or v <= 0:
        raise ValueError("INVALID_NUMERIC_POINT")
    return v


def original_source(root: Path, year: int, week: int) -> tuple[dict[str, Any], dict[str, Any], datetime, datetime, str]:
    directory = root / ROOT / str(year) / f"W{week:02d}"
    fp, rp = directory / FORECAST, directory / RECEIPT
    if rp.is_symlink() or not rp.is_file():
        raise ValueError("ORIGINAL_FREEZE_RECEIPT_REQUIRED")
    if fp.is_symlink() or not fp.is_file():
        raise ValueError("ORIGINAL_FORECAST_REQUIRED")
    receipt, forecast = json_file(rp), json_file(fp)
    digest = sha(fp)
    if receipt.get("contract") != "CN_SITE_PUBLIC_FREEZE_RECEIPT_v1":
        raise ValueError("ORIGINAL_FREEZE_RECEIPT_CONTRACT")
    if receipt.get("forecast_week") != f"{year}-W{week:02d}":
        raise ValueError("ORIGINAL_FORECAST_WEEK_MISMATCH")
    if receipt.get("source_forecast_freeze_sha256") != digest:
        raise ValueError("ORIGINAL_FORECAST_SHA256_MISMATCH")
    if receipt.get("status") != "SITE_FROZEN_SOURCE_OF_RECORD":
        raise ValueError("ORIGINAL_RECEIPT_NOT_PUBLISHED")
    issued = utc(receipt.get("daily_product_acceptance", {}).get("issued_at_utc"))
    valid = utc(receipt.get("scoring_valid_from_utc"))
    monday = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), tzinfo=timezone.utc)
    if not monday <= issued < monday + timedelta(days=7) or valid < issued:
        raise ValueError("ORIGINAL_FORECAST_CLOCK_INCONSISTENT")
    if forecast.get("daily_price_path", {}).get("forecast_week") != f"{year}-W{week:02d}":
        raise ValueError("ORIGINAL_DAILY_PATH_WEEK_MISMATCH")
    if forecast.get("daily_price_path", {}).get("contract") != "CN_FROZEN_DAILY_PRICE_PATH_v1":
        raise ValueError("ORIGINAL_DAILY_PATH_CONTRACT")
    if forecast.get("daily_range_plan", {}).get("contract") != "CN_FROZEN_DAILY_RANGE_PLAN_v1":
        raise ValueError("ORIGINAL_DAILY_RANGE_CONTRACT")
    for asset in ASSETS:
        if forecast.get("price_quote", {}).get(asset) != "USDT":
            raise ValueError("QUOTE_PARITY_NOT_DECLARED")
        path = forecast["daily_price_path"].get(asset, {})
        plan = forecast["daily_range_plan"].get(asset, {})
        if path.get("status") != "PUBLISHED" or plan.get("status") != "PUBLISHED":
            raise ValueError("ORIGINAL_DAILY_PATH_NOT_ISSUED")
        pts, bands = path.get("points"), plan.get("points")
        if not isinstance(pts, list) or not isinstance(bands, list) or len(pts) != 7 or len(bands) != 7:
            raise ValueError("ORIGINAL_DAILY_PATH_SEVEN_REQUIRED")
        for i, (point, band) in enumerate(zip(pts, bands), 1):
            if point.get("day") != i or band.get("day") != i:
                raise ValueError("ORIGINAL_DAILY_PATH_DAY_ORDER")
            target = number(point["expected_close"])
            lo, hi = number(point["low"]), number(point["high"])
            if lo > target or target > hi:
                raise ValueError("ORIGINAL_DAILY_BAND_INCONSISTENT")
            if lo != number(band["low"]) or hi != number(band["high"]):
                raise ValueError("ORIGINAL_RANGE_PLAN_MISMATCH")
    return receipt, forecast, issued, valid, digest


def completed_day_rows(root: Path, start: datetime, end: datetime, asset: str) -> tuple[str, list[dict[str, Any]], str | None]:
    """Use candle OPEN as identity, never collector source_window_end_utc."""
    daily = root / "03_DAILY_CAPTURE_LOGS/hourly" / str(start.year) / f"{start.month:02d}" / (start.date().isoformat() + ".csv")
    if daily.is_symlink() or not daily.is_file():
        return "SOURCE_GAP", [], None
    digest = sha(daily)
    try:
        with daily.open(newline="", encoding="utf-8") as handle:
            records = list(csv.DictReader(handle))
        found: dict[datetime, dict[str, Any]] = {}
        for r in records:
            t = utc(r.get("timestamp_utc", ""))
            if not start <= t < end:
                continue
            if t in found:
                raise ValueError("DUPLICATE_CANDLE")
            if r.get("spot_status") not in ("PASS", "OK"):
                raise ValueError("SOURCE_SPOT_NOT_PASS")
            o, h, l, c = (number(r[f"{asset.lower()}_{k}"]) for k in ("open", "high", "low", "close"))
            if l > min(o, c) or h < max(o, c) or l > h:
                raise ValueError("INVALID_HOURLY_OHLC")
            found[t] = {"time": t, "open": o, "high": h, "low": l, "close": c}
        expected = [start + timedelta(hours=i) for i in range(int((end - start).total_seconds() // 3600))]
        if sorted(found) != expected:
            raise ValueError("INCOMPLETE_HOURLY_CENSUS")
        return "MATURED_DESCRIPTIVE_ONLY", [found[t] for t in expected], digest
    except (ValueError, KeyError, TypeError, OSError, csv.Error):
        return "SOURCE_GAP", [], digest


def build(root: Path, year: int = 2026, week: int = 46, as_of: datetime | None = None) -> dict[str, Any]:
    root = root.resolve()
    as_of = as_of if as_of is not None else datetime.now(timezone.utc)
    if as_of.tzinfo is None or as_of.utcoffset() != timedelta(0):
        raise ValueError("AS_OF_MUST_BE_UTC")
    receipt, freeze, issued, valid, freeze_sha = original_source(root, year, week)
    monday = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), tzinfo=timezone.utc)
    outcome_rows = []
    for asset in ASSETS:
        for day in range(1, 8):
            point = freeze["daily_price_path"][asset]["points"][day - 1]
            start = monday + timedelta(days=day - 1)
            end = start + timedelta(days=1)
            eligible_start = max(start, valid)
            record: dict[str, Any] = {
                "asset": asset, "quote": "USDT", "day": day,
                "horizon_id": "H5_7D", "target_type": "UTC_DAILY_CLOSE",
                "target_end_utc": iso(end), "forecast_issued_at_utc": iso(issued),
                "forecast_expected_close": number(point["expected_close"]),
                "forecast_low": number(point["low"]), "forecast_high": number(point["high"]),
                "original_forecast_sha256": freeze_sha,
                "provider_original_first_known": "UNVERIFIED",
                "delivery_to_investor": "UNVERIFIED",
                "scientific_edge_admitted": False,
                "official_scoring_authority": False,
                "source_window_end_used_as_candle_clock": False,
            }
            if as_of < end:
                record.update(status="UNMATURED", actual_close=None, abs_error=None, band_status="UNMATURED")
            elif eligible_start >= end:
                record.update(status="ISSUED_TOO_LATE_FOR_TARGET", actual_close=None, abs_error=None, band_status="NOT_EVALUABLE")
            else:
                status, rows, source_hash = completed_day_rows(root, eligible_start, end, asset)
                record["source_daily_csv_sha256"] = source_hash
                record["eligible_observed_hours"] = len(rows)
                record["expected_eligible_hours"] = int((end - eligible_start).total_seconds() // 3600)
                if status != "MATURED_DESCRIPTIVE_ONLY":
                    record.update(status="SOURCE_GAP", actual_close=None, abs_error=None, band_status="NOT_EVALUABLE")
                else:
                    close = rows[-1]["close"]
                    pred = record["forecast_expected_close"]
                    partial = eligible_start > start
                    record.update(
                        status=status,
                        actual_close=close,
                        abs_error=round(abs(pred - close), 2),
                        pct_abs_error=round(100.0 * abs(pred - close) / close, 4),
                        realized_post_issue_low=min(r["low"] for r in rows),
                        realized_post_issue_high=max(r["high"] for r in rows),
                        interval_width=round(record["forecast_high"] - record["forecast_low"], 2),
                        band_status="PARTIAL_DAY_UNSCORED" if partial else "FULL_DAY_DESCRIPTIVE_ONLY",
                        joint_band_contains_extrema=None if partial else (
                            record["forecast_low"] <= min(r["low"] for r in rows)
                            and max(r["high"] for r in rows) <= record["forecast_high"]
                        ),
                    )
            outcome_rows.append(record)
    counts: dict[str, int] = {}
    for item in outcome_rows:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    return {
        "contract": CONTRACT, "research_owner_issue": 1596,
        "forecast_week": f"{year}-W{week:02d}", "as_of_utc": iso(as_of),
        "public_issue_number": receipt.get("public_issue_number"),
        "original_site_receipt_sha256": sha(root / ROOT / str(year) / f"W{week:02d}" / RECEIPT),
        "original_forecast_sha256": freeze_sha, "scoring_valid_from_utc": iso(valid),
        "classification": "DESCRIPTIVE_RESEARCH_NO_PROSPECTIVE_PIT_ADMISSION",
        "no_production_model_change": True, "no_public_score": True,
        "no_action_or_pnl_authority": True,
        "maturity_counts": counts, "total_original_daily_targets": len(outcome_rows),
        "baseline_and_proper_interval_score": "PENDING_INDEPENDENT_AS_OF_PRICE_AND_NOMINAL_QUANTILES",
        "rows": outcome_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--week", type=int, default=46)
    parser.add_argument("--as-of-utc", default=None)
    args = parser.parse_args()
    as_of = utc(args.as_of_utc) if args.as_of_utc else None
    print(json.dumps(build(args.repo_root, args.year, args.week, as_of), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
