#!/usr/bin/env python3
"""Append-only CN weekly graph archive and source-only public BTC timeline.

No model, market decision or forecast is created here. W45 is the first
eligible week; immutable source freezes are never rewritten.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.cycle_navigator.daily_price_journey import validate_daily_path

START = date(2026, 11, 2)
CONTRACT = "CN_GRAPH_HISTORY_v1"
ROOT = Path("05_CYCLE_NAVIGATOR/graph_history/v1")
WEEKLY = Path("05_CYCLE_NAVIGATOR/weekly")
HOURLY = Path("03_DAILY_CAPTURE_LOGS/hourly")
PUBLIC = Path("05_CYCLE_NAVIGATOR/site/dist/data")
UTC = timezone.utc


def iso(t):
    return t.astimezone(UTC).isoformat().replace("+00:00", "Z")


def dt(value):
    if not isinstance(value, str):
        raise ValueError("invalid_source_clock")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timezone_required")
    return result.astimezone(UTC)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def write(path, payload, *, immutable=False):
    data = canonical(payload)
    if path.exists() and path.read_bytes() == data:
        return
    if immutable and path.exists():
        raise ValueError(f"IMMUTABLE_HISTORY_CONFLICT:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_bytes(data)
    os.replace(temp, path)


def week_label(monday):
    y, w, _ = monday.isocalendar()
    return f"{y}-W{w:02d}", y, w


def week_folder(root, monday):
    _, y, w = week_label(monday)
    return root / ROOT / "weeks" / str(y) / f"W{w:02d}"


def weekly_folder(root, monday):
    _, y, w = week_label(monday)
    return root / WEEKLY / str(y) / f"W{w:02d}"


def load_original(root, monday):
    label, year, week = week_label(monday)
    folder = weekly_folder(root, monday)
    freeze_file = folder / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    if not freeze_file.is_file():
        return None
    original_bytes = freeze_file.read_bytes()
    original_sha = digest(original_bytes)
    pointer = read(folder / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json")
    machine = read(folder / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json")
    if (pointer.get("forecast_freeze_sha256") != original_sha or
            pointer.get("iso_year") != year or pointer.get("iso_week") != week or
            machine.get("public_issue_number") != pointer.get("public_issue_number")):
        raise ValueError(f"ORIGINAL_FREEZE_BINDING_MISMATCH:{label}")
    receipt_file = folder / "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json"
    receipt = read(receipt_file) if receipt_file.exists() else {}
    if receipt and (receipt.get("forecast_week") != label or
                    receipt.get("source_forecast_freeze_sha256") != original_sha or
                    receipt.get("public_issue_number") != pointer.get("public_issue_number")):
        raise ValueError(f"PUBLIC_FREEZE_RECEIPT_MISMATCH:{label}")
    freeze = json.loads(original_bytes)
    path = validate_daily_path(freeze.get("daily_price_path"), freeze, year, week)
    if path is None:
        path = {"forecast_week": label, "BTC": {"status": "UNAVAILABLE", "points": [], "reason": "NO_ORIGINAL_DAILY_PATH"},
                "ETH": {"status": "UNAVAILABLE", "points": [], "reason": "NO_ORIGINAL_DAILY_PATH"}}
    issued = datetime.fromtimestamp(int(machine["generated_unix"]), UTC)
    first_eligible = dt(receipt["scoring_valid_from_utc"]) if receipt.get("scoring_valid_from_utc") else (
        issued.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
    monday_utc = datetime.combine(monday, datetime.min.time(), UTC)
    eligible = monday_utc <= issued < monday_utc + timedelta(days=1) and issued < first_eligible
    asset_rows = {}
    for asset in ("BTC", "ETH"):
        row = path[asset]
        published = row["status"] == "PUBLISHED" and eligible
        asset_rows[asset] = {
            "status": "PUBLISHED" if published else "UNAVAILABLE",
            "reason": None if published else ("ORIGINAL_FIRST_KNOWN_NOT_PROSPECTIVE" if row["status"] == "PUBLISHED" else row.get("reason") or "NOT_ISSUED"),
            "points": [{"day": p["day"], "expected_close": p["expected_close"], "low": p["low"], "high": p["high"]}
                       for p in row["points"]] if published else [],
        }
    return {
        "contract": "CN_GRAPH_HISTORY_FORECAST_v1", "forecast_week": label,
        "public_issue_number": pointer["public_issue_number"],
        "original_source_path": str(freeze_file.relative_to(root)),
        "original_source_sha256": original_sha, "issued_at_utc": iso(issued),
        "first_eligible_utc": iso(first_eligible), "forecast_quote_unit": "USD",
        "authoritative_forecast": False, "portfolio_action": False,
        "BTC": asset_rows["BTC"], "ETH": asset_rows["ETH"],
    }


def observed(root, monday):
    """Publicly owned hourly spot closes, never interpolate or mask missing hours."""
    label, _, _ = week_label(monday)
    start = datetime.combine(monday, datetime.min.time(), UTC)
    slots = {}
    for offset in range(7):
        day = monday + timedelta(days=offset)
        path = root / HOURLY / str(day.year) / f"{day.month:02d}" / f"{day.isoformat()}.csv"
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                try:
                    opened = dt(row["timestamp_utc"])
                    if not start <= opened < start + timedelta(days=7) or opened.minute or opened.second or opened.microsecond:
                        continue
                    if row.get("spot_status", "").upper() not in ("PASS", "OK"):
                        continue
                    prices = [float(row[f"{asset.lower()}_close"]) for asset in ("BTC", "ETH")]
                    if not all(math.isfinite(p) and p > 0 for p in prices):
                        continue
                    key = iso(opened + timedelta(hours=1))
                    payload = {"observed_at_utc": key, "BTC": prices[0], "ETH": prices[1]}
                    if key in slots and slots[key] != payload:
                        raise ValueError(f"CONFLICTING_SOURCE_HOUR:{label}:{key}")
                    slots[key] = payload
                except (ValueError, KeyError) as exc:
                    if isinstance(exc, ValueError) and str(exc).startswith("CONFLICTING_SOURCE_HOUR:"):
                        raise
                    continue
    result = [slots[key] for key in sorted(slots)]
    return {"contract": "CN_GRAPH_HISTORY_ACTUAL_v1", "forecast_week": label,
            "actual_quote_unit": "USDT", "semantics": "PASS_HOURLY_CLOSE_ONLY",
            "observed_hours": len(result), "expected_hours": 168,
            "status": "COMPLETE" if len(result) == 168 else "PARTIAL",
            "points": result}


def archive(root, target):
    if target < START:
        return {"contract": CONTRACT, "status": "NOT_STARTED", "weeks": []}
    result = []
    cursor = START
    previous = None
    chain = "0" * 64
    while cursor <= target:
        label, _, _ = week_label(cursor)
        folder = week_folder(root, cursor)
        forecast_file = folder / "forecast-reference.json"
        actual_file = folder / "actual-series.json"
        original = load_original(root, cursor)
        if original is not None:
            write(forecast_file, original, immutable=True)
            # Only completed weeks are durably materialized. The live week
            # remains in existing hourly/PAGES readback until its next Monday.
            if cursor < target:
                actual = observed(root, cursor)
                if actual_file.exists():
                    prior = read(actual_file)
                    old = prior.get("points", [])
                    new_map = {r["observed_at_utc"]: r for r in actual["points"]}
                    if any(new_map.get(p["observed_at_utc"]) != p for p in old):
                        raise ValueError(f"ACTUAL_MUTATION_OR_LOST_HOUR:{label}")
                write(actual_file, actual)
        status = "MISSING_FREEZE" if original is None else "RECORDED"
        sha = original["original_source_sha256"] if original is not None else None
        chain = digest(canonical({"previous": chain, "week": label, "source_sha256": sha, "status": status}))
        result.append({"forecast_week": label, "status": status, "previous_week": previous,
                       "source_sha256": sha, "chain_digest": chain,
                       "forecast_path": str(forecast_file.relative_to(root)) if original else None,
                       "actual_path": str(actual_file.relative_to(root)) if actual_file.exists() else None})
        previous = label
        cursor += timedelta(days=7)
    payload = {"contract": CONTRACT, "start_week": "2026-W45",
               "semantics": "SOURCE_ONLY_PRESENTATION_NO_TRADING_AUTHORITY",
               "weeks": result, "chain_tip": chain}
    write(root / ROOT / "index.json", payload)
    return payload


def publish(root):
    index_file = root / ROOT / "index.json"
    index = read(index_file) if index_file.exists() else {"contract": CONTRACT, "weeks": []}
    if index.get("contract") != CONTRACT:
        raise ValueError("INVALID_HISTORY_INDEX")
    weeks, actual = [], []
    for item in index["weeks"]:
        label = item["forecast_week"]
        prediction = read(root / item["forecast_path"]) if item.get("forecast_path") else None
        past = read(root / item["actual_path"]) if item.get("actual_path") else None
        if prediction and prediction.get("original_source_sha256") != item["source_sha256"]:
            raise ValueError(f"HISTORY_SOURCE_HASH_MISMATCH:{label}")
        weeks.append({"week": label, "status": item["status"],
                      "source_sha256": item.get("source_sha256"),
                      "issued_at_utc": prediction["issued_at_utc"] if prediction else None,
                      "first_eligible_utc": prediction["first_eligible_utc"] if prediction else None,
                      "forecast_status": prediction["BTC"]["status"] if prediction else "UNAVAILABLE",
                      "forecast": prediction["BTC"]["points"] if prediction else [],
                      "forecast_reason": prediction["BTC"]["reason"] if prediction else "MISSING_FREEZE",
                      "actual_status": past["status"] if past else "PENDING",
                      "observed_hours": past["observed_hours"] if past else 0})
        if past:
            actual.extend({"time": p["observed_at_utc"], "close": p["BTC"]} for p in past["points"])
    # The site's existing LIVE source is the only owner for current-week points.
    live_file = root / PUBLIC / "latest.json"
    if weeks and live_file.exists():
        latest = read(live_file)
        live = latest.get("public_live_precision") or {}
        prices = live.get("hourly_price_path") or {}
        current = weeks[-1]
        if (live.get("contract") == "CN_PUBLIC_LIVE_PRICE_PRECISION_v1" and
                prices.get("contract") == "CN_PUBLIC_HOURLY_PRICE_PATH_v1" and
                prices.get("source") == "HOURLY_SPOT_PASS_ONLY" and
                prices.get("forecast_week") == current["week"] and
                live.get("forecast_week") == current["week"]):
            seen = {x["time"] for x in actual}
            for p in prices.get("BTC", []):
                try:
                    clock = dt(p["observed_at_utc"])
                    value = float(p["close"])
                    if math.isfinite(value) and value > 0 and iso(clock) not in seen:
                        actual.append({"time": iso(clock), "close": value})
                        seen.add(iso(clock))
                except (KeyError, TypeError, ValueError):
                    continue
            current["actual_status"] = "LIVE"
            current["observed_hours"] = len(prices.get("BTC", []))
    actual.sort(key=lambda p: p["time"])
    payload = {"contract": "CN_GRAPH_HISTORY_TIMELINE_v1", "start_week": "2026-W45",
               "forecast_unit": "USD", "actual_unit": "USDT",
               "comparison_precision_eligible": False,
               "comparison_caveat": "Nominal USD forecasts vs USDT spot observations; no calibrated forecast accuracy claim.",
               "weeks": weeks, "actual": actual}
    dist = root / PUBLIC / "graph-history"
    write(dist / "timeline.json", payload)
    preview = root / "05_CYCLE_NAVIGATOR/site/graph-history/index.html"
    if preview.exists():
        destination = root / "05_CYCLE_NAVIGATOR/site/dist/graph-history/index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(preview.read_bytes())
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--mode", choices=("archive", "public"), required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    if args.mode == "archive":
        ptr = read(root / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
        target = date.fromisocalendar(int(ptr["iso_year"]), int(ptr["iso_week"]), 1)
        result = archive(root, target)
        print(json.dumps({"mode": "archive", "status": "PASS", "weeks": len(result["weeks"]),
                          "target_week": week_label(target)[0]}, sort_keys=True))
    else:
        result = publish(root)
        print(json.dumps({"mode": "public", "status": "PASS", "weeks": len(result["weeks"]),
                          "actual_hours": len(result["actual"])}, sort_keys=True))


if __name__ == "__main__":
    main()
