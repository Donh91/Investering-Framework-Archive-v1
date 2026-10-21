#!/usr/bin/env python3
"""Task2 public metadata-only CFGI 4h capture clock audit, 2026-10-14..20.

Reads original public Daily Live Anchor v3 index summaries. NO provider values,
prices, scores, components or restricted evidence may enter audit outputs.
The archived retrieval time is an upper bound on *local* known availability:
provider first-publication, original delivery, PIT, edge, and fills are unproved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

CONTRACT = "TASK2_CFGI_4H_CLOCK_READBACK_v1"
START_DAY = date(2026, 10, 14)
END_DAY = date(2026, 10, 20)
EXPECTED_DAYS = 7
EXPECTED_CAPTURES_PER_DAY = 6
EXPECTED_FIELDS = frozenset({"score", "volatility", "volume", "impulse", "technical",
                             "social", "dominance", "trends", "whales", "orders"})
EXPECTED_SYMBOLS = frozenset({"MARKET", "BTC", "ETH"})
EXPLICIT_HARMLESS_ROOTS = {"authority", "contract", "capture_lane", "captured_at_utc",
                           "run_id", "owners", "market_metrics", "status"}
AUTHORITY = {"research_only":True, "hypothesis_testing":False,
             "outcome_scoring":False, "trading":False,
             "cfgi_inference":False, "source_provider_first_publication_verified":False}
ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "03_DAILY_CAPTURE_LOGS/captures"

def time_utc(raw):
    if not isinstance(raw,str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z",raw):
        raise ValueError("NOT_EXPLICIT_UTC_SECOND_CLOCK")
    result = datetime.fromisoformat(raw[:-1]+"+00:00")
    if result.utcoffset() != timedelta(0):
        raise ValueError("NOT_EXPLICIT_UTC_SECOND_CLOCK")
    return result

def git_blob(content):
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()

def permitted_metadata(doc, *, source_name):
    """Reject ambiguous source-time/symbol/owner metadata before any aggregation."""
    if not isinstance(doc,dict) or doc.get("contract")!="DAILY_LIVE_ANCHOR_INDEX_v3":
        raise ValueError("WRONG_OR_MISSING_ORIGINAL_ANCHOR_CONTRACT")
    captured = time_utc(doc.get("captured_at_utc"))
    if doc.get("run_id") is None or not str(doc["run_id"]).startswith("gh-"):
        raise ValueError("ORIGINAL_RUN_NOT_BOUND")
    owners = doc.get("owners")
    if not isinstance(owners,list):
        raise ValueError("OWNER_EVIDENCE_NOT_ARRAY")
    own = [o for o in owners if isinstance(o,dict) and o.get("owner_id")=="cfgi_sentiment"]
    if len(own)!=1:
        raise ValueError("CFGI_OWNER_MISSING_OR_DUPLICATED")
    owner=own[0]
    if owner.get("status")!="PASS" or owner.get("collector_exit_code") not in (0,"0"):
        raise ValueError("CFGI_OWNER_DID_NOT_PASS")
    files=owner.get("files")
    if not isinstance(files,list):
        raise ValueError("OWNER_FILES_NOT_ARRAY")
    def find_file(suffix):
        matched=[f for f in files if isinstance(f,dict) and f.get("path")==suffix]
        if len(matched)!=1 or not isinstance(matched[0].get("summary"),dict):
            raise ValueError("CFGI_ORIGINAL_FILE_RECEIPT_MISSING")
        if not re.fullmatch(r"[0-9a-f]{64}",str(matched[0].get("sha256"))):
            raise ValueError("UNBOUND_ORIGINAL_OWNER_FILE_SHA256")
        return matched[0]["summary"]
    snap=find_file("cfgi-owner-output/owner_snapshot.json")
    receipt=find_file("cfgi-owner-output/receipt.json")
    if snap.get("source")!="CFGI_V3" or snap.get("timeframe")!="4h" or receipt.get("timeframe")!="4h":
        raise ValueError("CFGI_SOURCE_ERA_OR_TIMEFRAME_CHANGED")
    fields=snap.get("fields")
    if not isinstance(fields,list) or len(fields)!=10 or set(fields)!=EXPECTED_FIELDS or receipt.get("fields")!=fields:
        raise ValueError("UNEXPECTED_CFGI_FIELDS")
    retrieved=time_utc(snap.get("retrieved_at_utc"))
    if receipt.get("retrieved_at_utc")!=snap.get("retrieved_at_utc") or retrieved>captured:
        raise ValueError("COLLECTOR_RETRIEVAL_CLOCK_CONFLICT")
    if captured-retrieved>timedelta(minutes=10):
        raise ValueError("EXCESSIVE_CAPTURE_TO_RETRIEVAL_LAG")
    if receipt.get("status")!="PASS" or receipt.get("row_count")!=3:
        raise ValueError("CFGI_RECEIPT_NOT_PASS_3_ROWS")
    rows=snap.get("rows")
    if not isinstance(rows,list) or len(rows)!=3 or {r.get("symbol") for r in rows if isinstance(r,dict)}!=EXPECTED_SYMBOLS:
        raise ValueError("CFGI_SYMBOL_POPULATION_MISMATCH")
    bound={}
    for row in rows:
        symbol=row["symbol"]
        if row.get("owner_status")!="PASS" or row.get("stale") is not False:
            raise ValueError("UNASSESSABLE_OR_STALE_CFGI_ROW")
        original=time_utc(row.get("timestamp"))
        if original>retrieved:
            raise ValueError("CFGI_ORIGINAL_ROW_FROM_THE_FUTURE")
        age=row.get("age_seconds")
        age_clock=(retrieved-original).total_seconds()
        if (not isinstance(age,(float,int)) or isinstance(age,bool) or
                age<0 or abs(age_clock-age)>2):
            raise ValueError("CFGI_ROW_AGE_NOT_RECONCILED")
        bound[symbol]={"original_row_utc":row["timestamp"],
                       "local_retrieved_no_later_than_utc":snap["retrieved_at_utc"],
                       "original_row_age_seconds":int(round(age_clock))}
    stamp_span=(max(time_utc(r["original_row_utc"]) for r in bound.values())-
                min(time_utc(r["original_row_utc"]) for r in bound.values())).total_seconds()
    return {"original_index_filename":source_name, "run_id":doc["run_id"],
            "capture_utc":doc["captured_at_utc"],"retrieval_utc":snap["retrieved_at_utc"],
            "source_symbol_times":bound,
            "within_capture_symbol_clock_skew_seconds":int(round(stamp_span)),
            "symbols_aligned_to_same_original_clock":stamp_span==0,
            "clock_quality":"SYMBOL_CLOCKS_NOT_IDENTICAL" if stamp_span else "SYMBOL_CLOCKS_EQUAL",
            "provider_first_publication_verified":False}

def audit(root=CAPTURE,start=START_DAY,end=END_DAY):
    if (end-start).days != 6:
        raise ValueError("WINDOW_NOT_FROZEN_SEVEN_DAYS")
    entries=[]
    daycounts={}
    all_receipts=[]
    for i in range(EXPECTED_DAYS):
        day=start+timedelta(days=i)
        folder=root / day.strftime("%Y/%m/%d")
        files=sorted(folder.glob("*.json"))
        if len(files)!=EXPECTED_CAPTURES_PER_DAY:
            raise ValueError("DAY_MISSING_OR_DUPLICATED_EXPECTED_6_CAPTURES:"+day.isoformat())
        receipts=[]
        for file in files:
            payload=file.read_bytes()
            doc=json.loads(payload)
            record=permitted_metadata(doc,source_name=file.name)
            if time_utc(record["capture_utc"]).date()!=day:
                raise ValueError("CAPTURE_DAY_FOLDER_MISMATCH")
            record["original_index_git_blob_sha1"]=git_blob(payload)
            receipts.append(record)
        times=[time_utc(r["capture_utc"]) for r in receipts]
        if len(set(times))!=len(times) or len({r["run_id"] for r in receipts})!=len(receipts):
            raise ValueError("DUPLICATE_RUN_OR_CAPTURE_CLOCK")
        entries.extend(receipts)
        daycounts[day.isoformat()]=len(receipts)
    # Scientific attribution must never re-use provider row timestamp as a
    # verified first-known time. These are *timestamp metadata* receipts only.
    skewed=[r for r in entries if not r["symbols_aligned_to_same_original_clock"]]
    max_skew=max(r["within_capture_symbol_clock_skew_seconds"] for r in entries)
    timestamps=set()
    for r in entries:
        for symbol,clock in r["source_symbol_times"].items():
            key=(r["run_id"],symbol)
            if key in timestamps:
                raise ValueError("DUPLICATED_SOURCE_IDENTITY")
            timestamps.add(key)
    result={"contract":CONTRACT, "authority":AUTHORITY,
            "first_utc_day":start.isoformat(),"last_utc_day":end.isoformat(),
            "daily_original_capture_counts":daycounts,
            "original_capture_count":len(entries),
            "original_symbol_rows_count":len(timestamps),
            "source_timeframe":"4h","declared_field_count":10,
            "symbol_clock_skewed_captures":len(skewed),
            "maximum_original_symbol_clock_skew_seconds":max_skew,
            "synchronous_3symbol_captures":len(entries)-len(skewed),
            "original_clock_receipts":entries,
            "source_class":"PUBLIC_CAPTURE_INDEX_METADATA_NOT_PRIVATE_RAW_PROVIDER",
            "scientific_admission":"NOT_PIT_PROVIDER_FIRST_PUBLICATION_NOT_VERIFIED",
            "market_values_emitted":False,
            "future_outcomes_used":False,"cfgi_predictive_edge_tested":False,
            "compass_predictive_edge_tested":False,
            "original_signal_or_market_rule_changed":False,
            "next_use":"READ_ONLY_PER_SYMBOL_ASOF_JOIN_CANDIDATES_AFTER_ORIGINAL_SOURCE_RECEIPT"};
    if len(entries)!=42 or len(timestamps)!=126:
        raise ValueError("SEVEN_DAY_CONTRACT_DENOMINATOR_CHANGED")
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=CAPTURE)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    report=audit(args.root)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({k:report[k] for k in ("contract","first_utc_day","last_utc_day",
        "original_capture_count","original_symbol_rows_count","symbol_clock_skewed_captures",
        "maximum_original_symbol_clock_skew_seconds","scientific_admission")},
        sort_keys=True))

if __name__=="__main__":
    main()
