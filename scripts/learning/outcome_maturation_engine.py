from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read(path: Path) -> dict[str, Any]: return json.loads(path.read_text())
def canon(v: Any) -> bytes: return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(v: Any) -> str: return hashlib.sha256(canon(v)).hexdigest()

def at_path(value: Any, path: str) -> Any:
    cur=value
    for part in path.split('.'):
        if isinstance(cur,dict): cur=cur.get(part)
        else: return None
    return cur

def parse_dt(s: str) -> datetime: return datetime.fromisoformat(s.replace('Z','+00:00'))

def classify(direction: str, start: float, end: float, threshold: float) -> str:
    move=(end/start-1.0)*100 if start else 0.0
    hit=(direction=='UP' and move>=threshold) or (direction=='DOWN' and move<=-threshold) or (direction=='RANGE' and abs(move)<threshold)
    return 'HIT' if hit else 'MISS'

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--forecast-root',type=Path,required=True); ap.add_argument('--evidence-root',type=Path,required=True); ap.add_argument('--output-root',type=Path,required=True); ap.add_argument('--now-utc')
    args=ap.parse_args(); now=parse_dt(args.now_utc) if args.now_utc else datetime.now(timezone.utc)
    evidence=[]
    for p in args.evidence_root.rglob('*.json') if args.evidence_root.exists() else []:
        try:
            v=read(p); ts=v.get('captured_at_utc') or v.get('freeze_utc') or v.get('created_at_utc')
            if ts: evidence.append((parse_dt(ts),p,v))
        except Exception: continue
    evidence.sort(key=lambda x:x[0])
    matured=0; pending=0; errors=[]
    for p in args.forecast_root.rglob('*.json') if args.forecast_root.exists() else []:
        try:
            f=read(p)
            if f.get('contract')!='FROZEN_FORECAST_v1': continue
            fid=f['forecast_id']; frozen=parse_dt(f['frozen_at_utc']); due=parse_dt(f['outcome_due_utc'])
            if now<due: pending+=1; continue
            dest=args.output_root/f'{fid}.json'
            if dest.exists(): continue
            candidates=[x for x in evidence if x[0]>=due]
            if not candidates:
                pending+=1; continue
            _,epath,ev=candidates[0]
            metric=f['metric_path']; end=at_path(ev,metric); start=f.get('start_value')
            if not isinstance(start,(int,float)) or not isinstance(end,(int,float)):
                outcome={'contract':'MATURED_OUTCOME_v1','forecast_id':fid,'status':'CENSORED','reason':'METRIC_UNAVAILABLE','forecast_sha256':sha(f),'evidence_path':str(epath),'created_at_utc':now.isoformat().replace('+00:00','Z')}
            else:
                outcome={'contract':'MATURED_OUTCOME_v1','forecast_id':fid,'status':'MATURED','result':classify(f['direction'],float(start),float(end),float(f.get('threshold_pct',0.0))),'start_value':start,'end_value':end,'return_pct':round((end/start-1)*100,8) if start else None,'forecast_sha256':sha(f),'evidence_path':str(epath),'evidence_sha256':sha(ev),'created_at_utc':now.isoformat().replace('+00:00','Z'),'authority':{'model_weight_change':False,'portfolio_action':False}}
            dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(canon(outcome)); matured+=1
        except Exception as e: errors.append({'path':str(p),'error':str(e)})
    print(json.dumps({'matured':matured,'pending':pending,'errors':errors},sort_keys=True))
    if errors: raise SystemExit(2)

if __name__=='__main__': main()
