#!/usr/bin/env python3
import argparse,csv,json
from datetime import date,timedelta
from pathlib import Path
TOPS=['2013-11-30','2017-12-17','2021-11-10']
def load(p):
 out=[]
 for r in csv.DictReader(p.open()):
  d=r.get('DATE') or r.get('observation_date'); v=r.get('BAMLH0A0HYM2')
  if d and v not in (None,'','.'): out.append((date.fromisoformat(d),float(v)))
 return out
def nearest(rows,target): return min(rows,key=lambda x:abs((x[0]-target).days)) if rows else None
def run(rows):
 res=[]
 for s in TOPS:
  t=date.fromisoformat(s); a=nearest(rows,t-timedelta(days=90)); b=nearest(rows,t)
  if not a or not b: continue
  res.append({'top':s,'t_minus_90':a[1],'top_value':b[1],'change':b[1]-a[1],'warned':b[1]>a[1]})
 status='KILL_DISTRIBUTION_WARNING' if len(res)>=3 and sum(x['warned'] for x in res)<=1 else 'NOT_FALSIFIED'
 return {'contract':'HY_OAS_PRE_TOP_T1_v1','status':status,'episodes':res,'authority':'RESEARCH_ONLY_NO_EXECUTION'}
def main():
 a=argparse.ArgumentParser();a.add_argument('--csv',type=Path,required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args(); d=run(load(x.csv)); x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(d));return 0
if __name__=='__main__':raise SystemExit(main())
