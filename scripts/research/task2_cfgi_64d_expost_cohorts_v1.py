#!/usr/bin/env python3
"""Task2 extended original CFGI v3 4h versus 1h spot momentum study.

EX-POST RESEARCH ONLY. Read only already archived daily anchors and price CSVs.
Never purchase/request vendor data. A local capture clock is an upper bound on
source availability, NOT verified vendor publication or original forecast.
No investment alpha, real fills, original Compass prediction or model promotion.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter,defaultdict
from datetime import date,datetime,timedelta,timezone
from pathlib import Path

from scripts.research import task2_cfgi_price_expost_4h_v1 as small
from scripts.research import task2_cfgi_capture_clock_audit_v1 as source

CONTRACT="TASK2_CFGI_64D_ORIGINAL_4H_ASSOCIATION_v1"
LABEL="EX_POST_CORRELATED_MULTIWEEK_DEVELOPMENT_NOT_PIT_OR_EDGE"
START=date(2026,8,18)
END=date(2026,10,20)
SOURCE_START=date(2026,8,8)
SOURCE_END=END
CAPTURE_ROOT=source.CAPTURE
PRICE_ROOT=CAPTURE_ROOT.parents[0] / "hourly"
AUTHORITY={"research_only":True,"raw_market_values_published":False,
           "provider_first_publication_verified":False,
           "original_forecast_issue_verified":False,
           "hypothesis_frozen_before_outcomes":False,
           "historical_edge_admitted":False,
           "trade_authorized":False,"new_vendor_requests":False}

def day_iter(start,end):
    n=(end-start).days
    if n<0 or n>365:raise ValueError("UNBOUNDED_SOURCE_SCAN")
    for i in range(n+1):yield start+timedelta(days=i)

def spot_index(root):
    rows={}
    receipts=[]
    missing=[]
    incomplete=[]
    for d in day_iter(SOURCE_START,SOURCE_END):
        path=root / d.strftime("%Y/%m") / (d.isoformat()+".csv")
        if not path.is_file():
            missing.append(d.isoformat())
            continue
        raw=path.read_bytes()
        sha=source.git_blob(raw)
        x=csv.DictReader(raw.decode("utf-8").splitlines())
        if not x.fieldnames or len(set(x.fieldnames))!=len(x.fieldnames):
            raise ValueError("INVALID_OR_DUPLICATE_SPOT_FIELDS")
        if not {"timestamp_utc","source_window_end_utc","spot_status","btc_close","eth_close"}.issubset(x.fieldnames):
            raise ValueError("MISSING_SPOT_OWNER_CONTRACT")
        n=0
        for y in x:
            t=source.time_utc(y["timestamp_utc"])
            if t.date()!=d or t.minute or t.second or t.microsecond:
                raise ValueError("WRONG_SPOT_DAY_OR_NONHOURLY_SOURCE")
            if t in rows:raise ValueError("DUPLICATE_SPOT_HOUR_ACROSS_DAYS")
            source.time_utc(y["source_window_end_utc"])
            rows[t]=y
            n+=1
        if n!=24:incomplete.append({"day":d.isoformat(),"rows":n})
        receipts.append({"day":d.isoformat(),"original_git_blob_sha1":sha,"rows":n})
    if len(rows)<500 or len(receipts)<15:raise ValueError("INSUFFICIENT_ORIGINAL_ARCHIVE")
    return rows,receipts,missing,incomplete

def source_archive(root, prices):
    records=[]
    skipped=Counter()
    original_counts=Counter()
    available_dates=0
    original_file_receipts=[]
    unique_runs=set()
    unique_symbol_source_timestamp=set()
    repeated_source_stamps=0
    clock_skewed=0
    for d in day_iter(START,END):
        folder=root / d.strftime("%Y/%m/%d")
        captures=sorted(folder.glob("*.json"))
        original_counts[d.isoformat()]=len(captures)
        if captures:available_dates+=1
        for f in captures:
            raw=f.read_bytes()
            obj=json.loads(raw)
            original_file_receipts.append((f.relative_to(root).as_posix(),source.git_blob(raw)))
            try:metadata=source.permitted_metadata(obj,source_name=f.name)
            except (ValueError,KeyError,TypeError) as exc:
                code=str(exc).split(":")[0]
                if len(code)>96 or not code.isupper():code="INVALID_ORIGINAL_CAPTURE_METADATA"
                skipped["CAPTURE:"+code]+=1
                continue
            t=source.time_utc(metadata["capture_utc"])
            if t.date()!=d:raise ValueError("CAPTURE_DATE_FOLDER_MISMATCH")
            if metadata["run_id"] in unique_runs:raise ValueError("DUPLICATE_PRODUCTION_CAPTURE_RUN")
            unique_runs.add(metadata["run_id"])
            if metadata["within_capture_symbol_clock_skew_seconds"]>0:
                clock_skewed+=1
            owner=next(a for a in obj["owners"] if a["owner_id"]=="cfgi_sentiment")
            snap=next(a["summary"] for a in owner["files"] if a["path"]=="cfgi-owner-output/owner_snapshot.json")
            classification=small.classify_opportunity(snap,metadata,prices)
            for item in classification:
                s=item["symbol"]
                original_ts=metadata["source_symbol_times"][s]["original_row_utc"]
                key=(s,original_ts)
                if key in unique_symbol_source_timestamp:repeated_source_stamps+=1
                unique_symbol_source_timestamp.add(key)
                if item["state"]!="EXPOST_JOIN_ONLY":
                    skipped["SYMBOL:"+item["state"]]+=1
                    continue
                item["week"]=f"{t.isocalendar().year}-W{t.isocalendar().week:02d}"
                item["capture_day"]=d.isoformat()
                records.append(item)
    if available_dates<15 or len(unique_runs)<30:raise ValueError("SOURCE_COHORT_TOO_SMALL_OR_MISSING")
    text="\n".join(f"{name}:{blob}" for name,blob in sorted(original_file_receipts))
    manifest=hashlib.sha256((text+"\n").encode()).hexdigest()
    return records,{"source_capture_files":len(original_file_receipts),
                    "validated_capture_runs":len(unique_runs),
                    "observed_capture_days":available_dates,
                    "total_calendar_days":(END-START).days+1,
                    "source_files_per_day":dict(original_counts),
                    "original_capture_manifest_sha256":manifest,
                    "duplicate_source_symbol_timestamp_occurrences":repeated_source_stamps,
                    "capture_symbol_clock_skewed_count":clock_skewed,
                    "excluded_opportunities_by_reason":dict(sorted(skipped.items()))}

def execute(captures=CAPTURE_ROOT,price_dir=PRICE_ROOT):
    prices,receipts,missing,incomplete=spot_index(price_dir)
    observations,source_status=source_archive(captures,prices)
    by_symbol={k:small.summarize([x for x in observations if x["symbol"]==k]) for k in small.SYMBOLS}
    weeks=sorted({q["week"] for q in observations})
    by_week={}
    for w in weeks:
        sub=[q for q in observations if q["week"]==w]
        by_week[w]={"capture_day_count":len({q["capture_day"] for q in sub}),
                    "symbol_observations":len(sub),
                    "by_symbol":{s:small.summarize([q for q in sub if q["symbol"]==s])
                                 for s in small.SYMBOLS}}
    unique_days=len({x["capture_day"] for x in observations})
    paired_counts=sum(v["symbol_observations"] for v in by_symbol.values())
    if paired_counts!=len(observations):
        raise ValueError("ORIGINAL_OPPORTUNITY_COUNTS_NONRECONCILING")
    return {"contract":CONTRACT,"classification":LABEL,"authority":AUTHORITY,
      "date_start_utc":START.isoformat(),"date_end_utc":END.isoformat(),
      "original_hours_price_available":len(prices),
      "price_source_provenance":{"file_receipts":receipts,"missing_days":missing,
                                 "partial_days":incomplete},
      "source_original_manifest":source_status,
      "joined_symbol_opportunities":len(observations),
      "joined_days":unique_days,
      "weekly_units":len(weeks),
      "by_week":by_week,"by_symbol":by_symbol,
      "fixed_heuristics":["CFGI score>50 vs <50","previous completed 4 1h price candles momentum direction"],
      "future_outcome":"following 4th complete 1h spot candle close relative to last preceding complete 1h spot close",
      "provider_publication_first_known_verified":False,
      "price_first_known_at_decision_verified":False,
      "hypothesis_registered_before_outcomes":False,
      "executed_forecast_model_included":False,
      "statistical_significance_claim":False,
      "after_cost_executable_portfolio_return_claim":False,
      "original_raw_cfgi_values_exported":False,
      "caution":"Not independent trial/event count. Retrospective observations of one regime and engine-v3 only; raw score and price private provider first-known not certified."}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path)
    a=p.parse_args();res=execute()
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"contract":CONTRACT,
      "original_capture_files":res["source_original_manifest"]["source_capture_files"],
      "validated_captures":res["source_original_manifest"]["validated_capture_runs"],
      "observed_days":res["source_original_manifest"]["observed_capture_days"],
      "joined":res["joined_symbol_opportunities"],
      "independent_calendar_week_units_not_market_events":res["weekly_units"],
      "by_symbol":res["by_symbol"]},sort_keys=True))
if __name__=="__main__":main()
