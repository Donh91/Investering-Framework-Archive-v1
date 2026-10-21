#!/usr/bin/env python3
"""Task2: bounded, EX-POST price-only mechanical stress on a frozen public archive.

NEVER forecast/CFGI/Kompas performance, true historical PIT, trade execution,
strategy optimization, economic edge or prospective OOS. No network, API, model,
orders, portfolio state, parameter selection, or source rewrites.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts"
PRICE = ART / "hourly_features.csv.gz"
EPISODES = ART / "EPISODE_CATALOG.json"
CFGI = ART / "CFGI_FIELD_COVERAGE.json"
PRICE_BLOB = "9df69fa3a5675c46d529a277ecd5a7a73693b1e2"
EPISODE_BLOB = "75ce4c0d7e5eda994895ee0377fdf5e27c63cf79"
CFGI_BLOB = "afbcbe41732bd05b59ed7fef5ffbcc71b2aba61b"
STATUS = "EX_POST_PRICE_ONLY_ENGINEERING_STRESS_NOT_FORECAST_EDGE"
COSTS = (0.0, .003, .01, .02)
THRESHOLDS = (.03, .05, .08)
LOOKBACK_H = (6, 12, 24, 48)
TRIMS = (.10, .25, .50)
REENTRY_H = (6, 24, 72, 168)
HOUR_MS = 3600000

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()

def locked_read(path: Path, expected: str) -> bytes:
    payload = path.read_bytes()
    if blob_sha(payload) != expected:
        raise ValueError("SOURCE_BLOB_DRIFT_RESEARCH_REVIEW_REQUIRED:" + path.name)
    return payload

def preflight(art: Path = ART) -> dict:
    episodes = json.loads(locked_read(art / EPISODES.name, EPISODE_BLOB))
    coverage = json.loads(locked_read(art / CFGI.name, CFGI_BLOB))
    ep = episodes.get("episodes")
    if episodes.get("episode_count") != 46 or not isinstance(ep, list) or len(ep) != 46:
        raise ValueError("EPISODE_CENSUS_NOT_46")
    by_era = defaultdict(int)
    for row in ep:
        if row.get("authority") != "OUTCOME_LABEL_RESEARCH_ONLY":
            raise ValueError("EPISODE_OUTCOME_AUTHORITY_CHANGED")
        by_era[row["research_window_id"]] += 1
    if dict(by_era) != {"ALTSEASON_2020_2021":45,"MODERN_ANALOGUE_2025_2026":1}:
        raise ValueError("EPISODE_ERA_POPULATION_CHANGED")
    if coverage.get("contract") != "CFGI_FIELD_COVERAGE_v3" or coverage.get("event_count") != 2:
        raise ValueError("CFGI_COVERAGE_CONTRACT_CHANGED")
    if coverage.get("expected_symbol_hours") != 726 or coverage.get("asof_available_symbol_hours") != 478:
        raise ValueError("CFGI_EXPECTED_COVERAGE_CHANGED")
    if coverage.get("exact_timestamp_symbol_hours") != 0:
        raise ValueError("CFGI_TIME_ALIGNMENT_CHANGED")
    fields = {r["symbol"]:r for r in coverage["field_coverage"] if r["field"]=="score"}
    if set(fields) != {"BTC","ETH","MARKET"} or any(fields[s]["asof_available_slots"]!=v for s,v in (("BTC",239),("ETH",239),("MARKET",0))):
        raise ValueError("CFGI_SCORE_POPULATION_CHANGED")
    return {"episode_counts":dict(by_era),
            "cfgi":{"two_event_scaffold":True,"asof_matched_symbol_hours":478,
                    "expected_symbol_hours":726,"btc_hourly_slots":239,
                    "eth_hourly_slots":239,"market_hourly_slots":0,
                    "exact_timestamp_matched_slots":0,
                    "engine_era_2025":"PRE_2026_07_08",
                    "original_vendor_first_publication_certified":False,
                    "price_only_grid_uses_cfgi":False},
            "source_git_blob":{"hourly_price":PRICE_BLOB,"episodes":EPISODE_BLOB,"cfgi_coverage":CFGI_BLOB},
            "scientific_admission":"BLOCKED_PIT_SOURCE_FIRST_KNOWN_AND_SELECTION"}

def fixture_grid():
    return tuple(itertools.product(THRESHOLDS,LOOKBACK_H,TRIMS,REENTRY_H,COSTS))

def parse_hour_utc(value: str) -> int:
    if not isinstance(value,str) or not value.endswith("Z"):
        raise ValueError("BAD_ARCHIVE_TIMESTAMP")
    timestamp = datetime.fromisoformat(value[:-1]+"+00:00")
    if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds()!=0:
        raise ValueError("BAD_ARCHIVE_TIMESTAMP")
    return int(timestamp.timestamp()*1000)

def load_price_segments(gz_bytes: bytes):
    segments=[]
    last_ms=None
    last_continuity=None
    last_era=None
    for row in csv.DictReader(gzip.decompress(gz_bytes).decode("utf-8").splitlines()):
        stamp=parse_hour_utc(row["timestamp_utc"])
        if stamp%HOUR_MS != 0:
            raise ValueError("NON_HOURLY_ARCHIVE_PRICE")
        price=float(row["ew_index"])
        if not math.isfinite(price) or price<=0:
            raise ValueError("NONFINITE_INDEX_LEVEL")
        continuity=int(row["continuity_segment_id"])
        era=("ALTSEASON_2020_2021" if stamp < parse_hour_utc("2022-01-01T00:00:00Z")
             else "MODERN_ANALOGUE_2025_2026" if stamp >= parse_hour_utc("2025-01-01T00:00:00Z")
             else None)
        if era is None:
            raise ValueError("UNREGISTERED_ARCHIVE_ERA")
        if last_ms is not None and stamp<=last_ms:
            raise ValueError("OUT_OF_ORDER_DUPLICATE_HOUR")
        split=(not segments or continuity!=last_continuity or era!=last_era or
               stamp-last_ms!=HOUR_MS)
        if split:
            segments.append({"era":era,"rows":[]})
        segments[-1]["rows"].append((stamp,price))
        last_ms,last_continuity,last_era=stamp,continuity,era
    if sum(len(s["rows"]) for s in segments)!=25506:
        raise ValueError("ARCHIVED_25506_ROW_COUNT_CHANGED")
    return segments

def simulate_one(rows,config):
    """One unlevered incumbent holder, at most one trim and fixed-time reentry.

    Signal at completed observation i; hypothetical fill at next observed close
    i+1 (not a validated executable fill). No alert on future top/trough label.
    """
    threshold,lookback,trim,reentry,cost=config
    if len(rows)<max(lookback+2,reentry+2):
        return {"state":"SKIP_INSUFFICIENT_CONTIGUOUS_HOURS"}
    price0=rows[0][1]
    holder_units=10000.0/price0
    units=holder_units;cash=0.0;sale_i=None;buy_i=None
    for i in range(lookback,len(rows)-1):
        if sale_i is None:
            rolling_peak=max(v for _,v in rows[i-lookback:i+1])
            if rows[i][1]/rolling_peak - 1 <= -threshold:
                # No same observation fill; the next close is an illustrative
                # execution proxy, never an authenticated tradable quote.
                sale_i=i+1
                proceeds=holder_units*trim*rows[sale_i][1]*(1-cost)
                units-=holder_units*trim
                cash+=proceeds
        elif buy_i is None and i>=sale_i+reentry:
            # If the chosen reentry close exists, it is observed before
            # this loop iteration ends; never choose the best subsequent bar.
            if cash>0:
                units+=cash*(1-cost)/rows[i][1]
                cash=0.0
                buy_i=i
                break
    terminal=rows[-1][1]
    vs_hold=(units*terminal+cash) - holder_units*terminal
    return {"state":"ONE_TRIM" if sale_i is not None else "NO_SIGNAL",
            "reentered":buy_i is not None,"delta_vs_hold_pct_initial":vs_hold/100,
            "not_live_executable":True}

def execute(art: Path=ART) -> dict:
    checked=preflight(art)
    segments=load_price_segments(locked_read(art/PRICE.name,PRICE_BLOB))
    grouped=defaultdict(list)
    for seg in segments:grouped[seg["era"]].append(seg["rows"])
    if set(grouped)!={"ALTSEASON_2020_2021","MODERN_ANALOGUE_2025_2026"}:
        raise ValueError("UNEXPECTED_ERA_UNIVERSE")
    configs=fixture_grid()
    if len(configs)!=576 or len(set(configs))!=576:
        raise ValueError("SIMULATION_GRID_NOT_FROZEN")
    by_era={}
    for era,streams in sorted(grouped.items()):
        tested=trims=skipped=positive=0
        deltas=[]
        for config in configs:
            results=[simulate_one(rows,config) for rows in streams]
            eligible=[x for x in results if x["state"]!="SKIP_INSUFFICIENT_CONTIGUOUS_HOURS"]
            if not eligible:skipped+=1;continue
            tested+=1
            if any(x["state"]=="ONE_TRIM" for x in eligible):trims+=1
            # Unit-capital segments are NOT pooled as an actual historical
            # multi-asset portfolio; mean is diagnostic only.
            mean_delta=sum(x["delta_vs_hold_pct_initial"] for x in eligible)/len(eligible)
            deltas.append(mean_delta)
            if mean_delta>0:positive+=1
        by_era[era]={"configured_cells":576,"assessed_cells":tested,
                     "skipped_cells":skipped,"cells_triggering_illustrative_trim":trims,
                     "cells_positive_vs_hold_descriptive":positive,
                     "price_segments":len(streams),
                     "sum_of_segment_hours":sum(map(len,streams)),
                     "independent_market_event_families_certified":0,
                     "best_cell_or_selected_parameter":None,
                     "causal_market_edge":"NOT_ESTABLISHED"}
    return {"contract":"TASK2_PRICE_ONLY_ARCHIVE_STRESS_v1",
            "classification":STATUS,"parameter_space":{"thresholds":[3,5,8],
                "lookback_hours":list(LOOKBACK_H),"trim_fractions":list(TRIMS),
                "reentry_hours":list(REENTRY_H),"illustrative_round_trip_one_side_costs":list(COSTS)},
            "era_cells_configured":1152,
            "price_eras":by_era,
            "source_preflight":checked,
            "candidate_winner_selected":False,"forecast_model_tested":False,
            "CFGI_predictive_edge_tested":False,"counterfactual_fill_certified":False,
            "holdout_untouched":False,"automatic_trading_authorized":False,
            "takeaway":"Engineering stress only. Do NOT select a winner or infer market edge."}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ART)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=execute(a.root)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,sort_keys=True))
