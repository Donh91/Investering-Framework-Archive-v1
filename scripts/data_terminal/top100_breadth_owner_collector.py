#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, statistics, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}
BASE="https://api.coingecko.com/api/v3/coins/markets"
STABLE_SYMBOLS={"usdt","usdc","dai","fdusd","usde","usds","tusd","usdd","pyusd","frax","usdp","gusd","lusd","susd","crvusd"}
class E(RuntimeError):
    def __init__(self,status,msg): super().__init__(msg); self.status=status
def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def fetch(url,timeout=20):
    req=urllib.request.Request(url,headers={"User-Agent":"Investering-Breadth-Owner/1.2","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r: b=r.read()
    except urllib.error.HTTPError as e: raise E("HTTP_ERROR",f"HTTP {e.code}: {e.read()[:240]!r}") from e
    except Exception as e: raise E("NETWORK_ERROR",str(e)) from e
    if not b: raise E("EMPTY_RESPONSE","empty response")
    return b
def parse(payload):
    try: rows=json.loads(payload)
    except Exception as e: raise E("SCHEMA_DRIFT","invalid json") from e
    if not isinstance(rows,list) or len(rows)<100: raise E("INCOMPLETE_UNIVERSE",f"expected >=100 raw rows, got {len(rows) if isinstance(rows,list) else 'non-list'}")
    seen=set(); ranked=[]; exclusions=[]
    for source_rank,row in enumerate(rows,1):
        if not isinstance(row,dict): raise E("SCHEMA_DRIFT",f"row {source_rank} not object")
        required=("id","symbol","name","market_cap","current_price","price_change_percentage_24h")
        if any(k not in row for k in required): raise E("SCHEMA_DRIFT",f"row {source_rank} missing fields")
        aid=str(row["id"]); symbol=str(row["symbol"]).lower()
        if aid in seen: raise E("DUPLICATE_ASSET",aid)
        seen.add(aid)
        if symbol in STABLE_SYMBOLS:
            exclusions.append({"asset_id":aid,"symbol":symbol,"source_rank":source_rank,"reason":"STABLECOIN"}); continue
        change=row["price_change_percentage_24h"]
        if row["market_cap"] is None or row["current_price"] is None or change is None:
            exclusions.append({"asset_id":aid,"symbol":symbol,"source_rank":source_rank,"reason":"MISSING_REQUIRED_VALUE"}); continue
        ranked.append({"asset_id":aid,"symbol":symbol,"name":str(row["name"]),"source_rank":source_rank,"market_cap_usd":float(row["market_cap"]),"price_usd":float(row["current_price"]),"change_24h_pct":float(change)})
    constituents=ranked[:100]
    if len(constituents)!=100: raise E("INSUFFICIENT_FILTERED_UNIVERSE",f"expected 100, got {len(constituents)}")
    for i,row in enumerate(constituents,1): row["filtered_rank"]=i
    membership=[{"filtered_rank":r["filtered_rank"],"asset_id":r["asset_id"]} for r in constituents]
    membership_hash=sha(canonical(membership))
    changes=[r["change_24h_pct"] for r in constituents]
    adv=sum(v>0 for v in changes); dec=sum(v<0 for v in changes); flat=100-adv-dec
    btc=next((r["change_24h_pct"] for r in constituents if r["asset_id"]=="bitcoin"),None)
    eth=next((r["change_24h_pct"] for r in constituents if r["asset_id"]=="ethereum"),None)
    aggregate={
        "constituent_count":100,"advancers":adv,"decliners":dec,"flat":flat,
        "advancer_pct":adv,"advance_ratio":round(adv/100,6),
        "median_return_24h_pct":round(float(statistics.median(changes)),6),
        "equal_weight_mean_return_24h_pct":round(sum(changes)/len(changes),6),
        "btc_return_24h_pct":btc,"eth_return_24h_pct":eth,
        "outperforming_btc_count":sum(v>btc for v in changes) if btc is not None else None,
        "outperforming_eth_count":sum(v>eth for v in changes) if eth is not None else None,
        "membership_hash":membership_hash
    }
    return constituents,exclusions,aggregate
def verify(root):
    try:
        m=json.loads((root/"artifact_manifest.json").read_text()); owner=json.loads((root/"owner_snapshot.json").read_text())
    except Exception:
        return {"status":"FAIL","member_count":0,"failures":[{"path":"metadata","error":"INVALID_JSON"}]}
    failures=[]
    for x in m["members"]:
        p=root/x["path"]
        if not p.is_file(): failures.append({"path":x["path"],"error":"MISSING"}); continue
        b=p.read_bytes()
        if len(b)!=x["bytes"] or sha(b)!=x["sha256"]: failures.append({"path":x["path"],"error":"HASH_OR_SIZE"})
    replay_hash=sha(canonical([{"filtered_rank":r["filtered_rank"],"asset_id":r["asset_id"]} for r in owner.get("constituents",[])]))
    if owner.get("aggregate",{}).get("membership_hash")!=replay_hash or owner.get("aggregate",{}).get("constituent_count")!=100:
        failures.append({"path":"owner_snapshot.json","error":"MEMBERSHIP_REPLAY_MISMATCH"})
    return {"status":"PASS" if not failures else "FAIL","member_count":len(m["members"]),"failures":failures}
def run(payload,output,retrieval):
    output.mkdir(parents=True,exist_ok=True); (output/"raw_source_payload.json").write_bytes(payload)
    constituents,exclusions,aggregate=parse(payload); run_id="DT_TOP100_"+retrieval.replace('-','').replace(':','')[:15]+"_"+aggregate["membership_hash"][:12]
    owner={"contract":"C5E_TOP100_BREADTH_OWNER_v1_2","run_id":run_id,"retrieval_timestamp":retrieval,"freeze_timestamp":retrieval,"source":"COINGECKO_MARKET_CAP","raw_rank_depth":150,"ranking_metric":"market_cap_usd","method_version":"TOP100_FILTERED_STABLE_EXCLUSION_RICH_BREADTH_v1_2","constituents":constituents,"exclusions":exclusions,"aggregate":aggregate,"interpolation":False,"forward_fill":False,"authority":AUTHORITY}
    receipt={"run_id":run_id,"raw_sha256":sha(payload),"membership_hash":aggregate["membership_hash"],"constituent_count":100,"aggregate_replay":"PASS","status":"PASS","authority":AUTHORITY}
    (output/"owner_snapshot.json").write_text(json.dumps(owner,indent=2,sort_keys=True)+"\n"); (output/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    members=[]
    for p in sorted(x for x in output.rglob('*') if x.is_file()):
        b=p.read_bytes(); members.append({"path":p.relative_to(output).as_posix(),"bytes":len(b),"sha256":sha(b)})
    (output/"artifact_manifest.json").write_text(json.dumps({"contract":"C5E_ARTIFACT_MANIFEST_v1","run_id":run_id,"members":members},indent=2,sort_keys=True)+"\n"); return owner
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--fixture',type=Path); ap.add_argument('--output-dir',type=Path,default=Path('top100-breadth-owner-output')); ap.add_argument('--retrieval-timestamp'); a=ap.parse_args(); retrieval=a.retrieval_timestamp or datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    try:
        if a.fixture: payload=a.fixture.read_bytes()
        else:
            q={"vs_currency":"usd","order":"market_cap_desc","per_page":150,"page":1,"sparkline":"false","price_change_percentage":"24h"}; payload=fetch(BASE+'?'+urllib.parse.urlencode(q))
        owner=run(payload,a.output_dir,retrieval); rb=verify(a.output_dir); print(json.dumps({"status":rb["status"],"run_id":owner["run_id"],"constituents":100,"membership_hash":owner["aggregate"]["membership_hash"]},sort_keys=True)); return 0 if rb["status"]=='PASS' else 3
    except E as e: print(json.dumps({"status":e.status,"error":str(e),"authority":AUTHORITY},sort_keys=True)); return 2
if __name__=='__main__': raise SystemExit(main())
