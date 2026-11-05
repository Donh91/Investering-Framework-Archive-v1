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
    # The archive is BTC-only. Its quote must come from the *original frozen
    # source*, never a static USD convention or the observed Binance USDT feed.
    original_units = freeze.get("price_quote")
    quoted_btc = original_units.get("BTC") if isinstance(original_units, dict) else None
    original_btc_quote = quoted_btc if quoted_btc in ("USD", "USDT") else "UNAVAILABLE"
    return {
        "contract": "CN_GRAPH_HISTORY_FORECAST_v1", "forecast_week": label,
        "public_issue_number": pointer["public_issue_number"],
        "original_source_path": str(freeze_file.relative_to(root)),
        "original_source_sha256": original_sha, "issued_at_utc": iso(issued),
        "first_eligible_utc": iso(first_eligible), "forecast_quote_unit": original_btc_quote,
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


def verify_index_chain(index, root=None):
    if index.get("contract") != CONTRACT or not isinstance(index.get("weeks"), list):
        raise ValueError("INVALID_HISTORY_INDEX")
    prior_weeks = {}
    prior_chain = "0" * 64
    prior_label = None
    for row in index["weeks"]:
        label = row.get("forecast_week")
        expected_monday = START + timedelta(days=7 * len(prior_weeks))
        expected_label, year, week = week_label(expected_monday)
        if label != expected_label or label in prior_weeks or row.get("previous_week") != prior_label:
            raise ValueError("INVALID_HISTORY_INDEX_SEQUENCE")
        expected_folder = ROOT / "weeks" / str(year) / f"W{week:02d}"
        expected_forecast = str(expected_folder / "forecast-reference.json")
        expected_actual = str(expected_folder / "actual-series.json")
        if ((row.get("forecast_path") != expected_forecast if row.get("status") == "RECORDED"
             else row.get("forecast_path") is not None) or
                row.get("actual_path") not in (None, expected_actual)):
            raise ValueError("INVALID_HISTORY_INDEX_PATH")
        if row.get("status") not in ("MISSING_FREEZE", "RECORDED"):
            raise ValueError("INVALID_HISTORY_INDEX_STATUS")
        sha = row.get("source_sha256")
        if (row["status"] == "MISSING_FREEZE" and sha is not None) or (
                row["status"] == "RECORDED" and not isinstance(sha, str)):
            raise ValueError("INVALID_HISTORY_INDEX_SOURCE")
        prior_chain = digest(canonical({"previous": prior_chain, "week": label,
                                        "source_sha256": sha, "status": row["status"]}))
        if row.get("chain_digest") != prior_chain:
            raise ValueError("INVALID_HISTORY_INDEX_CHAIN")
        # A rehashed index is not proof that the original frozen forecast
        # disappeared. Bind index status and source identity to the durable
        # on-disk forecast copy whenever the working archive is available.
        if root is not None:
            disk_forecast = root / expected_forecast
            if row["status"] == "MISSING_FREEZE" and disk_forecast.exists():
                raise ValueError(f"INDEX_DISK_RECORD_CONFLICT:{label}")
            if row["status"] == "RECORDED":
                if not disk_forecast.is_file():
                    raise ValueError(f"INDEX_DISK_RECORD_CONFLICT:{label}")
                if read(disk_forecast).get("original_source_sha256") != sha:
                    raise ValueError(f"INDEX_DISK_RECORD_CONFLICT:{label}")
            # Never let null actual_path hide a durable actual-series file.
            # A missing file is legitimate only when the index also says null.
            disk_actual = root / expected_actual
            if disk_actual.is_file() and row.get("actual_path") != expected_actual:
                raise ValueError(f"INDEX_DISK_ACTUAL_OMITTED:{label}")
            if row.get("actual_path") == expected_actual and not disk_actual.is_file():
                raise ValueError(f"INDEX_DISK_ACTUAL_MISSING:{label}")
        prior_weeks[label] = row
        prior_label = label
    if index.get("chain_tip") != prior_chain:
        raise ValueError("INVALID_HISTORY_INDEX_TIP")

    if root is not None:
        # A correctly re-chained prefix must not erase any durable suffix from
        # public history. This is LOCAL filesystem consistency, not an external
        # checkpoint against coordinated deletion of both index and files.
        represented = {path for row in index["weeks"]
                       for path in (row.get("forecast_path"), row.get("actual_path"))
                       if path is not None}
        weeks_dir = root / ROOT / "weeks"
        if weeks_dir.is_dir():
            for filename in ("forecast-reference.json", "actual-series.json"):
                for path in weeks_dir.rglob(filename):
                    if not path.is_file():
                        raise ValueError(f"INDEX_DISK_HISTORY_NOT_REGULAR_FILE:{path}")
                    relative = str(path.relative_to(root))
                    if relative not in represented:
                        raise ValueError(f"INDEX_DISK_UNINDEXED_HISTORY:{relative}")

    return prior_weeks


def _read_index_or_fail_missing_history(root):
    """Never silently bootstrap over an existing durable history after index loss.

    This is local consistency protection, NOT an external trusted checkpoint:
    deletion of the entire history tree remains outside its proof boundary.
    """
    index_file = root / ROOT / "index.json"
    if index_file.exists():
        return read(index_file)
    weeks_dir = root / ROOT / "weeks"
    for pattern in ("forecast-reference.json", "actual-series.json"):
        if weeks_dir.exists() and next(weeks_dir.rglob(pattern), None) is not None:
            raise ValueError("HISTORY_INDEX_MISSING_WITH_EXISTING_RECORDS")
    if (root / ROOT / "index.json.tmp").exists():
        raise ValueError("HISTORY_INDEX_MISSING_WITH_EXISTING_RECORDS")
    return None


def archive(root, target):
    if target < START:
        return {"contract": CONTRACT, "status": "NOT_STARTED", "weeks": []}
    index_file = root / ROOT / "index.json"
    old_index = _read_index_or_fail_missing_history(root)
    prior_weeks = verify_index_chain(old_index, root) if old_index is not None else {}
    result = []
    cursor = START
    previous = None
    chain = "0" * 64
    while cursor <= target:
        label, _, _ = week_label(cursor)
        folder = week_folder(root, cursor)
        forecast_file = folder / "forecast-reference.json"
        actual_file = folder / "actual-series.json"
        prior = prior_weeks.get(label)
        # Once a week's forecast status is recorded, it must never be backfilled
        # or silently withdrawn on a later archive run.
        original = None if prior and prior["status"] == "MISSING_FREEZE" else load_original(root, cursor)
        if prior and prior["status"] == "RECORDED" and (
                original is None or original["original_source_sha256"] != prior["source_sha256"]):
            raise ValueError(f"INDEX_HISTORY_REWRITE:{label}")
        if original is not None:
            if prior and cursor == START and forecast_file.is_file():
                # Pre-fix W45 used a static USD tag in its immutable reference
                # even though original W45 has no typed quote. Retain EXACT
                # historical bytes for compatibility, never reissue its values.
                # Public Graph History independently reads the hash-bound
                # original freeze's price_quote and still reports UNAVAILABLE.
                historical = read(forecast_file)
                if (historical.get("forecast_quote_unit") == "USD"
                        and original.get("forecast_quote_unit") == "UNAVAILABLE"
                        and {**historical, "forecast_quote_unit": "UNAVAILABLE"} == original):
                    original = historical
            write(forecast_file, original, immutable=True)
        # Historical green Hourly observations are independently sourced:
        # absence of a blue forecast MUST NOT erase valid actual closes.
        if cursor < target:
            actual = observed(root, cursor)
            if actual_file.exists():
                older_actual = read(actual_file)
                old = older_actual.get("points", [])
                new_map = {r["observed_at_utc"]: r for r in actual["points"]}
                if any(new_map.get(p["observed_at_utc"]) != p for p in old):
                    raise ValueError(f"ACTUAL_MUTATION_OR_LOST_HOUR:{label}")
            write(actual_file, actual)
        status = "MISSING_FREEZE" if original is None else "RECORDED"
        sha = original["original_source_sha256"] if original is not None else None
        chain = digest(canonical({"previous": chain, "week": label, "source_sha256": sha, "status": status}))
        if prior and prior.get("chain_digest") != chain:
            raise ValueError(f"INDEX_HISTORY_REWRITE:{label}")
        result.append({"forecast_week": label, "status": status, "previous_week": previous,
                       "source_sha256": sha, "chain_digest": chain,
                       "forecast_path": str(forecast_file.relative_to(root)) if original else None,
                       "actual_path": str(actual_file.relative_to(root)) if actual_file.exists() else None})
        previous = label
        cursor += timedelta(days=7)
    if set(prior_weeks) - {w["forecast_week"] for w in result}:
        raise ValueError("INDEX_HISTORY_TRUNCATION")
    payload = {"contract": CONTRACT, "start_week": "2026-W45",
               "semantics": "SOURCE_ONLY_PRESENTATION_NO_TRADING_AUTHORITY",
               "weeks": result, "chain_tip": chain}
    write(root / ROOT / "index.json", payload)
    return payload


def publish_w45_research_preview(root):
    """Optional clearly labeled SHADOW page, isolated from Graph B and CN output.

    Never issues, promotes, or modifies a forecast. Bad research evidence is
    quarantined WITHOUT blocking publication of the original green actual
    timeline or the canonical site.
    """
    original = root / "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_MIDWEEK_PROSPECTIVE_BENCHMARK_v1.json"
    html = root / "05_CYCLE_NAVIGATOR/site/research-w45/index.html"
    dst_data = root / "05_CYCLE_NAVIGATOR/site/dist/data/research-w45-shadow.json"
    dst_page = root / "05_CYCLE_NAVIGATOR/site/dist/research-w45/index.html"
    dst_outcomes = root / "05_CYCLE_NAVIGATOR/site/dist/data/research-w45-outcomes.json"
    dst_thursday = root / "05_CYCLE_NAVIGATOR/site/dist/data/research-w45-thursday-outcomes.json"
    frozen_thursday = root / "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_THURSDAY_SELFTEST_v1.json"
    def discard():
        for path in (dst_data, dst_page, dst_outcomes, dst_thursday):
            if path.exists():
                path.unlink()
    if not original.is_file() or not html.is_file():
        discard()
        return "NOT_AVAILABLE"
    try:
        # No authority promotion: the verifier requires both issuer and
        # first-known flags to remain research-only with original W45 0/7.
        from scripts.research.verify_w45_midweek_shadow_benchmark import verify
        verified = verify(read(original))
        if verified.get("status") != "PASS_RESEARCH_ONLY" or verified.get("official_cn_issued_points") != 0:
            raise ValueError("RESEARCH_W45_AUTHORITY_GUARD")
        markup = html.read_text(encoding="utf-8")
        if ('noindex,nofollow' not in markup or
                "RESEARCH_W45_MIDWEEK_FORWARD_BENCHMARK_v1" not in markup or
                "site_blue_original_forecast_eligible" not in markup or
                "Original blå mandagsprognose" not in markup):
            raise ValueError("RESEARCH_W45_PREVIEW_DISCLOSURE_GUARD")
        from scripts.research.w45_rehearsal_outcomes import compile_from_repo
        # Derive prospective, source-verified (or explicitly unavailable)
        # BTC+ETH outcome receipts from the already existing public capture.
        # This never updates the original research forecast or Monday CN.
        outcomes = compile_from_repo(root)
        if (outcomes.get("contract") != "RESEARCH_W45_PROSPECTIVE_OUTCOMES_v1"
                or outcomes.get("research_only") is not True
                or outcomes.get("official_scoring_eligible") is not False
                or outcomes.get("portfolio_action_authority") is not False):
            raise ValueError("W45_REHEARSAL_AUTHORITY_GUARD")
        dst_data.parent.mkdir(parents=True, exist_ok=True)
        dst_page.parent.mkdir(parents=True, exist_ok=True)
        # Preserve exact source bytes in the public research-only snapshot.
        dst_data.write_bytes(original.read_bytes())
        dst_outcomes.write_bytes(canonical(outcomes))
        dst_page.write_bytes(html.read_bytes())
        # Independent original owner comment-issued Thursday experiment.
        # Bad/missing optional experiment must NEVER block the original
        # Wednesday shadow page, original Graph B or canonical Pages.
        if frozen_thursday.is_file():
            try:
                from scripts.research.w45_thursday_selftest_outcomes import compile_from_repo as thursday_outcomes
                thursday = thursday_outcomes(root)
                if (thursday.get("contract") != "RESEARCH_W45_THURSDAY_SELFTEST_OUTCOMES_v1"
                        or thursday.get("research_only") is not True
                        or thursday.get("official_scoring_eligible") is not False
                        or thursday.get("portfolio_action_authority") is not False
                        or thursday.get("original_monday_daily_issued") != {"BTC": 0, "ETH": 0}):
                    raise ValueError("THURSDAY_SELFTEST_AUTHORITY_GUARD")
                dst_thursday.write_bytes(canonical(thursday))
            except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError):
                if dst_thursday.exists():
                    dst_thursday.unlink()
        elif dst_thursday.exists():
            dst_thursday.unlink()
        return "RESEARCH_ONLY_PUBLISHED"
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError):
        discard()
        return "RESEARCH_QUARANTINED"


