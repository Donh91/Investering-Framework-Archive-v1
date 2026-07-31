#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}
SYMBOLS=("BTCUSDT","ETHUSDT"); BASE="https://data-api.binance.vision/api/v3"; LEVELS=(5,20,50)
class SourceError(RuntimeError):
 def __init__(self,status,message): super().__init__(message); self.status=status
def sha(b): return hashlib.sha256(b).hexdigest()
def iso(ms): return datetime.fromtimestamp(ms/1000,tz=timezone.utc).isoformat().replace('+00:00','Z')
def fetch(url,timeout=10):
 req=urllib.request.Request(url,headers={"User-Agent":"Investering-T4-Microstructure/0.1","Accept":"application/json"})
 try:
  with urllib.request.urlopen(req,timeout=timeout) as r: b=r.read()
 except urllib.error.HTTPError as e:
  body=e.read().decode('utf-8','replace'); status='GEO_RESTRICTED' if e.code in (403,451) or 'restricted location' in body.lower() else 'HTTP_ERROR'; raise SourceError(status,f'HTTP {e.code}: {body[:240]}') from e
 except (urllib.error.URLError,TimeoutError,OSError) as e: raise SourceError('NETWORK_ERROR',str(e)) from e
 if not b: raise SourceError('EMPTY_RESPONSE','empty payload')
 return b
def load(b):
 try: v=json.loads(b)
 except Exception as e: raise SourceError('SCHEMA_DRIFT','invalid JSON') from e
 if isinstance(v,dict) and 'code' in v and 'msg' in v:
  msg=str(v['msg']); raise SourceError('GEO_RESTRICTED' if 'restricted location' in msg.lower() else 'SOURCE_ERROR',msg)
 return v
def side(rows,name):
 if not isinstance(rows,list) or not rows: raise SourceError('EMPTY_RESPONSE',f'empty {name}')
 out=[]
 for i,r in enumerate(rows):
  if not isinstance(r,list) or len(r)<2: raise SourceError('SCHEMA_DRIFT',f'{name} {i}')
  try: p,q=float(r[0]),float(r[1])
  except Exception as e: raise SourceError('SCHEMA_DRIFT',f'{name} {i}') from e
  if p<=0 or q<0: raise SourceError('INVALID_BOOK',f'{name} {i}')
  out.append((p,q))
 return out
def parse_depth(b,symbol):
 v=load(b)
 if not isinstance(v,dict) or 'lastUpdateId' not in v: raise SourceError('SCHEMA_DRIFT',f'{symbol} depth')
 bids,asks=side(v.get('bids'),'bid'),side(v.get('asks'),'ask')
 if any(bids[i][0]<bids[i+1][0] for i in range(len(bids)-1)) or any(asks[i][0]>asks[i+1][0] for i in range(len(asks)-1)): raise SourceError('INVALID_BOOK_SORT',symbol)
 bb,ba=bids[0][0],asks[0][0]
 if bb>=ba: raise SourceError('CROSSED_BOOK',symbol)
 mid=(bb+ba)/2; metrics={}
 for n in LEVELS:
  used=min(n,len(bids),len(asks)); bn=sum(p*q for p,q in bids[:used]); an=sum(p*q for p,q in asks[:used]); total=bn+an
  if total<=0: raise SourceError('INVALID_BOOK',f'{symbol} zero depth')
  metrics[str(n)]={"levels_used":used,"bid_quote_notional":bn,"ask_quote_notional":an,"quote_notional_imbalance":(bn-an)/total}
 return {"symbol":symbol,"snapshot_type":"POINT_IN_TIME_DEPTH","last_update_id":int(v['lastUpdateId']),"best_bid":bb,"best_ask":ba,"midpoint":mid,"spread_bps":((ba-bb)/mid)*10000,"depth_metrics":metrics,"replenishment_available":False,"cancellation_rate_available":False}
def parse_trades(b,symbol):
 rows=load(b)
 if not isinstance(rows,list) or not rows: raise SourceError('EMPTY_RESPONSE',f'{symbol} trades')
 out=[]; seen=set()
 for i,r in enumerate(rows):
  if not isinstance(r,dict) or not {'a','p','q','T','m'}.issubset(r): raise SourceError('SCHEMA_DRIFT',f'{symbol} trade {i}')
  tid=int(r['a'])
  if tid in seen: raise SourceError('DUPLICATE_TRADE_ID',f'{symbol} {tid}')
  seen.add(tid)
  try: p,q=float(r['p']),float(r['q'])
  except Exception as e: raise SourceError('SCHEMA_DRIFT',f'{symbol} trade {i}') from e
  if p<=0 or q<=0: raise SourceError('INVALID_TRADE',f'{symbol} {i}')
  out.append((int(r['T']),tid,p,q,p*q,bool(r['m'])))
 out.sort(); buy=sum(x[4] for x in out if not x[5]); sell=sum(x[4] for x in out if x[5]); total=buy+sell; base=sum(x[3] for x in out)
 if total<=0 or base<=0: raise SourceError('INVALID_TRADE',symbol)
 prices=[x[2] for x in out]
 return {"symbol":symbol,"window_type":"LATEST_N_AGGREGATE_TRADES","trade_count":len(out),"first_trade_time":iso(out[0][0]),"last_trade_time":iso(out[-1][0]),"open":prices[0],"high":max(prices),"low":min(prices),"close":prices[-1],"base_volume":base,"quote_volume":total,"vwap":total/base,"aggressive_buy_quote":buy,"aggressive_sell_quote":sell,"taker_quote_imbalance":(buy-sell)/total,"trade_id_first":out[0][1],"trade_id_last":out[-1][1]}
