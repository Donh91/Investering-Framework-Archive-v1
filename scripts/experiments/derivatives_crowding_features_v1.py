#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

CONTRACT='DERIVATIVES_HOURLY_SOURCE_CAPTURE_V1'
OUTPUT='DERIVATIVES_CROWDING_FEATURE_VECTOR_V1'
HOUR_MS=3600000
WINDOWS=(1,4,12,24)

def iso_ms(value:str)->int:
    if not isinstance(value,str) or not value.strip():raise ValueError('decision_cutoff_utc_required')
    d=datetime.fromisoformat(value.replace('Z','+00:00'))
    if d.utcoffset() is None:raise ValueError('decision_cutoff_timezone_required')
    d=d.astimezone(timezone.utc)
    if d.minute or d.second or d.microsecond:raise ValueError('decision_cutoff_must_be_hour_aligned')
    return int(d.timestamp()*1000)

def finite(v,name):
    if isinstance(v,bool):raise ValueError(name+'_must_be_number')
    x=float(v)
    if not math.isfinite(x):raise ValueError(name+'_must_be_finite')
    return x

def rows_by_ts(rows:list[dict[str,Any]], value_field:str|None=None)->dict[int,dict[str,Any]]:
    out={}
    for row in rows:
        if not isinstance(row,dict):raise ValueError('row_must_be_object')
        ts=int(row.get('timestamp_ms'))
        if ts%HOUR_MS:raise ValueError('hourly_timestamp_not_aligned')
        if ts in out:raise ValueError('duplicate_hourly_timestamp')
        if value_field is not None:finite(row.get(value_field),value_field)
        out[ts]=row
    return out

def funding_before(rows,cutoff_ms):
    candidates=[]
    for r in rows:
        ts=int(r.get('timestamp_ms'))
        rate=finite(r.get('funding_rate'),'funding_rate')
        if ts < cutoff_ms:candidates.append((ts,rate))
    if not candidates:return None
    ts,rate=max(candidates)
    return {'timestamp_ms':ts,'funding_rate':rate}

def sign(v):
    if v is None:return 'UNKNOWN'
    if v>0:return 'POSITIVE'
    if v<0:return 'NEGATIVE'
    return 'ZERO'

def tags(features):
    p=features['price_return_pct'];o=features['oi_value_delta_pct'];f=features['futures_taker_imbalance'];s=features['spot_taker_imbalance']
    if None in (p,o,f,s):return []
    out=[]
    if s>0 and f<0:out.append('SPOT_ABSORPTION_SHORT_PRESSURE_COMPATIBLE')
    if s>0 and f>0 and o>0 and p>0:out.append('BROAD_RISK_ON_COMPATIBLE')
    if s<=0 and f>0 and o>0 and p>0:out.append('LEVERAGE_LED_PUMP_COMPATIBLE')
    if s<0 and f>0 and o>0:out.append('DISTRIBUTION_INTO_LEVERAGED_LONGS_FLOW_COMPATIBLE')
    if f<0 and o<0 and s>=0 and p>=0:out.append('HEALTHY_DELEVERAGING_COMPATIBLE')
    if s<0 and f<0 and p<0:out.append('BROAD_WEAKNESS_COMPATIBLE')
    return out

