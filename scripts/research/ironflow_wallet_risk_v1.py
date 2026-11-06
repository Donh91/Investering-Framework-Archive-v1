#!/usr/bin/env python3
"""Public Hyperliquid liquidation wallet concentration study, NOT a smart-wallet score.
Source attribution: Ironflow (ironflow.sh), CC BY 4.0.
"""
import argparse,json
from pathlib import Path
import pandas as pd
MONTHS=("2025-10","2026-09","2026-10")
def analyze(root,months=MONTHS):
    ts=[]
    for m in months:
        p=root/"liquidations"/(m+".parquet")
        x=pd.read_parquet(p,columns=["timestamp","market","wallet","notional_usd","position_side"])
        x["timestamp"]=pd.to_datetime(x.timestamp,utc=True,errors="coerce")
        x["month"]=m
        ts.append(x)
    d=pd.concat(ts,ignore_index=True)
    if d.timestamp.isna().any() or d.wallet.isna().any() or (d.notional_usd<0).any():
        raise ValueError("missing/invalid event fields")
    report=[]
    for (m,market),x in d.groupby(["month","market"]):
        if market not in ("BTC-PERP","ETH-PERP","HYPE-PERP"):
            continue
        grouped=x.groupby("wallet").agg(liquidation_events=("wallet","size"),
                                        liquidated_notional_usd=("notional_usd","sum"))
        repeated=int((grouped.liquidation_events>1).sum())
        notional=grouped.liquidated_notional_usd.sort_values(ascending=False)
        k=max(1,int(len(notional)*0.01+0.999))
        report.append({
            "month":m,"market":market,"event_count":len(x),
            "distinct_public_wallet_count":len(grouped),
            "wallets_with_multiple_liquidations":repeated,
            "fraction_wallets_with_multiple_liquidations":round(repeated/len(grouped),6) if len(grouped) else None,
            "top_1pct_wallets_share_of_liquidated_notional":round(float(notional.iloc[:k].sum()/notional.sum()),6) if notional.sum()>0 else None,
            "long_events":int((x.position_side=="long").sum()),
            "short_events":int((x.position_side=="short").sum()),
            "interpretation":"LIQUIDATED_NOTIONAL_NOT_REALIZED_PROFIT_OR_INSIDER_LINK"})
    # Keep cross-month recurring EOA count aggregate, no wallet addresses in output.
    sub=d[d.market.isin(("BTC-PERP","ETH-PERP","HYPE-PERP"))]
    wallet_months=sub.groupby("wallet")["month"].nunique()
    overall={"distinct_public_wallet_count":int(wallet_months.size),
             "wallets_liquidated_in_at_least_two_studied_months":int((wallet_months>=2).sum()),
             "wallets_liquidated_in_all_three_studied_months":int((wallet_months>=3).sum())}
    return {"contract":"IRONFLOW_HL_WALLET_RISK_V1",
            "source":"Ironflow (ironflow.sh), CC BY 4.0",
            "classification":"RETROSPECTIVE_LOSS_EVENT_CHARACTERIZATION_ONLY",
            "wallet_profitability_proven":False,
            "not_equivalent_to_ethereum_memecoin_creator_or_ownership":True,
            "selection_window":list(months),
            "wallet_recurrence":overall,"market_month_cohorts":report}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    output=analyze(a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(output,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":"WALLET_CONCENTRATION_RESEARCH_ONLY",
                      "market_month_cohorts":len(output["market_month_cohorts"])}))
if __name__=="__main__":main()
