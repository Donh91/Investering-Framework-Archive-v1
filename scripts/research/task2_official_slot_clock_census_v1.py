#!/usr/bin/env python3
"""Task2 original Official Compass scheduling labels vs issue clocks.

CENSUS, NOT schedule lateness, original first-delivery, PIT or scoring.
The later-day SCHEDULED_EVENING label may belong to a previous run: NEVER
retro-assign a forecast to a same-day nominal slot based only on run_reason.
Uses only frozen original public Official Compass JSONs and workflow source.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from scripts.research import task2_official_r1_original_evidence_gate_v1 as original

CONTRACT="TASK2_OFFICIAL_SCHEDULE_LABEL_VERSUS_ISSUANCE_CLOCK_CENSUS_v1"
ROOT=Path(__file__).resolve().parents[2]
FORECAST_ROOT=ROOT/"04_MARKET_LEARNING/handlekompas/official/daily"
WORKFLOW=ROOT/".github/workflows/daily-compass.yml"
FIRST=date(2026,10,12)
LAST=date(2026,10,20)
EXPECTED_SLOTS=("SCHEDULED_MORNING","SCHEDULED_EVENING")
CET_OFFSET_HOURS=2  # Research period strictly before Oct25 DST change.
NOMINAL_UTC_MINUTES={"SCHEDULED_MORNING":6*60+17,
                     "SCHEDULED_EVENING":18*60+17}
SOURCE_STATES=("EVENT_DRIVEN","ON_DEMAND",*EXPECTED_SLOTS)
OWNER="OFFICIAL_DAILY_COMPASS_ORIGINAL_PUBLIC_ARCHIVE"

def source_contract(workflow: Path):
    s=workflow.read_text(encoding="utf-8")
    required=[
        "name: Official Daily Compass",
        "- cron: '17 6 * * *'",
        "- cron: '17 7 * * *'",
        "- cron: '17 18 * * *'",
        "- cron: '17 19 * * *'",
        "The slot gate below activates exactly one candidate per local slot."
    ]
    absent=[x for x in required if x not in s]
    if absent:raise ValueError("PRODUCER_WORKFLOW_CRON_CONTRACT_NOT_RECOGNIZED")
    return {"captured_at_source":"CURRENT_WORKFLOW_TEXT_NOT_HISTORICAL_PER_RUN",
            "declared_local_clocks":["08:17","20:17"],
            "research_utc_offset_hours":CET_OFFSET_HOURS,
            "observed_run_or_action_dispatch_proof":False,
            "historical_workflow_at_every_issued_date_verified":False}

def score(original_files, workflow=WORKFLOW, *, strict=True):
    """Accept list of (relative repository source path, original bytes); no prices."""
    schedule=source_contract(workflow)
    seen=set()
    dirs={}
    causes=Counter()
    per_day={}
    source_receipts=[]
    odd=[]
    for name,raw in original_files:
        p=Path(name)
        if p.as_posix() in seen:raise ValueError("DUPLICATE_ORIGINAL_FORECAST_FILE")
        seen.add(p.as_posix())
        try:
            day=date.fromisoformat("/".join(p.parts[-4:-1]).replace("/","-"))
        except ValueError as exc:
            raise ValueError("ORIGINAL_FORECAST_PATH_DAY_INVALID") from exc
        if p.suffix!=".json" or not (FIRST<=day<=LAST):
            raise ValueError("OUTSIDE_FIXED_ARCHIVE_COHORT")
        if p.parent.as_posix().endswith(day.strftime("%Y/%m/%d")) is False:
            raise ValueError("BAD_ORIGINAL_ISSUE_FOLDER")
        j=json.loads(raw)
        problems=original.preflight_forecast(j,p,day)
        if problems:raise ValueError("ORIGINAL_FORECAST_PREFLIGHT_INVALID:"+",".join(problems))
        reason=j.get("run_reason")
        if reason not in SOURCE_STATES:raise ValueError("UNKNOWN_ORIGINAL_RUN_REASON")
        issue=original.utc(j["issued_at_utc"])
        if issue.date()!=day:raise ValueError("ISSUE_DATE_MISMATCH")
        if day not in dirs:
            dirs[day]={"total_original":0,"scheduled_morning":0,"scheduled_evening":0,
                       "other_original":0}
        dirs[day]["total_original"]+=1
        causes[reason]+=1
        if reason in EXPECTED_SLOTS:
            key=("scheduled_morning" if reason=="SCHEDULED_MORNING" else "scheduled_evening")
            dirs[day][key]+=1
            if dirs[day][key]>1:raise ValueError("DUPLICATE_SAME_DAY_SCHEDULE_REASON")
            mins=issue.hour*60+issue.minute+issue.second/60
            skew=round(mins-NOMINAL_UTC_MINUTES[reason],4)
            state=("ISSUED_BEFORE_SAME_DAY_NOMINAL_SLOT" if skew<0
                   else "ISSUED_AFTER_NOMINAL_BY_MORE_THAN_90_MINUTES" if skew>90
                   else "ISSUED_WITHIN_90_MINUTES_OF_SAME_DAY_NOMINAL")
            odd.append({"forecast_id":j["compass_id"],"day":day.isoformat(),
                        "reason":reason,"issued_at_utc":j["issued_at_utc"],
                        "same_day_nominal_clock_diagnostic_minutes":skew,
                        "diagnostic_class":state,
                        "verified_actual_schedule_lateness":False,
                        "original_github_run_id_binding_verified":False})
        else:
            dirs[day]["other_original"]+=1
        source_receipts.append({"path":p.as_posix(),
                                "original_git_blob_sha1":original.blob_sha(raw)})
    d=FIRST
    while d<=LAST:
        dirs.setdefault(d,{"total_original":0,"scheduled_morning":0,
                           "scheduled_evening":0,"other_original":0})
        d+=timedelta(days=1)
    counts=Counter()
    states=Counter()
    for o in odd:states[o["diagnostic_class"]]+=1
    for d,c in sorted(dirs.items()):
        for reason,key in (("SCHEDULED_MORNING","scheduled_morning"),
                           ("SCHEDULED_EVENING","scheduled_evening")):
            if c[key]==0:
                counts["missing_same_day_declared_reason"]+=1
    counts["expected_local_schedule_slot_dates"]=len(dirs)*len(EXPECTED_SLOTS)
    counts["observed_original_forecasts"]=len(source_receipts)
    counts["scheduled_reason_files"]=sum(causes[x] for x in EXPECTED_SLOTS)
    counts["event_driven_or_on_demand"]=sum(causes[x] for x in ("EVENT_DRIVEN","ON_DEMAND"))
    counts["first_delivery_verified"]=0
    counts["original_github_run_dispatch_verified"]=0
    counts["scientifically_admitted_forecast_causality"]=0
    if counts["scheduled_reason_files"]+counts["event_driven_or_on_demand"]!=len(source_receipts):
        raise ValueError("FORECAST_REASON_DENOMINATOR_BROKEN")
    if counts["expected_local_schedule_slot_dates"]!=counts["scheduled_reason_files"]+counts["missing_same_day_declared_reason"]:
        raise ValueError("SCHEDULE_REASON_CENSUS_BROKEN")
    if strict and (len(source_receipts)!=70 or counts["scheduled_reason_files"]!=17):
        raise ValueError("ORIGINAL_OCT12_OCT20_SCHEDULE_COHORT_DRIFT")
    return {"contract":CONTRACT,"classification":"ORIGINAL_ISSUANCE_REASON_FORENSICS_NOT_SCHEDULE_LATENCY",
            "research_cutoff":"2026-10-21",
            "original_archive_source":OWNER,
            "current_workflow_source":WORKFLOW.relative_to(ROOT).as_posix(),
            "workflow_evidence":schedule,
            "observation_clock_semantics":"DECLARED_FORECAST_ISSUE_TIME_NOT_VERIFIED_PUBLIC_DELIVERY",
            "original_reason_counts":dict(sorted(causes.items())),
            "counts":dict(counts),
            "diagnostic_counts":dict(states),
            "by_day":[{"day":day.isoformat(),**c} for day,c in sorted(dirs.items())],
            "scheduled_originals":odd,
            "original_source_git_blob_manifest":source_receipts,
            "source_sha_identity_admitted":True,
            "same_day_schedule_assignment_proven":False,
            "clock_diagnostic_is_actual_job_delay":False,
            "provider_first_publication_verified":False,
            "first_delivery_verified":False,
            "scientific_edge_established":False,
            "next_required_evidence":"Original GH Actions workflow run ID/event/created_at/run_started_at and exact immutable forecast-emitting commit, cross-day attribution plus source first-known, actual user delivery."}

def execute(root=FORECAST_ROOT,workflow=WORKFLOW):
    files=[]
    d=FIRST
    while d<=LAST:
        directory=root/d.strftime("%Y/%m/%d")
        if not directory.is_dir():raise ValueError("SOURCE_DAY_DIRECTORY_MISSING")
        for p in sorted(directory.glob("CMP-*.json")):
            files.append((p.relative_to(ROOT).as_posix(),p.read_bytes()))
        d+=timedelta(days=1)
    return score(files,workflow=workflow)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    result=execute()
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"contract":CONTRACT,"counts":result["counts"],
                     "reason_counts":result["original_reason_counts"],
                     "clock_diagnostics":result["diagnostic_counts"]},sort_keys=True))
if __name__=="__main__":
    main()
