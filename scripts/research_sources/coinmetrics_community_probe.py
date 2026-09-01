#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, io, json, urllib.request
from datetime import datetime, timezone
from typing import Any

CONTRACT="COINMETRICS_COMMUNITY_RESEARCH_PROBE_v0_1"
URL_TEMPLATE="https://raw.githubusercontent.com/coinmetrics/data/{ref}/csv/btc.csv"
UA={"User-Agent":"Investering-Research-Source-Probe/0.1","Accept":"text/csv"}
REQUIRED_FIELDS=("time","PriceUSD","CapMVRVCur")
AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False,"automatic_promotion":False}

class ProbeError(ValueError): pass

def sha256(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def now_utc()->str: return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def fetch_bytes(url:str)->bytes:
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=45) as r:
        raw=r.read()
        if getattr(r,"status",200)!=200: raise ProbeError(f"http_status_{r.status}")
        return raw

def summarize_csv(raw:bytes, source_ref:str)->dict[str,Any]:
    try: text=raw.decode("utf-8-sig")
    except UnicodeDecodeError as e: raise ProbeError("non_utf8_csv") from e
    reader=csv.DictReader(io.StringIO(text))
    fields=reader.fieldnames or []
    if "time" not in fields: raise ProbeError("missing_time_field")
    rows=0; earliest=None; latest=None
    non_null={k:0 for k in REQUIRED_FIELDS if k in fields}
    for row in reader:
        d=(row.get("time") or "").strip()
        if not d: continue
        rows+=1
        earliest=d if earliest is None or d<earliest else earliest
        latest=d if latest is None or d>latest else latest
        for k in non_null:
            if (row.get(k) or "").strip()!="": non_null[k]+=1
    if rows==0: raise ProbeError("no_rows")
    return {
        "contract":CONTRACT,
        "source":"COIN_METRICS_COMMUNITY_GITHUB_ARCHIVE",
        "source_ref":source_ref,
        "source_ref_mutable":source_ref in {"main","master"},
        "payload_sha256":sha256(raw),
        "payload_bytes":len(raw),
        "row_count":rows,
        "earliest_date":earliest,
        "latest_date":latest,
        "field_count":len(fields),
        "required_field_presence":{k:(k in fields) for k in REQUIRED_FIELDS},
        "non_null_counts":non_null,
        "raw_persisted":False,
        "authority":AUTHORITY,
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--ref",default="main",help="Git ref. Evidence runs should use an immutable commit SHA.")
    a=ap.parse_args()
    url=URL_TEMPLATE.format(ref=a.ref)
    receipt=summarize_csv(fetch_bytes(url),a.ref)
    receipt["url"]=url; receipt["retrieved_at_utc"]=now_utc()
    print(json.dumps(receipt,sort_keys=True,separators=(",",":")))
    return 0

if __name__=="__main__": raise SystemExit(main())
