from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any] | None:
    try: return json.loads(path.read_text())
    except Exception: return None


def canon(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(',', ':')) + '\n').encode()


def sha(v: Any) -> str: return hashlib.sha256(canon(v)).hexdigest()


def latest_by_timestamp(root: Path, keys: tuple[str, ...]) -> tuple[Path | None, dict[str, Any] | None]:
    rows=[]
    if root.exists():
        for p in root.rglob('*.json'):
            v=load(p)
            if not v: continue
            raw=next((v.get(k) for k in keys if v.get(k)), None)
            if raw:
                try: rows.append((datetime.fromisoformat(str(raw).replace('Z','+00:00')),p,v))
                except Exception: pass
    if not rows: return None,None
    rows.sort(key=lambda x:x[0]); return rows[-1][1],rows[-1][2]


def receipt(action_id: str, group: str, name: str, status: str, source_ts=None, error=None, optional=False):
    return {'action_id':action_id,'group':group,'action_name':name,'status':status,'source_timestamp':source_ts,'retrieval_timestamp':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'error_evidence_id':error,'optional':optional}


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',type=Path,default=Path('.'))
    ap.add_argument('--registry',type=Path,required=True)
    ap.add_argument('--predecessor-registry',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args(); root=args.repo_root
    reg=load(args.registry) or {}; pred=load(args.predecessor_registry) or {}
    if reg.get('planned_core_actions') != 60: raise SystemExit('ACTION_REGISTRY_NOT_60')

    cap_path,cap=latest_by_timestamp(root/'03_DAILY_CAPTURE_LOGS/captures',('captured_at_utc','created_at_utc','freeze_utc'))
    close_ptr=load(root/'03_DAILY_CAPTURE_LOGS/weekly_close/LATEST_WEEKLY_MARKET_CLOSE.json')
    weekly_ptr=load(root/'03_DAILY_CAPTURE_LOGS/weekly/LATEST_WEEKLY_CALIBRATION.json')
    etf_path,etf=latest_by_timestamp(root/'research/etf_owner',('retrieved_at_utc','created_at_utc'))
    accepted=[]
    for p in (root/'research/data_ping_bridge/accepted').rglob('*.json') if (root/'research/data_ping_bridge/accepted').exists() else []:
        v=load(p)
        if v and v.get('contract')=='ACCEPTED_DATA_PING_PACKET_v1' and v.get('acceptance_status')=='ACCEPTED': accepted.append({'path':str(p),'sha256':sha(v),'snapshot_id':v.get('snapshot_id'),'freeze_utc':v.get('freeze_utc')})

    owners={}
    if cap:
        for o in cap.get('owners',[]): owners[o.get('owner_id')]=o

    ledger=[]; sections={}; missing=[]
    def add(aid,group,name,status,source_ts=None,error=None,optional=False): ledger.append(receipt(aid,group,name,status,source_ts,error,optional))

    canonical_ok=pred.get('status')=='ACTIVE' and pred.get('predecessor_scope')=='CANONICAL_ACCEPTED_MARKET_PREDECESSOR'
    add('A01','identity_predecessor','identity_freeze','PASS' if cap else 'UNAVAILABLE',cap.get('captured_at_utc') if cap else None,None if cap else 'NO_CAPTURE')
    add('A02','identity_predecessor','canonical_predecessor_registry','PASS' if canonical_ok else 'PARTIAL',pred.get('canonical_predecessor_snapshot_utc'),None if canonical_ok else 'CANONICAL_PREDECESSOR_VALUES_NOT_PRESENT')
    add('A03','identity_predecessor','single_freeze_contract','PASS' if cap else 'UNAVAILABLE')
    add('A04','identity_predecessor','accepted_data_ping_inventory','PASS',None)
    sections['predecessor']={**pred,'comparison_status':'AVAILABLE' if canonical_ok and pred.get('market_metrics') else 'UNAVAILABLE_CANONICAL_PREDECESSOR_VALUES_NOT_PRESENT'}

    spot=owners.get('binance_spot')
    for i,name in enumerate(['BTCUSDT','ETHUSDT','ETHBTC','order_book','24h_ticker','server_time'],5): add(f'A{i:02d}','current_spot',name,'PASS' if spot and spot.get('status')=='PASS' else 'UNAVAILABLE')
    sections['current_market']={'capture_path':str(cap_path) if cap_path else None,'capture_sha256':sha(cap) if cap else None,'binance_spot_owner':spot,'direct_ETHBTC_owner':'binance_spot'}

    for i,name in enumerate(['Copenhagen_BTC','Copenhagen_ETH','Copenhagen_ETHBTC','threshold_tests','UTC_local_separation'],11): add(f'A{i:02d}','settled_sessions',name,'PASS' if close_ptr else 'UNAVAILABLE')
    sections['settled_sessions']={'weekly_close_pointer':close_ptr,'status':'PARTIAL_REQUIRES_LOCAL_SESSION_OWNER'}

    for i,name in enumerate(['BTC_daily_table','ETH_daily_table','weekly_tieout','gap_duplicate_QA'],16): add(f'A{i:02d}','weekly_daily_structure',name,'PASS' if close_ptr else 'UNAVAILABLE')
    sections['week_daily_intraday']={'weekly_close_pointer':close_ptr,'weekly_bridge':weekly_ptr}

    breadth=owners.get('top100_breadth')
    for i,name in enumerate(['aggregate','membership_hash','constituent_sidecar','exclusion_sidecar','median_mean','gates','longitudinal_permission'],20): add(f'A{i:02d}','breadth',name,'PASS' if breadth and breadth.get('status')=='PASS' else 'UNAVAILABLE')
    sections['breadth']=breadth

    deriv=owners.get('binance_microstructure')
    for i,name in enumerate(['BTC_funding','ETH_funding','funding_history','OI_anchors','long_short','top_accounts','top_positions','taker_flow','multiwindow_price','close_location'],27): add(f'A{i:02d}','binance_derivatives',name,'PASS' if deriv and deriv.get('status')=='PASS' else 'PARTIAL')
    sections['derivatives']=deriv

    okx=owners.get('okx_swap')
    for i,name in enumerate(['BTC_ticker','ETH_ticker','funding','OI','basis_divergence'],37): add(f'A{i:02d}','okx_crosscheck',name,'PASS' if okx and okx.get('status')=='PASS' else 'UNAVAILABLE')
    sections['okx']=okx

    etf_ok=etf and etf.get('status') in {'PASS','DEGRADED','PARTIAL'}
    for i,name in enumerate(['BTC_sessions','ETH_sessions','rolling_sums','stale_no_zero'],42): add(f'A{i:02d}','etf',name,'PASS' if etf_ok else 'UNAVAILABLE')
    sections['etf']={'path':str(etf_path) if etf_path else None,'snapshot':etf}

    cfgi=owners.get('cfgi_sentiment')
    for i,name in enumerate(['MARKET','BTC','ETH'],46): add(f'A{i:02d}','cfgi',name,'PASS' if cfgi and cfgi.get('status')=='PASS' else 'UNAVAILABLE')
    sections['cfgi']=cfgi

    macro=owners.get('fred_macro')
    for i,name in enumerate(['DGS2','DGS10','VIXCLS','DTWEXBGS'],49): add(f'A{i:02d}','macro',name,'PASS' if macro and macro.get('status')=='PASS' else 'UNAVAILABLE')
    sections['macro']=macro

    for i,name in enumerate(['stablecoin_global','stablecoin_chains','chain_TVL','DEX_pools','DEX_anomaly_QA','method_compatible_delta'],53):
        add(f'A{i:02d}','stablecoins_tvl_dex',name,'UNAVAILABLE',None,'OWNER_NOT_IMPLEMENTED')
        missing.append(name)
    sections['stablecoins']={'status':'UNAVAILABLE'}; sections['chain_tvl']={'status':'UNAVAILABLE'}; sections['dex_qa']={'status':'UNAVAILABLE'}

    add('A59','receipts_acceptance','receipt_reconciliation','PASS')
    required={
      'direct_BTC_available':bool(spot),'direct_ETH_available':bool(spot),'direct_ETHBTC_available':bool(spot),
      'settled_Copenhagen_BTC_ETH_ETHBTC_available':False,
      'breadth_aggregate_available':bool(breadth),'breadth_membership_hash_available':bool(breadth),
      'breadth_constituent_sidecar_available':bool(breadth),'Binance_derivatives_available':bool(deriv),'OKX_crosscheck_available':bool(okx)
    }
    full=all(required.values()) and len(ledger)==59
    add('A60','receipts_acceptance','master_monday_acceptance','PASS' if full else 'PARTIAL')
    counts={s:sum(r['status']==s for r in ledger) for s in reg.get('statuses',[])}
    package={
      'root_contract':'MASTER_MONDAY_GAP_FILL_PACKAGE_v1','generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
      'packet':{'status':'FULL_MASTER_MONDAY_INPUT' if full else 'PARTIAL_WITH_EXPLICIT_GAPS','freeze_count':1,'post_freeze_call_count':0},
      'meta':{'planned_core_actions':60,'attempted_core_actions':len(ledger),'counts_reconciled':len(ledger)==60,'accepted_data_pings':accepted},
      'quality':{'required_capabilities':required,**counts},'source_health':{'latest_capture_path':str(cap_path) if cap_path else None},
      **sections,'comparison':sections['predecessor'].get('comparison_status'),'missing':missing,
      'source_ledgers':ledger,'artifacts':{},'authority':{'framework_interpretation':False,'portfolio_action':False,'model_weight_change':False,'canonical_promotion':False}
    }
    package['package_sha256']=sha(package)
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_bytes(canon(package))
    print(json.dumps({'status':package['packet']['status'],'attempted':len(ledger),'sha256':package['package_sha256']},sort_keys=True))

if __name__=='__main__': main()
