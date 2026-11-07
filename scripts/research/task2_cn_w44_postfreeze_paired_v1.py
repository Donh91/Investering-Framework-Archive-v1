#!/usr/bin/env python3
"""Task2 #1596: native frozen W44 CN vs original same-clock four-week B1.

Research-only source-based 162 post-issue hourly interval LOW/HIGH comparisons.
This is NOT a properly scored joint probabilistic forecast, PIT-admitted alpha,
the official CN scorecard or an additional market/trading authority.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CONTRACT="TASK2_CN_W44_POSTFREEZE_CN_VS_PREISSUED_B1_v1"
OWNER_ISSUE=1596
ORIGINAL_WEEK="2026-W44"
ISSUE_COMMIT="ca7563d4e47117b963d7c9c92db080a996d35cf8"
SOURCES={
 "hourly":("03_DAILY_CAPTURE_LOGS/weekly/2026/W44/WEEKLY_HOURLY_ENRICHED.csv",
           "962d5e44fe5274692ad6b63e2a9da5e4035e5a35"),
 "weekly":("03_DAILY_CAPTURE_LOGS/weekly/2026/W44.json",
           "b5b30a81a6a161c8ebe022a3438b78f09fc511ac"),
 "original_cn":("05_CYCLE_NAVIGATOR/weekly/2026/W44/CYCLE_NAVIGATOR_FORECAST_FREEZE.json",
                "4920c9f5c23279ecd540948b19cbd92c34dbebdf"),
 "original_b1":("05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W44.json",
                "c2422efa183e5d1bc9199fab8d458b0cfdf17414"),
 "original_site_receipt":("05_CYCLE_NAVIGATOR/weekly/2026/W44/CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json",
                          "a7214cac7222d3aecdab8a07631f878fc795e4b9"),
 "prior_scorecard":("05_CYCLE_NAVIGATOR/weekly/2026/W45/CYCLE_NAVIGATOR_SCORECARD.json",
                    "f69d6dfe31ce1e50660312ddb370fe0ebb16c0fd")
}
DAY_OPEN=datetime(2026,10,26,tzinfo=timezone.utc)
DAY_END=datetime(2026,11,2,tzinfo=timezone.utc)
EXPECTED_FREEZE="2026-10-26T07:00:00Z"
EXPECTED_ISSUE_UTC="2026-10-26T06:57:49Z"
INSTRUMENT_NOTE="ORIGINAL_CN_USD_RANGE_AGAINST_PUBLIC_BINANCE_USDT_HOURLY_OUTCOME_NOT_SAME_QUOTE"

def git_blob(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def locked_read(root:Path,key:str)->tuple[bytes,dict]:
    path,expected=SOURCES[key]
    target=root/path
    if (not target.is_file() or target.is_symlink()
        or not target.resolve().is_relative_to(root.resolve())):
        raise ValueError("UNSAFE_OR_MISSING_ORIGINAL_SOURCE:"+key)
    raw=target.read_bytes()
    if git_blob(raw)!=expected:
        raise ValueError("ORIGINAL_GIT_BLOB_DRIFT:"+key)
    if not raw or len(raw)>2_000_000:
        raise ValueError("ORIGINAL_SOURCE_SIZE_INVALID:"+key)
    return raw,{"path":path,"git_blob_sha1":expected,
                "sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}

def utc(value:str)->datetime:
    d=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if d.tzinfo is None or d.utcoffset()!=timedelta():
        raise ValueError("SOURCE_CLOCK_NOT_UTC")
    return d.astimezone(timezone.utc)

def joint_score(lo:float,hi:float,actual_lo:float,actual_hi:float,anchor:float)->dict:
    if not all(math.isfinite(x) for x in (lo,hi,actual_lo,actual_hi,anchor)):
        raise ValueError("NONFINITE_W44_RANGE")
    if not (0<lo<hi and 0<actual_lo<=actual_hi and anchor>0):
        raise ValueError("INVALID_W44_ORIGINAL_BAND")
    joint=lo<=actual_lo and hi>=actual_hi
    overlap=max(0.,min(hi,actual_hi)-max(lo,actual_lo))
    union=max(hi,actual_hi)-min(lo,actual_lo)
    return {
        "predicted_low":lo,"predicted_high":hi,
        "actual_low":actual_lo,"actual_high":actual_hi,
        "joint_full_low_and_high_contained":joint,
        "normalized_predicted_width_pct":round((hi-lo)/anchor*100,6),
        "jaccard_overlap":round(overlap/union,6),
        "low_breach":round(max(0.,lo-actual_lo),6),
        "high_breach":round(max(0.,actual_hi-hi),6),
        "probabilistic_calibration_or_alpha_score":None,
    }

def build(root:Path=ROOT)->dict:
    root=root.resolve()
    raw={}
    identities={}
    for key in SOURCES:
        raw[key],identities[key]=locked_read(root,key)
    data={key:json.loads(raw[key]) for key in SOURCES if key!="hourly"}
    rec=data["original_site_receipt"]
    issue=datetime.fromtimestamp(rec["frozen_unix"],tz=timezone.utc)
    cut=utc(rec["scoring_valid_from_utc"])
    if (issue!=utc(EXPECTED_ISSUE_UTC)
        or cut!=utc(EXPECTED_FREEZE)
        or cut<issue
        or not (DAY_OPEN<issue<DAY_END)
        or rec["forecast_week"]!=ORIGINAL_WEEK
        or rec["source_forecast_freeze_path"]!=SOURCES["original_cn"][0]
        or rec["status"]!="SITE_FROZEN_SOURCE_OF_RECORD"):
        raise ValueError("W44_NATIVE_SOURCE_FREEZE_CLOCK_CHANGED")
    weekly=data["weekly"]
    if (weekly["hourly_gap_diagnostics"]["expected_hours"]!=168
        or weekly["hourly_gap_diagnostics"]["observed_hours"]!=168
        or weekly["hourly_gap_diagnostics"]["missing_hour_count"]!=0):
        raise ValueError("W44_WEEKLY_OUTCOME_NOT_CONTIGUOUS")
    b1=data["original_b1"]
    if (b1["status"]!="READY" or b1["target_iso_week"]!=44 or
        not b1["independence"]["generated_without_cycle_navigator_model_output"]
        or b1["expected_anchor_iso_week"]!=43):
        raise ValueError("W44_B1_NOT_PREISSUED_FROZEN_BASELINE")
    scorecard=data["prior_scorecard"]
    if scorecard["completed_iso_week"]!=44 or scorecard["score_status"]!="REPRODUCIBLE":
        raise ValueError("ORIGINAL_W44_SCORECARD_TARGET_CHANGED")
    original=data["original_cn"]
    if original["daily_price_path"]["BTC"]["status"]!="UNAVAILABLE":
        raise ValueError("W44_DAILY_PRICE_PATH_WAS_NOT_PUBLISHED")
    csvrows=list(csv.DictReader(raw["hourly"].decode().splitlines()))
    if len(csvrows)!=168:raise ValueError("ORIGINAL_W44_HOURLY_ROW_COUNT_DRIFT")
    seen=set()
    qualifying=[]
    last=None
    for row in csvrows:
        t=utc(row["source_window_end_utc"])
        if t in seen or (last and t-last!=timedelta(hours=1)):
            raise ValueError("MISSING_OR_DUPLICATE_HOURLY_SOURCE")
        seen.add(t)
        last=t
        if cut<=t<=DAY_END:
            qualifying.append(row)
    if len(qualifying)!=162 or utc(qualifying[0]["source_window_end_utc"])!=cut or utc(qualifying[-1]["source_window_end_utc"])!=DAY_END:
        raise ValueError("W44_POSTFREEZE_ELIGIBLE_SOURCE_COUNT_CHANGED")
    output={}
    for asset in ("BTC","ETH"):
        a=asset.lower()
        lows=[float(row[a+"_low"]) for row in qualifying]
        highs=[float(row[a+"_high"]) for row in qualifying]
        al=min(lows);ah=max(highs)
        anchor=b1["assets"][asset]["anchor_price"]
        cn=joint_score(float(original[a+"_range_low"]),float(original[a+"_range_high"]),al,ah,anchor)
        base=joint_score(float(b1["assets"][asset]["low"]),float(b1["assets"][asset]["high"]),al,ah,anchor)
        official=next((r for r in scorecard["parameter_scores"] if r.get("parameter_id")==a+"_range"),None)
        if not official or official["status"]!="SUPPORTED" or not cn["joint_full_low_and_high_contained"]:
            raise ValueError("CN_W44_ORIGINAL_SCORECARD_CONTROVERSY_"+asset)
        if base["joint_full_low_and_high_contained"]:
            raise ValueError("B1_W44_ORIGINAL_NEGATIVE_CONTROL_DISAPPEARED_"+asset)
        output[asset]={
            "asset":asset,"postfreeze_hourly_extrema":{ "low":al,"high":ah},
            "CN":cn,"ORIGINAL_PREISSUED_B1":base,
            "CN_width_over_B1_width":round((cn["predicted_high"]-cn["predicted_low"])/(base["predicted_high"]-base["predicted_low"]),6),
            "CN_contained_B1_missed_and_B1_jaccard_higher":
                cn["joint_full_low_and_high_contained"] and not base["joint_full_low_and_high_contained"]
                and base["jaccard_overlap"]>cn["jaccard_overlap"],
        }
    return {
       "contract":CONTRACT,"original_owner_issue":OWNER_ISSUE,
       "classification":"EXPOSED_AFTER_FACT_DIAGNOSTIC_W44_NOT_PIT_ALPHATEST",
       "forecast_week":ORIGINAL_WEEK,"original_publishing_git_commit":ISSUE_COMMIT,
       "original_publishing_git_commit_independent_live_ancestry_checked_by_this_script":False,
       "source_identity":identities,
       "issue_at_utc":issue.isoformat(),"postfreeze_first_eligible_hour_utc":cut.isoformat(),
       "full_week_completed_hours":168,"postfreeze_eligible_hours":len(qualifying),
       "last_eligible_complete_hour_end_utc":DAY_END.isoformat(),
       "currency_semantics":INSTRUMENT_NOTE,
       "results":output,
       "original_vendor_first_known_proven":False,
       "independent_market_event_families":None,
       "joint_probabilistic_interval_skill_proven":False,
       "confirmed_incremental_forecast_edge":False,
       "trading_or_public_score_change":False,
       "round3_analysis_performed":False,
       "no_model_selection_or_parameter_tuning":True,
       "next":"Prospectively score original committed B1 and CN after UTC first eligible hour on independent weeks; measure width+breaches+source clock and actual quote type; no ad hoc scalar joint Winkler."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    r=build()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"contract":CONTRACT,"postfreeze_hours":r["postfreeze_eligible_hours"],
                      "results":{k:{"CN_contained":v["CN"]["joint_full_low_and_high_contained"],
                      "B1_contained":v["ORIGINAL_PREISSUED_B1"]["joint_full_low_and_high_contained"],
                      "CN_J":v["CN"]["jaccard_overlap"],
                      "B1_J":v["ORIGINAL_PREISSUED_B1"]["jaccard_overlap"]}
                      for k,v in r["results"].items()}},sort_keys=True))

if __name__=="__main__":
    main()
