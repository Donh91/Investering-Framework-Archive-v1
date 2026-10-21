#!/usr/bin/env python3
"""Task2: incremental archived CFGI v3 over price+realized-vol chronological control.

This is an *inspected-history* train/validation/test diagnostic, NOT an untouched
pre-registered holdout, true provider PIT, original Compass forecast or alpha.
Public Daily Capture anchors only; never reads restricted Round3 provider data.
No secrets, external calls, threshold search, trading, strategy promotion.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from scripts.research import task2_cfgi_64d_expost_cohorts_v1 as archive
from scripts.research import task2_cfgi_price_expost_4h_v1 as simple
from scripts.research import task2_cfgi_capture_clock_audit_v1 as source

CONTRACT="TASK2_CFGI_INCREMENTAL_PRICE_VOL_CHRONOLOGY_v1"
AUTHORITY={"research_only":True,"round3_private_values_read":False,
           "private_source_write":False,"hypothesis_registered_before_outcomes":False,
           "original_compass_issued_predictions_scored":False,
           "provider_first_publication_proven":False,"original_price_first_known_proven":False,
           "holdout_unseen_before_study_design":False,"investable_after_cost_edge":False,
           "live_rule_change":False,"new_provider_requests":False}

# Frozen ex-post study dates. 24h train/validation and 72h validation/test
# embargoes are wider than the 4h outcome horizon. Test period already analysed
# in past development and is NOT pristine OOS.
TRAIN_END=date(2026,9,27)
VAL_START=date(2026,9,29)
VAL_END=date(2026,10,5)
TEST_START=date(2026,10,9)
TEST_END=date(2026,10,20)
HOUR=timedelta(hours=1)
BASE_FIELDS=("mom4_pct","vol8_pct")
AUG_FIELDS=("mom4_pct","vol8_pct","cfgi_centered")
RIDGE=0.3
LEARNING_RATE=0.08
ITERATIONS=750

def vintage_partition(day):
    if day<=TRAIN_END:return "train"
    if VAL_START<=day<=VAL_END:return "validation"
    if TEST_START<=day<=TEST_END:return "test_inspected_history"
    return "embargo_not_scored"

def past_realized_vol(prices, base_clock, symbol):
    """8 realized hourly log returns using ONLY completed spot candles at/before base."""
    vals=[]
    for j in range(8,-1,-1):
        time=base_clock-j*HOUR
        item=prices.get(time)
        if item is None:return None
        p=simple.usd_price(item,symbol)
        if p is None:return None
        vals.append(p)
    rets=[math.log(vals[i]/vals[i-1]) for i in range(1,len(vals))]
    mean=sum(rets)/8
    vol=math.sqrt(sum((x-mean)**2 for x in rets)/8)*100
    return vol if math.isfinite(vol) else None

def source_cases(captures, prices):
    """One earliest valid CFGI event per exact symbol/provider-row timestamp."""
    out=[];counts=Counter();source_receipts=[]
    keys=set()
    for day in archive.day_iter(archive.START,archive.END):
        folder=captures/day.strftime("%Y/%m/%d")
        paths=sorted(folder.glob("*.json"))
        counts["source_original_capture_files"]+=len(paths)
        for file in paths:
            raw=file.read_bytes()
            doc=json.loads(raw)
            receipt={"git_blob_sha1":source.git_blob(raw),"file":file.relative_to(captures).as_posix()}
            source_receipts.append(receipt)
            try:meta=source.permitted_metadata(doc,source_name=file.name)
            except (KeyError,ValueError,TypeError):
                counts["excluded_capture_source_receipt_invalid"]+=1
                continue
            local_clock=source.time_utc(meta["capture_utc"])
            if local_clock.date()!=day:raise ValueError("ORIGINAL_CAPTURE_FOLDER_DAY_MISMATCH")
            own=next(x for x in doc["owners"] if x["owner_id"]=="cfgi_sentiment")
            snap=next(x["summary"] for x in own["files"] if x["path"]=="cfgi-owner-output/owner_snapshot.json")
            cases=simple.classify_opportunity(snap,meta,prices)
            counts["validated_original_capture_count"]+=1
            base=local_clock.replace(minute=0,second=0,microsecond=0)-HOUR
            for row in cases:
                symbol=row["symbol"]
                original_stamp=meta["source_symbol_times"][symbol]["original_row_utc"]
                ident=(symbol,original_stamp)
                counts["symbol_original_candidates"]+=1
                if ident in keys:
                    counts["excluded_duplicate_provider_source_timestamp"]+=1
                    continue
                keys.add(ident)
                if row["state"]!="EXPOST_JOIN_ONLY":
                    counts["excluded_"+row["state"]]+=1
                    continue
                vol=past_realized_vol(prices,base,symbol)
                if vol is None:
                    counts["excluded_missing_past_volatility"]+=1
                    continue
                day_part=vintage_partition(day)
                counts["time_partition_"+day_part]+=1
                # Original source/scores/prices never exported to report.
                out.append({"symbol":symbol,"day":day.isoformat(),"week":f"{day.isocalendar().year}-W{day.isocalendar().week:02d}",
                            "partition":day_part,"mom4_pct":row["momentum_4h_pct"],
                            "vol8_pct":vol,"cfgi_centered":row["score_centered"],
                            "y":int(row["following_4h_pct"]>0),
                            "future_flat":int(row["following_4h_pct"]==0),
                            "price_batch_end_uncertain":row["price_batch_end_after_nominal_close"]})
    if counts["validated_original_capture_count"]<100 or len(out)<400:
        raise ValueError("INSUFFICIENT_PROSPECTIVE_ARCHIVE_SOURCE_CENSUS")
    return out,counts,source_receipts

def sigmoid(x):
    return 1/(1+math.exp(-max(-25,min(25,x))))

def transform_fit(rows,fields):
    if len(rows)<20:raise ValueError("INSUFFICIENT_FIT_SAMPLE")
    center=[];scale=[]
    for field in fields:
        values=[float(r[field]) for r in rows]
        if not all(math.isfinite(v) for v in values):raise ValueError("NONFINITE_TRAIN_FEATURE")
        mu=sum(values)/len(values)
        std=math.sqrt(sum((v-mu)**2 for v in values)/len(values))
        center.append(mu);scale.append(max(std,1e-9))
    return center,scale

def transform(row, fields, center, scale):
    return [1.0]+[max(-6,min(6,(row[field]-c)/s)) for field,c,s in zip(fields,center,scale)]

def fit(rows, fields):
    center,scale=transform_fit(rows,fields)
    matrix=[transform(r,fields,center,scale) for r in rows]
    coeff=[0.0]*(len(fields)+1)
    for _ in range(ITERATIONS):
        grad=[0.0]*len(coeff)
        for row,x in zip(rows,matrix):
            z=sum(w*v for w,v in zip(coeff,x))
            error=sigmoid(z)-row["y"]
            for j in range(len(coeff)):grad[j]+=error*x[j]
        n=len(rows)
        for j in range(len(coeff)):
            grad[j]=grad[j]/n+(RIDGE*coeff[j] if j>0 else 0.0)
            coeff[j]-=LEARNING_RATE*grad[j]
    if not all(math.isfinite(v) for v in coeff):raise ValueError("NONFINITE_FITTED_PARAMETERS")
    return {"fields":fields,"center":center,"scale":scale,"coef":coeff}

def predict(model,row):
    xx=transform(row,model["fields"],model["center"],model["scale"])
    return sigmoid(sum(w*v for w,v in zip(model["coef"],xx)))

def metrics(rows,models):
    def arm(model):
        predicted=[predict(model,r) for r in rows]
        if not predicted:return None
        brier=sum((p-r["y"])**2 for p,r in zip(predicted,rows))/len(rows)
        logloss=-sum(r["y"]*math.log(max(1e-9,p))+(1-r["y"])*math.log(max(1e-9,1-p)) for p,r in zip(predicted,rows))/len(rows)
        yes=sum(1 for p,r in zip(predicted,rows) if p>=0.5 and r["y"]==1)
        no=sum(1 for p,r in zip(predicted,rows) if p<0.5 and r["y"]==0)
        return {"n":len(rows),"brier":round(brier,8),"logloss":round(logloss,8),
                "accuracy_0_5_threshold":round((yes+no)/len(rows),6)}
    base=arm(models["price_vol"])
    aug=arm(models["price_vol_cfgi"])
    return {"rows":len(rows),
            "distinct_utc_calendar_days":len({r["day"] for r in rows}),
            "distinct_iso_weeks":len({r["week"] for r in rows}),
            "positive_outcome":sum(r["y"] for r in rows),
            "negative_outcome":sum(r["y"]==0 for r in rows),
            "future_flat_rows":sum(r["future_flat"] for r in rows),
            "price_batch_clock_unverified":sum(r["price_batch_end_uncertain"] for r in rows),
            "price_vol":base,"price_vol_cfgi":aug,
            "descriptive_brier_improvement_vs_price_vol":round(base["brier"]-aug["brier"],8) if base and aug else None,
            "descriptive_logloss_improvement_vs_price_vol":round(base["logloss"]-aug["logloss"],8) if base and aug else None,
            "market_edge_admitted":False}

def execute(capture_root=archive.CAPTURE_ROOT,spot_root=archive.PRICE_ROOT):
    spot,receipt,missing,partial=archive.spot_index(spot_root)
    rows,counts,captures=source_cases(capture_root,spot)
    split={}
    for symbol in simple.SYMBOLS:
        by=[r for r in rows if r["symbol"]==symbol]
        train=[r for r in by if r["partition"]=="train"]
        validation=[r for r in by if r["partition"]=="validation"]
        test=[r for r in by if r["partition"]=="test_inspected_history"]
        if len(train)<100 or len(validation)<10 or len(test)<20:
            raise ValueError("INSUFFICIENT_SEPARATE_TIME_SPLITS")
        models={"price_vol":fit(train,BASE_FIELDS),"price_vol_cfgi":fit(train,AUG_FIELDS)}
        split[symbol]={"train":metrics(train,models),
                       "validation":metrics(validation,models),
                       "test_inspected_history":metrics(test,models),
                       "coefficient_tuning_on_validation_or_test":False,
                       "model_selection_after_validation":False,
                       "independent_shock_families_certified":0}
    return {"contract":CONTRACT,"classification":"EX_POST_INSPECTED_HISTORY_TEMPORAL_DIAGNOSTIC_NOT_SCIENTIFIC_PIT",
            "authority":AUTHORITY,"chronology":{"train_end":TRAIN_END.isoformat(),
              "validation_start":VAL_START.isoformat(),"validation_end":VAL_END.isoformat(),
              "test_start":TEST_START.isoformat(),"test_end":TEST_END.isoformat(),
              "holdout_truly_unseen":False,"label_horizon_hours":4,"embargo_hours_at_least":24},
            "counts":dict(counts),"original_source_manifest":{"spot":receipt,
              "spot_missing_days":missing,"spot_partial_days":partial,
              "capture_index_sha1":[x["git_blob_sha1"] for x in captures]},
            "asset_results":split,"variant_count":2,
            "locked_fit":{"optimizer":"deterministic full batch logistic sigmoid",
              "l2_penalty":RIDGE,"gradient_step":LEARNING_RATE,
              "iterations":ITERATIONS,
              "baseline_features":list(BASE_FIELDS),
              "incremental_feature":"original 4h CFGI v3 composite score centered at 50",
              "volatility":"std dev previous 8 completed 1h log returns percent",
              "scaling":"train-only zscore capped +/-6"},
            "underlying_source_values_emitted":False,
            "current_kompas_performance_evaluated":False,
            "statistical_significance_or_economic_edge_claim":False,
            "interpretation":"Temporal retrospective model diagnostic only; all historical outcomes were already exposed when model designed, and actual provider/price first-known is not certified."}

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path);q=p.parse_args()
    result=execute()
    if q.out:
        q.out.parent.mkdir(parents=True,exist_ok=True)
        q.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    compact={"contract":CONTRACT,"counts":result["counts"],
             "assets":{symbol:{split:{"n":metrics_["rows"],
                                      "days":metrics_["distinct_utc_calendar_days"],
                                      "brier_price_vol":metrics_["price_vol"]["brier"],
                                      "brier_plus_cfgi":metrics_["price_vol_cfgi"]["brier"],
                                      "brier_lift":metrics_["descriptive_brier_improvement_vs_price_vol"]}
                               for split,metrics_ in values.items() if split in ("train","validation","test_inspected_history")}
                       for symbol,values in result["asset_results"].items()}}
    print(json.dumps(compact,sort_keys=True))
if __name__=="__main__":main()
