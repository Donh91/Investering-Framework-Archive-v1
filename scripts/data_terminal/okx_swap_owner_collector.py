#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}
INSTRUMENTS=("BTC-USDT-SWAP","ETH-USDT-SWAP")
BASE="https://www.okx.com"
ENDPOINTS={"funding":"/api/v5/public/funding-rate","open_interest":"/api/v5/public/open-interest","mark_price":"/api/v5/public/mark-price"}
class E(RuntimeError):
    def __init__(self,status,msg): super().__init__(msg); self.status=status
def sha(b): return hashlib.sha256(b).hexdigest()
def fetch(url,timeout=12):
    req=urllib.request.Request(url,headers={"User-Agent":"Investering-OKX-Owner/1.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r: b=r.read()
    except urllib.error.HTTPError as e: raise E("HTTP_ERROR",f"HTTP {e.code}: {e.read()[:200]!r}") from e
    except Exception as e: raise E("NETWORK_ERROR",str(e)) from e
    if not b: raise E("EMPTY_RESPONSE","empty response")
    return b
def parse(payload,metric,inst):
    try: doc=json.loads(payload)
    except Exception as e: raise E("SCHEMA_DRIFT","invalid json") from e
    if str(doc.get("code"))!="0": raise E("SOURCE_ERROR",str(doc))
    data=doc.get("data")
    if not isinstance(data,list) or not data: raise E("EMPTY_RESPONSE","no data")
    row=data[0]
    if row.get("instId")!=inst: raise E("SCHEMA_DRIFT","instrument mismatch")
    if metric=="funding": out={"funding_rate":float(row["fundingRate"]),"next_funding_rate":float(row.get("nextFundingRate") or row["fundingRate"]),"funding_time":int(row["fundingTime"])}
    elif metric=="open_interest": out={"open_interest_contracts":float(row["oi"]),"open_interest_ccy":float(row["oiCcy"]),"timestamp":int(row["ts"])}
    else: out={"mark_price":float(row["markPx"]),"timestamp":int(row["ts"])}
    out.update({"venue":"OKX","instrument":inst,"metric":metric}); return out
def verify(root):
    m=json.loads((root/"artifact_manifest.json").read_text()); failures=[]
    for x in m["members"]:
        p=root/x["path"]
        if not p.is_file(): failures.append({"path":x["path"],"error":"MISSING"}); continue
        b=p.read_bytes()
        if len(b)!=x["bytes"] or sha(b)!=x["sha256"]: failures.append({"path":x["path"],"error":"HASH_OR_SIZE"})
    return {"status":"PASS" if not failures else "FAIL","member_count":len(m["members"]),"failures":failures}
def run(payloads,output,retrieval):
    output.mkdir(parents=True,exist_ok=True); raw=output/"raw"; raw.mkdir(exist_ok=True); rows=[]; lineage=[]
    for inst in INSTRUMENTS:
        for metric in ENDPOINTS:
            b=payloads[(inst,metric)]; name=f"{inst}_{metric}.json"; (raw/name).write_bytes(b)
            rows.append(parse(b,metric,inst)); lineage.append({"path":f"raw/{name}","bytes":len(b),"sha256":sha(b),"instrument":inst,"metric":metric})
    run_id="DT_OKX_SWAP_"+retrieval.replace('-','').replace(':','')[:15]+"_"+sha(json.dumps(lineage,sort_keys=True).encode())[:12]
    owner={"contract":"C5D1_OKX_SWAP_OWNER_v1","run_id":run_id,"retrieval_timestamp":retrieval,"venue":"OKX","instruments":list(INSTRUMENTS),"rows":rows,"interpolation":False,"forward_fill":False,"authority":AUTHORITY}
    receipt={"run_id":run_id,"source_id":"OKX_PUBLIC_SWAP_OWNER","source_payloads":lineage,"status":"PASS","authority":AUTHORITY}
    (output/"owner_snapshot.json").write_text(json.dumps(owner,indent=2,sort_keys=True)+"\n"); (output/"receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    members=[]
    for p in sorted(x for x in output.rglob('*') if x.is_file()):
        b=p.read_bytes(); members.append({"path":p.relative_to(output).as_posix(),"bytes":len(b),"sha256":sha(b)})
    (output/"artifact_manifest.json").write_text(json.dumps({"contract":"C5D1_ARTIFACT_MANIFEST_v1","run_id":run_id,"members":members},indent=2,sort_keys=True)+"\n"); return owner
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--fixture-dir',type=Path); ap.add_argument('--output-dir',type=Path,default=Path('okx-swap-owner-output')); ap.add_argument('--retrieval-timestamp'); a=ap.parse_args(); retrieval=a.retrieval_timestamp or datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    try:
        payloads={}
        for inst in INSTRUMENTS:
            for metric,path in ENDPOINTS.items():
                if a.fixture_dir: payloads[(inst,metric)]=(a.fixture_dir/f"{inst}_{metric}.json").read_bytes()
                else:
                    q={"instId":inst};
                    if metric in ("open_interest","mark_price"): q["instType"]="SWAP"
                    payloads[(inst,metric)]=fetch(BASE+path+'?'+urllib.parse.urlencode(q))
        owner=run(payloads,a.output_dir,retrieval); rb=verify(a.output_dir); print(json.dumps({"status":rb["status"],"run_id":owner["run_id"],"members":rb["member_count"]},sort_keys=True)); return 0 if rb["status"]=='PASS' else 3
    except E as e: print(json.dumps({"status":e.status,"error":str(e),"authority":AUTHORITY},sort_keys=True)); return 2
if __name__=='__main__': raise SystemExit(main())
