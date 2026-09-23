#!/usr/bin/env python3
"""Build v1.1 ETF features using trading sessions only; raw closure rows remain preserved."""
from __future__ import annotations
from pathlib import Path
import math
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
DECISION_REF="research/etf_temporal_integrity/2026-09-23/ETF_KNOWLEDGE_TIME_OWNER_DECISION_v1.json"

def load_asset(asset: str) -> pd.DataFrame:
    paths=sorted(DATA.glob(f"us_spot_{asset}_etf_flows_daily_*.csv"))
    if not paths: raise FileNotFoundError(asset)
    return pd.concat([pd.read_csv(p) for p in paths],ignore_index=True).sort_values("date").reset_index(drop=True)

def trading_sessions(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[df["session_status"].eq("TRADING_SESSION")].copy().reset_index(drop=True)

def streaks(series: pd.Series) -> tuple[list[int],list[int]]:
    positive,negative,ps,ns=[],[],0,0
    for value in series:
        if value>0: ps,ns=ps+1,0
        elif value<0: ps,ns=0,ns+1
        else: ps,ns=0,0
        positive.append(ps);negative.append(ns)
    return positive,negative

def main() -> None:
    generated=ROOT/"generated";generated.mkdir(exist_ok=True)
    longs,features,totals=[],[],[]
    for asset in ("btc","eth"):
        raw=load_asset(asset)
        funds=[c for c in raw.columns if c not in {"date","Total","session_status"}]
        long=raw.melt(id_vars=["date","session_status"],value_vars=funds+["Total"],var_name="fund",value_name="net_flow_usd_m")
        long.insert(1,"asset",asset.upper());long["is_total"]=long["fund"].eq("Total");longs.append(long)

        df=trading_sessions(raw)
        s=df["Total"].astype(float)
        feat=pd.DataFrame({"date":df["date"],"asset":asset.upper(),"session_status":df["session_status"],"total_flow_usd_m":s})
        for window in (3,5,10,20):
            feat[f"flow_sum_{window}s_usd_m"]=s.rolling(window,min_periods=1).sum()
            feat[f"flow_mean_{window}s_usd_m"]=s.rolling(window,min_periods=1).mean()
        feat["flow_change_1s_usd_m"]=s.diff()
        mean20=s.rolling(20,min_periods=5).mean()
        std20=s.rolling(20,min_periods=5).std(ddof=0).replace(0,math.nan)
        feat["flow_zscore_20s"]=(s-mean20)/std20
        for window in (5,20):
            feat[f"positive_sessions_{window}s"]=(s>0).astype(int).rolling(window,min_periods=1).sum().astype(int)
            feat[f"negative_sessions_{window}s"]=(s<0).astype(int).rolling(window,min_periods=1).sum().astype(int)
        feat["positive_streak_sessions"],feat["negative_streak_sessions"]=streaks(s)
        feat["cumulative_total_flow_usd_m"]=s.cumsum()
        values=df[funds].astype(float)
        feat["funds_positive_count"]=(values>0).sum(axis=1)
        feat["funds_negative_count"]=(values<0).sum(axis=1)
        feat["funds_zero_count"]=(values==0).sum(axis=1)
        feat["largest_inflow_fund"]=values.idxmax(axis=1)
        feat["largest_inflow_usd_m"]=values.max(axis=1)
        feat["largest_outflow_fund"]=values.idxmin(axis=1)
        feat["largest_outflow_usd_m"]=values.min(axis=1)
        feat["knowledge_time_status"]="NOT_ASSIGNED_BY_ROW_INTEGRITY_PACK"
        feat["knowledge_time_owner_decision_ref"]=DECISION_REF
        feat["feature_method_id"]="ETF_TRAILING_TRADING_SESSIONS_ONLY_v1_1"
        features.append(feat)
        totals.append(raw[["date","Total","session_status"]].rename(columns={"Total":f"{asset}_total_flow_usd_m","session_status":f"{asset}_session_status"}))

    pd.concat(longs,ignore_index=True).to_csv(generated/"us_spot_btc_eth_etf_flows_daily_long.csv",index=False,float_format="%.1f")
    pd.concat(features,ignore_index=True).to_csv(generated/"us_spot_btc_eth_etf_flow_trailing_features.csv",index=False,float_format="%.6f")
    totals[0].merge(totals[1],on="date",how="outer").sort_values("date").to_csv(generated/"us_spot_btc_eth_etf_daily_totals_join.csv",index=False,float_format="%.1f")

if __name__=="__main__":
    main()
