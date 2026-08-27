#!/usr/bin/env python3
"""Preregistered T-1 falsification for NFCICREDIT.

Input is deterministic vintage CSV: observation_date,vintage_asof,value.
Each frozen T-90 date must have its own ALFRED vintage snapshot. No network or
LLM extraction occurs in this evaluator.
"""
import argparse,csv,json
from datetime import date,timedelta
from pathlib import Path

TOPS=(date(2013,11,30),date(2017,12,17),date(2021,11,10))
LOOKBACK_DAYS=90
PERCENTILE_YEARS=3


def load(path):
    rows=[]
    with path.open(newline='') as f:
        for r in csv.DictReader(f):
            ds=r.get('observation_date') or r.get('DATE')
            vs=r.get('vintage_asof') or r.get('realtime_end') or r.get('REALTIME_END')
            raw=r.get('value') or r.get('NFCICREDIT')
            if not ds or not vs or raw in (None,'','.'):
                continue
            rows.append((date.fromisoformat(ds),date.fromisoformat(vs),float(raw)))
    return sorted(rows)


def percentile(history,value):
    return 100.0*sum(x <= value for x in history)/len(history) if history else None


def run(rows):
    episodes=[]
    for top in TOPS:
        asof=top-timedelta(days=LOOKBACK_DAYS)
        vintage=[x for x in rows if x[1] == asof and x[0] <= asof]
        start=asof-timedelta(days=365*PERCENTILE_YEARS)
        hist=[v for d,_,v in vintage if start <= d <= asof]
        obs=max(vintage,key=lambda x:x[0]) if vintage else None
        if obs is None or len(hist) < 100:
            episodes.append({'top':top.isoformat(),'asof':asof.isoformat(),'status':'NOT_PRESENT','vintage_rows':len(vintage),'history_rows':len(hist)})
            continue
        pct=percentile(hist,obs[2])
        episodes.append({'top':top.isoformat(),'asof':asof.isoformat(),'status':'OBSERVED','observation_date':obs[0].isoformat(),'value':obs[2],'trailing_3y_percentile':pct,'below_median':pct < 50.0,'history_rows':len(hist)})
    observed=[x for x in episodes if x['status']=='OBSERVED']
    if len(observed) != len(TOPS): verdict='NOT_TESTABLE_SOURCE_UNAVAILABLE'
    elif sum(x['below_median'] for x in observed) >= 2: verdict='KILL_DISTRIBUTION_WARNING_LANE'
    else: verdict='NOT_FALSIFIED_ADMIT_ONLY_TO_INCREMENTAL_SHADOW_TEST'
    return {'contract':'NFCICREDIT_T1_PRE_TOP_v1','verdict':verdict,'rule':'kill if trailing-3y percentile is below median at T-90 for >=2 of 3 frozen BTC tops','tops':[x.isoformat() for x in TOPS],'episodes':episodes,'authority':'RESEARCH_ONLY_NO_EXECUTION','k17':'DETERMINISTIC_VINTAGE_INPUT_REQUIRED'}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--csv',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    out=run(load(a.csv)); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,sort_keys=True)); return 0

if __name__=='__main__': raise SystemExit(main())
