#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}
SYMBOLS=("BTCUSDT","ETHUSDT","ETHBTC")
BASE_URL="https://api.binance.com/api/v3/klines"

class CollectorError(RuntimeError):
    def __init__(self,status:str,message:str): super().__init__(message); self.status=status

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def iso_ms(ms:int)->str: return datetime.fromtimestamp(ms/1000,tz=timezone.utc).isoformat().replace("+00:00","Z")
def canonical(v)->bytes: return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def fetch(url:str,timeout:float=10)->bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"Investering-Spot-Owner/1.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            payload=r.read()
    except urllib.error.HTTPError as e:
        body=e.read().decode("utf-8","replace")
        status="GEO_RESTRICTED" if e.code in (403,451) or "restricted location" in body.lower() else "HTTP_ERROR"
        raise CollectorError(status,f"HTTP {e.code}: {body[:240]}") from e
    except (urllib.error.URLError,TimeoutError,OSError) as e: raise CollectorError("NETWORK_ERROR",str(e)) from e
    if not payload: raise CollectorError("EMPTY_RESPONSE","empty Binance payload")
    return payload

def parse(payload:bytes,symbol:str):
    try: rows=json.loads(payload)
    except Exception as e: raise CollectorError("SCHEMA_DRIFT","invalid JSON") from e
    if isinstance(rows,dict):
        msg=str(rows.get("msg",rows))
        status="GEO_RESTRICTED" if "restricted location" in msg.lower() else "SOURCE_ERROR"
        raise CollectorError(status,msg)
    if not isinstance(rows,list) or not rows: raise CollectorError("EMPTY_RESPONSE","no candle rows")
    out=[]; seen=set()
    for i,row in enumerate(rows):
        if not isinstance(row,list) or len(row)<12: raise CollectorError("SCHEMA_DRIFT",f"row {i} malformed")
        ot,ct=int(row[0]),int(row[6])
        if ot in seen: raise CollectorError("DUPLICATE_TIMESTAMP",f"{symbol} {ot}")
        seen.add(ot)
        try: o,h,l,c,v=map(float,(row[1],row[2],row[3],row[4],row[5]))
        except Exception as e: raise CollectorError("SCHEMA_DRIFT",f"row {i} numeric parse") from e
        if min(o,h,l,c,v)<0 or h<max(o,c) or l>min(o,c): raise CollectorError("INVALID_OHLC",f"row {i}")
        out.append({"symbol":symbol,"open_time":iso_ms(ot),"close_time":iso_ms(ct),"open":o,"high":h,"low":l,"close":c,"volume":v,"trades":int(row[8]),"closed":True})
    out.sort(key=lambda x:x["open_time"])
    return out

def verify(root:Path):
    m=json.loads((root/"artifact_manifest.json").read_text())
    failures=[]
    for item in m["members"]:
        p=root/item["path"]
        if not p.is_file(): failures.append({"path":item["path"],"error":"MISSING"}); continue
        b=p.read_bytes()
        if len(b)!=item["bytes"] or sha(b)!=item["sha256"]: failures.append({"path":item["path"],"error":"HASH_OR_SIZE"})
    return {"status":"PASS" if not failures else "FAIL","member_count":len(m["members"]),"failures":failures,"authority":AUTHORITY}

def run(payloads:dict[str,bytes],output:Path,retrieval:str,interval:str):
    output.mkdir(parents=True,exist_ok=True); raw=output/"raw"; raw.mkdir(exist_ok=True)
    normalized={}; lineage=[]
    for symbol in SYMBOLS:
        b=payloads[symbol]; (raw/f"{symbol}.json").write_bytes(b)
        normalized[symbol]=parse(b,symbol)
        lineage.append({"symbol":symbol,"path":f"raw/{symbol}.json","bytes":len(b),"sha256":sha(b)})
    run_id=f"DT_BINANCE_SPOT_{retrieval.replace('-','').replace(':','')[:15]}_{sha(canonical(lineage))[:12]}"
    owner={"contract":"WP04C5C_BINANCE_SPOT_OWNER_v1","run_id":run_id,"retrieval_timestamp":retrieval,"interval":interval,"symbols":list(SYMBOLS),"direct_ethbtc":True,"settled_only":True,"interpolation":False,"forward_fill":False,"candles":normalized,"authority":AUTHORITY}
    receipt={"run_id":run_id,"source_id":"BINANCE_SPOT_KLINES_OWNER","source_urls":{s:BASE_URL+"?"+urllib.parse.urlencode({"symbol":s,"interval":interval,"limit":1000}) for s in SYMBOLS},"source_payloads":lineage,"owner_sha256":sha(canonical(owner)),"status":"PASS","authority":AUTHORITY}
    (output/"owner_snapshot.json").write_text(json.dumps(owner,indent=2,sort_keys=True)+"\n")
    (output/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    members=[]
    for p in sorted(x for x in output.rglob("*") if x.is_file()):
        b=p.read_bytes(); members.append({"path":p.relative_to(output).as_posix(),"bytes":len(b),"sha256":sha(b)})
    manifest={"contract":"WP04C5C_ARTIFACT_MANIFEST_v1","run_id":run_id,"members":members,"member_count":len(members),"authority":AUTHORITY}
    (output/"artifact_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    return owner

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--fixture-dir",type=Path); ap.add_argument("--output-dir",type=Path,default=Path("binance-spot-owner-output")); ap.add_argument("--interval",default="1h"); ap.add_argument("--limit",type=int,default=1000); ap.add_argument("--retrieval-timestamp"); a=ap.parse_args()
    retrieval=a.retrieval_timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    try:
        payloads={}
        for s in SYMBOLS:
            if a.fixture_dir: payloads[s]=(a.fixture_dir/f"{s}.json").read_bytes()
            else: payloads[s]=fetch(BASE_URL+"?"+urllib.parse.urlencode({"symbol":s,"interval":a.interval,"limit":a.limit}))
        owner=run(payloads,a.output_dir,retrieval,a.interval); rb=verify(a.output_dir)
        print(json.dumps({"status":rb["status"],"run_id":owner["run_id"],"member_count":rb["member_count"]},sort_keys=True)); return 0 if rb["status"]=="PASS" else 3
    except CollectorError as e:
        print(json.dumps({"status":e.status,"error":str(e),"retrieval_timestamp":retrieval,"authority":AUTHORITY},sort_keys=True)); return 2
if __name__=="__main__": raise SystemExit(main())
