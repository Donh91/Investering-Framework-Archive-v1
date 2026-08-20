from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

TIMESTAMP_KEYS = ("captured_at_utc","retrieved_at_utc","created_at_utc","generated_at_utc","completed_at_utc","published_at_utc","freeze_utc","snapshot_utc","created_unix")

# Evidence-quality observation window and censor-rate threshold (TASK3 R3-08).
# These signals exist to separate PLUMBING HEALTH from EVIDENCE HEALTH: a job
# that exits zero can still be operationally RED if its evidence is unusable.
EVIDENCE_WINDOW_DAYS = 14
EVIDENCE_CENSOR_RATE_AMBER = 0.60
OUTCOME_CONTRACTS = {"MATURED_OUTCOME_v2","MATURED_OUTCOME_v3"}


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value=json.loads(path.read_text())
        return value if isinstance(value,dict) else None
    except Exception:return None
def parse_dt(value: object) -> datetime | None:
    if isinstance(value,(int,float)):
        try:return datetime.fromtimestamp(value,timezone.utc)
        except Exception:return None
    if not isinstance(value,str):return None
    try:
        dt=datetime.fromisoformat(value.replace('Z','+00:00'))
        return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except Exception:return None
def row_timestamp(value: dict[str,Any]) -> datetime | None:
    for key in TIMESTAMP_KEYS:
        dt=parse_dt(value.get(key))
        if dt:return dt
    for nested_key in ('packet','meta','receipt'):
        nested=value.get(nested_key)
        if isinstance(nested,dict):
            for key in TIMESTAMP_KEYS:
                dt=parse_dt(nested.get(key))
                if dt:return dt
    return None
def latest_json(root: Path):
    rows=[]
    if root.exists():
        for path in root.rglob('*.json'):
            value=read_json(path)
            if value is None:continue
            ts=row_timestamp(value)
            if ts is not None:rows.append((ts,str(path),path,value))
    if not rows:return None,None,None
    ts,_,path,value=max(rows,key=lambda row:(row[0],row[1]));return path,value,ts
def latest_paired_output(root:Path,output_name:str,receipt_name:str):
    rows=[]
    if root.exists():
        for path in root.rglob(output_name):
            output=read_json(path)
            if output is None:continue
            rp=path.with_name(receipt_name);receipt=read_json(rp) if rp.exists() else None;ts=row_timestamp(output) or row_timestamp(receipt or {})
            if ts is not None:rows.append((ts,str(path),path,output,rp if receipt else None))
    if not rows:return None,None,None,None
    ts,_,path,output,rp=max(rows,key=lambda row:(row[0],row[1]));return path,output,ts,rp
def age_hours(now,ts):return None if ts is None else max(0.0,(now-ts).total_seconds()/3600.0)
def find_cfgi_remaining(owner):
    for row in owner.get('files',[]):
        summary=row.get('summary') if isinstance(row,dict) else None
        if not isinstance(summary,dict):continue
        if isinstance(summary.get('credits_remaining'),int):return summary['credits_remaining']
        billing=summary.get('billing')
        if isinstance(billing,dict) and isinstance(billing.get('credits_remaining'),int):return billing['credits_remaining']
    return None

