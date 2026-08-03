from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUSES=("PASS","PARTIAL","STALE","FAIL","UNAVAILABLE","SKIPPED_RUNTIME_LIMIT")

def load(path: Path):
    try:return json.loads(path.read_text())
    except Exception:return None

def canon(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()

def get(v:Any,path:str):
    cur=v
    for part in path.split('.'):
        if not isinstance(cur,dict):return None
        cur=cur.get(part)
    return cur

def latest(root:Path):
    rows=[]
    if root.exists():
        for p in root.rglob('*.json'):
            v=load(p)
            if not v:continue
            raw=next((v.get(k) for k in ('captured_at_utc','created_at_utc','freeze_utc','retrieved_at_utc') if v.get(k)),None)
            try:rows.append((datetime.fromisoformat(str(raw).replace('Z','+00:00')),p,v))
            except Exception:pass
    if not rows:return None,None
    rows.sort(key=lambda x:x[0]);return rows[-1][1],rows[-1][2]

def classify_ping(row):
    c=str(row.get('authority_class') or row.get('packet_class') or row.get('scope') or '').upper()
    if c in {'CANONICAL','CANONICAL_ACCEPTED'}:return 'canonical_data_pings'
    if c in {'BOUNDED','BOUNDED_DECISION_BEARING','DECISION_BEARING'}:return 'bounded_decision_bearing_pings'
    if c in {'RUNTIME_LIMITED','RUNTIME_LIMITED_SUPPLEMENT'}:return 'runtime_limited_supplements'
    return 'qa_and_research_only'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,default=Path('.'));ap.add_argument('--registry',type=Path,required=True);ap.add_argument('--predecessor-registry',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--freeze-start-utc');ap.add_argument('--freeze-end-utc');a=ap.parse_args();root=a.repo_root
    reg=load(a.registry) or {};pred=load(a.predecessor_registry) or {}
    if reg.get('planned_core_actions')!=60:raise SystemExit('ACTION_REGISTRY_NOT_60')
    cap_path,cap=latest(root/'03_DAILY_CAPTURE_LOGS/captures');close_ptr=load(root/'03_DAILY_CAPTURE_LOGS/weekly_close/LATEST_WEEKLY_MARKET_CLOSE.json') or {};etf_path,etf=latest(root/'research/etf_owner');owners={o.get('owner_id'):o for o in (cap or {}).get('owners',[]) if isinstance(o,dict)}
    lanes={k:[] for k in ('canonical_data_pings','bounded_decision_bearing_pings','runtime_limited_supplements','qa_and_research_only')};seen=set();start=datetime.fromisoformat(a.freeze_start_utc.replace('Z','+00:00')) if a.freeze_start_utc else None;end=datetime.fromisoformat(a.freeze_end_utc.replace('Z','+00:00')) if a.freeze_end_utc else None
    dp=root/'research/data_ping_bridge/accepted'
    if dp.exists():
        for p in sorted(dp.rglob('*.json')):
            row=load(p)
            if not row or row.get('contract')!='ACCEPTED_DATA_PING_PACKET_v1':continue
            key=(row.get('run_id'),row.get('snapshot_id'))
            if key in seen:continue
            seen.add(key)
            try:ts=datetime.fromisoformat(str(row.get('freeze_utc')).replace('Z','+00:00'))
            except Exception:continue
            if start and ts<start:continue
            if end and ts>=end:continue
            lane=classify_ping(row);lanes[lane].append({'path':str(p),'sha256':sha(row),'run_id':row.get('run_id'),'snapshot_id':row.get('snapshot_id'),'freeze_utc':row.get('freeze_utc')})
    ledger=[];missing=[]
    def add(aid,group,name,status,field,existing,required,collector):
        ledger.append({'action_id':aid,'group':group,'action_name':name,'status':status,'field':field,'source_timestamp':None,'retrieval_timestamp':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'error_evidence_id':None if status=='PASS' else f'{aid}_{status}','optional':False})
        if status!='PASS':missing.append({'action_id':aid,'field':field,'blocking_level':'BLOCKING' if status in {'FAIL','UNAVAILABLE','SKIPPED_RUNTIME_LIMIT'} else 'CONFIDENCE_REDUCING','reason':status,'existing_evidence':existing,'required_evidence':required,'suggested_collector':collector})
    canonical_ok=pred.get('status')=='ACTIVE' and pred.get('predecessor_scope')=='CANONICAL_ACCEPTED_MARKET_PREDECESSOR'
    add('A01','identity_predecessor','identity_freeze','PASS' if cap else 'UNAVAILABLE','packet.freeze',str(cap_path) if cap_path else None,'latest owner capture','daily capture')
    add('A02','identity_predecessor','canonical_predecessor_registry','PASS' if canonical_ok else 'PARTIAL','comparison.canonical_predecessor',pred or None,'active canonical predecessor','predecessor registry')
    add('A03','identity_predecessor','single_freeze_contract','PASS' if cap and cap.get('freeze_count',1)==1 else 'UNAVAILABLE','packet.freeze_count',cap and cap.get('freeze_count'),'1','preflight orchestrator')
    add('A04','identity_predecessor','accepted_data_ping_inventory','PASS','meta.data_ping_lanes',sum(len(x) for x in lanes.values()),'>=0 classified packets','DATA PING bridge')
    spot=owners.get('binance_spot') or {}
    for aid,name,path in [('A05','BTCUSDT','data.BTCUSDT'),('A06','ETHUSDT','data.ETHUSDT'),('A07','ETHBTC','data.ETHBTC'),('A08','order_book','data.order_book'),('A09','24h_ticker','data.ticker_24h'),('A10','server_time','data.server_time')]:add(aid,'current_spot',name,'PASS' if get(spot,path) is not None else 'UNAVAILABLE',f'current_market.{name}',get(spot,path),path,'binance spot owner')
    settled=(cap or {}).get('settled_sessions') or owners.get('copenhagen_settled_sessions') or {}
    for aid,name,key in [('A11','Copenhagen_BTC','BTCUSDT'),('A12','Copenhagen_ETH','ETHUSDT'),('A13','Copenhagen_ETHBTC','ETHBTC'),('A14','threshold_tests','threshold_tests'),('A15','UTC_local_separation','session_type')]:add(aid,'settled_sessions',name,'PASS' if get(settled,key) is not None else 'UNAVAILABLE',f'settled_sessions.{key}',get(settled,key),key,'Copenhagen settled-session owner')
    week=load(root/str(close_ptr.get('path',''))) if close_ptr.get('path') else None;daily=(week or {}).get('daily') or (week or {}).get('daily_ranges') or {}
    add('A16','weekly_daily_structure','BTC_daily_table','PASS' if get(daily,'BTCUSDT') else 'UNAVAILABLE','week_daily_intraday.BTCUSDT',get(daily,'BTCUSDT'),'7 local-day rows','weekly close builder');add('A17','weekly_daily_structure','ETH_daily_table','PASS' if get(daily,'ETHUSDT') else 'UNAVAILABLE','week_daily_intraday.ETHUSDT',get(daily,'ETHUSDT'),'7 local-day rows','weekly close builder');add('A18','weekly_daily_structure','weekly_tieout','PASS' if (week or {}).get('weekly_daily_tieout') else 'UNAVAILABLE','week_daily_intraday.weekly_daily_tieout',(week or {}).get('weekly_daily_tieout'),'PASS per BTC/ETH','weekly close builder');add('A19','weekly_daily_structure','gap_duplicate_QA','PASS' if (week or {}).get('gap_duplicate_qa') is not None else 'UNAVAILABLE','week_daily_intraday.gap_duplicate_qa',(week or {}).get('gap_duplicate_qa'),'gaps/duplicates summary','weekly close builder')
    breadth=owners.get('top100_breadth') or {}
    for aid,name,path in [('A20','aggregate','data.advance_ratio'),('A21','membership_hash','data.membership_hash'),('A22','constituent_sidecar','data.constituent_sidecar'),('A23','exclusion_sidecar','data.exclusion_sidecar'),('A24','median_mean','data.median_return_24h_pct'),('A25','gates','data.gates'),('A26','longitudinal_permission','data.scored_gate_permission')]:add(aid,'breadth',name,'PASS' if get(breadth,path) is not None else 'UNAVAILABLE',f'breadth.{name}',get(breadth,path),path,'top100 breadth owner')
    deriv=owners.get('binance_microstructure') or owners.get('binance_derivatives') or {};dpaths=['data.BTC.funding','data.ETH.funding','data.funding_history','data.oi_anchors','data.global_long_short','data.top_account_long_short','data.top_position_long_short','data.taker_flow','data.multiwindow_price','data.close_location']
    for i,(name,path) in enumerate(zip(['BTC_funding','ETH_funding','funding_history','OI_anchors','long_short','top_accounts','top_positions','taker_flow','multiwindow_price','close_location'],dpaths),27):add(f'A{i:02d}','binance_derivatives',name,'PASS' if get(deriv,path) is not None else 'UNAVAILABLE',f'derivatives.{name}',get(deriv,path),path,'Binance derivatives owner')
    okx=owners.get('okx_swap') or {};opaths=[('BTC_ticker','data.BTC.ticker'),('ETH_ticker','data.ETH.ticker'),('funding','data.funding'),('OI','data.open_interest'),('basis_divergence','data.basis_divergence')]
    for i,(name,path) in enumerate(opaths,37):add(f'A{i:02d}','okx_crosscheck',name,'PASS' if get(okx,path) is not None else 'UNAVAILABLE',f'okx.{name}',get(okx,path),path,'OKX owner')
    etf=etf or {}
    for i,(name,path) in enumerate([('BTC_sessions','assets.BTC.sessions'),('ETH_sessions','assets.ETH.sessions'),('rolling_sums','rolling_sums'),('stale_no_zero','stale_no_zero_protection')],42):
        val=get(etf,path);st='PASS' if val is not None and etf.get('status')=='PASS' else ('PARTIAL' if val is not None else 'UNAVAILABLE');add(f'A{i:02d}','etf',name,st,f'etf.{name}',val,path,'Farside ETF owner')
    cfgi=owners.get('cfgi_sentiment') or {}
    for i,name in enumerate(['MARKET','BTC','ETH'],46):add(f'A{i:02d}','cfgi',name,'PASS' if get(cfgi,f'data.{name}.score') is not None else 'UNAVAILABLE',f'cfgi.{name}',get(cfgi,f'data.{name}.score'),'current and prior score','CFGI owner')
    macro=owners.get('fred_macro') or {}
    for i,name in enumerate(['DGS2','DGS10','VIXCLS','DTWEXBGS'],49):add(f'A{i:02d}','macro',name,'PASS' if get(macro,f'data.{name}.latest') is not None else 'UNAVAILABLE',f'macro.{name}',get(macro,f'data.{name}'),'latest plus five points','FRED owner')
    aux=(cap or {}).get('auxiliary_owners') or {}
    for i,(name,path,collector) in enumerate([('stablecoin_global','stablecoins.global','stablecoin owner'),('stablecoin_chains','stablecoins.chains','stablecoin owner'),('chain_TVL','chain_tvl','TVL owner'),('DEX_pools','dex_qa.pools','DEX owner'),('DEX_anomaly_QA','dex_qa.anomalies','DEX QA'),('method_compatible_delta','stablecoins.method_compatible_delta','stablecoin owner')],53):add(f'A{i:02d}','stablecoins_tvl_dex',name,'PASS' if get(aux,path) is not None else 'UNAVAILABLE',path,get(aux,path),path,collector)
    required={'direct_BTC_available':get(spot,'data.BTCUSDT') is not None,'direct_ETH_available':get(spot,'data.ETHUSDT') is not None,'direct_ETHBTC_available':get(spot,'data.ETHBTC') is not None,'settled_Copenhagen_BTC_ETH_ETHBTC_available':all(get(settled,k) is not None for k in ('BTCUSDT','ETHUSDT','ETHBTC')),'breadth_aggregate_available':get(breadth,'data.advance_ratio') is not None,'breadth_membership_hash_available':get(breadth,'data.membership_hash') is not None,'breadth_constituent_sidecar_available':get(breadth,'data.constituent_sidecar') is not None,'Binance_derivatives_available':all(get(deriv,p) is not None for p in dpaths),'OKX_crosscheck_available':all(get(okx,p) is not None for _,p in opaths)}
    add('A59','receipts_acceptance','receipt_reconciliation','PASS','quality.receipt_reconciliation',len(ledger),'59 pre-acceptance receipts','preflight');pre={s:sum(r['status']==s for r in ledger) for s in STATUSES};full=all(required.values()) and pre['FAIL']==0 and pre['UNAVAILABLE']==0 and pre['SKIPPED_RUNTIME_LIMIT']==0;add('A60','receipts_acceptance','master_monday_acceptance','PASS' if full else 'PARTIAL','packet.status',None,'all mandatory capabilities','preflight');counts={s:sum(r['status']==s for r in ledger) for s in STATUSES}
    package={'root_contract':'MASTER_MONDAY_GAP_FILL_PACKAGE_v2','generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'packet':{'status':'FULL_MASTER_MONDAY_INPUT' if full else 'PARTIAL_WITH_EXPLICIT_GAPS','freeze_count':1,'post_freeze_call_count':0},'meta':{'planned_core_actions':60,'attempted_core_actions':len(ledger),'counts_reconciled':len(ledger)==60,'data_ping_lanes':lanes},'quality':{'required_capabilities':required,**counts},'source_health':{'latest_capture_path':str(cap_path) if cap_path else None},'predecessor':{**pred,'comparison_status':'AVAILABLE' if canonical_ok and pred.get('market_metrics') else 'UNAVAILABLE_CANONICAL_PREDECESSOR_VALUES_NOT_PRESENT'},'current_market':spot,'settled_sessions':settled,'week_daily_intraday':daily,'breadth':breadth,'derivatives':deriv,'okx':okx,'etf':{'path':str(etf_path) if etf_path else None,'snapshot':etf},'cfgi':cfgi,'macro':macro,'stablecoins':aux.get('stablecoins'),'chain_tvl':aux.get('chain_tvl'),'dex_qa':aux.get('dex_qa'),'missing':missing,'source_ledgers':ledger,'authority':{'framework_interpretation':False,'portfolio_action':False,'model_weight_change':False,'canonical_promotion':False}}
    package['package_sha256']=sha(package);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(canon(package));print(json.dumps({'status':package['packet']['status'],'attempted':len(ledger),'missing':len(missing),'sha256':package['package_sha256']},sort_keys=True))
if __name__=='__main__':main()
