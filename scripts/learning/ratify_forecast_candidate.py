from __future__ import annotations
import argparse,hashlib,json
from datetime import datetime,timedelta,timezone
from pathlib import Path


def canon(v):return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def load(p):return json.loads(p.read_text())
def at_path(v,path):
    cur=v
    for part in path.split('.'):
        if not isinstance(cur,dict):return None
        cur=cur.get(part)
    return cur

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--ratification',type=Path,required=True);ap.add_argument('--baseline-evidence',type=Path,required=True);ap.add_argument('--output-root',type=Path,required=True);a=ap.parse_args()
    c=load(a.candidate);r=load(a.ratification);b=load(a.baseline_evidence)
    if c.get('contract')!='FORECAST_CANDIDATE_v1' or c.get('ratification_status')!='PENDING':raise SystemExit('CANDIDATE_NOT_PENDING')
    if r.get('contract')!='FORECAST_RATIFICATION_PACKET_v1' or r.get('decision')!='RATIFY':raise SystemExit('RATIFICATION_REQUIRED')
    if r.get('candidate_id')!=c.get('candidate_id'):raise SystemExit('CANDIDATE_ID_MISMATCH')
    if r.get('authority') not in {'CHATGPT_FRAMEWORK_OWNER','EXPLICIT_USER_MANDATE'}:raise SystemExit('INVALID_RATIFICATION_AUTHORITY')
    candidate=c['candidate'];metric=candidate['metric_path'];start=at_path(b,metric)
    if not isinstance(start,(int,float)):raise SystemExit('BASELINE_METRIC_UNAVAILABLE')
    frozen_at=datetime.now(timezone.utc);horizon=int(candidate['horizon_days']);direction=candidate['direction']
    frozen={'contract':'FROZEN_FORECAST_v1','forecast_id':'ff_'+hashlib.sha256(canon({'candidate':c['candidate_id'],'ratification':r,'baseline':hashlib.sha256(canon(b)).hexdigest()})).hexdigest()[:24],'candidate_id':c['candidate_id'],'frozen_at_utc':frozen_at.isoformat().replace('+00:00','Z'),'outcome_due_utc':(frozen_at+timedelta(days=horizon)).isoformat().replace('+00:00','Z'),'horizon_days':horizon,'metric_path':metric,'direction':direction,'start_value':start,'threshold_pct':candidate.get('threshold') if direction in {'UP','DOWN'} else None,'range_lower_pct':candidate.get('range_low') if direction=='RANGE' else None,'range_upper_pct':candidate.get('range_high') if direction=='RANGE' else None,'rationale':candidate.get('rationale'),'model':c.get('model'),'task':c.get('task'),'prompt_sha256':c.get('prompt_sha256'),'context_sha256':c.get('context_sha256'),'source_output_sha256':c.get('source_output_sha256'),'candidate_sha256':hashlib.sha256(canon(c)).hexdigest(),'ratification_sha256':hashlib.sha256(canon(r)).hexdigest(),'baseline_evidence_path':str(a.baseline_evidence),'baseline_evidence_sha256':hashlib.sha256(canon(b)).hexdigest(),'authority':{'portfolio_action':False,'model_weight_change':False,'canonical_promotion':False}}
    out=a.output_root/f"{frozen['forecast_id']}.json";out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(canon(frozen));print(json.dumps({'status':'FROZEN','forecast_id':frozen['forecast_id'],'path':str(out)},sort_keys=True))
if __name__=='__main__':main()