def publish(root):
    index_file = root / ROOT / "index.json"
    index = _read_index_or_fail_missing_history(root) or {"contract": CONTRACT, "weeks": []}
    if index_file.exists():
        verify_index_chain(index, root)
    elif index.get("contract") != CONTRACT:
        raise ValueError("INVALID_HISTORY_INDEX")
    weeks, actual = [], []
    for item in index["weeks"]:
        label = item["forecast_week"]
        prediction = read(root / item["forecast_path"]) if item.get("forecast_path") else None
        past = read(root / item["actual_path"]) if item.get("actual_path") else None
        if prediction and prediction.get("original_source_sha256") != item["source_sha256"]:
            raise ValueError(f"HISTORY_SOURCE_HASH_MISMATCH:{label}")
        # The original W45 freeze does not declare a quote. Historical
        # forecast-reference.json is immutable and contains a legacy USD
        # label; the PUBLIC quote cannot inherit that unproven default.
        declared_quote = "UNAVAILABLE"
        if prediction:
            source_path = root / prediction["original_source_path"]
            if (not source_path.is_file() or
                    digest(source_path.read_bytes()) != prediction["original_source_sha256"]):
                raise ValueError(f"HISTORY_ORIGINAL_QUOTE_SOURCE_MISMATCH:{label}")
            original_quote = read(source_path).get("price_quote")
            if isinstance(original_quote, dict) and original_quote.get("BTC") in ("USD", "USDT"):
                declared_quote = original_quote["BTC"]
        weeks.append({"week": label, "status": item["status"],
                      "forecast_model_declared_quote": declared_quote,
                      "source_sha256": item.get("source_sha256"),
                      "public_issue_number": prediction["public_issue_number"] if prediction else None,
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
                live.get("forecast_week") == current["week"] and
                type(live.get("public_issue_number")) is int and
                live["public_issue_number"] > 0 and
                prices.get("public_issue_number") == live["public_issue_number"] and
                (current["public_issue_number"] is None or
                 live["public_issue_number"] == current["public_issue_number"])):
            monday = date.fromisocalendar(int(current["week"][:4]), int(current["week"][6:]), 1)
            week_start = datetime.combine(monday, datetime.min.time(), UTC)
            week_end = week_start + timedelta(days=7)
            cutoff = dt(prices["observed_through_utc"])
            seen = {x["time"] for x in actual}
            for p in prices.get("BTC", []):
                try:
                    clock = dt(p["observed_at_utc"])
                    value = float(p["close"])
                    if (math.isfinite(value) and value > 0 and
                            week_start < clock <= week_end and clock <= cutoff and
                            clock.minute == 0 and clock.second == 0 and iso(clock) not in seen):
                        actual.append({"time": iso(clock), "close": value})
                        seen.add(iso(clock))
                except (KeyError, TypeError, ValueError):
                    continue
            current["actual_status"] = "LIVE"
            current["observed_hours"] = len(prices.get("BTC", []))
    actual.sort(key=lambda p: p["time"])
    payload = {"contract": "CN_GRAPH_HISTORY_TIMELINE_v1", "start_week": "2026-W45",
               "forecast_unit": "PER_WEEK_DECLARED_OR_UNAVAILABLE", "actual_unit": "USDT",
               "comparison_precision_eligible": False,
               "comparison_caveat": "Forecast quote is source-declared per week or unavailable; observed native Binance spot is USDT. No automatic currency conversion or calibrated accuracy claim.",
               "weeks": weeks, "actual": actual}
    dist = root / PUBLIC / "graph-history"
    write(dist / "timeline.json", payload)
    preview = root / "05_CYCLE_NAVIGATOR/site/graph-history/index.html"
    if preview.exists():
        destination = root / "05_CYCLE_NAVIGATOR/site/dist/graph-history/index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(preview.read_bytes())
    # Independent optional research route: never modifies graph-history
    # response identity, official Blue/Green status or original freeze.
    research_status = publish_w45_research_preview(root)
    print(json.dumps({"research_preview": research_status}, sort_keys=True))
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
