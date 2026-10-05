#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BASE_URL="https://data-api.binance.vision"
SYMBOL="BTCUSDT"
REFERENCE_TIME=datetime(2026,7,8,14,3,tzinfo=timezone.utc)
REFERENCE_PRICE=61784.48
MINUTE_MS=60_000

EXPECTED={
    24:{
        "high":63283.26,
        "low":61544.56,
        "close":63031.52,
        "maturity":datetime(2026,7,9,14,3,tzinfo=timezone.utc),
    },
    72:{
        "high":64692.83,
        "low":61544.56,
        "close":64248.00,
        "maturity":datetime(2026,7,11,14,3,tzinfo=timezone.utc),
    },
}


def canonical(o:Any)->bytes:
    return (json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()


def fetch_page(start_ms:int,end_ms:int)->tuple[list[list[Any]],str]:
    q=urllib.parse.urlencode({
        "symbol":SYMBOL,
        "interval":"1m",
        "startTime":start_ms,
        "endTime":end_ms-1,
        "limit":1000,
    })
    url=BASE_URL+"/api/v3/klines?"+q
    req=urllib.request.Request(url,headers={"User-Agent":"investering-framework-m6-t4-reconstruction/1.0"})
    with urllib.request.urlopen(req,timeout=60) as resp:
        raw=resp.read()
    obj=json.loads(raw)
    if not isinstance(obj,list):
        raise ValueError("invalid_binance_payload")
    return obj,hashlib.sha256(raw).hexdigest()


def fetch_window(start:datetime,end:datetime)->tuple[list[list[Any]],list[dict[str,Any]]]:
    s=int(start.timestamp()*1000)
    e=int(end.timestamp()*1000)
    rows=[]
    receipts=[]
    cursor=s
    while cursor<e:
        page,page_sha=fetch_page(cursor,e)
        if not page:
            raise ValueError(f"empty_page_at:{cursor}")
        receipts.append({
            "request_start_ms":cursor,
            "request_end_ms_exclusive":e,
            "row_count":len(page),
            "response_sha256":page_sha,
        })
        rows.extend(page)
        nxt=int(page[-1][0])+MINUTE_MS
        if nxt<=cursor:
            raise ValueError("pagination_not_advancing")
        cursor=nxt
    # exact window + unique sorted
    by={}
    for row in rows:
        if not isinstance(row,list) or len(row)<7:
            raise ValueError("invalid_kline_shape")
        ot=int(row[0]); ct=int(row[6])
        if ot<s or ot>=e:
            continue
        if ot%MINUTE_MS!=0 or ct!=ot+MINUTE_MS-1:
            raise ValueError("invalid_minute_interval")
        vals=[float(row[i]) for i in range(1,5)]
        if not all(math.isfinite(x) and x>0 for x in vals):
            raise ValueError("invalid_ohlc")
        if vals[1]<max(vals[0],vals[3]) or vals[2]>min(vals[0],vals[3]):
            raise ValueError("invalid_ohlc_geometry")
        if ot in by and by[ot]!=row:
            raise ValueError("conflicting_duplicate_minute")
        by[ot]=row
    ordered=[by[k] for k in sorted(by)]
    expected=int((end-start).total_seconds()/60)
    if len(ordered)!=expected:
        raise ValueError(f"incomplete_minute_window:{len(ordered)}!={expected}")
    for i,row in enumerate(ordered):
        if int(row[0])!=s+i*MINUTE_MS:
            raise ValueError(f"minute_gap_at:{i}")
    return ordered,receipts


def summarize(rows:list[list[Any]],hours:int)->dict[str,Any]:
    high=max(float(r[2]) for r in rows)
    low=min(float(r[3]) for r in rows)
    close=float(rows[-1][4])
    high_i=max(range(len(rows)),key=lambda i:float(rows[i][2]))
    low_i=min(range(len(rows)),key=lambda i:float(rows[i][3]))
    return {
        "horizon_hours":hours,
        "minute_count":len(rows),
        "horizon_high":high,
        "horizon_low":low,
        "horizon_close":close,
        "max_drawdown_pct":(low/REFERENCE_PRICE-1)*100,
        "max_rebound_pct":(high/REFERENCE_PRICE-1)*100,
        "close_move_from_reference_pct":(close/REFERENCE_PRICE-1)*100,
        "time_to_low_minutes":low_i,
        "time_to_high_minutes":high_i,
        "low_minute_open_utc":datetime.fromtimestamp(int(rows[low_i][0])/1000,tz=timezone.utc).isoformat().replace("+00:00","Z"),
        "high_minute_open_utc":datetime.fromtimestamp(int(rows[high_i][0])/1000,tz=timezone.utc).isoformat().replace("+00:00","Z"),
        "horizon_close_timestamp_utc":datetime.fromtimestamp(int(rows[-1][6])/1000,tz=timezone.utc).isoformat().replace("+00:00","Z"),
    }


def check_expected(got:dict[str,Any],expected:dict[str,Any],label:str)->dict[str,Any]:
    deltas={k:got[f"horizon_{k}"]-float(expected[k]) for k in ("high","low","close")}
    passed=all(abs(v)<=0.011 for v in deltas.values())
    return {"label":label,"passed":passed,"deltas_usd":deltas,"tolerance_usd":0.011}


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    end=REFERENCE_TIME+timedelta(days=7)
    rows,receipts=fetch_window(REFERENCE_TIME,end)

    summaries={}
    controls=[]
    for h in (24,72):
        n=h*60
        sm=summarize(rows[:n],h)
        summaries[str(h)]=sm
        controls.append(check_expected(sm,EXPECTED[h],f"{h}H_CANONICAL_POSITIVE_CONTROL"))
    if not all(x["passed"] for x in controls):
        raise SystemExit("CANONICAL_POSITIVE_CONTROL_FAILED")

    seven=summarize(rows,168)
    summaries["168"]=seven

    result={
        "contract":"M6_T4_7D_RESEARCH_RECONSTRUCTION_v1",
        "mission_id":"RL-DISTRIBUTION-SURVIVAL-META-006",
        "event_id":"PULLBACK_EDGE_20260708_01",
        "status":"RESEARCH_RECONSTRUCTED_NOT_ORIGINAL_MATURATION",
        "authority":{
            "historical_archive_rewrite":False,
            "canonical_t4_maturity":False,
            "market_rule_change":False,
            "portfolio_action":False,
        },
        "reference":{
            "timestamp_utc":REFERENCE_TIME.isoformat().replace("+00:00","Z"),
            "btc_price":REFERENCE_PRICE,
            "source":"CANONICAL_T4_EVENT_ANCHOR",
        },
        "source":{
            "provider":"BINANCE_PUBLIC_MARKET_DATA",
            "endpoint":BASE_URL+"/api/v3/klines",
            "symbol":SYMBOL,
            "interval":"1m",
            "window_end_exclusive_utc":end.isoformat().replace("+00:00","Z"),
            "request_receipts":receipts,
        },
        "positive_controls":controls,
        "summaries":summaries,
        "interpretation_boundary":[
            "24h and 72h canonical rows are used only as positive controls.",
            "168h is a research reconstruction because the scheduled original 7d maturity row is absent from current main.",
            "This artifact may inform M6 research but may not be inserted into historical T4 as if it had been persisted in July 2026.",
            "No sell, trim or portfolio rule follows from one episode.",
        ],
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(canonical(result))
    print(json.dumps({
        "status":"PASS",
        "positive_controls":controls,
        "seven_day":seven
    },sort_keys=True))


if __name__=="__main__":
    main()
