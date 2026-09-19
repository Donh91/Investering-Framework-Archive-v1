#!/usr/bin/env python3
"""Prospective-only SHADOW-04 harness. TEST EVIDENCE, never production/alerts."""
import argparse,collections,hashlib,json,os,sqlite3,time,urllib.request,urllib.error
RPCS=[x for x in os.environ.get("RH_RPCS","https://rpc.mainnet.chain.robinhood.com,https://robinhood-mainnet-rpc.blockreq.com/v1/rpc/public").split(",") if x]
UA="alpha-lab-shadow-prospective/1.0"; CHAIN="0x1237"
FACTORY="0x7eD598BcEf8bd9Edd8C97A195C6d13f40801EC7e"
TOPIC0="0x8d4aad4953d0ca700d468f3753aa14432d1b35b43ec6409f051fb6aa43a89607"
LAG=5
def call(url,m,p,timeout=20):
 req=urllib.request.Request(url,data=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),headers={"Content-Type":"application/json","User-Agent":UA})
 try:
  with urllib.request.urlopen(req,timeout=timeout) as r:o=json.load(r)
  return o.get("result"),o.get("error")
 except Exception as e:return None,f"{type(e).__name__}:{e}"
def heads():
 out=[]
 for u in RPCS:
  h,e=call(u,"eth_blockNumber",[])
  if h:out.append((u,int(h,16)))
 return out
def decode(l):
 t=l["topics"]; return {"tx":l["transactionHash"],"li":int(l["logIndex"],16),"block":int(l["blockNumber"],16),"ca":"0x"+t[1][-40:],"curve":"0x"+t[2][-40:],"topic3":"0x"+t[3][-40:]}
def text32(x):
 if not x or x=="0x":return None
 try:
  b=bytes.fromhex(x[2:]); n=int.from_bytes(b[32:64],"big"); return b[64:64+n].decode("utf8","replace")
 except:return None
def main(a):
 hs=heads()
 if len(hs)<2: raise SystemExit("FAIL preflight: need >=2 providers")
 chain=[]
 for u,_ in hs:
  c,e=call(u,"eth_chainId",[]); chain.append((u,c,e))
 if any(c!=CHAIN for _,c,_ in chain):raise SystemExit("FAIL chainId")
 # Freeze BEFORE future start. +20 blocks guarantees the credited window did not exist at freeze.
 freeze_wall=time.time(); future_start=max(h for _,h in hs)+20
 spec={"test":"SHADOW-04-PROSPECTIVE","frozen_at":freeze_wall,"future_start_block":future_start,"target_launches":a.launches,"chain_id":CHAIN,"factory":FACTORY,"topic0":TOPIC0,"providers":RPCS,"source_sha":os.environ.get("GITHUB_SHA","UNKNOWN"),"assertions":["future-only","raw-log+receipt-first-seen","two-provider-event-set","ticker-never-identity","no-retrospective-credit"]}
 spec["spec_sha256"]=hashlib.sha256(json.dumps(spec,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 json.dump(spec,open(a.freeze,"w"),indent=2)
 db=sqlite3.connect(a.db); db.execute("PRAGMA journal_mode=WAL"); db.executescript("""CREATE TABLE IF NOT EXISTS seen(tx TEXT,li INTEGER,block INTEGER,ca TEXT,topic3 TEXT,receipt_from TEXT,symbol TEXT,name TEXT,t_seen REAL,raw_log TEXT,raw_receipt TEXT,PRIMARY KEY(tx,li));""");db.commit()
 print(json.dumps(spec,indent=2),flush=True)
 cursor=future_start-1; provider_sets=[set() for _ in RPCS]; errors=[]; start=time.time()
 while db.execute("SELECT COUNT(*) FROM seen").fetchone()[0] < a.launches and time.time()-start<a.max_seconds:
  hs=heads()
  if len(hs)<2: errors.append("provider_quorum");time.sleep(1);continue
  safe=min(h for _,h in hs)-LAG
  if safe<=cursor:time.sleep(.4);continue
  all_logs=[]
  for pi,u in enumerate(RPCS):
   lg,e=call(u,"eth_getLogs",[{"fromBlock":hex(cursor+1),"toBlock":hex(safe),"address":FACTORY,"topics":[TOPIC0]}],30)
   if lg is None:errors.append(f"{pi}:{e}");continue
   for l in lg:
    k=(l["transactionHash"],int(l["logIndex"],16));provider_sets[pi].add(k)
    if pi==0:all_logs.append(l)
  now=time.time()
  for l in all_logs:
   if len(l.get("topics",[]))!=4:continue
   d=decode(l); rc,e=call(RPCS[0],"eth_getTransactionReceipt",[d["tx"]])
   if not rc:errors.append("receipt:"+str(e));continue
   sym,_=call(RPCS[0],"eth_call",[{"to":d["ca"],"data":"0x95d89b41"},"latest"])
   nam,_=call(RPCS[0],"eth_call",[{"to":d["ca"],"data":"0x06fdde03"},"latest"])
   db.execute("INSERT OR IGNORE INTO seen VALUES(?,?,?,?,?,?,?,?,?,?,?)",(d["tx"],d["li"],d["block"],d["ca"],d["topic3"],rc.get("from","").lower(),text32(sym),text32(nam),now,json.dumps(l),json.dumps(rc)))
  db.commit();cursor=safe
  print("progress",db.execute("SELECT COUNT(*) FROM seen").fetchone()[0],"cursor",cursor,flush=True)
  time.sleep(.4)
 rows=db.execute("SELECT ca,topic3,receipt_from,symbol,name FROM seen ORDER BY block,li LIMIT ?",(a.launches,)).fetchall()
 syms=collections.Counter((r[3] or "").upper().strip() for r in rows if r[3])
 diverge=sum(1 for r in rows if r[2] and r[2]!=r[1].lower())
 reused=collections.Counter(r[2] for r in rows if r[2])
 common=set.intersection(*provider_sets) if provider_sets else set()
 union=set.union(*provider_sets) if provider_sets else set()
 first_meta=db.execute("SELECT block,t_seen FROM seen ORDER BY block,li LIMIT 1").fetchone()\n res={"test":"SHADOW-04-PROSPECTIVE","spec_sha256":spec["spec_sha256"],"source_sha":spec["source_sha"],"n":len(rows),"future_start_block":future_start,"first_observed_block":first_meta[0] if first_meta else None,"first_observed_unix":first_meta[1] if first_meta else None,"end_block":cursor,"receipt_topic3_divergence":diverge,"divergence_pct":round(100*diverge/max(1,len(rows)),2),"nonunique_symbol_rows":sum(v for v in syms.values() if v>1),"nonunique_symbol_pct":round(100*sum(v for v in syms.values() if v>1)/max(1,len(rows)),2),"receipt_from_reused_keys":sum(1 for v in reused.values() if v>1),"provider_union":len(union),"provider_intersection":len(common),"provider_disagreement":len(union-common),"errors":errors[-50:],"prospective":True,"PASS_COLLECTION":len(rows)>=a.launches and len(union-common)==0}
 json.dump(res,open(a.out,"w"),indent=2);print(json.dumps(res,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--launches",type=int,default=1000);p.add_argument("--max-seconds",type=int,default=7200);p.add_argument("--db",default="shadow04.sqlite");p.add_argument("--freeze",default="shadow04_freeze.json");p.add_argument("--out",default="shadow04_result.json");main(p.parse_args())
