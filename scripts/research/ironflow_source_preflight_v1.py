#!/usr/bin/env python3
"""Ironflow source provenance T1 audit. Research-only. CC BY 4.0, Ironflow."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

DATASETS={
"liquidations":("ironflow/hyperliquid-liquidations","7e89a460214631013946e081ffd06a84a65ee710","data/events"),
"funding":("ironflow/hyperliquid-funding","6e64357c3ff723a2c4f0e757ba708f2b71cca773","data"),
"oi":("ironflow/hyperliquid-open-interest","0106c103b4933263c96f727ddab02d771203e27b","data"),
"candles":("ironflow/hyperliquid-candles-1h","9f262cc27d89112b8c56550cf4c9455346f5eece","data")
}
MONTHS=("2025-10","2026-09","2026-10")
COLUMNS={
"liquidations":["timestamp","market","wallet","position_side","notional_usd"],
"funding":["timestamp","market","funding_rate"],
"oi":["timestamp","market","open_interest_usd","oracle_price","mark_price"],
"candles":["timestamp","market","market_class","open","high","low","close","volume"]
}
def sha256_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def check_parquet(p):
    with p.open("rb") as f:
        if f.read(4)!=b"PAR1":raise ValueError("Invalid Parquet magic")
def audit_one(root,month,family):
    p=root/family/(month+".parquet")
    if not p.exists():raise FileNotFoundError(str(p))
    if p.stat().st_size<1000 or p.stat().st_size>25000000:
        raise ValueError("Unexpected file size")
    check_parquet(p)
    d=pd.read_parquet(p,columns=COLUMNS[family])
    d["timestamp"]=pd.to_datetime(d.timestamp,utc=True,errors="coerce")
    if d.timestamp.isna().any():raise ValueError("Null or invalid timestamps")
    keys=["market","timestamp"]
    dup_count=int(d.duplicated(keys).sum()) if family!="liquidations" else None
    if dup_count and family!="liquidations":raise ValueError("Duplicate market/hour keys")
    m=d[d.market.isin(["BTC-PERP","ETH-PERP","HYPE-PERP"])]
    out={"source":DATASETS[family][0],"revision":DATASETS[family][1],
         "family":family,"month":month,"actual_bytes":p.stat().st_size,
         "actual_sha256":sha256_file(p),"actual_rows":len(d),
         "eligible_btc_eth_hype_rows":len(m),"duplicate_market_timestamp":dup_count,
         "utc_min":d.timestamp.min().isoformat(),"utc_max":d.timestamp.max().isoformat(),
         "null_count":{k:int(d[k].isna().sum()) for k in COLUMNS[family]}}
    if family=="candles":
        bad=((d.low>d.high)|(d.open<d.low)|(d.open>d.high)|(d.close<d.low)|(d.close>d.high))
        out["invalid_ohlc_bounds"]=int(bad.sum())
        if out["invalid_ohlc_bounds"]:raise ValueError("Invalid OHLC bounds")
    return out
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--months",nargs="+",choices=MONTHS,default=list(MONTHS))
    a=parser.parse_args()
    rows=[audit_one(a.root,m,k) for m in a.months for k in DATASETS]
    payload={"contract":"IRONFLOW_SOURCE_T1_v1","source_attribution":"Ironflow (ironflow.sh); CC BY 4.0",
             "temporal_class":"RETROSPECTIVE_ONLY_NO_2025_OR_OCT2026_PIT_CREDIT",
             "permitted_market_or_trade_action":False,"data":rows}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(payload,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({"status":"T1_SOURCE_QA_GENERATED","month_count":len(a.months),
                      "audited_files":len(rows),"output":str(a.output)}))
if __name__=="__main__":main()
