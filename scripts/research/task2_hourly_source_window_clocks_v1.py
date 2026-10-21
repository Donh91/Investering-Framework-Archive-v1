#!/usr/bin/env python3
"""Task2 archived hourly CSV batch-window temporal audit (source-safe, research only).

source_window_end_utc is per-owner BATCH REQUEST WINDOW END, not an event's
independent detection or provider first-publication time. Never presume that a
closed hourly spot candle or derivative row was locally available at its nominal
timestamp. This script reads frozen public original CSVs and emits only clock
distribution/source Git blob metadata. It DOES NOT propagate prices or scores.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "03_DAILY_CAPTURE_LOGS/hourly/2026/10"
DAYS = tuple(range(14,21))
HOUR = timedelta(hours=1)
CONTRACT = "TASK2_HOURLY_BATCH_END_CLOCK_AUDIT_v1"
PINNED = {
    14:"37e437bbeca1bcd3d1248b945b891576d19c7e5c",
    15:"20acce69b60ae79d938bc57f0c692c731d50dd69",
    16:"127094125f712c5eed06972aaade46054cce5293",
    17:"8a5f675e475d537162b55cf4cf39293627824e7c",
    18:"0a8a66405ee90b38d8d379c5c3af82091b9fabdd",
    19:"8f4fdef8ff23c0c9a5dfeb2a69ec35a5ba571cbd",
    20:"14b69ca05ac77d0746517760e2e22cbd162b2081",
}
CLOCK_FIELDS = {"timestamp_utc","source_window_end_utc"}
DENY = {"btc_close","eth_close","ethbtc_close","btc_high","eth_high","btc_volume","eth_volume","score"}

def git_blob(data:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def utc(raw:str)->datetime:
    if not isinstance(raw,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",raw):
        raise ValueError("CLOCK_NOT_EXPLICIT_UTC")
    return datetime.fromisoformat(raw[:-1]+"+00:00")

def audit_day(data:bytes, day:int, *, expected_blob=None)->dict:
    if day not in PINNED:
        raise ValueError("UNREGISTERED_FROZEN_DAY")
    if expected_blob is not None and git_blob(data)!=expected_blob:
        raise ValueError("ORIGINAL_HOURLY_BLOB_DRIFT")
    content=data.decode("utf-8")
    rows=csv.DictReader(content.splitlines())
    if rows.fieldnames is None or len(set(rows.fieldnames))!=len(rows.fieldnames) or not CLOCK_FIELDS.issubset(rows.fieldnames):
        raise ValueError("CLOCK_SCHEMA_MISSING_OR_DUPLICATE")
    if not {"spot_status","derivatives_status"}.issubset(rows.fieldnames):
        raise ValueError("SOURCE_OWNER_STATUS_COLUMNS_ABSENT")
    parsed=list(rows)
    if len(parsed)!=24:
        raise ValueError("MISSING_OR_DUPLICATE_HOURLY_ROW")
    hist=Counter()
    slots=set()
    sampled=[]
    start=datetime(2026,10,day,tzinfo=timezone.utc)
    for i,row in enumerate(parsed):
        nominal=utc(row["timestamp_utc"])
        batch_end=utc(row["source_window_end_utc"])
        if nominal!=start+i*HOUR or nominal in slots:
            raise ValueError("NONCANONICAL_24_HOUR_SEQUENCE")
        slots.add(nominal)
        if (batch_end-nominal).total_seconds()%3600:
            raise ValueError("NONINTEGRAL_BATCH_WINDOW_END")
        delta=int((batch_end-nominal)/HOUR)
        if not 1<=delta<=24:
            raise ValueError("INVALID_BATCH_WINDOW_END_SPAN")
        hist[delta]+=1
        if delta>1:
            sampled.append({"hour_utc":row["timestamp_utc"],"batch_end_utc":row["source_window_end_utc"],"delta_hours":delta})
    return {
        "day_utc":start.date().isoformat(),
        "original_hourly_blob_git_sha1":git_blob(data),
        "hourly_rows":len(parsed),
        "source_batch_end_equals_nominal_candle_end":hist.get(1,0),
        "source_batch_end_after_nominal_candle_end":len(parsed)-hist.get(1,0),
        "batch_window_end_minus_hour_start_distribution":{str(k):hist[k] for k in sorted(hist)},
        "max_batch_window_end_minus_start_hours":max(hist),
        "sample_different_batch_window_end":sampled[:2]
    }

def execute(folder:Path=SOURCE)->dict:
    per_day=[]
    hist=Counter()
    for d in DAYS:
        path=folder/f"2026-10-{d:02d}.csv"
        row=audit_day(path.read_bytes(),d,expected_blob=PINNED[d])
        per_day.append(row)
        for k,v in row["batch_window_end_minus_hour_start_distribution"].items():
            hist[int(k)]+=v
    total=sum(v["hourly_rows"] for v in per_day)
    later=sum(v["source_batch_end_after_nominal_candle_end"] for v in per_day)
    if total!=168 or later!=104:
        raise ValueError("FROZEN_SEVEN_DAY_CENSUS_CHANGED")
    return {
        "contract":CONTRACT,
        "authority":{"research_only":True,"market_prediction":False,"original_outcomes_mutated":False,"trade_actions":False},
        "source_semantics":"source_window_end_utc IS OWNER_BATCH_REQUEST_END_NOT_DETECTION_OR_VENDOR_FIRST_KNOWN",
        "frozen_period_utc":"2026-10-14..2026-10-20",
        "original_hour_rows":total,
        "batch_end_after_candle_end_count":later,
        "batch_end_equals_candle_end_count":total-later,
        "max_batch_end_minus_hour_start_hours":max(hist),
        "batch_end_minus_hour_start_hours_distribution":{str(k):hist[k] for k in sorted(hist)},
        "by_day":per_day,
        "per_row_provider_first_known_certified":False,
        "after_batch_end_data_unavailable_proven":False,
        "before_batch_end_data_available_proven":False,
        "warning":"BATCH END CLOCK IS NOT A DETECTION OR PUSH CLOCK. Earliest spot close timestamp is not first known.",
        "cfgi_or_compass_edge_tested":False,"values_disclosed":False,
        "status":"DESCRIPTIVE_BATCH_WINDOW_QA_NOT_A_PIT_ELIGIBILITY_GATE"
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--folder",type=Path,default=SOURCE)
    a.add_argument("--output",type=Path)
    o=a.parse_args()
    result=execute(o.folder)
    if o.output:
        o.output.parent.mkdir(parents=True,exist_ok=True)
        o.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("contract","original_hour_rows","batch_end_after_candle_end_count","batch_end_equals_candle_end_count","max_batch_end_minus_hour_start_hours","status")},sort_keys=True))
if __name__=="__main__":
    main()
