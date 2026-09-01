#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, statistics, urllib.parse, urllib.request
from datetime import datetime, timezone
from typing import Any

CONTRACT="BGEOMETRICS_RESEARCH_PROBE_v0_1"
BASE="https://api.bgeometrics.com/v1"
ALLOWED=("mvrv","sth-mvrv","sopr","vdd","urpd")
UA={"User-Agent":"Investering-Research-Source-Probe/0.1","Accept":"application/json"}
AUTHORITY={"binding":False,"canonical_acceptance":False,"state_change":False,"portfolio_action":False,"automatic_promotion":False}
PERSISTENCE={"raw_public_persistence":False,"receipt_only":True,"reason":"provider_terms_restrict_raw_redistribution"}

class ProbeError(ValueError): pass
def sha256(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def now_utc()->str: return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def fetch_bytes(url:str)->bytes:
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=45) as r:
        raw=r.read()
        if getattr(r,"status",200)!=200: raise ProbeError(f"http_status_{r.status}")
        return raw

def _date_value(row:dict[str,Any])->str|None:
    for k in ("theDate","d","date","time","timestamp","unixTs"):
        v=row.get(k)
        if v not in (None,""): return str(v)
    return None

def _as_float(v:Any)->float|None:
    try: return float(v)
    except (TypeError,ValueError): return None

def summarize_series(raw:bytes, metric:str)->dict[str,Any]:
    try: doc=json.loads(raw)
    except json.JSONDecodeError as e: raise ProbeError("invalid_json") from e
    if not isinstance(doc,list) or not doc: raise ProbeError("empty_or_nonlist_payload")
    fields=sorted({str(k) for r in doc if isinstance(r,dict) for k in r})
    dates=sorted(d for r in doc if isinstance(r,dict) and (d:=_date_value(r)) is not None)
    if not dates: raise ProbeError("no_dates")
    return {
        "contract":CONTRACT,"source":"BGEOMETRICS","metric":metric,
        "payload_sha256":sha256(raw),"payload_bytes":len(raw),"row_count":len(doc),
        "earliest_observation":dates[0],"latest_observation":dates[-1],
        "field_names":fields,"raw_persisted":False,"persistence":PERSISTENCE,"authority":AUTHORITY,
    }

def summarize_urpd(raw:bytes)->dict[str,Any]:
    try: doc=json.loads(raw)
    except json.JSONDecodeError as e: raise ProbeError("invalid_json") from e
    if not isinstance(doc,list) or not doc: raise ProbeError("empty_or_nonlist_payload")
    rows=[r for r in doc if isinstance(r,dict)]
    dates=sorted({str(r.get("theDate")) for r in rows if r.get("theDate")})
    if not dates: raise ProbeError("urpd_missing_snapshot_date")
    lows=[_as_float(r.get("priceLower")) for r in rows]; highs=[_as_float(r.get("priceUpper")) for r in rows]
    lows=[x for x in lows if x is not None]; highs=[x for x in highs if x is not None]
    pct=[_as_float(r.get("pctSupply")) for r in rows]; pct=[x for x in pct if x is not None]
    supply=[_as_float(r.get("btcSupply")) for r in rows]; supply=[x for x in supply if x is not None]
    widths=[h-l for l,h in zip(lows,highs) if h>=l] if len(lows)==len(highs) else []
    return {
        "contract":CONTRACT,"source":"BGEOMETRICS","metric":"urpd",
        "payload_sha256":sha256(raw),"payload_bytes":len(raw),"row_count":len(rows),
        "snapshot_dates":dates,"price_min":min(lows) if lows else None,"price_max":max(highs) if highs else None,
        "median_bin_width":statistics.median(widths) if widths else None,
        "pct_supply_sum":round(sum(pct),8) if pct else None,
        "btc_supply_sum":round(sum(supply),8) if supply else None,
        "raw_persisted":False,"persistence":PERSISTENCE,"authority":AUTHORITY,
    }

def build_url(metric:str, day:str|None)->str:
    if metric not in ALLOWED: raise ProbeError("metric_not_allowlisted")
    url=f"{BASE}/{metric}"
    if day:
        if metric!="urpd": raise ProbeError("day_only_allowed_for_urpd")
        url += "?" + urllib.parse.urlencode({"day":day})
    return url

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--metric",choices=ALLOWED,required=True)
    ap.add_argument("--day",help="Point-in-time URPD date YYYY-MM-DD.")
    a=ap.parse_args()
    url=build_url(a.metric,a.day); raw=fetch_bytes(url)
    receipt=summarize_urpd(raw) if a.metric=="urpd" else summarize_series(raw,a.metric)
    receipt["url"]=url; receipt["retrieved_at_utc"]=now_utc()
    print(json.dumps(receipt,sort_keys=True,separators=(",",":")))
    return 0

if __name__=="__main__": raise SystemExit(main())
