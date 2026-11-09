#!/usr/bin/env python3
"""Research Task2 #1596: W45 original CN vs original independent B1 (source-only).

An entire candle must have opened after the original issue to join the
postissue OHLC cohort. Endpoint-only observations are recorded separately.
USD/USDT equivalence and vendor first-known remain unverified.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scripts.research.task2_cn_w44_postfreeze_paired_v1 import (
    joint_score, validated_hourly_candle_clocks,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "TASK2_W45_ORIGINAL_CN_B1_PAIRED_v1"
FIRST_COMMIT = "ae6a3b5f61ac26e86257d25decd5f2fb96bf0ad2"
ISSUE = "2026-11-02T08:19:08Z"
CUT = "2026-11-02T09:00:00Z"
START = "2026-11-02T00:00:00Z"
END = "2026-11-09T00:00:00Z"
SOURCES = {
    "hourly": ("03_DAILY_CAPTURE_LOGS/weekly/2026/W45/WEEKLY_HOURLY_ENRICHED.csv",
               "b8cb918e779c46e2521766ae4ee82ddfa9048546"),
    "weekly": ("03_DAILY_CAPTURE_LOGS/weekly/2026/W45.json",
               "343567105f0155daa95df58e4ecb706ce53a1669"),
    "cn": ("05_CYCLE_NAVIGATOR/weekly/2026/W45/CYCLE_NAVIGATOR_FORECAST_FREEZE.json",
           "2e78b08162f9592c643722ee4596072b77c7c7c0"),
    "b1": ("05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W45.json",
           "d3f41b067793d106d2767db2fbe1ef73771f1992"),
    "receipt": ("05_CYCLE_NAVIGATOR/weekly/2026/W45/CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json",
                "c4420bf45060a8e9d5f4916a0cc45ba020ba4caf"),
    "scorecard": ("05_CYCLE_NAVIGATOR/weekly/2026/W46/CYCLE_NAVIGATOR_SCORECARD.json",
                  "1f717563011386cee8ea59613386cfd1fb1c29d4"),
}

def utc(s):
    if not isinstance(s, str) or not s.endswith("Z"):
        raise ValueError("STRICT_UTC_Z_REQUIRED")
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.utcoffset() != timedelta():
        raise ValueError("NON_UTC_CLOCK")
    return d.astimezone(timezone.utc)

def read_locked(root, key):
    relative, expected = SOURCES[key]
    root = Path(root).resolve()
    path = root / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError("MISSING_OR_UNSAFE_SOURCE:" + key)
    raw = path.read_bytes()
    if not raw or len(raw) > 500_000:
        raise ValueError("EMPTY_OR_OVERSIZE_SOURCE:" + key)
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != expected:
        raise ValueError("SOURCE_GIT_BLOB_DRIFT:" + key)
    return raw

def build(root=ROOT):
    raw = {name: read_locked(root, name) for name in SOURCES}
    weekly = json.loads(raw["weekly"])
    cn = json.loads(raw["cn"])
    b1 = json.loads(raw["b1"])
    receipt = json.loads(raw["receipt"])
    scorecard = json.loads(raw["scorecard"])
    start, end, issue, cut = (utc(x) for x in (START, END, ISSUE, CUT))
    if (datetime.fromtimestamp(receipt["frozen_unix"], timezone.utc) != issue
            or utc(receipt["scoring_valid_from_utc"]) != cut
            or receipt["forecast_week"] != "2026-W45"
            or receipt["status"] != "SITE_FROZEN_SOURCE_OF_RECORD"
            or receipt["source_forecast_freeze_path"] != SOURCES["cn"][0]
            or not start < issue < cut < end):
        raise ValueError("ORIGINAL_W45_ISSUE_OR_RECEIPT_DRIFT")
    if (b1["status"] != "READY" or b1["target_iso_year"] != 2026
            or b1["target_iso_week"] != 45 or b1["expected_anchor_iso_week"] != 44
            or not b1["independence"]["generated_without_cycle_navigator_model_output"]):
        raise ValueError("B1_ORIGINAL_INDEPENDENCE_DRIFT")
    diagnostics = weekly["hourly_gap_diagnostics"]
    if (diagnostics["expected_hours"] != 168 or diagnostics["observed_hours"] != 168
            or diagnostics["missing_hour_count"] != 0
            or scorecard["completed_iso_week"] != 45
            or scorecard["score_status"] != "REPRODUCIBLE"):
        raise ValueError("W45_MATURITY_OR_HOURLY_COVERAGE_INVALID")
    if any(cn["daily_price_path"][a]["status"] != "UNAVAILABLE" for a in ("BTC", "ETH")):
        raise ValueError("W45_FROZEN_DAILY_PATH_DRIFT")
    rows = list(csv.DictReader(io.StringIO(raw["hourly"].decode("utf-8"))))
    if len(rows) != 168:
        raise ValueError("W45_HOURLY_COUNT_INVALID")
    endpoints, whole = [], []
    for n, r in enumerate(rows):
        opened, closed, _ = validated_hourly_candle_clocks(r)
        if opened != start + timedelta(hours=n):
            raise ValueError("NONCONTIGUOUS_HOURLY_SOURCE")
        if cut <= closed <= end:
            endpoints.append(r)
        if opened >= issue and closed <= end:
            whole.append(r)
    if (len(endpoints) != 160 or len(whole) != 159
            or utc(whole[0]["timestamp_utc"]) != cut):
        raise ValueError("POSTISSUE_COHORT_INVALID")
    results = {}
    for asset in ("BTC", "ETH"):
        name = asset.lower()
        actual_low = min(float(r[name + "_low"]) for r in whole)
        actual_high = max(float(r[name + "_high"]) for r in whole)
        anchor = float(b1["assets"][asset]["anchor_price"])
        official = joint_score(float(cn[name + "_range_low"]),
                               float(cn[name + "_range_high"]),
                               actual_low, actual_high, anchor)
        baseline = joint_score(float(b1["assets"][asset]["low"]),
                               float(b1["assets"][asset]["high"]),
                               actual_low, actual_high, anchor)
        row = next((s for s in scorecard["parameter_scores"]
                    if s.get("parameter_id") == name + "_range"), None)
        if (not row or row["status"] != "SUPPORTED"
                or not official["joint_full_low_and_high_contained"]
                or baseline["joint_full_low_and_high_contained"]):
            raise ValueError("ORIGINAL_W45_SCORE_OR_CHALLENGER_DRIFT")
        results[asset] = {
            "observed_whole_candle_low_high_USDT": [actual_low, actual_high],
            "CN_original_USD_vs_USDT_proxy": official,
            "B1_original_vs_USDT_proxy": baseline,
            "CN_to_B1_width_ratio": round(
                (official["predicted_high"] - official["predicted_low"]) /
                (baseline["predicted_high"] - baseline["predicted_low"]), 6),
        }
    return {
        "contract": CONTRACT,
        "original_owner": "Archive#1596", "CN_owner": "Archive#1516",
        "target": "2026-W45", "original_first_issue_commit": FIRST_COMMIT,
        "issue_utc": ISSUE, "first_scoring_hour_close_utc": CUT,
        "complete_hourly_source_n": 168, "postfreeze_closed_endpoint_n": 160,
        "whole_candles_opening_after_issue_n": 159,
        "source_blobs": {k: v[1] for k, v in SOURCES.items()},
        "results": results,
        "claim": "SOURCE_LOCKED_RETROSPECTIVE_DESCRIPTIVE_ONLY",
        "first_commit_ancestry_checked_by_offline_script": False,
        "quote_USD_USDT_equivalence_proven": False,
        "vendor_original_first_known_proven": False,
        "user_delivery_proven": False,
        "independent_future_market_regime_n": 0,
        "statistically_proven_CN_edge": False,
        "model_weights_or_official_scores_changed": False,
        "portfolio_or_trading_authority": False,
    }

if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
