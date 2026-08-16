#!/usr/bin/env python3
from __future__ import annotations
import argparse, gzip, hashlib, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE="https://stablecoins.llama.fi"
UA={"User-Agent":"Investering-Stablecoin-Owner/1.1","Accept":"application/json"}
AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}

def now_utc()->str: return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def canonical(v:Any)->bytes: return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def fetch(path:str)->tuple[Any,dict[str,Any]]:
    url=BASE+path; req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=30) as r: raw=r.read(); status=r.status
    return json.loads(raw),{"url":url,"http_status":status,"payload_sha256":sha(raw),"payload_bytes":len(raw)}
def usd(v:Any)->float|None:
    if isinstance(v,(int,float)): return float(v)
    if isinstance(v,dict):
        for k in ("peggedUSD","usd","USD"):
            if isinstance(v.get(k),(int,float)): return float(v[k])
    return None
def chart_rows(doc:Any)->list[dict[str,Any]]:
    if not isinstance(doc,list): return []
    out=[]
    for r in doc:
        if not isinstance(r,dict): continue
        raw_date=r.get("date") or r.get("timestamp"); total=usd(r.get("totalCirculatingUSD"))
        if total is None: total=usd(r.get("totalCirculating"))
        try: ts=int(raw_date)
        except Exception: continue
        if total is not None: out.append({"timestamp":ts,"total_usd":total})
    return sorted(out,key=lambda x:x["timestamp"])
def nearest_back(rows:list[dict[str,Any]],seconds:int)->dict[str,Any]|None:
    if not rows:return None
    target=rows[-1]["timestamp"]-seconds; eligible=[r for r in rows if r["timestamp"]<=target]
    return eligible[-1] if eligible else None
def pct(latest:float,old:dict[str,Any]|None)->float|None:
    if not old or not old.get("total_usd"):return None
    return round((latest/float(old["total_usd"])-1)*100,6)
def chains(doc:Any)->list[dict[str,Any]]:
    if not isinstance(doc,list): return []
    out=[]
    for r in doc:
        if not isinstance(r,dict): continue
        total=usd(r.get("totalCirculatingUSD")); name=r.get("name") or r.get("chain")
        if name and total is not None: out.append({"chain":str(name),"total_usd":total})
    return sorted(out,key=lambda x:x["total_usd"],reverse=True)
def write_history(path:Path,rows:list[dict[str,Any]])->dict[str,Any]:
    body=b"".join(canonical(r)+b"\n" for r in rows)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="",mode="wb",fileobj=fh,mtime=0) as gz: gz.write(body)
    compressed=path.read_bytes()
    return {"path":str(path),"row_count":len(rows),"uncompressed_sha256":sha(body),"compressed_sha256":sha(compressed),"compressed_bytes":len(compressed),"deterministic_gzip_mtime":0}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output-root",type=Path,default=Path("03_DAILY_CAPTURE_LOGS/stablecoin_liquidity")); a=ap.parse_args()
    retrieval_start=now_utc()
    chart,cr=fetch("/stablecoincharts/all"); chain_doc,ccr=fetch("/stablecoinchains")
    retrieval_complete=now_utc()
    rows=chart_rows(chart)
    if not rows: raise SystemExit("stablecoin_global_chart_unparseable")
    latest=rows[-1]; chain_rows=chains(chain_doc)
    history=write_history(a.output_root/"backfill"/"global_history.jsonl.gz",rows)
    normalization_time=now_utc()
    payload={"contract":"DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1","retrieved_at_utc":retrieval_complete,"source":"DEFILLAMA_STABLECOINS","lifecycle":{"retrieval_start_time":retrieval_start,"retrieval_complete_time":retrieval_complete,"normalization_time":normalization_time},"global":{"timestamp":latest["timestamp"],"total_usd":latest["total_usd"],"change_1d_pct":pct(latest["total_usd"],nearest_back(rows,86400)),"change_7d_pct":pct(latest["total_usd"],nearest_back(rows,7*86400)),"change_30d_pct":pct(latest["total_usd"],nearest_back(rows,30*86400))},"historical_backfill":history,"chains":chain_rows,"source_receipts":{"global_chart":cr,"chains":ccr},"interpolation":False,"forward_fill":False,"authority":AUTHORITY}
    payload["payload_sha256"]=sha(canonical(payload)); day=a.output_root/datetime.now(timezone.utc).strftime("%Y/%m/%d"); day.mkdir(parents=True,exist_ok=True); path=day/f"{datetime.now(timezone.utc).strftime('%H%M%S')}.json"; path.write_bytes(canonical(payload)+b"\n"); (a.output_root/"LATEST.json").write_bytes(canonical(payload)+b"\n"); print(json.dumps({"status":"PASS","global_total_usd":latest["total_usd"],"historical_rows":history["row_count"],"chain_count":len(chain_rows),"payload_sha256":payload["payload_sha256"],"lifecycle":payload["lifecycle"]},sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
