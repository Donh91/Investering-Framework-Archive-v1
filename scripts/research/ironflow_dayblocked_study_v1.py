#!/usr/bin/env python3
"""Day-blocked Ironflow causal-timing diagnostic. Descriptive research, NO edge admission.
Data: Ironflow (ironflow.sh) CC BY 4.0; frozen Nov-2026 historical snapshots.
"""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from ironflow_hourly_stress_v1 import build, H
M=("2025-10","2026-09","2026-10")
COL={
"candles":["timestamp","market","market_class","open","high","low","close","volume"],
"oi":["timestamp","market","open_interest_usd"],
"funding":["timestamp","market","funding_rate"],
"liquidations":["timestamp","market","position_side","notional_usd"]}
def load(root,months):
    out={}
    for k,cols in COL.items():
        t=[pd.read_parquet(root/k/(m+".parquet"),columns=cols) for m in months]
        out[k]=pd.concat(t,ignore_index=True)
    return out
def day_anchors(panel):
    pieces=[]
    for market,d in panel.groupby("market"):
        d=d.sort_values("timestamp").copy()
        d["segment"]=(d.timestamp.diff()!=H).cumsum()
        for _,x in d.groupby("segment",sort=False):
            x=x.copy()
            qv=(x.volume*x.close)
            rollvol=qv.rolling(24,min_periods=24).sum()
            x["liq_ratio_24h"]=x.liq_usd.rolling(24,min_periods=24).sum()/rollvol.replace(0,np.nan)
            x["past_price_return_24h"]=x.close/x.close.shift(24)-1
            x["past_volatility_24h"]=x.price_change_1h.rolling(24,min_periods=24).std(ddof=0)
            x["oi_change_24h"]=x.open_interest_usd/x.open_interest_usd.shift(24).replace(0,np.nan)-1
            x["settled_funding_sum_24h"]=x.funding_rate.rolling(24,min_periods=24).sum()
            x=x[(x.timestamp.dt.hour==23)].copy()
            need=["liq_ratio_24h","past_price_return_24h","past_volatility_24h",
                  "oi_change_24h","settled_funding_sum_24h","drawdown_next_24h"]
            x=x.dropna(subset=need)
            pieces.append(x[["market","timestamp","decision_at_utc",*need]].copy())
    if not pieces:raise ValueError("no 24h anchors")
    out=pd.concat(pieces,ignore_index=True).sort_values(["market","timestamp"])
    out["month"]=out.timestamp.dt.strftime("%Y-%m")
    out["drawdown_2pct_next_day"]=out.drawdown_next_24h<=-0.02
    out["liq_stress_1pct"]=out.liq_ratio_24h>0.01
    out["past_price_down_2pct"]=out.past_price_return_24h<=-0.02
    return out
def summary(a):
    rows=[]
    for (market,month),x in a.groupby(["market","month"]):
        for label,mask in [
            ("all_days",pd.Series(True,index=x.index)),
            ("liquidation_pressure_gt_1pct",x.liq_stress_1pct),
            ("liquidation_pressure_below_1pct",~x.liq_stress_1pct),
            ("past_price_down_gt_2pct",x.past_price_down_2pct),
            ("past_price_not_down_gt_2pct",~x.past_price_down_2pct)]:
            y=x.loc[mask,"drawdown_2pct_next_day"]
            rows.append({"market":market,"month":month,"cohort":label,
                         "n_nonoverlap_day_anchors":int(len(y)),
                         "next_24h_2pct_drawdown_rate":round(float(y.mean()),6) if len(y) else None})
        subset=x[x.liq_stress_1pct & (~x.past_price_down_2pct)]
        y=subset.drawdown_2pct_next_day
        rows.append({"market":market,"month":month,
                     "cohort":"liq_gt_1pct_without_prior_2pct_price_drop",
                     "n_nonoverlap_day_anchors":int(len(y)),
                     "next_24h_2pct_drawdown_rate":round(float(y.mean()),6) if len(y) else None})
    return rows
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    d=load(args.root,M)
    panel=build(d["candles"],d["oi"],d["funding"],d["liquidations"])
    anchors=day_anchors(panel)
    result={
        "contract":"IRONFLOW_DAYBLOCKED_RESEARCH_V1",
        "source":"Ironflow (ironflow.sh); CC BY 4.0",
        "status":"RETROSPECTIVE_NON_OVERLAPPING_DAILY_ANCHORS_ONLY",
        "selection_clock":"UTC 23:00 candle; decision eligible after UTC 00:00 of next day",
        "lookback_hours":24,"outcome_hours":24,
        "original_source_2025_or_Oct2026_asof":"UNPROVEN_NOV_2026_PUBLICATION",
        "no_independent_heldout_edge_or_trading_authority":True,
        "months":list(M),"n_day_anchors":len(anchors),
        "cohorts":summary(anchors)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":"DAYBLOCKED_COMPLETE","n_day_anchors":len(anchors),
                      "output":str(args.output)}))
if __name__=="__main__":main()
