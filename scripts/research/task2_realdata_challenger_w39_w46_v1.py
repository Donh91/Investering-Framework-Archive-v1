#!/usr/bin/env python3
"""Task2 #1596. Real original CN-vs-naive ranges + archival price-only warning replay.

Only public Archive evidence. Non-promotional, historical pilot. No source fetch,
model call, portfolio/forecast write, or claimed provider-first-known time.
All original freeze timestamps and full denominators are retained. W46 excluded
from final event scoring until the original target windows have matured.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CONTRACT = "TASK2_W39_W46_NATIVE_REALDATA_CHALLENGER_V1"
LEDGER = Path("05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl")
CAPTURE_ROOT = Path("03_DAILY_CAPTURE_LOGS/weekly/2026")
WINDOWS = {"day_1_2": "DAY1_2", "day_3_4": "DAY3_4", "day_5_7": "DAY5_7"}
MODELS = ("ORIGINAL_CN", "PREV_WEEK_RANGE", "PREV_CLOSE_HALF_WIDTH", "PREV_CLOSE_FULL_WIDTH")
RISK_RULES = {
    "PRICE_24H_MINUS3": {"pct24": -3.0},
    "PRICE_24H_MINUS5": {"pct24": -5.0},
    "PRICE_ACCEL_MINUS3_AND_4H_MINUS1_5": {"pct24": -3.0, "pct4": -1.5},
}
MAX_LAST_COMPLETED_WEEK = 45
WINDOW_ALPHA_DIAGNOSTIC = 0.1  # diagnostic penalty, NOT a nominal CN 90% interval
NO_API = True
FIRST_KNOWN = "UNKNOWN_PROVIDER_FIRST_PUBLISHED"
FIRST_DELIVERED = "UNKNOWN_USER_DELIVERY"


def get_json(root: Path, relative: Path) -> dict:
    with (root / relative).open(encoding="utf-8") as f:
        return json.load(f)


def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            buf = f.read(1024 * 1024)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def stamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("SOURCE_UTC_TIMESTAMP_REQUIRED")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.utcoffset() != timedelta(0):
        raise ValueError("UTC_OFFSET_REQUIRED")
    return dt.astimezone(timezone.utc)


def safe_number(value) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("NONFINITE_OR_NONNUMERIC_PRICE")
    return float(value)


def week_bounds(label: str):
    year, week = label.split("-W")
    monday = date.fromisocalendar(int(year), int(week), 1)
    start = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
    return start, start + timedelta(days=7)


def actual_range(weekpack: dict, key: str, asset: str):
    windows = weekpack["day_window_actuals"]["windows"]
    chosen = list(windows.values()) if key == "weekly" else [windows[WINDOWS[key]]]
    return (
        min(safe_number(w[asset.lower()]["low"]) for w in chosen),
        max(safe_number(w[asset.lower()]["high"]) for w in chosen),
        chosen[-1][asset.lower()]["close"],
    )


def range_score(pred_low, pred_high, actual_low, actual_high, anchor):
    low, high, al, ah, ref = map(safe_number, (
        pred_low, pred_high, actual_low, actual_high, anchor))
    if not (ref > 0 and 0 < low <= high and 0 < al <= ah):
        raise ValueError("BAD_PRICE_RANGE_OR_ANCHOR")
    extra = max(0.0, low - al) + max(0.0, ah - high)
    width = high - low
    union = max(high, ah) - min(low, al)
    return {
        "full_extreme_containment": al >= low and ah <= high,
        "range_jaccard": (max(0., min(high, ah) - max(low, al)) / union) if union else 1.,
        "normalized_width_pct": width / ref * 100.,
        "tail_breach_pct_anchor": extra / ref * 100.,
        "width_penalty_a10_diagnostic": (width + (2. / WINDOW_ALPHA_DIAGNOSTIC) * extra) / ref * 100.,
    }


def unique_freezes(lines):
    selected, duplicate_count = {}, 0
    for line in lines:
        if line.get("contract") != "CN_FORWARD_RANGE_FREEZE_v2":
            continue
        label = line.get("forecast_week", "")
        if not label.startswith("2026-W"):
            continue
        week = int(label.split("-W")[-1])
        if not 39 <= week <= 46:
            continue
        key = (label, line.get("asset"), line.get("window"))
        if key in selected:
            old = selected[key]
            freeze_fields = ("forecast_low", "forecast_high", "generated_unix", "status")
            if any(old.get(k) != line.get(k) for k in freeze_fields):
                raise ValueError("CONFLICTING_ORIGINAL_FREEZE:" + str(key))
            duplicate_count += 1
        else:
            selected[key] = line
    return list(selected.values()), duplicate_count


def forecast_study(root: Path):
    path = root / LEDGER
    if not path.exists():
        raise ValueError("FROZEN_PROSPECTIVE_LEDGER_MISSING")
    freeze, duplicates = unique_freezes(
        json.loads(s) for s in path.read_text().splitlines() if s.strip())
    rows = []
    refusals = defaultdict(int)
    source_files = {str(LEDGER): checksum(path)}
    weeks_checked = set()
    for item in sorted(freeze, key=lambda x: (x["forecast_week"], x["asset"], x["window"])):
        label = item["forecast_week"]
        week = int(label.split("-W")[1])
        asset = item["asset"]
        window = item["window"]
        start, end = week_bounds(label)
        issue = item.get("generated_unix")
        base = {"forecast_week": label, "asset": asset, "window": window,
                "issue_epoch": issue, "original_freeze_status": item.get("status"),
                "provider_first_published_at": None,
                "user_first_delivered_at": None}
        if week > MAX_LAST_COMPLETED_WEEK:
            refusals["UNMATURED_W46"] += 1
            continue
        if asset not in {"BTC", "ETH"} or window not in (set(WINDOWS) | {"weekly"}):
            refusals["UNSUPPORTED_ASSET_OR_WINDOW"] += 1
            continue
        if type(issue) is not int:
            refusals["UNKNOWN_ORIGINAL_ISSUE_TIME"] += 1
            continue
        issued = datetime.fromtimestamp(issue, timezone.utc)
        prior = CAPTURE_ROOT / ("W%02d.json" % (week - 1))
        outcome = CAPTURE_ROOT / ("W%02d.json" % week)
        if not (root / prior).exists() or not (root / outcome).exists():
            refusals["MISSING_SOURCE_WEEK"] += 1
            continue
        first = get_json(root, prior)
        later = get_json(root, outcome)
        for rel in (prior, outcome):
            source_files[str(rel)] = checksum(root / rel)
        if first.get("contract") != "WEEKLY_RAW_CALIBRATION_PACK_v3" or later.get("contract") != "WEEKLY_RAW_CALIBRATION_PACK_v3":
            refusals["BAD_SOURCE_CONTRACT"] += 1
            continue
        if (first["hourly_gap_diagnostics"]["observed_hours"] != 168 or
            first["hourly_gap_diagnostics"]["missing_hour_count"] != 0 or
            later["hourly_gap_diagnostics"]["observed_hours"] != 168 or
            later["hourly_gap_diagnostics"]["missing_hour_count"] != 0):
            refusals["SOURCE_HOURLY_COVERAGE_GAP"] += 1
            continue
        if stamp(first["generated_at_utc"]) > issued:
            refusals["PREV_WEEK_CAPTURE_PUBLISHED_AFTER_FORECAST"] += 1
            continue
        if stamp(later["generated_at_utc"]) < end:
            refusals["OUTCOME_SOURCE_BEFORE_MATURITY"] += 1
            continue
        # Whole-week and Mon/Tue windows start before the Monday issuance;
        # scoring their entire intraday extrema as prospective is invalid.
        window_start = start + {
            "weekly": timedelta(0), "day_1_2": timedelta(0),
            "day_3_4": timedelta(days=2), "day_5_7": timedelta(days=4),
        }[window]
        if issued >= window_start:
            refusals["WINDOW_BEGAN_BEFORE_ISSUANCE"] += 1
            continue
        pre_lo, pre_hi, pre_close = actual_range(first, "weekly", asset)
        target_low, target_high, _ = actual_range(later, window, asset)
        prior_width = pre_hi - pre_lo
        candidates = {
            "ORIGINAL_CN": (item["forecast_low"], item["forecast_high"]),
            "PREV_WEEK_RANGE": (pre_lo, pre_hi),
            "PREV_CLOSE_HALF_WIDTH": (
                max(.01, pre_close - prior_width / 2.),
                pre_close + prior_width / 2.),
            "PREV_CLOSE_FULL_WIDTH": (
                max(.01, pre_close - prior_width),
                pre_close + prior_width),
        }
        for model, (lo, hi) in candidates.items():
            m = range_score(lo, hi, target_low, target_high, pre_close)
            rows.append({**base, "claim_class": "ORIGINAL_FROZEN_BUT_DELIVERY_UNKNOWN" if model == "ORIGINAL_CN" else "MECHANICAL_SAME_SOURCE_BASELINE",
                         "model": model, "anchor_last_known": pre_close,
                         "forecast_low": round(lo, 6), "forecast_high": round(hi, 6),
                         "actual_low": target_low, "actual_high": target_high,
                         **m})
        weeks_checked.add(label)
    summary = {"contract": CONTRACT, "study": "forecast_range",
               "source_class": "FROZEN_PROSPECTIVE_ORIGINAL_FORECAST_DELIVERY_UNKNOWN",
               "source_clock_limit": FIRST_KNOWN,
               "delivery_clock_limit": FIRST_DELIVERED,
               "regime_period": "2026-W39..W45, W46 still unscored",
               "source_sha256": dict(sorted(source_files.items())),
               "eligible_independent_week_groups": len(weeks_checked),
               "eligible_asset_week_window_groups": len(rows)//len(MODELS),
               "duplicate_ledger_rows_deduped": duplicates,
               "exclusions": dict(sorted(refusals.items())),
               "model_metrics": {},
               "statistical_claim": "DESCRIPTIVE_ONLY_ORIGIN_CLUSTER_N_SMALL",
               "interval_penalty_semantics": "a10 exploratory penalty, original CN never issued a calibrated 90pct interval",
               "no_model_promotion": True, "no_api_or_wallet": True}
    for model in MODELS:
        item = [r for r in rows if r["model"] == model]
        if not item:
            continue
        summary["model_metrics"][model] = {
            "rows": len(item),
            "distinct_origin_weeks": len({r["forecast_week"] for r in item}),
            "mean_diagnostic_penalty": round(sum(x["width_penalty_a10_diagnostic"] for x in item) / len(item), 6),
            "mean_width_pct_anchor": round(sum(x["normalized_width_pct"] for x in item) / len(item), 6),
            "containment_pct": round(100 * sum(x["full_extreme_containment"] for x in item)/len(item), 6),
            "mean_jaccard": round(sum(x["range_jaccard"] for x in item)/len(item), 6),
        }
    # Decision-time horizons within one source week are correlated.
    # Bootstrap pairs of four asset/windows BY ORIGINAL FORECAST WEEK, never by row.
    origin_weeks = sorted(weeks_checked)
    block = {}
    for w in origin_weeks:
        block[w] = {}
        for model in MODELS:
            z = [r["width_penalty_a10_diagnostic"] for r in rows
                 if r["forecast_week"] == w and r["model"] == model]
            if len(z) != 4:
                raise ValueError("INCOMPLETE_ORIGINAL_WEEK_BLOCK")
            block[w][model] = sum(z) / len(z)
    summary["paired_week_bootstrap"] = {}
    for alternative in MODELS[1:]:
        delta = [block[w]["ORIGINAL_CN"] - block[w][alternative] for w in origin_weeks]
        if len(delta) < 4:
            continue
        rnd = random.Random(1309)
        simulations = sorted(
            sum(rnd.choices(delta, k=len(delta))) / len(delta)
            for _ in range(5000)
        )
        summary["paired_week_bootstrap"][alternative] = {
            "independent_week_block_n": len(delta),
            "mean_CN_minus_baseline_penalty": round(sum(delta)/len(delta), 6),
            "CN_better_week_count": sum(v < 0 for v in delta),
            "bootstrap_ci_95_pct_penalty": [
                round(simulations[125], 6), round(simulations[4875], 6)],
            "status": "EXPLORATORY_DEVELOPMENT_NOT_PRE_REGISTERED_SKILL",
            "method": "fixed-seed 5000 resamples of seven weekly paired averages",
        }
    return summary, rows


def hourly_study(root: Path):
    """Non-original, posthoc 72h downside replay, with complete UTC source windows.

    We intentionally omit W46 as the source pack has no finished 168h tape.
    Decision at 12:00 UTC. Input bars must be closed AND source_window_end <=
    decision; the latter is only a replay proxy, NOT provider first-known.
    """
    rows = []
    source_files = {}
    missing = []
    for week in range(39, 46):
        path = CAPTURE_ROOT / ("W%02d" % week) / "WEEKLY_HOURLY_ENRICHED.csv"
        if not (root/path).exists():
            missing.append(str(path))
            continue
        source_files[str(path)] = checksum(root/path)
        with (root/path).open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if not row.get("timestamp_utc"):
                    continue
                row["_open"] = stamp(row["timestamp_utc"])
                row["_end"] = row["_open"] + timedelta(hours=1)
                row["_source_window_end"] = stamp(row["source_window_end_utc"])
                rows.append(row)
    rows.sort(key=lambda r: r["_open"])
    if missing:
        return {"status": "BLOCKED_SOURCE_MISSING", "missing": missing}, []
    if len(rows) != 7*168 or any(rows[i+1]["_open"] - rows[i]["_open"] != timedelta(hours=1) for i in range(len(rows)-1)):
        return {"status": "BLOCKED_HOURLY_GAPS_OR_DUPLICATES", "rows": len(rows)}, []
    for row in rows:
        if row.get("spot_status") != "PASS":
            return {"status":"BLOCKED_INVALID_SPOT_SOURCE"},[]
        for asset in ("btc", "eth"):
            for field in ("_close", "_low"):
                if safe_number(float(row[asset+field])) <= 0:
                    return {"status":"BLOCKED_BAD_HOURLY_VALUE"}, []
    experiments, refused = [], defaultdict(int)
    first = rows[0]["_open"].date()
    last = rows[-1]["_end"]
    day = first
    while datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc) + timedelta(hours=72) <= last:
        cutoff = datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc)
        idx = [i for i,r in enumerate(rows) if r["_end"] <= cutoff and r["_source_window_end"] <= cutoff]
        if not idx:
            refused["NO_SOURCE_ELIGIBLE_LOOKBACK"] += 1
            day += timedelta(days=1)
            continue
        i = idx[-1]
        # An outcome anchor must be the fully completed bar at the precise
        # decision cutoff, not an earlier last-eligible (stale) source price.
        if rows[i]["_end"] != cutoff:
            refused["NO_SAME_CUTOFF_SOURCE_ELIGIBLE_BAR"] += 1
            day += timedelta(days=1)
            continue
        # Both 24h and 4h windows must predate cutoff and be consecutive.
        if i < 24 or not all(rows[z]["_source_window_end"] <= cutoff for z in range(i-24,i+1)):
            refused["INCOMPLETE_24H_PREKNOWN_LOOKBACK"] += 1
            day += timedelta(days=1)
            continue
        target = [r for r in rows if cutoff < r["_end"] <= cutoff + timedelta(hours=72)]
        if (len(target) != 72 or
            target[0]["_end"] != cutoff + timedelta(hours=1) or
            target[-1]["_end"] != cutoff + timedelta(hours=72)):
            refused["INCOMPLETE_MATURED_72H_TARGET"] += 1
            day += timedelta(days=1)
            continue
        for asset in ("btc","eth"):
            now = safe_number(float(rows[i][asset+"_close"]))
            p24 = safe_number(float(rows[i-24][asset+"_close"]))
            p4 = safe_number(float(rows[i-4][asset+"_close"]))
            pct24 = 100*(now/p24-1)
            pct4 = 100*(now/p4-1)
            target_min = min(safe_number(float(x[asset+"_low"])) for x in target)
            outcome = target_min <= now * 0.92
            close72 = safe_number(float(target[-1][asset+"_close"]))
            for name, thresholds in RISK_RULES.items():
                alerted = pct24 <= thresholds["pct24"] and (("pct4" not in thresholds) or pct4 <= thresholds["pct4"])
                experiments.append({
                    "decision_utc": cutoff.isoformat().replace("+00:00","Z"),
                    "asset":asset.upper(),"rule":name,
                    "lookback_source_utc": rows[i]["_source_window_end"].isoformat().replace("+00:00","Z"),
                    "decision_anchor_bar_end_utc": rows[i]["_end"].isoformat().replace("+00:00","Z"),
                    "decision_anchor_source_window_end_utc": rows[i]["_source_window_end"].isoformat().replace("+00:00","Z"),
                    "provider_first_published_utc": None,
                    "claim_class": "RETROSPECTIVE_SOURCE_WINDOW_PROXY_NOT_ISSUED_COMPASS",
                    "anchor_price":now,"pct24":round(pct24,5),"pct4":round(pct4,5),
                    "alerted":alerted,"down8_within_72h":outcome,
                    "target_low":target_min,"target_close_72h":close72,
                    "target_close_return_pct":round(100*(close72/now-1),5),
                    "hypothetical_exit_vs_hold_net_pp":round(-100*(close72/now-1)-.3,5) if alerted else 0.0,
                    "cost_assumption_roundtrip_pct":0.3,
                })
        day += timedelta(days=1)
    aggregate = {}
    for asset in ("BTC","ETH"):
        for rule in RISK_RULES:
            subset = [r for r in experiments if r["asset"] == asset and r["rule"] == rule]
            a = [r for r in subset if r["alerted"]]
            tp=sum(r["alerted"] and r["down8_within_72h"] for r in subset)
            fp=sum(r["alerted"] and not r["down8_within_72h"] for r in subset)
            fn=sum((not r["alerted"]) and r["down8_within_72h"] for r in subset)
            tn=sum((not r["alerted"]) and not r["down8_within_72h"] for r in subset)
            positives=sorted([stamp(r["decision_utc"]) for r in subset if r["down8_within_72h"]])
            clusters=[]
            for d in positives:
                if not clusters or d-clusters[-1][-1] > timedelta(hours=72):
                    clusters.append([d])
                else:
                    clusters[-1].append(d)
            aggregate[asset+"_"+rule]={
                "n_daily_decisions_correlated":len(subset),
                "n_positive_origin_days_correlated":tp+fn,
                "independent_positive_event_clusters_upper_bound":len(clusters),
                "TP":tp,"FP":fp,"FN":fn,"TN":tn,
                "alert_rate_pct":round(100*len(a)/len(subset),4) if subset else None,
                "mean_costed_exit_vs_hold_pp_when_alert":round(sum(x["hypothetical_exit_vs_hold_net_pp"] for x in a)/len(a),5) if a else None,
                "note":"POSTHOC price-only counterfactual, no real issued risk score, fills, liquidity or causal inference",
            }
    summary={
        "contract":CONTRACT,"study":"historical_risk_price_only_replay",
        "status":"RETROSPECTIVE_RESEARCH_ONLY",
        "source_sha256":source_files,
        "quote":"BTCUSDT/ETHUSDT source fields; USD/USDT not silently interchanged",
        "provider_first_published":None,"actual_first_known":None,
        "hours_in_qualified_tape":len(rows),
        "independent_weeks":7,
        "decision_cutoffs":"12:00 UTC daily, available completed-bar and recorded source-window-end <= cutoff",
        "refusals":dict(refused),"outcome":"intraday -8pct low within following 72 completed hours",
        "risk_candidates":aggregate,
        "multiple_testing":"EXPLORATORY_NO_SIGNIFICANCE_OR_SCORE_PROMOTION",
        "no_wallet_execution":True, "no_model_promotion":True,
    }
    return summary, experiments


def save_csv(path: Path, rows):
    if not rows:
        path.write_text("",encoding="utf-8")
        return
    with path.open("w",newline="",encoding="utf-8") as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=Path("."))
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--lane",choices=("forecast","risk","both"),default="both")
    args=p.parse_args()
    root=args.repo_root.resolve()
    out=args.out_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    outputs={}
    if args.lane in ("forecast","both"):
        summary,rows=forecast_study(root)
        (out/"forecast_summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
        save_csv(out/"forecast_rows.csv",rows)
        outputs["forecast"]={"rows":len(rows),"summary":summary["model_metrics"],
                             "refusals":summary["exclusions"]}
    if args.lane in ("risk","both"):
        summary,rows=hourly_study(root)
        (out/"risk_summary.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
        save_csv(out/"risk_rows.csv",rows)
        outputs["risk"]={"rows":len(rows),"status":summary.get("status"),
                         "groups":summary.get("risk_candidates")}
    print(json.dumps({"contract":CONTRACT,"source":"ACTUAL_PUBLIC_ARCHIVE_BYTES",
                      "result":outputs,"no_forecast_or_trading_authority":True},sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
