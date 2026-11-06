#!/usr/bin/env python3
"""18-month Hyperliquid liquidation wallet ecology: PUBLIC AGGREGATES ONLY.
Data attribution: Ironflow (ironflow.sh), CC BY 4.0. No EOA exports,
no private-wallet inference, trading edge or wallet profit classification.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import pandas as pd

MONTHS=[f"{y}-{m:02d}" for y in (2025,2026) for m in range(1,13)
        if (y==2025 and m>=5) or (y==2026 and m<=10)]
SELECTED=("BTC-PERP","ETH-PERP","HYPE-PERP")

def run(root,months=MONTHS):
    ds=[]
    for month in months:
        p=root/"liquidations"/(month+".parquet")
        d=pd.read_parquet(p,columns=["timestamp","market","wallet","notional_usd","position_side"])
        d["timestamp"]=pd.to_datetime(d["timestamp"],utc=True,errors="coerce")
        if d.timestamp.isna().any() or d.wallet.isna().any() or d.notional_usd.isna().any():
            raise ValueError("invalid event provenance")
        if (d.notional_usd<0).any():raise ValueError("negative liquidation notional")
        if not d.position_side.isin(("long","short")).all():raise ValueError("liquidation side taxonomy drift")
        d["month"]=month
        ds.append(d)
    d=pd.concat(ds,ignore_index=True)
    latest=d.timestamp.max()
    w=d.groupby("wallet").agg(
        event_count=("wallet","size"),months=("month","nunique"),
        market_count=("market","nunique"),total_liquidated_notional=("notional_usd","sum"),
        first=("timestamp","min"))
    top=max(1,math.ceil(len(w)*0.01))
    total=float(d.notional_usd.sum())
    first_two=d.sort_values(["wallet","timestamp"],kind="stable").groupby("wallet",sort=False).head(2)
    first_two["seq"]=first_two.groupby("wallet").cumcount()
    times=first_two.pivot(index="wallet",columns="seq",values="timestamp")
    one=times[0]
    second=times[1] if 1 in times.columns else pd.Series(pd.NaT,index=times.index)
    next_delta=(second-one).dt.total_seconds()/86400
    recurrence={}
    for days in (7,30,90):
        eligible=one<=(latest-pd.Timedelta(days=days))
        n=int(eligible.sum())
        repeat=int((eligible & next_delta.ge(0) & next_delta.le(days)).sum())
        recurrence[str(days)+"d"]={
            "first_observed_liquidation_wallets_with_full_followup":n,
            "had_second_observed_liquidation_in_window":repeat,
            "repeat_event_rate":round(repeat/n,6) if n else None,
            "censoring":"left_truncated_at_data_start; post-final-event followup censored"}
    monthly=[]
    for month,x in d.groupby("month",sort=True):
        keys=x.groupby("wallet").notional_usd.sum().sort_values(ascending=False)
        share=float(keys.iloc[:max(1,math.ceil(len(keys)*.01))].sum()/keys.sum()) if keys.sum() else None
        monthly.append({
            "month":month,"all_markets_liquidated_positions":int(len(x)),
            "all_markets_liquidated_notional_usd":round(float(x.notional_usd.sum()),2),
            "unique_liquidated_wallet_addresses":int(x.wallet.nunique()),
            "long_liquidated_notional_usd":round(float(x.loc[x.position_side=="long","notional_usd"].sum()),2),
            "short_liquidated_notional_usd":round(float(x.loc[x.position_side=="short","notional_usd"].sum()),2),
            "top_1pct_liquidated_wallets_share_of_liquidated_notional":
                round(share,6) if share is not None else None,
            "BTC_ETH_HYPE_liquidated_position_events":int(x.market.isin(SELECTED).sum())})
    return {
        "contract":"IRONFLOW_18M_LIQUIDATION_WALLET_ECOLOGY_V1",
        "source":"Ironflow (ironflow.sh), CC BY 4.0",
        "interpretation":"OBSERVED_LIQUIDATION_CONCENTRATION_ONLY_NOT_TRADER_PNL_OR_ASSET_IDENTITY",
        "left_truncation":"start_of_publisher_archive_2025_05_25",
        "right_censoring_end":latest.isoformat(),
        "all_market_liquidation_events":int(len(d)),
        "distinct_liquidated_wallet_addresses":int(len(w)),
        "wallets_with_2plus_events":int((w.event_count>=2).sum()),
        "wallets_with_2plus_distinct_calendar_months":int((w.months>=2).sum()),
        "wallets_with_3plus_distinct_calendar_months":int((w.months>=3).sum()),
        "wallets_with_6plus_distinct_calendar_months":int((w.months>=6).sum()),
        "wallets_with_12plus_distinct_calendar_months":int((w.months>=12).sum()),
        "wallets_liquidated_in_2plus_markets":int((w.market_count>=2).sum()),
        "top_1pct_liquidated_wallet_share_total_notional":
            round(float(w.total_liquidated_notional.nlargest(top).sum()/total),6) if total else None,
        "repeated_liquidation_windows":recurrence,
        "month_cohorts":monthly,
        "economic_edge":"UNPROVEN",
        "actual_trades_or_profit_of_same_wallet":"UNOBSERVED_FULL_DENOMINATOR",
        "wallet_ownership_attribution":"NOT_AUTHORIZED_OR_PROVEN",
        "public_wallet_addresses_exported":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    out=run(a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":"RETROSPECTIVE_WALLET_ECOLOGY_COMPLETE",
                      "liquidated_positions":out["all_market_liquidation_events"],
                      "unique_addresses":out["distinct_liquidated_wallet_addresses"],
                      "no_wallet_PnL_claim":True}))
if __name__=="__main__":main()
