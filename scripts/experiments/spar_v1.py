from __future__ import annotations
import argparse,csv,json,statistics
from dataclasses import dataclass
from datetime import datetime,timezone,timedelta
from pathlib import Path

CONTRACT='SPAR_REPLAY_REPORT_v1'; FRAGILITY_CONTRACT='SPAR_FRAGILITY_REPORT_v1'
INPUT_ADAPTER='SPAR_INPUT_ADAPTER_v2'
V2_CONTRACT='DAILY_RAW_CAPTURE_INDEX_v2'
V3_CONTRACT='DAILY_LIVE_ANCHOR_INDEX_v3'
def ts(x:str)->datetime:return datetime.fromisoformat(x.replace('Z','+00:00')).astimezone(timezone.utc)
def pct(a:float,b:float):return None if b==0 else (a/b-1)*100
def med(x):return statistics.median(x) if x else None
@dataclass(frozen=True)
class Snapshot:
 p:str;t:datetime;btc:float;eth:float;eb:float;adv:float;dec:float;fund:float;oi:float
 @property
 def breadth(self):return self.adv-self.dec

def completed_hour_open(t:datetime)->datetime:
 return t.replace(minute=0,second=0,microsecond=0)-timedelta(hours=1)

def load_hourly_spot_rows(root:Path):
 rows={}
 if not root.exists():return rows
 for p in sorted(root.rglob('*.csv')):
  try:
   with p.open(newline='') as fh:
    for row in csv.DictReader(fh):
     if row.get('spot_status')!='PASS':continue
     try:
      t=ts(row['timestamp_utc'])
      rows[t]={'btc':float(row['btc_close']),'eth':float(row['eth_close']),'eb':float(row['ethbtc_close']),'path':str(p)}
     except Exception:continue
  except Exception:continue
 return rows

def load_snapshot(p:Path,hourly_spot=None):
 try:o=json.loads(p.read_text());m=o['market_metrics']
 except Exception:return None
 contract=o.get('contract')
 try:
  if contract==V2_CONTRACT:
   return Snapshot(str(p),ts(o['captured_at_utc']),float(m['spot']['BTCUSDT']['close']),float(m['spot']['ETHUSDT']['close']),float(m['spot']['ETHBTC']['close']),float(m['breadth']['advancers']),float(m['breadth']['decliners']),float(m['derivatives']['BTC-USDT-SWAP']['funding']['funding_rate']),float(m['derivatives']['BTC-USDT-SWAP']['open_interest']['open_interest_ccy']))
  if contract==V3_CONTRACT:
   t=ts(o['captured_at_utc']);row=(hourly_spot or {}).get(completed_hour_open(t))
   if not row:return None
   return Snapshot(str(p),t,float(row['btc']),float(row['eth']),float(row['eb']),float(m['breadth']['advancers']),float(m['breadth']['decliners']),float(m['derivatives']['BTC-USDT-SWAP']['funding']['funding_rate']),float(m['derivatives']['BTC-USDT-SWAP']['open_interest']['open_interest_ccy']))
 except Exception:return None
 return None

def load_snapshots(root:Path):
 d={};hourly=load_hourly_spot_rows(root.parent/'hourly')
 for p in root.rglob('*.json'):
  if p.name=='LATEST.json':continue
  s=load_snapshot(p,hourly)
  if s:d[s.t]=s
 return [d[k] for k in sorted(d)]

def transition(a:Snapshot,b:Snapshot):
 return {'breadth_deterioration':b.breadth<a.breadth,'leverage_build':b.oi>a.oi and b.fund>a.fund,'eth_relative_weakness':b.eb<a.eb,'btc_resilience':b.btc>=a.btc}

def ordered(tr,start,names,max_steps):
 pos=start;end=min(len(tr),start+max_steps)
 for name in names:
  hit=next((i for i in range(pos,end) if tr[i].get(name)),None)
  if hit is None:return None
  pos=hit+1
 return pos-1

def detect_events(snaps,cooldown_hours=72):
 out={k:[] for k in ('SPAR-P1','SPAR-P2','SPAR-P3')}
 if len(snaps)<2:return out
 tr=[transition(snaps[i-1],snaps[i]) for i in range(1,len(snaps))]
 raw={k:[] for k in out}
 for i in range(len(tr)):
  a=ordered(tr,i,['breadth_deterioration','leverage_build','eth_relative_weakness'],4)
  b=ordered(tr,i,['leverage_build','breadth_deterioration','eth_relative_weakness'],4)
  if a is not None:raw['SPAR-P1'].append(a+1)
  if b is not None:raw['SPAR-P2'].append(b+1)
  if tr[i]['btc_resilience'] and tr[i]['breadth_deterioration']:
   c=next((j for j in range(i,min(len(tr),i+3)) if tr[j]['eth_relative_weakness']),None)
   if c is not None:raw['SPAR-P3'].append(c+1)
 for k,idxs in raw.items():
  last=None
  for idx in sorted(set(idxs)):
   if last is None or (snaps[idx].t-snaps[last].t).total_seconds()>=cooldown_hours*3600:
    out[k].append(idx);last=idx
 return out

