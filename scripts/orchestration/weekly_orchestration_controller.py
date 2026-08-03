from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]: return json.loads(path.read_text())
def digest(value: Any) -> str: return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()).hexdigest()
def parse_ts(raw: Any) -> datetime: return datetime.fromisoformat(str(raw).replace('Z','+00:00')).astimezone(timezone.utc)

def expected_completed_week(now: datetime):
    monday=(now-timedelta(days=now.weekday())).replace(hour=0,minute=0,second=0,microsecond=0)
    start=monday-timedelta(days=7); iso=start.isocalendar()
    return iso.year,iso.week,start,monday

def lane(row:dict[str,Any])->str:
    cls=str(row.get('authority_class') or row.get('packet_class') or row.get('scope') or '').upper()
    if cls in {'CANONICAL','CANONICAL_ACCEPTED'}: return 'canonical_data_pings'
    if cls in {'BOUNDED','BOUNDED_DECISION_BEARING','DECISION_BEARING'}: return 'bounded_decision_bearing_pings'
    if cls in {'RUNTIME_LIMITED','RUNTIME_LIMITED_SUPPLEMENT'}: return 'runtime_limited_supplements'
    return 'qa_and_research_only'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture-root',type=Path,required=True);ap.add_argument('--accepted-data-ping-root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--now-utc');a=ap.parse_args()
    now=parse_ts(a.now_utc) if a.now_utc else datetime.now(timezone.utc);year,week,start,end=expected_completed_week(now)
    close_pointer=a.capture_root/'weekly_close/LATEST_WEEKLY_MARKET_CLOSE.json';weekly_pointer=a.capture_root/'weekly/LATEST_WEEKLY_CALIBRATION.json'
    if not close_pointer.exists():raise SystemExit('FINAL_WEEK_CLOSE_MISSING')
    if not weekly_pointer.exists():raise SystemExit('WEEKLY_CAPTURE_BRIDGE_MISSING')
    pointer=load(close_pointer)
    if pointer.get('contract')!='WEEKLY_MARKET_CLOSE_POINTER_v2':raise SystemExit('WEEK_CLOSE_POINTER_CONTRACT_INVALID')
    if pointer.get('final') is not True or pointer.get('close_mode')!='FINAL_COMPLETED_ISO_WEEK' or pointer.get('completeness')!='COMPLETE':raise SystemExit('WEEK_CLOSE_NOT_FINAL')
    package_path=a.capture_root/str(pointer.get('path',''))
    if not package_path.exists():raise SystemExit('WEEK_CLOSE_PACKAGE_MISSING')
    package=load(package_path);package_hash=digest(package)
    if package_hash!=pointer.get('sha256'):raise SystemExit('WEEK_CLOSE_HASH_MISMATCH')
    if package.get('final') is not True or package.get('close_mode')!='FINAL_COMPLETED_ISO_WEEK' or package.get('completeness')!='COMPLETE':raise SystemExit('WEEK_CLOSE_PACKAGE_NOT_FINAL')
    expected_end=end.isoformat().replace('+00:00','Z')
    for source in (pointer,package):
        if int(source.get('iso_year',-1))!=year or int(source.get('iso_week',-1))!=week:raise SystemExit('WEEK_CLOSE_WRONG_ISO_WEEK')
        if source.get('window_end_utc')!=expected_end:raise SystemExit('WEEK_CLOSE_WRONG_WINDOW_END')
    weekly=load(weekly_pointer)
    if weekly.get('iso_year') is not None and int(weekly['iso_year'])!=year:raise SystemExit('WEEKLY_BRIDGE_WRONG_ISO_YEAR')
    if weekly.get('iso_week') is not None and int(weekly['iso_week'])!=week:raise SystemExit('WEEKLY_BRIDGE_WRONG_ISO_WEEK')

    lanes={k:[] for k in ('canonical_data_pings','bounded_decision_bearing_pings','runtime_limited_supplements','qa_and_research_only')};errors=[];seen=set()
    if a.accepted_data_ping_root.exists():
        for p in sorted(a.accepted_data_ping_root.rglob('*.json')):
            try:row=load(p)
            except Exception as exc:errors.append({'path':str(p),'error':type(exc).__name__});continue
            if row.get('contract')!='ACCEPTED_DATA_PING_PACKET_v1':continue
            try:ts=parse_ts(row.get('freeze_utc'))
            except Exception:errors.append({'path':str(p),'error':'INVALID_FREEZE_UTC'});continue
            if not (start<=ts<end):continue
            key=(row.get('run_id'),row.get('snapshot_id'))
            if key in seen:continue
            seen.add(key);bucket=lane(row)
            lanes[bucket].append({'path':str(p),'run_id':row.get('run_id'),'snapshot_id':row.get('snapshot_id'),'freeze_utc':row.get('freeze_utc'),'sha256':digest(row),'authority_class':bucket})

    freeze={'contract':'WEEKLY_ORCHESTRATION_FREEZE_v3','created_at_utc':now.isoformat().replace('+00:00','Z'),'status':'READY','iso_year':year,'iso_week':week,'window_start_utc':start.isoformat().replace('+00:00','Z'),'window_end_utc':expected_end,'final_week_close':{'pointer_path':str(close_pointer),'pointer_sha256':digest(pointer),'package_path':str(package_path),'package_sha256':package_hash},'weekly_capture_bridge':{'path':str(weekly_pointer),'sha256':digest(weekly)},'data_ping_lanes':lanes,'data_ping_parse_errors':errors,'late_evidence_policy':'Evidence at or after window_end_utc is excluded and belongs in LATE_EVIDENCE_LEDGER.','handoff_targets':['RAW_WEEKLY_CALIBRATION','CYCLE_NAVIGATOR','MASTER_MONDAY_PREP','FORECAST_LEDGER'],'authority':{'canonical_promotion':False,'model_weight_change':False,'portfolio_action':False}}
    freeze['freeze_sha256']=digest(freeze);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(freeze,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps({'status':'READY','iso_year':year,'iso_week':week,'lane_counts':{k:len(v) for k,v in lanes.items()},'freeze_sha256':freeze['freeze_sha256']},sort_keys=True))
if __name__=='__main__':main()
