#!/usr/bin/env python3
import argparse,json,csv
from datetime import date,timedelta
from pathlib import Path
def load_btc(p):
 rows=[]
 for r in csv.DictReader(p.open()):
  d=r.get('date') or r.get('Date'); v=r.get('PriceUSD') or r.get('close') or r.get('Close')
  if d and v not in (None,''): rows.append((date.fromisoformat(d[:10]),float(v)))
 return rows
def main():
 a=argparse.ArgumentParser();a.add_argument('--owner-revision',type=Path,required=True);a.add_argument('--btc-csv',type=Path,required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args(); d=json.loads(x.owner_revision.read_text()); btc=load_btc(x.btc_csv); events=[]
 for anchor,bars in d['settled_2m'].items():
  for b in bars:
   if b['regime_state'] in ('TURNING_POSITIVE','TURNING_NEGATIVE'):
    knowledge=date.fromisoformat(b['bar_end_period']+'-01')+timedelta(days=32); knowledge=knowledge.replace(day=1)
    for shift,label in [(0,'REAL'),(91,'PLACEBO_91D')]:
     k=knowledge+timedelta(days=shift); future=[r for r in btc if r[0]>=k][:366]
     if len(future)<91: continue
     p0=future[0][1]; returns={str(h):next((p/p0-1 for dd,p in future if dd>=k+timedelta(days=h)),None) for h in (90,180,365)}
     events.append({'anchor':anchor,'state':b['regime_state'],'source_bar_end_period':b['bar_end_period'],'earliest_knowledge_date':knowledge.isoformat(),'event_date':k.isoformat(),'control':label,'returns':returns})
 out={'contract':'COPPER_GOLD_SLOW_CYCLE_EVENT_STUDY_v1','events':events,'small_n_warning':True,'authority':'RESEARCH_ONLY_NO_EXECUTION'};x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'events':len(events)}));return 0
if __name__=='__main__':raise SystemExit(main())
