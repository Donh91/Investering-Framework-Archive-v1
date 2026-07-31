#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}
SYMBOLS=("BTCUSDT","ETHUSDT")
BASE="https://fapi.binance.com"
ENDPOINTS={
    "funding":"/fapi/v1/fundingRate",
    "open_interest":"/fapi/v1/openInterest",
    "mark_price":"/fapi/v1/premiumIndex"
}
REQUIRED_FIELDS={
    "funding":("fundingRate","fundingTime"),
    "open_interest":("openInterest","time"),
    "mark_price":("markPrice","time")
}

class CollectorError(RuntimeError):
    def __init__(self,status:str,message:str): super().__init__(message); self.status=status

def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def now_iso()->str: return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def fetch(url:str,timeout:float=15.0)->bytes:
    req=urllib.request.Request(url,headers={"User-Agent":"Investering-USDM-Owner/1.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=timeout) as response: payload=response.read()
    except urllib.error.HTTPError as exc:
        body=exc.read().decode("utf-8","replace")
        status="GEO_RESTRICTED" if exc.code in (403,451) or "restricted location" in body.lower() else "HTTP_ERROR"
        raise CollectorError(status,f"HTTP {exc.code}: {body[:240]}") from exc
    except (urllib.error.URLError,TimeoutError,OSError) as exc: raise CollectorError("NETWORK_ERROR",str(exc)) from exc
    if not payload: raise CollectorError("EMPTY_RESPONSE","empty payload")
    return payload

def parse(metric:str,symbol:str,payload:bytes,retrieval:str):
    if metric not in REQUIRED_FIELDS: raise CollectorError("UNSUPPORTED_METRIC",metric)
    try: data=json.loads(payload)
    except Exception as exc: raise CollectorError("SCHEMA_DRIFT","invalid JSON") from exc
    if isinstance(data,dict) and "code" in data and "msg" in data:
        message=str(data["msg"])
        status="GEO_RESTRICTED" if "restricted location" in message.lower() else "SOURCE_ERROR"
        raise CollectorError(status,message)
    rows=data if isinstance(data,list) else [data]
    if not rows or not all(isinstance(row,dict) for row in rows): raise CollectorError("SCHEMA_DRIFT",f"{metric} malformed")
    out=[]
    for index,row in enumerate(rows):
        missing=[field for field in REQUIRED_FIELDS[metric] if field not in row]
        if missing: raise CollectorError("SCHEMA_DRIFT",f"{metric} row {index} missing {','.join(missing)}")
        try:
            if metric=="funding":
                value=float(row["fundingRate"]); ts=int(row["fundingTime"]); units="decimal_rate"
            elif metric=="open_interest":
                value=float(row["openInterest"]); ts=int(row["time"]); units="base_asset"
            else:
                value=float(row["markPrice"]); ts=int(row["time"]); units="USDT"
        except (TypeError,ValueError,OverflowError) as exc:
            raise CollectorError("SCHEMA_DRIFT",f"{metric} row {index} numeric parse") from exc
        if ts < 0: raise CollectorError("INVALID_TIMESTAMP",f"negative {metric} timestamp")
        if value < 0 and metric != "funding": raise CollectorError("INVALID_VALUE",f"negative {metric}")
        out.append({"venue":"BINANCE_USDM","symbol":symbol,"metric":metric,"source_timestamp":datetime.fromtimestamp(ts/1000,tz=timezone.utc).isoformat().replace("+00:00","Z"),"retrieval_timestamp":retrieval,"value":value,"units":units,"missing":False})
    return out

def verify(root:Path):
    manifest=json.loads((root/"artifact_manifest.json").read_text())
    failures=[]
    for item in manifest["members"]:
        path=root/item["path"]
        if not path.is_file(): failures.append({"path":item["path"],"error":"MISSING"}); continue
        payload=path.read_bytes()
        if len(payload)!=item["bytes"] or sha(payload)!=item["sha256"]: failures.append({"path":item["path"],"error":"HASH_OR_SIZE"})
    return {"status":"PASS" if not failures else "FAIL","member_count":len(manifest["members"]),"failures":failures,"authority":AUTHORITY}

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--output-dir",type=Path,default=Path("binance-usdm-owner-output")); parser.add_argument("--funding-limit",type=int,default=100); args=parser.parse_args()
    retrieval=now_iso(); root=args.output_dir; raw=root/"raw"; raw.mkdir(parents=True,exist_ok=True)
    try:
        normalized=[]; lineage=[]
        for symbol in SYMBOLS:
            queries={
                "funding":{"symbol":symbol,"limit":args.funding_limit},
                "open_interest":{"symbol":symbol},
                "mark_price":{"symbol":symbol}
            }
            for metric,params in queries.items():
                url=BASE+ENDPOINTS[metric]+"?"+urllib.parse.urlencode(params)
                payload=fetch(url)
                path=raw/f"{symbol}__{metric}.json"; path.write_bytes(payload)
                lineage.append({"symbol":symbol,"metric":metric,"path":path.relative_to(root).as_posix(),"bytes":len(payload),"sha256":sha(payload),"url":url})
                normalized.extend(parse(metric,symbol,payload,retrieval))
        owner={"contract":"WP04C5D_BINANCE_USDM_OWNER_v1","retrieval_timestamp":retrieval,"rows":normalized,"interpolation":False,"forward_fill":False,"authority":AUTHORITY}
        (root/"owner_snapshot.json").write_text(json.dumps(owner,indent=2,sort_keys=True)+"\n")
        (root/"receipt.json").write_text(json.dumps({"status":"PASS","source_payloads":lineage,"authority":AUTHORITY},indent=2,sort_keys=True)+"\n")
        members=[]
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            payload=path.read_bytes(); members.append({"path":path.relative_to(root).as_posix(),"bytes":len(payload),"sha256":sha(payload)})
        (root/"artifact_manifest.json").write_text(json.dumps({"contract":"WP04C5D_ARTIFACT_MANIFEST_v1","members":members,"member_count":len(members),"authority":AUTHORITY},indent=2,sort_keys=True)+"\n")
        readback=verify(root); print(json.dumps({"status":readback["status"],"rows":len(normalized),"member_count":readback["member_count"]},sort_keys=True)); return 0 if readback["status"]=="PASS" else 3
    except CollectorError as exc:
        print(json.dumps({"status":exc.status,"error":str(exc),"retrieval_timestamp":retrieval,"authority":AUTHORITY},sort_keys=True)); return 2

if __name__=="__main__": raise SystemExit(main())
