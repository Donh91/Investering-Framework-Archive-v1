#!/usr/bin/env python3
"""Preregistered T-1 falsification for NFCICREDIT.

Input is a deterministic ALFRED/FRED-style CSV containing observation_date,
realtime_start and value. No network or LLM extraction occurs here.
"""
import argparse,csv,json,math
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
            rs=r.get('realtime_start') or r.get('REALTIME_START')
            raw=r.get('value') or r.get('NFCICREDIT')
            if not ds or not rs or raw in (None,'','.'):
                continue
            rows.append((date.fromisoformat(ds),date.fromisoformat(rs),float(raw)))
    return sorted(rows)


def latest_known(rows, asof, target):
    eligible=[x for x in rows if x[0] <= target and x[1] <= asof]
    return max(eligible,key=lambda x:(x[0],x[1])) if eligible else None


def percentile(history,value):
    if not history: return None
    # deterministic empirical CDF, ties count at or below.
    return 100.0*sum(x <= value for x in history)/len(history)


def run(rows):
    episodes=[]
    for top in TOPS:
        asof=top-timedelta(days=LOOKBACK_DAYS)
        obs=latest_known(rows,asof,asof)
        start=asof-timedelta(days=365*PERCENTILE_YEARS)
        hist=[]
        for d,rt,v in rows:
            if start <= d <= asof and rt <= asof:
                hist.append(v)
        if obs is None or len(hist) < 100:
            episodes.append({'top':top.isoformat(),'asof':asof.isoformat(),'status':'NOT_PRESENT'})
            continue
        pct=percentile(hist,obs[2])
        episodes.append({'top':top.isoformat(),'asof':asof.isoformat(),'status':'OBSERVED','observation_date':obs[0].isoformat(),'realtime_start':obs[1].isoformat(),'value':obs[2],'trailing_3y_percentile':pct,'below_median':pct < 50.0})
    observed=[x for x in episodes if x['status']=='OBSERVED']
    if len(observed) != len(TOPS):
        verdict='NOT_TESTABLE_SOURCE_UNAVAILABLE'
    elif sum(x['below_median'] for x in observed) >= 2:
        verdict='KILL_DISTRIBUTION_WARNING_LANE'
    else:
        verdict='NOT_FALSIFIED_ADMIT_ONLY_TO_INCREMENTAL_SHADOW_TEST'
    return {'contract':'NFCICREDIT_T1_PRE_TOP_v1','verdict':verdict,'rule':'kill if trailing-3y percentile is below median at T-90 for >=2 of 3 frozen BTC tops','tops':[x.isoformat() for x in TOPS],'episodes':episodes,'authority':'RESEARCH_ONLY_NO_EXECUTION','k17':'DETERMINISTIC_INPUT_REQUIRED'}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--csv',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    out=run(load(a.csv)); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,sort_keys=True)); return 0

if __name__=='__main__': raise SystemExit(main())
