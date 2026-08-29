from __future__ import annotations
import argparse,csv,json
from pathlib import Path

UNIT_CONTRACT_VERSION='FORECAST_TARGET_UNITS_v2'
LINEAGE_CONTRACT='MODEL_CALIBRATION_DATA_PING_LINEAGE_v1'

def load(p):
    try:return json.loads(p.read_text())
    except Exception:return None

def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def legacy_unit_ambiguous(f):
    if f.get('contract')!='FROZEN_FORECAST_v1':return False
    if f.get('unit_contract_version')==UNIT_CONTRACT_VERSION:return False
    if f.get('source_candidate_id') and f.get('direction')=='RANGE':return False
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--forecast-root',type=Path,required=True);ap.add_argument('--outcome-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--lineage-output',type=Path);a=ap.parse_args()
    forecasts={}
    for p in a.forecast_root.rglob('*.json') if a.forecast_root.exists() else []:
        v=load(p)
        if v and v.get('contract')=='FROZEN_FORECAST_v1':forecasts[v.get('forecast_id')]=v
    rows=[];lineage_rows=[];quarantined=set()
    for p in a.outcome_root.rglob('*.json') if a.outcome_root.exists() else []:
        o=load(p)
        if not o or o.get('contract') not in {'MATURED_OUTCOME_v2','MATURED_OUTCOME_v3'}:continue
        f=forecasts.get(o.get('forecast_id'),{})
        if f and legacy_unit_ambiguous(f):
            quarantined.add(o.get('forecast_id'));continue
        rows.append({'scored_at_utc':o.get('created_at_utc'),'model':f.get('model'),'task':f.get('task'),'prompt_sha256':f.get('prompt_sha256'),'forecast_id':o.get('forecast_id'),'metric_path':f.get('metric_path'),'horizon_days':f.get('horizon_days'),'outcome':o.get('status'),'result':o.get('result'),'hit':1 if o.get('result')=='HIT' else (0 if o.get('result')=='MISS' else ''),'return_pct':o.get('return_pct'),'forecast_sha256':o.get('forecast_sha256'),'evidence_sha256':o.get('evidence_sha256')})
        lineage=f.get('data_ping_lineage') if isinstance(f.get('data_ping_lineage'),dict) else None
        if lineage:
            lineage_rows.append({'contract':LINEAGE_CONTRACT,'scored_at_utc':o.get('created_at_utc'),'forecast_id':o.get('forecast_id'),'forecast_sha256':o.get('forecast_sha256'),'accepted_packet_sha256':lineage.get('accepted_packet_sha256'),'accepted_packet_identity':lineage.get('accepted_packet_identity'),'accepted_packet_path':lineage.get('accepted_packet_path'),'action_compass_receipt_id':lineage.get('action_compass_receipt_id'),'action_compass_receipt_sha256':lineage.get('action_compass_receipt_sha256'),'canonical_repository':lineage.get('canonical_repository'),'canonical_commit_sha':lineage.get('canonical_commit_sha'),'owner_contract':lineage.get('owner_contract'),'portfolio_execution':False})
    rows.sort(key=lambda r:(str(r['scored_at_utc']),str(r['forecast_id'])))
    lineage_rows.sort(key=lambda r:(str(r['scored_at_utc']),str(r['forecast_id'])))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fields=['scored_at_utc','model','task','prompt_sha256','forecast_id','metric_path','horizon_days','outcome','result','hit','return_pct','forecast_sha256','evidence_sha256']
    with a.output.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    lineage_output=a.lineage_output or a.output.with_name(a.output.stem+'_DATA_PING_LINEAGE.jsonl')
    if lineage_rows:
        lineage_output.parent.mkdir(parents=True,exist_ok=True)
        lineage_output.write_text(''.join(canon(row)+'\n' for row in lineage_rows))
    elif lineage_output.exists():
        lineage_output.unlink()
    # A censored outcome is a recorded outcome, not a scored one. Counting it as
    # scored made an empty ledger indistinguishable from a healthy one and let a
    # 100% censoring rate report status PASS (TASK3 R3-07, R3-17 item 7).
    scored_count=sum(1 for r in rows if r['outcome']=='MATURED')
    censored_count=sum(1 for r in rows if r['outcome']=='CENSORED')
    print(json.dumps({'status':'PASS','scored_count':scored_count,'censored_count':censored_count,'ledger_row_count':len(rows),'data_ping_lineage_row_count':len(lineage_rows),'data_ping_lineage_output':str(lineage_output) if lineage_rows else None,'quarantined_legacy_unit_outcome_count':len(quarantined),'candidate_count':sum(1 for _ in (a.forecast_root.parent/'PENDING').rglob('*.json')) if (a.forecast_root.parent/'PENDING').exists() else 0,'frozen_count':len(forecasts)},sort_keys=True))
if __name__=='__main__':main()
