#!/usr/bin/env python3
"""Task2 source-bound EX-POST CFGI score vs simple price-momentum sign.

One frozen calendar week (Oct 14-20 2026), no API, zero market-rule changes.
This is a DESCRIPTIVE archive association from already observed outcomes, NOT
originally issued predictions, scientific PIT, calibration, alpha or trading.
Original local capture upper bounds exist; original venue price first-known and
provider CFGI first-publication are NOT certified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from scripts.research import task2_cfgi_capture_clock_audit_v1 as original_cfg
from scripts.research import task2_hourly_source_window_clocks_v1 as original_spot

CONTRACT="TASK2_CFGI_PRICE_4H_SAME_OPPORTUNITY_EXPOST_v1"
CLASSIFICATION="EX_POST_DEVELOPMENT_ASSOCIATION_NOT_PIT_NOT_ORIGINAL_COMPASS_EDGE"
DAYS=tuple(range(14,21))
HOUR=timedelta(hours=1)
SYMBOLS=("BTC","ETH")
CAPTURE_ROOT=original_cfg.CAPTURE
SPOT_ROOT=original_spot.SOURCE
AUTHORITY={"research_only":True,"historical_model_issued":False,
           "source_provider_publication_first_known_certified":False,
           "price_first_known_at_decision_certified":False,
           "scientific_hypothesis_pre_registered":False,
           "model_promotion":False,"portfolio_action":False}
PRICE_COL={"BTC":"btc_close","ETH":"eth_close"}

def usd_price(row, symbol):
    """Archive positive spot close only. No interpolation or substitute price."""
    if row.get("spot_status")!="PASS":
        return None
    try: price=float(row[PRICE_COL[symbol]])
    except (KeyError,ValueError,TypeError):return None
    if not math.isfinite(price) or price<=0:
        return None
    return price

def close_map(spot_folder=SPOT_ROOT):
    out={}
    archive_receipts=[]
    for day in DAYS:
        path=spot_folder/f"2026-10-{day:02d}.csv"
        payload=path.read_bytes()
        check=original_spot.audit_day(payload,day,expected_blob=original_spot.PINNED[day])
        archive_receipts.append({"day":check["day_utc"],"original_git_blob_sha1":check["original_hourly_blob_git_sha1"]})
        lines=csv.DictReader(payload.decode("utf-8").splitlines())
        for row in lines:
            dt=original_cfg.time_utc(row["timestamp_utc"])
            if dt in out:raise ValueError("DUPLICATE_ORIGINAL_SPOT_CANDLE")
            out[dt]=row
    if len(out)!=168:raise ValueError("PRICE_OWNER_168_HOURLY_SOURCE_CENSUS_CHANGED")
    return out,archive_receipts

def signed(value, *, tolerance=1e-12):
    if not math.isfinite(value):raise ValueError("NONFINITE_SIGN")
    return 1 if value>tolerance else -1 if value < -tolerance else 0

def classify_opportunity(snapshot, rowmeta, spot):
    captured=original_cfg.time_utc(rowmeta["capture_utc"])
    current_hour=captured.replace(minute=0,second=0,microsecond=0)
    base_start=current_hour-HOUR   # completed candle at or before original local receipt
    historic_start=base_start-4*HOUR
    future_start=base_start+4*HOUR # fixed target, independent of CFGI outcome

    cases=[]
    for symbol in SYMBOLS:
        rows={key:spot.get(clock) for key,clock in (
            ("base",base_start),("hist",historic_start),("future",future_start))}
        if any(v is None for v in rows.values()):
            cases.append({"symbol":symbol,"state":"MISSING_ARCHIVED_PRICE_BOUNDARY"})
            continue
        values={k:usd_price(v,symbol) for k,v in rows.items()}
        if any(v is None for v in values.values()):
            cases.append({"symbol":symbol,"state":"INCOMPLETE_OR_DEGRADED_PRICE"})
            continue
        cfgi_rows=snapshot.get("rows",[])
        score_rows=[v for v in cfgi_rows if v.get("symbol")==symbol]
        if len(score_rows)!=1 or not isinstance(score_rows[0].get("score"),(float,int)) or isinstance(score_rows[0].get("score"),bool):
            cases.append({"symbol":symbol,"state":"NO_VALID_CFGI_SCORE"})
            continue
        score=score_rows[0]["score"]
        if not math.isfinite(score) or not 0<=score<=100:
            cases.append({"symbol":symbol,"state":"INVALID_CFGI_SCORE"})
            continue
        row_clock=original_cfg.time_utc(rowmeta["source_symbol_times"][symbol]["original_row_utc"])
        if row_clock>captured:
            raise ValueError("SOURCE_ROW_FUTURE_TO_CAPTURE")
        if current_hour>captured or base_start+HOUR>captured:
            raise ValueError("BASE_CLOSE_AFTER_CAPTURE")
        if future_start+HOUR<=captured:
            raise ValueError("OUTCOME_NOT_FUTURE")
        mom=values["base"]/values["hist"]-1.0
        following=values["future"]/values["base"]-1.0
        cases.append({"symbol":symbol,"state":"EXPOST_JOIN_ONLY",
                      "cfgi_score_sign":signed(score-50,tolerance=0),
                      "momentum_sign":signed(mom),
                      "outcome_sign":signed(following),
                      "momentum_4h_pct":mom*100,
                      "following_4h_pct":following*100,
                      "score_centered":score-50,
                      "price_batch_end_after_nominal_close":
                          original_cfg.time_utc(rows["base"]["source_window_end_utc"])>base_start+HOUR})
    return cases

def safe_correlation(a,b):
    if len(a)!=len(b) or len(a)<3: return None
    ma=sum(a)/len(a);mb=sum(b)/len(b)
    x=[v-ma for v in a];y=[v-mb for v in b]
    aa=sum(v*v for v in x);bb=sum(v*v for v in y)
    return round(sum(v*w for v,w in zip(x,y))/(aa*bb)**.5,6) if aa>0 and bb>0 else None

def summarize(rows):
    n=len(rows)
    score_nonzero=[r for r in rows if r["cfgi_score_sign"]!=0 and r["outcome_sign"]!=0]
    momentum_nonzero=[r for r in rows if r["momentum_sign"]!=0 and r["outcome_sign"]!=0]
    paired=[r for r in rows if r["cfgi_score_sign"]!=0 and r["momentum_sign"]!=0 and r["outcome_sign"]!=0]
    both=score_only=momentum_only=neither=0
    for r in paired:
        s=r["cfgi_score_sign"]==r["outcome_sign"]
        m=r["momentum_sign"]==r["outcome_sign"]
        if s and m:both+=1
        elif s:score_only+=1
        elif m:momentum_only+=1
        else:neither+=1
    if both+score_only+momentum_only+neither!=len(paired):
        raise ValueError("PAIRED_DENOMINATOR_BROKEN")
    return {"symbol_observations":n,
      "cfgi_score_sign_opportunities":len(score_nonzero),
      "momentum_sign_opportunities":len(momentum_nonzero),
      "strictly_paired_non_neutral_opportunities":len(paired),
      "cfgi_sign_correct":sum(r["cfgi_score_sign"]==r["outcome_sign"] for r in score_nonzero),
      "momentum_sign_correct":sum(r["momentum_sign"]==r["outcome_sign"] for r in momentum_nonzero),
      "paired_both_correct":both,"paired_cfgi_only_correct":score_only,
      "paired_momentum_only_correct":momentum_only,"paired_both_wrong":neither,
      "score_50_abstentions":sum(r["cfgi_score_sign"]==0 for r in rows),
      "price_flat_abstentions":sum(r["momentum_sign"]==0 for r in rows),
      "future_flat_excluded_from_direction_accuracy":sum(r["outcome_sign"]==0 for r in rows),
      "historical_price_batch_end_later_than_close":
         sum(r["price_batch_end_after_nominal_close"] for r in rows),
      "cfgi_score_future_4h_price_corr_expost":
         safe_correlation([r["score_centered"] for r in rows],[r["following_4h_pct"] for r in rows]),
      "prior_4h_price_momentum_future_4h_price_corr_expost":
         safe_correlation([r["momentum_4h_pct"] for r in rows],[r["following_4h_pct"] for r in rows]),
      "independent_event_families_admitted":0,
      "statistical_p_value":None}

def execute(capture_folder=CAPTURE_ROOT,spot_folder=SPOT_ROOT):
    spot,pinned=close_map(spot_folder)
    items=[]
    skipped=Counter()
    seen=0
    ids=set()
    originals=[]
    for day in DAYS:
        folder=capture_folder/f"2026/10/{day:02d}"
        files=sorted(folder.glob("*.json"))
        if len(files)!=6:raise ValueError("CFGI_FROZEN_6_CAPTURES_PER_DAY_CHANGED")
        for file in files:
            data=file.read_bytes()
            doc=json.loads(data)
            meta=original_cfg.permitted_metadata(doc,source_name=file.name)
            if original_cfg.time_utc(meta["capture_utc"]).date()!=date(2026,10,day):
                raise ValueError("CAPTURE_FOLDER_CLOCK_WRONG")
            if doc["run_id"] in ids: raise ValueError("DUPLICATE_CAPTURE_RUN")
            ids.add(doc["run_id"])
            seen+=1
            owner=next(x for x in doc["owners"] if x["owner_id"]=="cfgi_sentiment")
            snap=next(x["summary"] for x in owner["files"] if x["path"]=="cfgi-owner-output/owner_snapshot.json")
            rows=classify_opportunity(snap,meta,spot)
            for row in rows:
                if row["state"]=="EXPOST_JOIN_ONLY":
                    row["utc_day"]=day
                    items.append(row)
                else:skipped[row["state"]]+=1
            originals.append({"capture_index_sha1":original_cfg.git_blob(data),"utc_day":day})
    if seen!=42 or len(items)+sum(skipped.values())!=84:
        raise ValueError("ORIGINAL_CAPTURE_DENOMINATOR_OR_SYMBOL_ROWS_BROKEN")
    by_symbol={s:summarize([r for r in items if r["symbol"]==s]) for s in SYMBOLS}
    result={"contract":CONTRACT,"classification":CLASSIFICATION,"authority":AUTHORITY,
      "frozen_dates_utc":"2026-10-14..2026-10-20",
      "original_capture_opportunities":seen,
      "original_symbol_opportunities":seen*2,
      "joined_development_only_symbol_opportunities":len(items),
      "missing_or_degraded_symbol_opportunities":dict(sorted(skipped.items())),
      "source_manifest":{"price_archive_sha1_per_day":pinned,
                         "original_capture_index_sha1_per_file":originals},
      "by_symbol":by_symbol,
      "treatment":"fixed 4h later price-candle CLOSE vs preceding complete hour CLOSE, ex post",
      "cfgi_heuristic":"score >50 means bullish, <50 bearish, =50 abstain (post-hoc exploratory sign proxy, not original model)",
      "baseline_heuristic":"prior 4 closed one-hour price-bar momentum sign, zero abstains",
      "no_price_from_vendor":True,"original_price_asof_proven":False,
      "independent_provider_first_known_proven":False,
      "prediction_originally_issued":False,
      "multiple_family_independence_proven":False,"historical_or_live_cfgi_edge_proven":False,
      "warning":"RETROSPECTIVE, same BTC/ETH days and shared overlapping future prices. No strategy promotion. Source batch end not detection."}
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",type=Path);args=ap.parse_args()
    report=execute()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"contract":CONTRACT,"original_capture_opportunities":report["original_capture_opportunities"],
                      "joined":report["joined_development_only_symbol_opportunities"],
                      "skipped":report["missing_or_degraded_symbol_opportunities"],
                      "by_symbol":report["by_symbol"]},sort_keys=True))
if __name__=="__main__":main()
