#!/usr/bin/env python3
"""Ironflow complete common-history monthly walkforward, historical research ONLY.
Ironflow (ironflow.sh), CC BY 4.0, Nov-2026 source vintage. No live signal.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from ironflow_source_preflight_v1 import audit_one,DATASETS
from ironflow_hourly_stress_v1 import build
from ironflow_dayblocked_study_v1 import load,day_anchors
from ironflow_oot_ablation_v1 import model_prob,scores,paired_day_bootstrap

MONTHS=tuple(f"{year}-{month:02d}"
             for year in (2025,2026)
             for month in range(1,13)
             if (year==2025 and month>=5) or (year==2026 and month<=10))
def walkforward(anchors,months=MONTHS,min_train_months=6):
    """One fixed model family and two fixed baseline groups; no future-month training."""
    out=[]
    for k in range(min_train_months,len(months)):
        prior=set(months[:k])
        month=months[k]
        train=anchors[anchors.month.isin(prior)].copy()
        test=anchors[anchors.month==month].copy()
        # Target is 24 future hourly lows, not known until the final future
        # candle has closed. Freeze training before 00:00 UTC of test month.
        # Conservatively embargo the last 25h + equality boundary from train.
        test_month_start=pd.Timestamp(month+"-01T00:00:00Z")
        train["target_matures_at_utc"]=train.timestamp+pd.Timedelta(hours=25)
        embargoed=len(train)
        train=train[train.target_matures_at_utc<test_month_start].copy()
        embargoed-=len(train)
        if len(test)<10 or len(train)<60:
            out.append({"month":month,"status":"INSUFFICIENT_SOURCE_ANCHORS",
                        "train_n":len(train),"test_n":len(test)})
            continue
        y=test.drawdown_2pct_next_day.to_numpy(dtype=int)
        if len(np.unique(train.drawdown_2pct_next_day))<2:
            out.append({"month":month,"status":"TRAIN_ONE_CLASS","train_n":len(train),"test_n":len(test)})
            continue
        p0=np.full(len(test),float(train.drawdown_2pct_next_day.mean()))
        pb=model_prob(train,test,False)
        pdv=model_prob(train,test,True)
        uncertainty=paired_day_bootstrap(test,y,pb,pdv)
        per_market={}
        for market in ("BTC-PERP","ETH-PERP","HYPE-PERP"):
            mask=(test.market==market).to_numpy()
            yy=y[mask]
            if not len(yy): continue
            bm=scores(yy,pb[mask])
            dx=scores(yy,pdv[mask])
            per_market[market]={
                "n":int(len(yy)),
                "actual_next_24h_2pct_drawdown_rate":round(float(yy.mean()),6),
                "mean_price_only_predicted_prob":round(float(pb[mask].mean()),6),
                "mean_derivatives_predicted_prob":round(float(pdv[mask].mean()),6),
                "training_base_rate":round(float(train.drawdown_2pct_next_day.mean()),6),
                "price_only_brier":bm["brier"],
                "with_derivatives_brier":dx["brier"],
                "price_minus_derivatives_brier":round(bm["brier"]-dx["brier"],6),
                "source_quality_gate":"HISTORICAL_NOT_PIT"}
        out.append({"month":month,"status":"HISTORICAL_MONTH_REPLAY_OK",
                    "per_market_descriptive_failure_atlas":per_market,
                    "train_months":list(months[:k]),
                    "training_label_embargo_hours":25,
                    "training_boundary_cutoff_utc":test_month_start.isoformat(),
                    "training_labels_excluded_due_to_embargo":int(embargoed),
                    "max_train_label_maturity_utc":train.target_matures_at_utc.max().isoformat(),
                    "train_n":int(len(train)),"test_n":int(len(test)),
                    "test_distinct_UTC_dates":int(test.timestamp.dt.date.nunique()),
                    "constant":scores(y,p0),
                    "price_market_vol":scores(y,pb),
                    "plus_lagged_liquidations_oi_funding":scores(y,pdv),
                    "paired_day_uncertainty":uncertainty})
    return out
def summarize(results):
    rs=[x for x in results if x["status"]=="HISTORICAL_MONTH_REPLAY_OK"]
    diffs=np.array([r["paired_day_uncertainty"]["base_minus_deriv_brier"] for r in rs])
    if not len(diffs):return {"status":"NO_VALID_MONTHS","months":0}
    rng=np.random.default_rng(261106)
    # Month-level, not event-independent, descriptive uncertainty.
    boot=np.array([rng.choice(diffs,size=len(diffs),replace=True).mean()
                   for _ in range(2500)])
    return {"status":"DESCRIPTIVE_OVER_MONTHS_WITH_UNSEALED_ORIGINAL_SOURCE",
            "tested_months":int(len(rs)),
            "positive_months":int((diffs>0).sum()),
            "negative_months":int((diffs<0).sum()),
            "no_change_months":int((diffs==0).sum()),
            "mean_price_minus_derivative_brier":round(float(diffs.mean()),6),
            "month_bootstrap_95pct_interval":[round(float(x),6) for x in np.quantile(boot,[.025,.975])],
            "decision":"NO_CONFIRMED_TRADING_OR_INFORMATION_EDGE",
            "further_requirements":["original_original_time_first_known","new_frozen_forward_outcomes",
                                    "cross_venue_price_baselines","actual_user_delivery_and_trade_cost"]}
def source_checks(root,months=MONTHS):
    receipts=[]
    for month in months:
        for family in DATASETS:
            receipts.append(audit_one(root,month,family))
    return receipts
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--root",type=Path,required=True)
    a.add_argument("--output-dir",type=Path,required=True)
    args=a.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    receipts=source_checks(args.root)
    (args.output_dir/"FULL18M_T1_SOURCE_QA.json").write_text(
        json.dumps({"contract":"IRONFLOW_FULL18M_T1_QA_V1",
                    "source":"Ironflow (ironflow.sh), CC BY 4.0",
                    "status":"ACTUAL_FILES_SHA_VERIFIED_NOT_ORIGINAL_PIT",
                    "data":receipts},indent=2,allow_nan=False)+"\n")
    df=load(args.root,MONTHS)
    panel=build(df["candles"],df["oi"],df["funding"],df["liquidations"])
    anchors=day_anchors(panel)
    # February's missing day anchors must be explained from ORIGINAL source
    # field missingness, not silently dropped as if the market were quiet.
    feb=panel[(panel.timestamp>=pd.Timestamp("2026-02-10T00:00:00Z"))&
              (panel.timestamp<pd.Timestamp("2026-02-15T00:00:00Z"))].copy()
    feb["day_utc"]=feb.timestamp.dt.strftime("%Y-%m-%d")
    source_gap_census=[]
    for (market,day),part in feb.groupby(["market","day_utc"]):
        source_gap_census.append({
            "market":market,"day_utc":day,"hours":int(len(part)),
            "missing_open_interest_usd":int(part.open_interest_usd.isna().sum()),
            "missing_funding_rate":int(part.funding_rate.isna().sum()),
            "missing_prior_price_return":int(part.price_change_1h.isna().sum()),
            "missing_next_24h_drawdown_label":int(part.drawdown_next_24h.isna().sum()),
            "n_completed_23_utc_anchors":int((part.timestamp.dt.hour==23).sum())})
    results=walkforward(anchors)
    report={"contract":"IRONFLOW_FULL18M_CHRONOLOGICAL_REPLAY_V1",
            "source":"Ironflow (ironflow.sh), CC BY 4.0",
            "months":list(MONTHS),
            "dataset_vintage":"NOV_2026_POST_HOC",
            "initial_train_period":"2025-05..2025-10",
            "source_event_date_range":"2025-05-25..2026-10-31",
            "qualifying_day_anchors":int(len(anchors)),
            "eligible_hourly_rows":int(len(panel)),
            "privacy":"ONLY_SCOPED_PUBLIC_FUNDING_OI_CANDLE_LIQUIDATION_SUMMARIES",
            "source_first_known_at_original_era":"UNKNOWN",
            "real_trading_authority":False,
            "independent_confirmed_edge":False,
            "method":"expanding_train_6_months_then_12_monthly_out_of_time_tests_WITH_25H_PURGED_TRAIN_LABEL_BOUNDARY",
            "baseline_price_only":[ "market_dummies","past_price_return_24h","past_volatility_24h"],
            "additional_derivative_features":["liq_ratio_24h","oi_change_24h","settled_funding_sum_24h"],
            "hourly_clock":"completely_closed_hour_plus_1h",
            "outcome":"next_24h_any_downside_2pct",
            "selection_validity":"UNSEALED_HISTORICAL_RESEARCH_ONLY",
            "february_2026_original_source_hour_census":source_gap_census,
            "february_2026_eligible_utc_dates":{
                market:anchors[(anchors.month=="2026-02")&(anchors.market==market)].timestamp.dt.strftime("%Y-%m-%d").tolist()
                for market in ("BTC-PERP","ETH-PERP","HYPE-PERP")
            },
            "monthly_results":results,"month_summary":summarize(results)}
    (args.output_dir/"FULL18M_WALKFORWARD_RESEARCH.json").write_text(
        json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"result":"FULL18M_REPLAY_COMPLETED","files_verified":len(receipts),
                      "eligible_hourly_rows":report["eligible_hourly_rows"],
                      "day_anchors":report["qualifying_day_anchors"],
                      "tested_months":report["month_summary"].get("tested_months"),
                      "incremental_edge":"UNPROVEN"}))
if __name__=="__main__":main()