def build_vector(data:dict[str,Any])->dict[str,Any]:
    if data.get('contract')!=CONTRACT:raise ValueError('capture_contract_invalid')
    for k in ('source_id','venue','symbol','decision_cutoff_utc'):
        if not str(data.get(k,'')).strip():raise ValueError(k+'_required')
    cutoff=iso_ms(data['decision_cutoff_utc'])
    last_open=cutoff-HOUR_MS

    spot=rows_by_ts(data.get('spot_hourly') or [])
    oi=rows_by_ts(data.get('oi_hourly') or [], 'open_interest_value')
    taker=rows_by_ts(data.get('futures_taker_hourly') or [])
    basis=rows_by_ts(data.get('basis_hourly') or [], 'basis_rate')

    for name,series in (('spot',spot),('oi',oi),('futures_taker',taker),('basis',basis)):
        if last_open not in series:raise ValueError(name+'_missing_last_completed_hour')

    result={}
    for h in WINDOWS:
        baseline=last_open-h*HOUR_MS
        required=[spot.get(last_open),spot.get(baseline),oi.get(last_open),oi.get(baseline)]
        flow_ts=[last_open-i*HOUR_MS for i in range(h)]
        spot_flow=[spot.get(t) for t in flow_ts]
        fut_flow=[taker.get(t) for t in flow_ts]
        missing=[]
        if any(x is None for x in required):missing.append('PRICE_OR_OI_BASELINE')
        if any(x is None for x in spot_flow):missing.append('SPOT_FLOW')
        if any(x is None for x in fut_flow):missing.append('FUTURES_FLOW')
        if missing:
            result[f'{h}h']={'state':'INSUFFICIENT_WINDOW','missing':sorted(set(missing)),'compatibility_tags':[]}
            continue

        end_close=finite(spot[last_open]['close'],'spot_close')
        start_close=finite(spot[baseline]['close'],'spot_close')
        end_oi=finite(oi[last_open]['open_interest_value'],'open_interest_value')
        start_oi=finite(oi[baseline]['open_interest_value'],'open_interest_value')
        if start_close<=0 or start_oi<=0:raise ValueError('nonpositive_baseline')

        q=sum(finite(r['quote_volume'],'quote_volume') for r in spot_flow)
        tq=sum(finite(r['taker_buy_quote_volume'],'taker_buy_quote_volume') for r in spot_flow)
        if q<=0:raise ValueError('spot_quote_volume_nonpositive')
        if tq<0 or tq>q*(1+1e-9):raise ValueError('spot_taker_buy_quote_out_of_range')

        fb=sum(finite(r['buy_volume'],'buy_volume') for r in fut_flow)
        fs=sum(finite(r['sell_volume'],'sell_volume') for r in fut_flow)
        if fb<0 or fs<0 or fb+fs<=0:raise ValueError('futures_taker_volume_invalid')

        feat={
          'state':'COMPLETE',
          'price_return_pct':(end_close/start_close-1)*100,
          'oi_value_delta_pct':(end_oi/start_oi-1)*100,
          'spot_taker_imbalance':(2*tq-q)/q,
          'futures_taker_imbalance':(fb-fs)/(fb+fs),
          'spot_quote_volume':q,
          'futures_taker_total_volume':fb+fs,
          'row_count':h
        }
        feat['signs']={
          'price':sign(feat['price_return_pct']),
          'oi':sign(feat['oi_value_delta_pct']),
          'spot_taker':sign(feat['spot_taker_imbalance']),
          'futures_taker':sign(feat['futures_taker_imbalance'])
        }
        feat['compatibility_tags']=tags(feat)
        result[f'{h}h']=feat

    b=basis[last_open]
    latest_funding=funding_before(data.get('funding_events') or [],cutoff)
    return {
      'contract':OUTPUT,
      'authority':'RESEARCH_ONLY',
      'portfolio_action':False,
      'compass_authority':False,
      'thresholds_tuned':False,
      'source_id':data['source_id'],
      'venue':data['venue'],
      'symbol':data['symbol'],
      'decision_cutoff_utc':data['decision_cutoff_utc'],
      'last_completed_interval_open_utc':datetime.fromtimestamp(last_open/1000,tz=timezone.utc).isoformat().replace('+00:00','Z'),
      'latest_basis_rate':finite(b['basis_rate'],'basis_rate'),
      'latest_funding_rate':None if latest_funding is None else latest_funding['funding_rate'],
      'latest_funding_time_utc':None if latest_funding is None else datetime.fromtimestamp(latest_funding['timestamp_ms']/1000,tz=timezone.utc).isoformat().replace('+00:00','Z'),
      'windows':result,
      'interpretation_boundary':{
        'compatibility_tags_are_sign_logic_only':True,
        'multiple_tags_allowed':True,
        'warning_state_created':False,
        'sell_or_trim_action_created':False,
        'incomplete_intervals_excluded':True
      }
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    out=build_vector(json.loads(a.input.read_text()))
    text=json.dumps(out,sort_keys=True,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n')
    print(text)

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,json.JSONDecodeError) as e:raise SystemExit('DERIVATIVES_CROWDING_V1_BLOCKED:'+str(e))
