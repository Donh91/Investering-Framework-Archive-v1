from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def latest_json(root: Path) -> tuple[Path | None, dict[str, Any] | None]:
    files=sorted(root.rglob('*.json'),key=lambda p:p.stat().st_mtime) if root.exists() else []
    for p in reversed(files):
        v=read_json(p)
        if v is not None:
            return p,v
    return None,None


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',type=Path,default=Path('.'))
    ap.add_argument('--json-output',type=Path,required=True)
    ap.add_argument('--md-output',type=Path,required=True)
    args=ap.parse_args(); root=args.repo_root

    cap_path,cap=latest_json(root/'03_DAILY_CAPTURE_LOGS/captures')
    daily_path,daily=latest_json(root/'research/api_agent/outputs/daily')
    weekly_path,weekly=latest_json(root/'research/api_agent/outputs/weekly')
    etf_path,etf=latest_json(root/'research/etf_owner')
    ping_files=list((root/'research/data_ping_bridge/accepted').rglob('*.json')) if (root/'research/data_ping_bridge/accepted').exists() else []

    owners=[]
    cfgi_remaining=None
    if cap:
        for o in cap.get('owners',[]):
            owners.append({'owner_id':o.get('owner_id'),'status':o.get('status','UNKNOWN')})
            if o.get('owner_id')=='cfgi_sentiment':
                for f in o.get('files',[]):
                    s=f.get('summary') or {}
                    if isinstance(s,dict) and s.get('credits_remaining') is not None:
                        cfgi_remaining=s['credits_remaining']

    pass_count=sum(o['status']=='PASS' for o in owners)
    status='GREEN'
    blockers=[]
    if not cap:
        status='RED'; blockers.append('NO_DAILY_CAPTURE')
    elif pass_count < max(1,len(owners)-1):
        status='AMBER'; blockers.append('OWNER_COVERAGE_DEGRADED')
    if not weekly:
        status='AMBER' if status=='GREEN' else status; blockers.append('NO_WEEKLY_API_OUTPUT_YET')

    health={
        'contract':'ARCHITECTURE_HEALTH_DASHBOARD_v1',
        'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'status':status,
        'owners':{'count':len(owners),'pass_count':pass_count,'rows':owners},
        'latest_capture_path':str(cap_path) if cap_path else None,
        'latest_daily_director_path':str(daily_path) if daily_path else None,
        'latest_weekly_calibration_path':str(weekly_path) if weekly_path else None,
        'latest_etf_owner_path':str(etf_path) if etf_path else None,
        'accepted_data_ping_count':len(ping_files),
        'cfgi_credits_remaining':cfgi_remaining,
        'blockers':blockers,
        'authority':{'framework_state_change':False,'portfolio_action':False},
    }
    args.json_output.parent.mkdir(parents=True,exist_ok=True)
    args.json_output.write_text(json.dumps(health,sort_keys=True,separators=(',',':'))+'\n')
    lines=['# Architecture Health',f"Status: **{status}**",f"Generated: {health['generated_at_utc']}",'',f"Owners: {pass_count}/{len(owners)} PASS",f"Accepted DATA PINGs: {len(ping_files)}",f"CFGI credits remaining: {cfgi_remaining if cfgi_remaining is not None else 'UNKNOWN'}",'', '## Blockers']
    lines += [f'- {b}' for b in blockers] or ['- None']
    args.md_output.write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status':status,'blockers':blockers},sort_keys=True))


if __name__=='__main__':
    main()