def outcome(snaps,i,h):
 target=snaps[i].t+timedelta(hours=h);cand=[(abs((s.t-target).total_seconds()),j) for j,s in enumerate(snaps) if j>i and abs((s.t-target).total_seconds())<=6*3600]
 if not cand:return {'status':'PENDING'}
 _,j=min(cand);path=snaps[i:j+1];s0=snaps[i];sj=snaps[j]
 return {'status':'MATURED','target_timestamp_utc':sj.t.isoformat().replace('+00:00','Z'),'btc_return_pct':pct(sj.btc,s0.btc),'btc_mae_pct':min(pct(s.btc,s0.btc) for s in path),'btc_mfe_pct':max(pct(s.btc,s0.btc) for s in path),'eth_return_pct':pct(sj.eth,s0.eth),'eth_mae_pct':min(pct(s.eth,s0.eth) for s in path),'eth_mfe_pct':max(pct(s.eth,s0.eth) for s in path),'ethbtc_return_pct':pct(sj.eb,s0.eb)}

def build_replay(snaps,min_matured_events=5):
 ev=detect_events(snaps);patterns=[];ready=False
 for k,idxs in ev.items():
  rows=[]
  for i in idxs:rows.append({'event_timestamp_utc':snaps[i].t.isoformat().replace('+00:00','Z'),'source_path':snaps[i].p,'outcomes':{str(h):outcome(snaps,i,h) for h in (24,72,168)}})
  vals=[e['outcomes']['72']['btc_return_pct'] for e in rows if e['outcomes']['72']['status']=='MATURED'];ok=len(vals)>=min_matured_events;ready|=ok
  patterns.append({'pattern_id':k,'event_count':len(rows),'matured_72h_count':len(vals),'median_btc_return_72h_pct':med(vals),'status':'BASE_REVIEW_READY' if ok else 'INSUFFICIENT_EVIDENCE','events':rows})
 return {'contract':CONTRACT,'authority':'SHADOW_RESEARCH_ONLY','status':'READY_FOR_ROBUSTNESS_REVIEW' if ready else 'INSUFFICIENT_EVIDENCE','source':{'snapshot_count':len(snaps),'min_timestamp_utc':snaps[0].t.isoformat().replace('+00:00','Z') if snaps else None,'max_timestamp_utc':snaps[-1].t.isoformat().replace('+00:00','Z') if snaps else None},'method':{'future_leakage':False,'fitted_thresholds':False,'episode_cooldown_hours':72,'paid_api_calls':0,'input_adapter':INPUT_ADAPTER,'v3_spot_join_policy':'EXACT_PREVIOUS_COMPLETED_UTC_HOUR_ONLY','interpolation':False,'forward_fill':False},'patterns':patterns}

def loo_stable(vals):
 if len(vals)<3:return None
 base=med(vals)
 if base==0:return False
 sign=base>0
 return all(((med(vals[:i]+vals[i+1:]) or 0)>0)==sign for i in range(len(vals)))
def build_fragility(base,min_events=10):
 rows=[];ready=False
 for p in base.get('patterns',[]):
  vals=[float(e['outcomes']['72']['btc_return_pct']) for e in p.get('events',[]) if e.get('outcomes',{}).get('72',{}).get('status')=='MATURED'];ok=len(vals)>=min_events;ready|=ok
  rows.append({'pattern_id':p.get('pattern_id'),'matured_72h_count':len(vals),'median_btc_return_pct':med(vals),'leave_one_out_sign_stable':loo_stable(vals),'status':'READY_FOR_PLACEBO_AND_REGIME_SPLIT' if ok else 'INSUFFICIENT_EVIDENCE'})
 return {'contract':FRAGILITY_CONTRACT,'authority':'SHADOW_RESEARCH_ONLY','status':'ROBUSTNESS_REVIEW_READY' if ready else 'INSUFFICIENT_EVIDENCE','minimum_events_for_placebo_and_regime_split':min_events,'patterns':rows,'notes':['No candidate may be promoted from this report.','Placebo timestamps and regime splits remain blocked until event count is sufficient.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['replay','fragility'],required=True);p.add_argument('--capture-root',type=Path);p.add_argument('--base-report',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--min-matured-events',type=int,default=5);p.add_argument('--min-fragility-events',type=int,default=10);a=p.parse_args()
 if a.mode=='replay':
  if not a.capture_root:raise SystemExit('capture_root_required')
  r=build_replay(load_snapshots(a.capture_root),a.min_matured_events)
 else:
  if not a.base_report:raise SystemExit('base_report_required')
  r=build_fragility(json.loads(a.base_report.read_text()),a.min_fragility_events)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps({'contract':r['contract'],'status':r['status']},sort_keys=True))
if __name__=='__main__':main()
