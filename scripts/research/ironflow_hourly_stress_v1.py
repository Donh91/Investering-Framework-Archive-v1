#!/usr/bin/env python3
"""Ironflow historic hourly stress challenger. Ironflow (ironflow.sh), CC BY 4.0.
Descriptive development only: overlapping hours are NOT independent events.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
H=pd.Timedelta(hours=1)
MARKETS=("BTC-PERP","ETH-PERP","HYPE-PERP")
def build(c,o,f,l):
    for name,d in [("candles",c),("oi",o),("funding",f),("liquidations",l)]:
        d["timestamp"]=pd.to_datetime(d.timestamp,utc=True,errors="coerce")
        if d.timestamp.isna().any():raise ValueError("bad "+name+" timestamps")
    c=c[c.market.isin(MARKETS)&(c.market_class=="perp")].copy()
    o=o[o.market.isin(MARKETS)].copy()
    f=f[f.market.isin(MARKETS)].copy()
    l=l[l.market.isin(MARKETS)].copy()
    for name,d in [("candles",c),("oi",o),("funding",f)]:
        if d.duplicated(["market","timestamp"]).any():raise ValueError("duplicate "+name)
    if ((c.low>c.high)|(c.open<c.low)|(c.open>c.high)|(c.close<c.low)|(c.close>c.high)).any():
        raise ValueError("bad OHLC")
    l["hour"]=l.timestamp.dt.floor("h")
    l["long_usd"]=l.notional_usd.where(l.position_side=="long",0)
    liq=l.groupby(["market","hour"],as_index=False).agg(
        liq_usd=("notional_usd","sum"),
        liq_events=("notional_usd","size"),liq_long_usd=("long_usd","sum"))
    liq=liq.rename(columns={"hour":"timestamp"})
    d=c.merge(o[["market","timestamp","open_interest_usd"]],on=["market","timestamp"],how="left",validate="one_to_one")
    d=d.merge(f[["market","timestamp","funding_rate"]],on=["market","timestamp"],how="left",validate="one_to_one")
    d=d.merge(liq,on=["market","timestamp"],how="left",validate="one_to_one")
    for col in ("liq_usd","liq_events","liq_long_usd"):d[col]=d[col].fillna(0)
    d=d.sort_values(["market","timestamp"]).copy()
    d["decision_at_utc"]=d.timestamp+H
    d["liquidation_ratio_to_approx_quote_volume"]=d.liq_usd/(d.close*d.volume).replace(0,np.nan)
    outputs=[]
    for market,x in d.groupby("market"):
        x=x.copy()
        continuous=x.timestamp.diff()==H
        x["price_change_1h"]=(x.close/x.close.shift(1)-1).where(continuous)
        x["oi_change_1h"]=(x.open_interest_usd/x.open_interest_usd.shift(1).replace(0,np.nan)-1).where(continuous)
        for hours in (4,12,24,72):
            clock_ok=(x.timestamp.shift(-hours)-x.timestamp)==hours*H
            min_low=x.low.shift(-1).rolling(hours,min_periods=hours).min().shift(1-hours)
            x["drawdown_next_"+str(hours)+"h"]=(min_low/x.close-1).where(clock_ok)
            x["return_next_"+str(hours)+"h"]=(x.close.shift(-hours)/x.close-1).where(clock_ok)
        outputs.append(x)
    if not outputs:raise ValueError("no eligible markets")
    return pd.concat(outputs,ignore_index=True)
def describe(d):
    answer=[]
    for market,x in d.groupby("market"):
        for h in (4,12,24,72):
            y=x["drawdown_next_"+str(h)+"h"]
            eligible=y.notna()&x.price_change_1h.notna()&x.liquidation_ratio_to_approx_quote_volume.notna()
            cohorts={
                "all":eligible,
                "liquidations_gt_1pct_quote_volume":eligible&(x.liquidation_ratio_to_approx_quote_volume>0.01),
                "liquidations_gt_5pct_quote_volume":eligible&(x.liquidation_ratio_to_approx_quote_volume>0.05),
                "price_down_gt_1pct_last_1h":eligible&(x.price_change_1h<=-0.01),
                "open_interest_up_gt_1pct_last_1h":eligible&(x.oi_change_1h>=0.01)
            }
            for label,mask in cohorts.items():
                z=y[mask]
                answer.append({"market":market,"horizon_h":h,"cohort":label,
                    "n_overlapping_hours":int(len(z)),
                    "next_drawdown_ge_2pct_rate":float((z<=-0.02).mean()) if len(z) else None,
                    "median_next_drawdown":float(z.median()) if len(z) else None,
                    "note":"NOT_INDEPENDENT_NOT_OOS_NO_EDGE_CLAIM"})
    return answer
def run(root,months):
    results=[]
    for m in months:
        base={name:root/name/(m+".parquet") for name in ["candles","oi","funding","liquidations"]}
        for p in base.values():
            if not p.exists():raise FileNotFoundError(str(p))
        df={k:pd.read_parquet(v) for k,v in base.items()}
        d=build(df["candles"],df["oi"],df["funding"],df["liquidations"])
        by_market={m:int(c) for m,c in d.market.value_counts().items()}
        missing={k:int(d[k].isna().sum()) for k in ("open_interest_usd","funding_rate","price_change_1h")}
        results.append({"month":m,"eligible_hourly_rows":int(len(d)),"market_rows":by_market,
                        "missing":missing,"cohorts":describe(d)})
    return {"contract":"IRONFLOW_HOURLY_HISTORICAL_V1","status":"AFTER_FACT_DEVELOPMENT_ONLY",
        "source":"Ironflow (ironflow.sh), CC BY 4.0",
        "original_issue_time_provenance":"NOT_AVAILABLE_FROM_NOV_2026_SNAPSHOT",
        "signal_skill":"UNPROVEN","trading_or_alert_permission":False,
        "results":results}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--months",nargs="+",default=["2025-10","2026-09","2026-10"])
    args=p.parse_args()
    out=run(args.root,args.months)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":"RESEARCH_ONLY","months":len(out["results"]),"output":str(args.output)}))
if __name__=="__main__":main()
