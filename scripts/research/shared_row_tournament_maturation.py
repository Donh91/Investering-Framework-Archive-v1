#!/usr/bin/env python3
"""Append-only FNP maturation copier.
Outcome semantics are never invented here. Only already-registered shared-row outcomes are copied after frozen horizons elapse.
"""
from __future__ import annotations
import csv,datetime as dt,json
from pathlib import Path
ROOT=Path('06_RESEARCH_LAB/shared_row_model_tournament_v1'); ROWS=ROOT/'data/PROSPECTIVE_SHARED_ROW_LEDGER.csv'; FNP=ROOT/'14_DIVERGENCE_FNP_LEDGER.csv'
H={'24h':dt.timedelta(hours=24),'72h':dt.timedelta(hours=72),'7d':dt.timedelta(days=7)}
def read(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def parse(x):return dt.datetime.fromisoformat(x.replace('Z','+00:00'))
def main():
    rr={r['event_id']:r for r in read(ROWS)}; dd=read(FNP); now=dt.datetime.now(dt.timezone.utc); changed=0
    for d in dd:
        r=rr.get(d['event_id'])
        if not r: continue
        obs=parse(d['observation_timestamp_utc'])
        for h,delta in H.items():
            matured=f'matured_{h}_utc'; outcome=f'outcome_{h}'; mae=f'mae_{h}'; mfe=f'mfe_{h}'
            if d.get(matured) or now < obs+delta or not str(r.get(outcome,'')).strip(): continue
            d[outcome]=r.get(outcome,''); d[mae]=r.get(mae,''); d[mfe]=r.get(mfe,''); d[matured]=now.replace(microsecond=0).isoformat().replace('+00:00','Z'); changed+=1
    if changed and dd:
        fields=list(dd[0].keys())
        with FNP.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(dd)
    print(json.dumps({'status':'PASS','fields_matured':changed,'divergence_rows':len(dd),'outcome_semantics':'DEFERRED_TO_PREEXISTING_REGISTERED_OUTCOME_OWNER'},sort_keys=True))
if __name__=='__main__': main()
