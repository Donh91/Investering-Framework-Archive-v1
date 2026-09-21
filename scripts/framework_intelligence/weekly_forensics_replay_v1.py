#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PATHS={
 "pullback":"04_MARKET_LEARNING/pullback_learning/LATEST.json",
 "eligibility":"04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json",
 "automation":"research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
 "architecture":"research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json",
 "compounding":"00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json",
 "phase1":"research/framework_intelligence/phase1/LATEST.json",
}
def git(root,*args):
 return subprocess.run(["git","-C",str(root),*args],text=True,capture_output=True,check=False).stdout.strip()
def at(root,sha,path):
 raw=git(root,"show",f"{sha}:{path}")
 if not raw:return None
 try:return json.loads(raw)
 except Exception:return None
def hh(x):return hashlib.sha256(json.dumps(x,sort_keys=True,default=str).encode()).hexdigest()
def sunday_cutoffs(now,weeks):
 local=now.astimezone(ZoneInfo("Europe/Copenhagen"))
 d=local.date()-timedelta(days=(local.weekday()+1)%7)
 if local.weekday()==6 and local.hour<23:d-=timedelta(days=7)
 for i in range(weeks):
  day=d-timedelta(days=7*i)
  yield datetime(day.year,day.month,day.day,23,59,59,tzinfo=ZoneInfo("Europe/Copenhagen"))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--repo-root",default=".");ap.add_argument("--weeks",type=int,default=12);ap.add_argument("--output-root",default="research/framework_learning/weekly_forensics/replay");ap.add_argument("--as-of-utc");a=ap.parse_args()
 root=Path(a.repo_root);out=root/a.output_root
 now=datetime.fromisoformat(a.as_of_utc.replace("Z","+00:00")) if a.as_of_utc else datetime.now(timezone.utc)
 rows=[]
 for cutoff in reversed(list(sunday_cutoffs(now,a.weeks))):
  sha=git(root,"rev-list","-1",f"--before={cutoff.astimezone(timezone.utc).isoformat()}","HEAD")
  y,w,_=cutoff.isocalendar(); sources={}; available=0
  for k,p in PATHS.items():
   v=at(root,sha,p) if sha else None
   sources[k]={"path":p,"available":v is not None,"sha256":hh(v) if v is not None else None}
   available+=int(v is not None)
  pb=at(root,sha,PATHS["pullback"]) if sha else None
  au=at(root,sha,PATHS["automation"]) if sha else None
  cp=at(root,sha,PATHS["compounding"]) if sha else None
  rows.append({"iso_year":y,"iso_week":w,"cutoff_local":cutoff.isoformat(),"source_commit":sha or None,
   "evidence_coverage":{"available":available,"required":len(PATHS),"ratio":round(available/len(PATHS),3)},
   "observed":{"pullback_observation_count":(pb or {}).get("observation_count"),"pullback_eligibility_status":(pb or {}).get("eligibility_status"),
    "automation_red_count":(au or {}).get("red_count"),"automation_amber_count":(au or {}).get("amber_count"),
    "compounding_family_count":len((cp or {}).get("hypothesis_families") or [])},
   "sources":sources,"unknown_policy":"MISSING_AT_CUTOFF_IS_UNKNOWN_NOT_ZERO"})
 generated=now.astimezone(timezone.utc).isoformat().replace("+00:00","Z")
 doc={"contract":"WEEKLY_FORENSICS_REPLAY_BASELINE_v1","authority":"RESEARCH_ONLY_NON_CANONICAL","generated_at_utc":generated,
  "point_in_time_method":"git_commit_at_or_before_sunday_23_59_59_Europe_Copenhagen","anti_hindsight":True,"automatic_market_semantic_change":False,
  "portfolio_execution":False,"automatic_promotion":False,"weeks_requested":a.weeks,"weeks_materialized":len(rows),"weeks":rows,
  "learning_binding":{"consumer":"FRAMEWORK_LEARNING_SUPERVISOR","role":"BOOTSTRAP_BASELINE_AND_RECURRENCE_MEMORY","may_route_findings":True,
   "may_mutate_market_rules":False,"permanent_live_successor":"WEEKLY_FORENSICS_PACK_v1"}}
 out.mkdir(parents=True,exist_ok=True);(out/"LATEST_REPLAY_BASELINE.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":"PASS","weeks":len(rows),"output":str(out/"LATEST_REPLAY_BASELINE.json")}))
if __name__=="__main__":main()
