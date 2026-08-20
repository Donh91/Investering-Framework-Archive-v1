#!/usr/bin/env python3
from __future__ import annotations
import csv, gzip, json
from datetime import datetime
from pathlib import Path

HOUR_MS=3600_000
ROOT=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1")
ART=ROOT/"artifacts"

def ms(x): return int(datetime.fromisoformat(x.replace("Z","+00:00")).timestamp()*1000)

def main():
    catalog=json.loads((ART/"EPISODE_CATALOG.json").read_text())
    rows=[]
    with gzip.open(ART/"hourly_features.csv.gz","rt",encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            r["timestamp_ms"]=int(float(r["timestamp_ms"])); r["continuity_segment_id"]=int(float(r["continuity_segment_id"])); rows.append(r)
    by_ts={(r["continuity_segment_id"],r["timestamp_ms"]):r for r in rows}
    episodes={e["episode_id"]:e for e in catalog["episodes"]}
    selected=[]
    for x in catalog.get("cfgi_candidate_windows",{}).get("pullbacks",[]):
        e=episodes.get(x["episode_id"])
        if e: selected.append({"kind":"PULLBACK","event_id":e["episode_id"],"event_utc":e["top_utc"],"segment":e["continuity_segment_id"],"matched_to":None})
    for c in catalog.get("cfgi_candidate_windows",{}).get("controls",[]):
        cand=[r for r in rows if r["timestamp_utc"]==c["event_utc"]]
        if cand: selected.append({"kind":"CONTROL","event_id":c["control_id"],"event_utc":c["event_utc"],"segment":cand[0]["continuity_segment_id"],"matched_to":c.get("matched_episode_id")})
    out=[]; coverage=[]
    for ev in selected:
        t=ms(ev["event_utc"]); found=0
        for h in range(-72,49):
            r=by_ts.get((ev["segment"],t+h*HOUR_MS))
            if not r: continue
            found+=1; out.append({"kind":ev["kind"],"event_id":ev["event_id"],"matched_to":ev["matched_to"],"event_utc":ev["event_utc"],"relative_hour":h,"feature":r})
        coverage.append({"kind":ev["kind"],"event_id":ev["event_id"],"expected_hours":121,"available_hours":found,"coverage_ratio":found/121})
    with gzip.open(ART/"FREE_EVENT_PATHS.jsonl.gz","wt",encoding="utf-8") as fh:
        for r in out: fh.write(json.dumps(r,sort_keys=True)+"\n")
    (ART/"FREE_EVENT_PATHS_COVERAGE.json").write_text(json.dumps({"contract":"FREE_EVENT_PATHS_COVERAGE_v1","events":coverage},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","events":len(selected),"rows":len(out)},sort_keys=True))
if __name__=="__main__": main()
