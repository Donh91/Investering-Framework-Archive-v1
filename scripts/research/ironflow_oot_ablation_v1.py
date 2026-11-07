#!/usr/bin/env python3
"""Conservative historical out-of-time ablation of liquidation/OI/funding.
Ironflow (ironflow.sh) CC BY 4.0. Selection contaminated; not sealed holdout.
Never use this to change Compass policy, leverage or portfolio actions.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from ironflow_dayblocked_study_v1 import load,day_anchors,M
from ironflow_hourly_stress_v1 import build

PRICE=("past_price_return_24h","past_volatility_24h")
DERIV=("liq_ratio_24h","oi_change_24h","settled_funding_sum_24h")
MARKETS=("ETH-PERP","HYPE-PERP")
def matrix(df,extra):
    z=pd.DataFrame(index=df.index)
    for market in MARKETS:z["market_"+market]=(df.market==market).astype(float)
    for col in PRICE:z[col]=pd.to_numeric(df[col],errors="coerce")
    if extra:
        z["log_liq_ratio_24h"]=np.log1p(df.liq_ratio_24h.clip(lower=0)*100)
        z["oi_change_24h"]=df.oi_change_24h
        z["settled_funding_sum_24h"]=df.settled_funding_sum_24h
    if not np.isfinite(z.to_numpy(dtype=float)).all():raise ValueError("invalid feature matrix")
    return z
def model_prob(train,test,extra):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    xtrain=matrix(train,extra).to_numpy(dtype=float)
    xtest=matrix(test,extra).to_numpy(dtype=float)
    scaler=StandardScaler()
    a=scaler.fit_transform(xtrain)
    b=scaler.transform(xtest)
    b=np.clip(b,-8,8)
    model=LogisticRegression(C=1.0,max_iter=2000,random_state=42)
    model.fit(a,train.drawdown_2pct_next_day.to_numpy(dtype=int))
    return model.predict_proba(b)[:,1]
def scores(y,probs):
    from sklearn.metrics import brier_score_loss,log_loss,roc_auc_score
    p=np.clip(probs,1e-5,1-1e-5)
    return {"n":int(len(y)),"positives":int(y.sum()),
            "brier":round(float(brier_score_loss(y,p)),6),
            "log_loss":round(float(log_loss(y,p,labels=[0,1])),6),
            "auc":round(float(roc_auc_score(y,p)),6) if len(set(y))>1 else None}
def paired_day_bootstrap(test,y,p0,p1):
    # Cluster by UTC day, three assets are not independent observations.
    losses0=(p0-y)**2
    losses1=(p1-y)**2
    dates=test.timestamp.dt.strftime("%Y-%m-%d").to_numpy()
    groups=[np.where(dates==d)[0] for d in sorted(set(dates))]
    rng=np.random.default_rng(22061106)
    diffs=[]
    for _ in range(1200):
        sel=rng.integers(0,len(groups),len(groups))
        indices=np.concatenate([groups[i] for i in sel])
        diffs.append(float((losses0[indices]-losses1[indices]).mean()))
    return {
        "n_date_clusters":len(groups),
        "base_minus_deriv_brier":round(float((losses0-losses1).mean()),6),
        "paired_day_bootstrap_95pct_interval":[round(float(v),6) for v in np.quantile(diffs,[0.025,0.975])],
        "interval_description":"DESCRIPTIVE_NOT_SEALED_HOLDOUT_INFERENCE"}
def evaluate(anchors):
    segments=[
        (["2025-10"],"2026-09"),
        (["2025-10","2026-09"],"2026-10")]
    out=[]
    for months,test_month in segments:
        train=anchors[anchors.month.isin(months)].copy()
        test=anchors[anchors.month==test_month].copy()
        # The 24h future-low label completes at anchor t + 25h, NOT at t.
        # The last train month's outcome may otherwise include test-month
        # price lows. Purge any training outcome not matured before test start.
        embargo_start=pd.Timestamp(test_month+"-01T00:00:00Z")
        train["target_matures_at_utc"]=train.timestamp+pd.Timedelta(hours=25)
        excluded=len(train)
        train=train[train.target_matures_at_utc<embargo_start].copy()
        excluded-=len(train)
        if train.empty or test.empty:raise ValueError("no train/test rows")
        y=test.drawdown_2pct_next_day.to_numpy(dtype=int)
        pconstant=np.full(len(y),train.drawdown_2pct_next_day.mean())
        pprice=model_prob(train,test,False)
        pderiv=model_prob(train,test,True)
        out.append({
            "train_months":months,"test_month":test_month,
            "n_train":len(train),"n_test":len(test),
            "purged_unmatured_training_labels":int(excluded),
            "max_training_target_maturity_utc":train.target_matures_at_utc.max().isoformat(),
            "test_month_start_utc":embargo_start.isoformat(),
            "clock":"at 00:00UTC after 23:00 completed hour",
            "baseline_constant":scores(y,pconstant),
            "baseline_price_vol_market":scores(y,pprice),
            "challenger_add_lagged_liq_oi_funding":scores(y,pderiv),
            "clustered_paired_brier":paired_day_bootstrap(test,y,pprice,pderiv),
            "verdict":"EXPLORATORY_WITH_EXPLICIT_SELECTION_CONTAMINATION"})
    return out
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--root",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    d=load(args.root,M)
    panel=build(d["candles"],d["oi"],d["funding"],d["liquidations"])
    anchors=day_anchors(panel)
    result={"contract":"IRONFLOW_T02_T03_OOT_ABLATION_V1",
        "source":"Ironflow (ironflow.sh), CC BY 4.0",
        "point_in_time_status":"POST_HOC_SOURCE_PUBLICATION_NOT_ORIGINAL_KNOWN",
        "sealing":"NOT_PRE_REGISTERED_BEFORE_EXPOSURE_TO_OCT2026_OUTCOMES",
        "effective_independence":"DAY_CLUSTERED_3_CORRELATED_ASSETS",
        "candidate_edge":"UNPROVEN","automatic_policy_or_trading_authority":False,
        "features_price":list(PRICE),"features_challenger":list(DERIV),
        "segments":evaluate(anchors)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"result":"RETROSPECTIVE_OOT_ABLATION_DONE","segments":len(result["segments"]),
                      "eligible_day_anchors":len(anchors)}))
if __name__=="__main__":main()