def evidence_health(root: Path, now: datetime) -> dict[str, Any]:
    """Observe whether the accountability loop is producing usable evidence.

    Counts only outcomes adjudicated inside the observation window and only
    forecasts whose declared maturity fell inside the same window, so the signal
    reflects the loop's current behaviour rather than its whole history.
    """
    window_start=now-timedelta(days=EVIDENCE_WINDOW_DAYS)
    matured=censored=0
    outcome_root=root/'research/framework_memory/outcome_memory'
    if outcome_root.exists():
        for path in outcome_root.rglob('*.json'):
            value=read_json(path)
            if not value or value.get('contract') not in OUTCOME_CONTRACTS:continue
            ts=parse_dt(value.get('created_at_utc'))
            if ts is None or ts<window_start or ts>now:continue
            if value.get('status')=='MATURED':matured+=1
            elif value.get('status')=='CENSORED':censored+=1
    due=0
    forecast_root=root/'research/framework_memory/forecast_memory'
    if forecast_root.exists():
        for path in forecast_root.rglob('*.json'):
            value=read_json(path)
            if not value or value.get('contract')!='FROZEN_FORECAST_v1':continue
            ts=parse_dt(value.get('outcome_due_utc'))
            if ts is not None and window_start<=ts<=now:due+=1
    adjudicated=matured+censored
    return {'window_days':EVIDENCE_WINDOW_DAYS,'matured_outcome_count':matured,'censored_outcome_count':censored,'adjudicated_outcome_count':adjudicated,'censor_rate':round(censored/adjudicated,6) if adjudicated else None,'forecasts_due_in_window':due}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path('.'));ap.add_argument('--json-output',type=Path,required=True);ap.add_argument('--md-output',type=Path,required=True);ap.add_argument('--now-utc');args=ap.parse_args();root=args.repo_root;now=parse_dt(args.now_utc) if args.now_utc else datetime.now(timezone.utc);assert now
    cap_path,cap,cap_ts=latest_json(root/'03_DAILY_CAPTURE_LOGS/captures');daily_path,daily,daily_ts,daily_receipt_path=latest_paired_output(root/'research/api_agent/outputs/daily','DAILY_DIRECTOR_OUTPUT.json','DAILY_DIRECTOR_RECEIPT.json');weekly_path,weekly,weekly_ts=latest_json(root/'research/api_agent/outputs/weekly');etf_path,etf,etf_ts=latest_json(root/'research/etf_owner')
    experiment_path=root/'research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json';experiment=read_json(experiment_path);experiment_ts=row_timestamp(experiment or {})
    sync_path=root/'research/experiment_lifecycle/LATEST_EXPERIMENT_RECEIPT_SYNC.json';sync=read_json(sync_path);sync_ts=row_timestamp(sync or {})
    remediation_path=root/'research/remediation/LATEST_REMEDIATION_QUEUE.json';remediation=read_json(remediation_path);remediation_ts=row_timestamp(remediation or {})
    ping_files=list((root/'research/data_ping_bridge/accepted').rglob('*.json')) if (root/'research/data_ping_bridge/accepted').exists() else []
    owners=[];cfgi_remaining=None
    if cap:
        for owner in cap.get('owners',[]):
            if not isinstance(owner,dict):continue
            owners.append({'owner_id':owner.get('owner_id'),'status':owner.get('status','UNKNOWN')})
            if owner.get('owner_id')=='cfgi_sentiment':cfgi_remaining=find_cfgi_remaining(owner)
    pass_count=sum(row['status']=='PASS' for row in owners);blockers=[];severity=0
    def add(code,level):
        nonlocal severity
        if code not in blockers:blockers.append(code)
        severity=max(severity,level)
    ages={'capture':age_hours(now,cap_ts),'daily_director':age_hours(now,daily_ts),'weekly_calibration':age_hours(now,weekly_ts),'etf_owner':age_hours(now,etf_ts),'experiment_registry':age_hours(now,experiment_ts),'experiment_receipt_sync':age_hours(now,sync_ts),'remediation_queue':age_hours(now,remediation_ts)}
    if cap is None:add('NO_DAILY_CAPTURE',2)
    elif ages['capture'] is None or ages['capture']>8:add('DAILY_CAPTURE_STALE',2)
    if owners and pass_count<max(1,len(owners)-1):add('OWNER_COVERAGE_DEGRADED',1)
    if daily is None:add('NO_DAILY_DIRECTOR_OUTPUT',1)
    elif ages['daily_director'] is None or ages['daily_director']>36:add('DAILY_DIRECTOR_STALE',1)
    monday_or_later=(now.weekday()==0 and now.hour>=4) or now.weekday()>0
    if weekly is None:add('NO_WEEKLY_API_OUTPUT_YET',2 if monday_or_later else 1)
    elif ages['weekly_calibration'] is None or ages['weekly_calibration']>9*24:add('WEEKLY_API_OUTPUT_STALE',2)
    if etf is None:add('NO_ETF_OWNER_OUTPUT',1)
    else:
        rows=etf.get('rows',[]) if isinstance(etf,dict) else []
        if any(isinstance(row,dict) and row.get('total_parity') is False for row in rows):add('ETF_TOTAL_PARITY_FAILED',2)
        if etf.get('status') not in {'PASS','COMPLETE'}:add('ETF_OWNER_DEGRADED',1)
        if ages['etf_owner'] is None or ages['etf_owner']>96:add('ETF_OWNER_STALE',1)
    if experiment is None:add('NO_EXPERIMENT_REGISTRY',1)
    elif experiment.get('contract')!='EXPERIMENT_LIFECYCLE_REGISTRY_v1':add('EXPERIMENT_REGISTRY_INVALID',2)
    elif ages['experiment_registry'] is None or ages['experiment_registry']>48:add('EXPERIMENT_REGISTRY_STALE',1)
    if sync is not None and sync.get('status')=='FAIL':add('EXPERIMENT_RECEIPT_SYNC_FAILED',2)
    elif sync is not None and ages['experiment_receipt_sync'] is not None and ages['experiment_receipt_sync']>72:add('EXPERIMENT_RECEIPT_SYNC_STALE',1)
    if remediation is None:add('NO_REMEDIATION_QUEUE_YET',1)
    elif remediation.get('contract')!='REMEDIATION_MATURATION_ENGINE_v1':add('REMEDIATION_QUEUE_INVALID',2)
    elif ages['remediation_queue'] is None or ages['remediation_queue']>36:add('REMEDIATION_QUEUE_STALE',1)
    evidence=evidence_health(root,now)
    # E1 - the accountability loop has stopped producing usable evidence even
    # though forecasts reached maturity in the window. This is the signal that
    # would have caught the 2026-08 censoring incident on its first day.
    if evidence['forecasts_due_in_window']>0 and evidence['matured_outcome_count']==0:add('NO_MATURED_OUTCOMES_14D',2)
    # E2 - outcomes are being adjudicated but overwhelmingly censored.
    if evidence['censor_rate'] is not None:
        if evidence['censor_rate']>=1.0:add('OUTCOME_CENSOR_RATE_HIGH',2)
        elif evidence['censor_rate']>EVIDENCE_CENSOR_RATE_AMBER:add('OUTCOME_CENSOR_RATE_HIGH',1)
    status='RED' if severity>=2 else 'AMBER' if severity==1 else 'GREEN'
    health={'contract':'ARCHITECTURE_HEALTH_DASHBOARD_v2_3','evidence_health':evidence,'generated_at_utc':now.isoformat().replace('+00:00','Z'),'status':status,'freshness_hours':ages,'owners':{'count':len(owners),'pass_count':pass_count,'rows':owners},'latest_capture_path':str(cap_path) if cap_path else None,'latest_daily_director_path':str(daily_path) if daily_path else None,'latest_daily_director_receipt_path':str(daily_receipt_path) if daily_receipt_path else None,'latest_weekly_calibration_path':str(weekly_path) if weekly_path else None,'latest_etf_owner_path':str(etf_path) if etf_path else None,'experiment_lifecycle':{'path':str(experiment_path) if experiment else None,'candidate_count':(experiment or {}).get('candidate_count'),'state_counts':(experiment or {}).get('state_counts',{})},'experiment_receipt_sync':{'path':str(sync_path) if sync else None,'status':(sync or {}).get('status'),'imported':(sync or {}).get('imported'),'hash_mismatches':(sync or {}).get('hash_mismatches')},'remediation':{'path':str(remediation_path) if remediation else None,'summary':(remediation or {}).get('summary',{}),'automatic_code_write':(remediation or {}).get('automatic_code_write',False),'automatic_merge':(remediation or {}).get('automatic_merge',False)},'accepted_data_ping_count':len(ping_files),'cfgi_credits_remaining':cfgi_remaining,'blockers':blockers,'authority':{'framework_state_change':False,'portfolio_action':False}}
    args.json_output.parent.mkdir(parents=True,exist_ok=True);args.json_output.write_text(json.dumps(health,sort_keys=True,separators=(',',':'))+'\n')
    lines=['# Architecture Health',f'Status: **{status}**',f"Generated: {health['generated_at_utc']}",'',f'Owners: {pass_count}/{len(owners)} PASS',f'Accepted DATA PINGs: {len(ping_files)}',f"CFGI credits remaining: {cfgi_remaining if cfgi_remaining is not None else 'UNKNOWN'}",f"Experiment candidates: {(experiment or {}).get('candidate_count','UNKNOWN')}",f"Codex-ready remediation tasks: {((remediation or {}).get('summary') or {}).get('codex_ready','UNKNOWN')}",'','## Freshness hours']+[f"- {k}: {v if v is not None else 'UNKNOWN'}" for k,v in ages.items()]+['',f"## Evidence health (last {evidence['window_days']}d)",f"- Forecasts due in window: {evidence['forecasts_due_in_window']}",f"- Matured outcomes: {evidence['matured_outcome_count']}",f"- Censored outcomes: {evidence['censored_outcome_count']}",f"- Censor rate: {evidence['censor_rate'] if evidence['censor_rate'] is not None else 'UNKNOWN'}",'','## Blockers']+([f'- {x}' for x in blockers] or ['- None'])
    args.md_output.write_text('\n'.join(lines)+'\n');print(json.dumps({'status':status,'blockers':blockers},sort_keys=True))
if __name__=='__main__':main()