def verify(root):
 m=json.loads((root/'artifact_manifest.json').read_text()); failures=[]
 for x in m['members']:
  p=root/x['path']
  if not p.is_file(): failures.append({"path":x['path'],"error":"MISSING"}); continue
  b=p.read_bytes()
  if len(b)!=x['bytes'] or sha(b)!=x['sha256']: failures.append({"path":x['path'],"error":"HASH_OR_SIZE"})
 return {"status":"PASS" if not failures else "FAIL","member_count":len(m['members']),"failures":failures,"authority":AUTHORITY}
def run(payloads,root,retrieval):
 root.mkdir(parents=True,exist_ok=True); raw=root/'raw'; raw.mkdir(exist_ok=True); normalized={}; lineage=[]; urls={}
 for symbol in SYMBOLS:
  pair=payloads.get(symbol)
  if not pair or set(pair)!={'depth','aggTrades'}: raise SourceError('MISSING_PAYLOAD',symbol)
  d,t=pair['depth'],pair['aggTrades']; dp=raw/f'{symbol}_depth.json'; tp=raw/f'{symbol}_aggTrades.json'; dp.write_bytes(d); tp.write_bytes(t)
  normalized[symbol]={"depth":parse_depth(d,symbol),"agg_trades":parse_trades(t,symbol)}
  for kind,b,p in [('depth',d,dp),('aggTrades',t,tp)]: lineage.append({"symbol":symbol,"kind":kind,"path":p.relative_to(root).as_posix(),"bytes":len(b),"sha256":sha(b)})
  urls[f'{symbol}_depth']=BASE+'/depth?'+urllib.parse.urlencode({'symbol':symbol,'limit':100}); urls[f'{symbol}_aggTrades']=BASE+'/aggTrades?'+urllib.parse.urlencode({'symbol':symbol,'limit':1000})
 rid='T4_MICRO_'+retrieval.replace('-','').replace(':','')[:15]+'_'+sha(json.dumps(lineage,sort_keys=True).encode())[:12]
 owner={"contract":"T4_EXECUTION_MICROSTRUCTURE_SOURCE_v0_1","run_id":rid,"retrieval_timestamp":retrieval,"symbols":list(SYMBOLS),"source":"BINANCE_SPOT_MARKET_DATA_ONLY","data":normalized,"limitations":{"point_in_time_depth_only":True,"replenishment_available":False,"cancellation_rate_available":False,"historical_order_book_reconstruction":False},"authority":AUTHORITY}
 receipt={"run_id":rid,"source_urls":urls,"source_payloads":lineage,"owner_sha256":sha(json.dumps(owner,sort_keys=True,separators=(',',':')).encode()),"status":"PASS","authority":AUTHORITY}
 (root/'owner_snapshot.json').write_text(json.dumps(owner,indent=2,sort_keys=True)+'\n'); (root/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 members=[]
 for p in sorted(x for x in root.rglob('*') if x.is_file()):
  b=p.read_bytes(); members.append({"path":p.relative_to(root).as_posix(),"bytes":len(b),"sha256":sha(b)})
 (root/'artifact_manifest.json').write_text(json.dumps({"contract":"T4_EXECUTION_MICROSTRUCTURE_MANIFEST_v0_1","run_id":rid,"members":members,"member_count":len(members),"authority":AUTHORITY},indent=2,sort_keys=True)+'\n')
 return owner
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--fixture-dir',type=Path); ap.add_argument('--output-dir',type=Path,default=Path('binance-spot-microstructure-output')); ap.add_argument('--retrieval-timestamp'); a=ap.parse_args(); retrieval=a.retrieval_timestamp or datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
 try:
  payloads={}
  for symbol in SYMBOLS:
   if a.fixture_dir: payloads[symbol]={"depth":(a.fixture_dir/f'{symbol}_depth.json').read_bytes(),"aggTrades":(a.fixture_dir/f'{symbol}_aggTrades.json').read_bytes()}
   else: payloads[symbol]={"depth":fetch(BASE+'/depth?'+urllib.parse.urlencode({'symbol':symbol,'limit':100})),"aggTrades":fetch(BASE+'/aggTrades?'+urllib.parse.urlencode({'symbol':symbol,'limit':1000}))}
  owner=run(payloads,a.output_dir,retrieval); rb=verify(a.output_dir); print(json.dumps({"status":rb['status'],"run_id":owner['run_id'],"member_count":rb['member_count']},sort_keys=True)); return 0 if rb['status']=='PASS' else 3
 except SourceError as e: print(json.dumps({"status":e.status,"error":str(e),"retrieval_timestamp":retrieval,"authority":AUTHORITY},sort_keys=True)); return 2
if __name__=='__main__': raise SystemExit(main())
