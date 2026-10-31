#!/usr/bin/env python3
"""Source-bound rolling 14d and full-history Official Compass accountability.

This is EX-POST RESEARCH, not an original-issued point-in-time prediction audit,
a backtest that proves trading edge, or a mechanism for changing forecast weights.
It never changes original freezes, trading actions, CN, market data or forecasts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
# Imported as a package by unittest, but called as a standalone script in the
# EXISTING GitHub Outcomes workflow. Both must bind to the same official scorer.
if __package__:
    from scripts.learning.compass_outcomes import SIDEWAYS_TOLERANCE_PCT
    from scripts.learning.pullback_warning_timeliness_shadow import evaluate as evaluate_pullback_timebox
else:
    from compass_outcomes import SIDEWAYS_TOLERANCE_PCT
    from pullback_warning_timeliness_shadow import evaluate as evaluate_pullback_timebox

FORECAST_ROOT = Path("04_MARKET_LEARNING/handlekompas/official/daily")
HOURLY_ROOT = Path("03_DAILY_CAPTURE_LOGS/hourly")
OUTPUT_ROOT = Path("04_MARKET_LEARNING/handlekompas/research/rolling_14d")
CONTRACT = "KOMPAS_ROLLING_14D_HISTORICAL_ACCOUNTABILITY_v1"
HORIZONS = {"12h": ("NEXT_12H", 12), "72h": ("NEXT_1_3D", 72), "168h": ("NEXT_5_7D", 168)}
DIFFERENT_FROM_FORECAST = {"6h": 6, "24h": 24, "72h": 72}
EXPECTED_SCORING = "OFFICIAL_DAILY_COMPASS_SCORING_v3"
HOUR = timedelta(hours=1)


def stamp(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.astimezone(timezone.utc) if dt.utcoffset() is not None else None


def iso(dt: datetime | None) -> str | None:
    return dt.isoformat().replace("+00:00", "Z") if dt else None


def price(value) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_freezes(root: Path, asof: datetime, window_start: datetime | None):
    files = sorted((root / FORECAST_ROOT).rglob("CMP-*.json"))
    selected = []
    excluded = Counter()
    for path in files:
        try:
            raw = path.read_bytes()
            record = json.loads(raw)
            issued = stamp(record.get("issued_at_utc"))
            if record.get("contract") != "OFFICIAL_DAILY_COMPASS_v1" or issued is None:
                excluded["UNREADABLE_OR_BAD_CONTRACT"] += 1
                continue
            if issued > asof:
                excluded["AFTER_REPLAY_ASOF"] += 1
                continue
            if window_start and issued < window_start:
                excluded["OUTSIDE_14D_ISSUANCE_WINDOW"] += 1
                continue
            selected.append({"issued": issued, "data": record,
                             "path": path.relative_to(root).as_posix(),
                             "sha256": sha(raw)})
        except (OSError, ValueError, json.JSONDecodeError, TypeError):
            excluded["BAD_FILE_OR_JSON"] += 1
    selected.sort(key=lambda r: (r["issued"], r["path"]))
    return selected, {"all_discovered_files": len(files), "excluded": dict(excluded)}


def load_market(root: Path, start: datetime, end: datetime):
    day = (start - timedelta(days=1)).date()
    last = end.date()
    candles = {}
    conflict = set()
    files = []
    quality = Counter()
    while day <= last:
        rel = HOURLY_ROOT / f"{day:%Y/%m}/{day:%Y-%m-%d}.csv"
        path = root / rel
        day += timedelta(days=1)
        if not path.is_file():
            quality["missing_day_files"] += 1
            continue
        raw = path.read_bytes()
        files.append({"path": rel.as_posix(), "sha256": sha(raw)})
        try:
            rows = csv.DictReader(raw.decode("utf-8-sig").splitlines())
            for row in rows:
                opened = stamp(row.get("timestamp_utc"))
                if opened is None or opened.minute or opened.second or opened.microsecond:
                    quality["invalid_utc_hour_open"] += 1
                    continue
                closed = opened + HOUR
                if closed < start or closed > end:
                    continue
                collection_end = stamp(row.get("source_window_end_utc"))
                if collection_end is None or collection_end < closed:
                    quality["missing_or_invalid_collection_clock"] += 1
                    continue
                # Observed original availability is not provable from run coverage.
                if collection_end > end:
                    quality["not_known_by_analysis_asof"] += 1
                    continue
                b, e = price(row.get("btc_close")), price(row.get("eth_close"))
                if row.get("spot_status") != "PASS" or b is None or e is None:
                    quality["nonpass_or_missing_spot_close"] += 1
                    continue
                item = {"btc": b, "eth": e, "source_window_end_utc": iso(collection_end)}
                if closed in candles:
                    previous = candles[closed]
                    # The batch collection clock is NOT part of the candle's
                    # value/identity. Identical prices recollected at different
                    # batch ends must not fabricate a conflicting price bar.
                    if previous["btc"] != b or previous["eth"] != e:
                        conflict.add(closed)
                    else:
                        quality["matching_recollected_hour_rows"] += 1
                        # Retain the earliest archive collection marker only
                        # as metadata, NEVER as proven provider first-known.
                        previous_batch = stamp(previous["source_window_end_utc"])
                        if previous_batch is not None and collection_end < previous_batch:
                            candles[closed] = item
                else:
                    candles[closed] = item
        except (ValueError, UnicodeError, csv.Error):
            quality["bad_csv"] += 1
    for time in conflict:
        candles.pop(time, None)
    quality["conflicting_candle_clocks"] = len(conflict)
    return candles, files, dict(quality)


def one_report(entry: dict, candles: dict[datetime, dict], asof: datetime):
    f = entry["data"]
    issued = entry["issued"]
    ref = f.get("market_reference") or {}
    opened = stamp(ref.get("observation_open_utc"))
    t = opened + HOUR if opened else None
    r_btc = price(ref.get("btc_usdt"))
    r_eth = price(ref.get("eth_usdt"))
    age_h = round((issued - t).total_seconds()/3600, 4) if t else None
    if t is None or t > issued or (r_btc is None or r_eth is None):
        base_error = "QUARANTINE_INVALID_REFERENCE_OR_FUTURE_REFERENCE"
    else:
        base_error = None
    state = ((f.get("protection_tracker") or {}).get("pullback_risk_state") or "UNKNOWN")
    h = f.get("horizons") or {}
    # Frozen latest-momentum is only a NAIVE no-model comparison at the
    # same issue clock, not evidence of a prospective source timestamp.
    market_now = f.get("market_now") or {}
    momentum = market_now.get("btc_delta_pct")
    baseline_direction = ("UP" if isinstance(momentum, (int, float)) and
                          not isinstance(momentum, bool) and math.isfinite(momentum) and momentum > 0
                          else "DOWN" if isinstance(momentum, (int, float)) and
                          not isinstance(momentum, bool) and math.isfinite(momentum) and momentum < 0
                          else "UNAVAILABLE")
    signals = {}
    for label, (key, hours) in HORIZONS.items():
        predicted = (h.get(key) or {}).get("expected_direction") or "UNAVAILABLE"
        target = t + timedelta(hours=hours) if t else None
        # Nominal horizon starts at frozen reference candle CLOSE, not issue time.
        # Expose effective decision lead so users do not misread this as a
        # guaranteed 12h-forward path from publication.
        effective_lead_h = round((target - issued).total_seconds()/3600, 4) if target else None
        status = base_error
        ret = None
        if not status and f.get("scoring_contract") != EXPECTED_SCORING:
            status = "LEGACY_SCORING_CONTRACT_NOT_REINTERPRETED"
        elif not status and target <= issued:
            status = "QUARANTINE_NONPROSPECTIVE_TARGET"
        elif not status and target > asof:
            status = "PENDING_NOT_MATURE"
        elif not status:
            observed = candles.get(target)
            if observed is None:
                status = "UNAVAILABLE_TARGET_CANDLE"
            else:
                ret = 100*(observed["btc"]/r_btc-1)
                status = "MATURED_EXPOST_ONLY"
        if status == "MATURED_EXPOST_ONLY" and predicted in ("UP", "DOWN", "SIDEWAYS"):
            correct = ((ret > 0) if predicted == "UP" else
                       (ret < 0) if predicted == "DOWN" else
                       abs(ret) <= SIDEWAYS_TOLERANCE_PCT[label])
            scored = "CORRECT" if correct else "INCORRECT"
        elif predicted in ("MIXED", "NO_EDGE", "UNAVAILABLE"):
            scored = "ABSTAIN_NO_DIRECTIONAL_CLAIM"
        else:
            scored = "NOT_SCORED"
        signals[label] = {
            "expected_direction": predicted, "target_at_utc": iso(target),
            "nominal_hours_from_reference_close": hours,
            "effective_forward_hours_from_issuance": effective_lead_h,
            "time_basis": "REFERENCE_CANDLE_CLOSE_NOT_ISSUANCE",
            "status": status, "btc_close_return_pct": round(ret, 5) if ret is not None else None,
            "descriptive_direction_result": scored,
            "frozen_momentum_baseline_direction": baseline_direction,
            "momentum_baseline_result": (
                ("CORRECT" if ((ret > 0) if baseline_direction == "UP" else (ret < 0))
                 else "INCORRECT") if status == "MATURED_EXPOST_ONLY" and
                 baseline_direction in ("UP", "DOWN") else "NOT_SCORED"
            ),
            "point_in_time_issuance_verified": False,
            "official_sideways_tolerance_pct": SIDEWAYS_TOLERANCE_PCT[label],
        }
    descriptive = {}
    for label, hours in DIFFERENT_FROM_FORECAST.items():
        target = t + timedelta(hours=hours) if t else None
        observed = candles.get(target) if target and target <= asof and base_error is None else None
        descriptive[label] = {
            "status": "EXPOST_OBSERVED_NOT_ISSUED_FORECAST" if observed else "PENDING_OR_UNAVAILABLE",
            "btc_close_return_pct": round(100*(observed["btc"]/r_btc-1), 5) if observed else None,
        }
    return {
        "id": f.get("compass_id"), "path": entry["path"], "sha256": entry["sha256"],
        "issued_at_utc": iso(issued), "reference_close_at_utc": iso(t),
        "reference_age_hours": age_h, "data_status": (f.get("data_status") or {}).get("status") if isinstance(f.get("data_status"), dict) else f.get("data_status"),
        "scoring_contract": f.get("scoring_contract"), "run_reason": f.get("run_reason"),
        "action_now": f.get("action_now"), "pullback_risk_state": state,
        "price_reference": {"btc": r_btc, "eth": r_eth},
        "publication_verified_independently": False,
        "horizons": signals, "additional_expost_6_24_72h": descriptive,
    }


def aggregate(records: list[dict]) -> dict:
    counts = {"forecasts": len(records)}
    counts["actions"] = dict(Counter(r["action_now"] or "UNKNOWN" for r in records))
    counts["risk_states"] = dict(Counter(r["pullback_risk_state"] for r in records))
    counts["source_states"] = dict(Counter(str(r["data_status"]) for r in records))
    counts["reason"] = dict(Counter(str(r["run_reason"]) for r in records))
    counts["reference_age_at_issuance"] = {
        "available_n": sum(r["reference_age_hours"] is not None and r["reference_age_hours"] >= 0 for r in records),
        "over_30m_n": sum(r["reference_age_hours"] is not None and r["reference_age_hours"] > 0.5 for r in records),
        "over_60m_n": sum(r["reference_age_hours"] is not None and r["reference_age_hours"] > 1.0 for r in records),
        "over_120m_n": sum(r["reference_age_hours"] is not None and r["reference_age_hours"] > 2.0 for r in records),
        "over_180m_n": sum(r["reference_age_hours"] is not None and r["reference_age_hours"] > 3.0 for r in records),
        "clock_type": "ISSUE_FIELD_MINUS_INDIVIDUAL_CANDLE_CLOSE_NOT_PROVIDER_FIRST_KNOWN",
        "comparison": "TASK2_SOURCE_AGE_CENSUS_PR1857_IS_SEPARATE_257_ISSUANCE_COHORT",
    }
    results = {}
    for horizon in HORIZONS:
        hist = [r["horizons"][horizon] for r in records]
        eligible = [x for x in hist if x["status"] == "MATURED_EXPOST_ONLY"]
        testable = [x for x in eligible if x["expected_direction"] in ("UP", "DOWN")]
        correct = sum(x["descriptive_direction_result"] == "CORRECT" for x in testable)
        wrong = len(testable) - correct
        results[horizon] = {
            "issuances": len(hist), "status_counts": dict(Counter(x["status"] for x in hist)),
            "matured_expost_n": len(eligible), "directional_testable_n": len(testable),
            "directional_correct_n": correct, "directional_wrong_n": wrong,
            "expost_direction_rate": round(correct/len(testable), 5) if testable else None,
            "abstention_count": sum(x["expected_direction"] in ("MIXED","NO_EDGE","UNAVAILABLE") for x in hist),
            "sideways_testable_n": sum(x["status"] == "MATURED_EXPOST_ONLY" and x["expected_direction"] == "SIDEWAYS" for x in hist),
            "sideways_correct_n": sum(x["status"] == "MATURED_EXPOST_ONLY" and x["expected_direction"] == "SIDEWAYS" and x["descriptive_direction_result"] == "CORRECT" for x in hist),
            "point_in_time_certified_edge": None,
        }
        paired = [x for x in testable if x["momentum_baseline_result"] in ("CORRECT", "INCORRECT")]
        results[horizon]["matched_momentum_control"] = {
            "matched_n": len(paired),
            "compass_correct_n": sum(x["descriptive_direction_result"] == "CORRECT" for x in paired),
            "naive_momentum_correct_n": sum(x["momentum_baseline_result"] == "CORRECT" for x in paired),
            "incremental_certified_edge": None,
            "warning": "EXPOST_SAME_COHORT_DESCRIPTIVE_ONLY_WITHOUT_ORIGINAL_FIRST_KNOWN",
        }
    counts["horizons"] = results
    # Intraday event-driven issuance often repeats the same market shock.
    # Grouping is UTC fixed-slot descriptive, not statistical independence.
    by_day = defaultdict(list)
    for row in records:
        when = stamp(row["issued_at_utc"])
        if when:
            by_day[when.astimezone(ZoneInfo("Europe/Copenhagen")).date().isoformat()].append(row)
    counts["by_copenhagen_day"] = {
        day: {
            "issuances": len(items),
            "actions": dict(Counter(x["action_now"] or "UNKNOWN" for x in items)),
            "risk_states": dict(Counter(x["pullback_risk_state"] for x in items)),
            "12h_direction": dict(Counter(x["horizons"]["12h"]["expected_direction"] for x in items)),
            "12h_matured_directional_n": sum(
                x["horizons"]["12h"]["descriptive_direction_result"] in ("CORRECT","INCORRECT")
                for x in items
            ),
            "12h_direction_correct_n": sum(
                x["horizons"]["12h"]["descriptive_direction_result"] == "CORRECT"
                for x in items
            ),
        } for day, items in sorted(by_day.items())
    }
    return counts


def run(root: Path, asof: datetime, scope: str) -> dict:
    if scope not in ("rolling14", "all"):
        raise ValueError("BAD_SCOPE")
    start = asof - timedelta(days=14) if scope == "rolling14" else None
    freeze_rows, inventory = parse_freezes(root, asof, start)
    earliest = min((x["issued"] for x in freeze_rows), default=asof)
    market, sources, market_quality = load_market(root, earliest - timedelta(days=2), asof)
    rows = [one_report(x, market, asof) for x in freeze_rows]
    # Preserve every issued forecast for audit, but use one first-issued
    # forecast per fixed UTC 12h block to limit correlated repeated forecasts.
    groups: dict[int, dict] = {}
    for row in rows:
        issued = stamp(row["issued_at_utc"])
        key = int(issued.timestamp()) // (12*3600)
        groups.setdefault(key, row)
    clock_sample = list(groups.values())
    selected_hashes = [{"path": x["path"], "sha256": x["sha256"]} for x in freeze_rows]
    local = asof.astimezone(ZoneInfo("Europe/Copenhagen"))
    slot_summary = aggregate(clock_sample)
    matured_12 = slot_summary["horizons"]["12h"]
    risks = Counter(row["pullback_risk_state"] for row in rows)
    flags = []
    if matured_12["directional_testable_n"] >= 20 and matured_12["expost_direction_rate"] < 0.5:
        flags.append({
            "id": "TWELVE_HOUR_DIRECTION_LOW_DESCRIPTIVE_HITRATE",
            "evidence": {
                "testable_12h_slots": matured_12["directional_testable_n"],
                "hit_rate": matured_12["expost_direction_rate"],
            },
            "recommended_action": "EXAMINE_PROSPECTIVE_12H_NOWCAST_VS_FORWARD_SEMANTICS_AND_MATCHED_BASELINES",
            "automatic_weight_change": False,
        })
    if len(rows) >= 20 and risks and max(risks.values())/len(rows) > 0.8:
        flags.append({
            "id": "RISK_STATE_CONCENTRATION_MONITOR",
            "evidence": {"largest_state": risks.most_common(1)[0][0],
                         "count": risks.most_common(1)[0][1],
                         "denominator": len(rows)},
            "recommended_action": "INVESTIGATE_SEVERITY_DISCRIMINATION_AND_FALSE_ALARM_COST_BEFORE_ESCALATION",
            "automatic_weight_change": False,
        })
    if len(clock_sample) and len(rows) >= 2*len(clock_sample):
        flags.append({
            "id": "MULTIPLE_ISSUANCES_PER_UTC12_SLOT",
            "evidence": {"issuance_n": len(rows), "selected_slot_n": len(clock_sample)},
            "recommended_action": "NEVER_SCORE_ALL_EVENT_DRIVEN_ISSUANCES_AS_INDEPENDENT_TRADES",
            "automatic_weight_change": False,
        })
    clocks = sorted(market)
    start_bar = next((t for t in clocks if start is None or t >= start), None)
    end_bar = clocks[-1] if clocks else None
    descriptive_market_path = {
        "start_close_utc": iso(start_bar), "end_close_utc": iso(end_bar),
        "btc_start": market[start_bar]["btc"] if start_bar else None,
        "btc_end": market[end_bar]["btc"] if end_bar else None,
        "eth_start": market[start_bar]["eth"] if start_bar else None,
        "eth_end": market[end_bar]["eth"] if end_bar else None,
        "btc_return_pct": round(100*(market[end_bar]["btc"]/market[start_bar]["btc"]-1),5)
                          if start_bar and end_bar else None,
        "eth_return_pct": round(100*(market[end_bar]["eth"]/market[start_bar]["eth"]-1),5)
                          if start_bar and end_bar else None,
        "point_in_time_prediction_or_performance": False,
    }
    return {
        "contract": CONTRACT, "scope": scope,
        "generated_at_utc": iso(asof), "copenhagen_date": local.date().isoformat(),
        "window_start_utc": iso(start), "window_end_utc": iso(asof),
        "origin": "IMMUTABLE_OFFICIAL_FREEZE_FILES_PLUS_HOURLY_PUBLIC_ARCHIVE",
        "clock_selection_contract": "FIRST_ISSUANCE_PER_FIXED_UTC_12H_BLOCK_NOT_LOCAL_SCHEDULE",
        "frozen_forecasts_unchanged": True, "automatic_model_reweighting": False,
        "trade_permission": "NONE", "certified_predictive_skill": None,
        "first_known_publication_verified": False,
        "research_only": True, "data_inventory": inventory,
        "price_source_quality": market_quality, "complete_spot_close_rows": len(market),
        "source_manifest": {"official_freezes": selected_hashes, "hourly_csv": sources},
        "all_issuances": aggregate(rows), "deduplicated_12h_slots": slot_summary,
        "descriptive_market_path": descriptive_market_path,
        "nonbinding_calibration_research_flags": flags,
        "pullback_warning_timebox_shadow": evaluate_pullback_timebox(freeze_rows, market, asof),
        "all_issuance_rows": rows,
        "scientific_decision": {
            "status": "HOLD_UNTIL_ORIGINAL_PIT_RECEIPTS_AND_PRE_REGISTERED_HOLDOUT",
            "blocking_gates": [
                "NO_FIRST_KNOWN_FREEZE_COMMIT_PUBLICATION_VERIFICATION",
                "SOURCE_WINDOW_END_IS_COLLECTOR_WINDOW_NOT_ORIGINAL_MARKET_ISSUANCE",
                "OVERLAPPING_72H_AND_168H_OUTCOMES_NOT_INDEPENDENT",
                "MIXED_IS_ABSTENTION_NOT_DIRECTIONAL_HIT",
                "EARLY_WARNING_SEVERITY_AND_LEAD_TIME_UNVALIDATED",
                "NO_MATCHED_HORIZON_COST_BASELINE_OR_PROSPECTIVE_HOLDOUT",
            ],
            "admissible_automatic_calibration_changes": [],
            "recommendations": [
                "Audit unmodified frozen forecast source first-known Git chronology",
                "Register prospective validation before any parameter search",
                "Use independent matched-clock cohorts and embargo overlapping windows",
                "Keep source and investor action owners unchanged until approved",
            ],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--scope", choices=("rolling14", "all"), default="rolling14")
    ap.add_argument("--asof", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    now = stamp(args.asof)
    if now is None:
        raise ValueError("ASOF_REQUIRES_UTC_OFFSET")
    output = (args.repo / args.output).resolve()
    allowed = (args.repo / OUTPUT_ROOT).resolve()
    if not output.is_relative_to(allowed):
        raise ValueError("OUTSIDE_RESEARCH_OUTPUT_ROOT")
    report = run(args.repo, now, args.scope)
    if output.exists():
        # Idempotent writer, do not rewrite published historical audit.
        print(json.dumps({"status": "ALREADY_PUBLISHED", "path": str(args.output)}, sort_keys=True))
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+"\n"
    if len(payload.encode("utf-8")) > 8_000_000:
        raise ValueError("RESEARCH_REPORT_TOO_LARGE_SKIP_PUBLICATION")
    # Publish the complete report only after serialization and size checks.
    # A failed exploratory audit must not produce a half-written JSON file.
    import os
    import tempfile
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         prefix=".research-audit-", suffix=".tmp", delete=False) as handle:
            tmp = Path(handle.name)
            handle.write(payload)
        os.replace(tmp, output)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()
    print(json.dumps({"status":"PUBLISHED_RESEARCH_ONLY","scope":args.scope,
                      "path":str(args.output),
                      "forecast_issuances":report["all_issuances"]["forecasts"],
                      "deduplicated_12h_slots":report["deduplicated_12h_slots"]["forecasts"],
                      "automatic_model_reweighting":False},sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
