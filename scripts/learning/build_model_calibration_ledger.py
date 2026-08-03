from __future__ import annotations
import argparse,csv,json
from pathlib import Path

def load(p):
    try:return json.loads(p.read_text())
    except Exception:return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--forecast-root',type=Path,required=True);ap.add_argument('--outcome-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    forecasts={}
    for p in a.forecast_root.rglob('*.json') if a.forecast_root.exists() else []:
        v=load(p)
        if v and v.get('contract')=='FROZEN_FORECAST_v1':forecasts[v.get('forecast_id')]=v
    rows=[]
    for p in a.outcome_root.rglob('*.json') if a.outcome_root.exists() else []:
        o=load(p)
        if not o or o.get('contract')!='MATURED_OUTCOME_v2':continue
        f=forecasts.get(o.get('forecast_id'),{})
        rows.append({'scored_at_utc':o.get('created_at_utc'),'model':f.get('model'),'task':f.get('task'),'prompt_sha256':f.get('prompt_sha256'),'forecast_id':o.get('forecast_id'),'metric_path':f.get('metric_path'),'horizon_days':f.get('horizon_days'),'outcome':o.get('status'),'result':o.get('result'),'hit':1 if o.get('result')=='HIT' else (0 if o.get('result')=='MISS' else ''),'return_pct':o.get('return_pct'),'forecast_sha256':o.get('forecast_sha256'),'evidence_sha256':o.get('evidence_sha256')})
    rows.sort(key=lambda r:(str(r['scored_at_utc']),str(r['forecast_id'])))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fields=['scored_at_utc','model','task','prompt_sha256','forecast_id','metric_path','horizon_days','outcome','result','hit','return_pct','forecast_sha256','evidence_sha256']
    with a.output.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print(json.dumps({'status':'PASS','scored_count':len(rows),'candidate_count':sum(1 for _ in (a.forecast_root.parent/'PENDING').rglob('*.json')) if (a.forecast_root.parent/'PENDING').exists() else 0,'frozen_count':len(forecasts)},sort_keys=True))
if __name__=='__main__':main()
