from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED={'snapshot_id','freeze_utc','source_health','market_metrics','framework_interpretation','acceptance_status'}


def canonical(v: Any) -> bytes:
    return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()


def sha(v: Any) -> str:
    return hashlib.sha256(canonical(v)).hexdigest()


def validate(v: dict[str, Any]) -> None:
    if v.get('contract')!='ACCEPTED_DATA_PING_PACKET_v1':
        raise ValueError('wrong_contract')
    missing=sorted(REQUIRED-set(v))
    if missing:
        raise ValueError('missing:'+','.join(missing))
    if v['acceptance_status']!='ACCEPTED':
        raise ValueError('not_accepted')
    if not isinstance(v['source_health'],dict) or not isinstance(v['market_metrics'],dict):
        raise ValueError('invalid_owner_payload')
    forbidden={'portfolio_action','model_weight_change','canonical_promotion'}
    auth=v.get('authority',{})
    if any(auth.get(k) is True for k in forbidden):
        raise ValueError('forbidden_authority')


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--inbox',type=Path,required=True)
    ap.add_argument('--accepted-root',type=Path,required=True)
    ap.add_argument('--rejected-root',type=Path,required=True)
    args=ap.parse_args()
    accepted=rejected=0
    for p in sorted(args.inbox.glob('*.json')):
        try:
            v=json.loads(p.read_text())
            validate(v)
            freeze=datetime.fromisoformat(v['freeze_utc'].replace('Z','+00:00'))
            iso=freeze.isocalendar()
            dest=args.accepted_root/str(iso.year)/f'W{iso.week:02d}'/f"{v['snapshot_id']}.json"
            v['bridge_receipt']={'ingested_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'source_path':str(p),'packet_sha256':sha(v)}
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists() and json.loads(dest.read_text()).get('bridge_receipt',{}).get('packet_sha256')!=v['bridge_receipt']['packet_sha256']:
                raise ValueError('snapshot_id_collision')
            dest.write_bytes(canonical(v)); accepted+=1
        except Exception as e:
            args.rejected_root.mkdir(parents=True,exist_ok=True)
            (args.rejected_root/f'{p.stem}.error.json').write_text(json.dumps({'source':str(p),'error':str(e)},sort_keys=True)+'\n')
            rejected+=1
    print(json.dumps({'accepted':accepted,'rejected':rejected},sort_keys=True))
    if rejected:
        raise SystemExit(2)


if __name__=='__main__':
    main()
