"""Read-only R6 join for retained public source diagnostics.

Only a newly frozen snapshot can join a completed full intraday window.
No historical baseline reconstruction, partial window, or scientific admission.
Local content integrity and source agreement are NOT server first-acceptance
or original provider byte attestation. The existing scientific controller
must continue to receive zero eligible outcomes until that authority exists.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from scripts.cycle_navigator.materialize_public_scorecard import interval_score
from scripts.cycle_navigator.range_freeze_baselines import _bar, _aggregate, _clock, _number, _read

WINDOWS = {"day_1_2": (0, 2), "day_3_4": (2, 4), "day_5_7": (4, 7)}
METHODS = ("DUMB1.5", "DUMB2.0", "PREVWK")
FORMULA = "70pct_containment_plus_30pct_jaccard"
LEDGER = "05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(value, reason):
    if not value:
        raise ValueError(reason)


def obj(repo, path):
    raw = _read(repo, path)
    value = json.loads(raw)
    require(isinstance(value, dict), "INVALID_SOURCE_OBJECT")
    return raw, value


def _range(value):
    a, b = _number(value["low"]), _number(value["high"])
    require(a < b, "INVALID_RANGE")
    return a, b


def _forecast_range(freeze, asset, window):
    text = str(freeze["intraday_map"][window])
    found = re.findall(rf"{asset}\s*\$?([\d,]+(?:\.\d+)?)\s*[–-]\s*\$?([\d,]+(?:\.\d+)?)", text, re.I)
    require(len(found) == 1, "FROZEN_RANGE_AMBIGUOUS")
    return tuple(_number(v.replace(",", "")) for v in found[0])


def _join(repo, row, now):
    asset, window, label = row["asset"], row["window"], row["forecast_week"]
    require(row.get("contract") == "CN_FORWARD_RANGE_FREEZE_v2" and asset in ("BTC","ETH")
            and window in WINDOWS and re.fullmatch(r"[0-9]{4}-W[0-9]{2}", label), "UNSUPPORTED_IDENTITY")
    year, week = int(label[:4]), int(label[-2:])
    monday = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), timezone.utc)
    start, stop = (monday + timedelta(days=x) for x in WINDOWS[window])
    clock = row.get("generated_unix")
    require(type(clock) is int and row.get("status") == "FROZEN_PROSPECTIVE"
            and datetime.fromtimestamp(clock, timezone.utc) <= start, "NOT_FULL_WINDOW_PROSPECTIVE")
    require(now >= monday+timedelta(days=7), "WEEK_NOT_MATURE")
    public, machine = row["public_issue_number"], row["machine_issue_number"]
    require(type(public) is int and public > 0 and type(machine) is int and machine > 0, "INVALID_ISSUE_ID")
    folder = Path("05_CYCLE_NAVIGATOR/weekly") / str(year) / f"W{week:02d}"
    freeze_raw, freeze = obj(repo, folder/"CYCLE_NAVIGATOR_FORECAST_FREEZE.json")
    _, receipt = obj(repo, folder/"CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json")
    _, binding = obj(repo, folder/"CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json")
    manifest_raw, manifest = obj(repo, folder/"CYCLE_NAVIGATOR_SOURCE_MANIFEST.json")
    _, package = obj(repo, folder/"CYCLE_NAVIGATOR_MACHINE_PACKAGE.json")
    require(receipt["contract"] == "CN_SITE_PUBLIC_FREEZE_RECEIPT_v1"
            and receipt["status"] == "SITE_FROZEN_SOURCE_OF_RECORD"
            and receipt["forecast_week"] == label and receipt["frozen_unix"] == clock
            and receipt["public_issue_number"] == public and receipt["machine_issue_number"] == machine
            and receipt["source_forecast_freeze_path"] == (folder/"CYCLE_NAVIGATOR_FORECAST_FREEZE.json").as_posix()
            and receipt["source_forecast_freeze_sha256"] == sha(freeze_raw)
            and receipt["source_manifest_sha256"] == sha(manifest_raw)
            and receipt["source_binding_path"] == (folder/"CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json").as_posix()
            and receipt["score_formula"] == FORMULA and receipt["score_window_policy"] == "FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1"
            and _clock(receipt["scoring_valid_from_utc"]) <= start, "FREEZE_RECEIPT_MISMATCH")
    require(binding["contract"] == "CN_PUBLIC_SERIES_BINDING_v1" and binding["forecast_week"] == label
            and binding["public_issue_number"] == public and binding["machine_issue_number"] == machine
            and package["contract"] == "CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1"
            and package["generated_unix"] == clock and package["issue_number"] == machine
            and package["public_issue_number"] == public and package["forecast_freeze"] == freeze
            and package["source_manifest_sha256"] == sha(manifest_raw)
            and manifest["contract"] == "CYCLE_NAVIGATOR_SOURCE_MANIFEST_v1"
            and (manifest["target_iso_year"], manifest["target_iso_week"]) == (year,week)
            and manifest["issue_number"] == machine and manifest["public_issue_number"] == public,
            "MANIFEST_OR_MACHINE_MISMATCH")
    snapshot = manifest["range_benchmark_freeze"]
    payload = {k:v for k,v in snapshot.items() if k != "snapshot_sha256"}
    snapshot_hash = sha(json.dumps(payload, sort_keys=True, separators=(",",":"), allow_nan=False).encode())
    require(snapshot["contract"] == "CN_RANGE_BENCHMARK_FREEZE_v1" and snapshot["status"] == "FROZEN_RETAINED_SNAPSHOT"
            and snapshot["scientific_admission"] is False and snapshot["generated_unix"] == clock
            and snapshot["quote_unit"] == "USDT" and snapshot["history_days"] == 63
            and snapshot["snapshot_sha256"] == snapshot_hash == row["baseline_snapshot_sha256"] == receipt["range_benchmark_snapshot_sha256"]
            and row["baseline_quote_unit"] == freeze["price_quote"][asset] == "USDT", "BASELINE_SNAPSHOT_MISMATCH")
    baselines = snapshot["assets"][asset]
    require(all(row[k] == baselines[k] for k in METHODS), "BASELINE_VALUES_MISMATCH")
    ranges = {k:_range(baselines[k]) for k in METHODS}
    forecast = _forecast_range(freeze, asset, window)
    require(forecast == (_number(row["forecast_low"]), _number(row["forecast_high"])) and forecast[0] < forecast[1], "FORECAST_RANGE_MISMATCH")
    capture_path = Path("03_DAILY_CAPTURE_LOGS/weekly") / str(year) / f"W{week:02d}.json"
    actual_raw, actual = obj(repo, capture_path)
    seq, diag = actual["hourly_sequence"], actual["hourly_gap_diagnostics"]
    actual_clock = _clock(actual["generated_at_utc"])
    quote = seq["spot_flow_readback"][asset]
    require(actual["contract"] == "WEEKLY_RAW_CALIBRATION_PACK_v3" and actual["readiness"] == "READY"
            and (actual["iso_year"], actual["iso_week"]) == (year,week)
            and diag["observed_hours"] == seq["spot_complete_hours"] == 168 and diag["missing_hour_count"] == 0
            and quote["symbol"] == asset+"USDT" and quote["quote_unit"] == "USDT"
            and monday+timedelta(days=7) <= actual_clock <= now, "ACTUAL_PACK_UNQUALIFIED")
    csv_path = capture_path.with_suffix("")/"WEEKLY_HOURLY_ENRICHED.csv"
    require(actual["enriched_hourly_path"] == csv_path.relative_to("03_DAILY_CAPTURE_LOGS").as_posix(), "ACTUAL_CSV_PATH_MISMATCH")
    hourly_raw = _read(repo, csv_path)
    reader = csv.DictReader(io.StringIO(hourly_raw.decode()))
    require(reader.fieldnames and len(set(reader.fieldnames)) == len(reader.fieldnames), "AMBIGUOUS_ACTUAL_FIELDS")
    rows = list(reader)
    require(len(rows) == 168, "INCOMPLETE_ACTUAL_ROWS")
    all_bars, selected = [], []
    for i, r in enumerate(rows):
        at = monday+timedelta(hours=i)
        require(None not in r and r["spot_status"] == "PASS" and _clock(r["timestamp_utc"]) == at
                and at+timedelta(hours=1) <= _clock(r["source_window_end_utc"]) <= actual_clock, "INVALID_ACTUAL_HOUR")
        bar = _bar([r[asset.lower()+"_"+k] for k in ("open","high","low","close")])
        all_bars.append(bar)
        if start <= at < stop:
            selected.append(bar)
    summary = seq[asset.lower()]["week_range"]
    require(_aggregate(all_bars) == _bar([summary[k] for k in ("open","high","low","close")])
            and len(selected) == int((stop-start).total_seconds()/3600), "ACTUAL_AGGREGATE_MISMATCH")
    _, high, low, _ = _aggregate(selected)
    score_path = Path("05_CYCLE_NAVIGATOR/public_scorecards") / str(year) / f"W{week:02d}" / f"CN{public}_PUBLIC_SCORECARD.json"
    score_raw, scorecard = obj(repo, score_path)
    precision = scorecard["price_range_precision"]
    proof = scorecard["lineage"]["public_proof"]
    require(scorecard["contract"] == "CN_PUBLIC_WEEKLY_SCORECARD_v1" and scorecard["status"] == "FINAL_DUAL_TRACK"
            and scorecard["forecast_week"] == scorecard["outcome_week"] == label and scorecard["public_issue_number"] == public
            and scorecard["lineage"]["machine_issue_number"] == machine
            and proof["channel"] == "SITE_SOURCE_OF_RECORD" and proof["freeze_sha256"] == sha(freeze_raw)
            and proof["receipt"] == (folder/"CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json").as_posix()
            and precision["source"] == LEDGER and precision["actuals"] == capture_path.as_posix()
            and precision["actuals_hourly_coverage"] == 168 and precision["formula"] == FORMULA
            and precision["score_window_policy"] == receipt["score_window_policy"]
            and precision["scoring_valid_from_utc"] == receipt["scoring_valid_from_utc"], "SCORECARD_SOURCE_MISMATCH")
    scores = [s for s in precision["rows"] if (s["asset"],s["window"]) == (asset,window)]
    require(len(scores) == 1, "SCORECARD_ROW_AMBIGUOUS")
    s = scores[0]
    cn_score = interval_score(*map(float, (*forecast,low,high)))
    require((_number(s["forecast_low"]),_number(s["forecast_high"])) == forecast
            and (_number(s["actual_low"]),_number(s["actual_high"])) == (low,high)
            and s["score_window_policy"] == receipt["score_window_policy"]
            and type(s["score"]) in (int,float) and s["score"] == cn_score, "SCORECARD_NUMERIC_MISMATCH")
    return {"public_issue_number":public,"forecast_week":label,"asset":asset,"window":window,
            "freeze_clock":clock,"snapshot_sha256":snapshot_hash,"source_manifest_sha256":sha(manifest_raw),
            "actual_pack_sha256":sha(actual_raw),"actual_hourly_sha256":sha(hourly_raw),"scorecard_sha256":sha(score_raw),
            "actual_low":float(low),"actual_high":float(high),"CN":cn_score,
            "benchmarks":{k:interval_score(*map(float, (*v,low,high))) for k,v in ranges.items()},
            "formula":FORMULA,"benchmark_scope":"WEEKLY_BANDS_APPLIED_TO_SAME_FULL_INTRADAY_WINDOW_DIAGNOSTIC",
            "scientific_admission":False,"independent_source_attestation":False}


def join_diagnostics(repo, rows, now):
    repo = Path(repo).resolve()
    if not isinstance(now, datetime) or now.utcoffset() is None:
        raise ValueError("aware evaluation clock required")
    counts, joined = Counter(), []
    identities = Counter((r.get("public_issue_number"),r.get("forecast_week"),r.get("asset"),r.get("window")) for r in rows)
    for row in rows:
        identity = (row.get("public_issue_number"),row.get("forecast_week"),row.get("asset"),row.get("window"))
        if identities[identity] != 1:
            counts["DUPLICATE_FREEZE_IDENTITY"] += 1
            continue
        if row.get("baseline_status") != "FROZEN_RETAINED_SNAPSHOT":
            counts["NO_ORIGINAL_FROZEN_BENCHMARK"] += 1
            continue
        try:
            joined.append(_join(repo, row, now))
        except ValueError as exc:
            reason = str(exc)
            counts[reason if re.fullmatch("[A-Z_]+",reason) else "MALFORMED_OR_UNAVAILABLE_SOURCE"] += 1
        except (OSError, KeyError, TypeError, AttributeError, ArithmeticError, OverflowError):
            counts["MALFORMED_OR_UNAVAILABLE_SOURCE"] += 1
    return {"contract":"CN_R6_RETAINED_OUTCOME_JOIN_DIAGNOSTIC_v1",
            "raw_rows":len(rows),"joined_rows":len(joined),"excluded":dict(sorted(counts.items())),
            "scientifically_eligible_rows":0,"independence_attested":False,"rows":joined}
