from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def digest(value: Any) -> str:
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
    return hashlib.sha256(raw).hexdigest()


def newest(paths: list[Path]) -> Path | None:
    valid=[p for p in paths if p.exists()]
    return max(valid,key=lambda p:p.stat().st_mtime) if valid else None


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--capture-root',type=Path,required=True)
    ap.add_argument('--accepted-data-ping-root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()

    close_pointer=args.capture_root/'weekly_close'/'LATEST_WEEKLY_MARKET_CLOSE.json'
    weekly_pointer=args.capture_root/'weekly'/'LATEST_WEEKLY_CALIBRATION.json'
    if not close_pointer.exists():
        raise SystemExit('FINAL_WEEK_CLOSE_MISSING')
    if not weekly_pointer.exists():
        raise SystemExit('WEEKLY_CAPTURE_BRIDGE_MISSING')

    close=load(close_pointer)
    weekly=load(weekly_pointer)
    close_mode=str(close.get('close_mode') or close.get('package_mode') or '').upper()
    is_final=close.get('final') is True or 'FINAL' in close_mode or close.get('completeness')=='COMPLETE'
    if not is_final:
        raise SystemExit('WEEK_CLOSE_NOT_FINAL')

    accepted=[]
    if args.accepted_data_ping_root.exists():
        for p in sorted(args.accepted_data_ping_root.rglob('*.json')):
            try:
                row=load(p)
            except Exception:
                continue
            if row.get('contract')=='ACCEPTED_DATA_PING_PACKET_v1' and row.get('acceptance_status')=='ACCEPTED':
                accepted.append({'path':str(p),'snapshot_id':row.get('snapshot_id'),'freeze_utc':row.get('freeze_utc'),'sha256':digest(row)})

    freeze={
        'contract':'WEEKLY_ORCHESTRATION_FREEZE_v1',
        'created_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'status':'READY',
        'final_week_close':{'path':str(close_pointer),'sha256':digest(close)},
        'weekly_capture_bridge':{'path':str(weekly_pointer),'sha256':digest(weekly)},
        'accepted_data_pings':accepted,
        'handoff_targets':['RAW_WEEKLY_CALIBRATION','CYCLE_NAVIGATOR','MASTER_MONDAY_PREP','FORECAST_LEDGER'],
        'authority':{'canonical_promotion':False,'model_weight_change':False,'portfolio_action':False},
    }
    freeze['freeze_sha256']=digest(freeze)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(freeze,sort_keys=True,separators=(',',':'))+'\n')
    print(json.dumps({'status':'READY','accepted_data_pings':len(accepted),'freeze_sha256':freeze['freeze_sha256']},sort_keys=True))


if __name__=='__main__':
    main()
