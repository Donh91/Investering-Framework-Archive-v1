#!/usr/bin/env python3
"""Research-only Hyperliquid first-trade/listing-decay proxy.
Source: Ironflow (ironflow.sh), CC BY 4.0. No trading authority.
NOT a replication of 0xArchive's reported funded 74.6% book.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from bisect import bisect_left
from collections import defaultdict
from pathlib import Path
import pandas as pd

HOUR = pd.Timedelta(hours=1)
DAY = pd.Timedelta(days=1)


def ingest(files):
    if not files:
        raise ValueError("NO_DATA_FILES")
    files = sorted(files)
    for a,b in zip(files, files[1:]):
        if pd.Period(b.stem, freq="M") != pd.Period(a.stem, freq="M") + 1:
            raise ValueError("MISSING_MONTH_BETWEEN:" + a.stem + ":" + b.stem)
    cols = ["timestamp","coin","dex","market_class","open","high","low","close","volume"]
    data = []
    receipts = []
    for p in files:
        raw=p.read_bytes()
        receipts.append({"file":p.name,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)})
        df=pd.read_parquet(p, columns=cols)
        data.append(df.loc[(df.market_class=="perp") & (df.dex.fillna("")=="")])
    df=pd.concat(data,ignore_index=True).copy()
    df["timestamp"]=pd.to_datetime(df.timestamp,utc=True)
    for c in ("open","high","low","close","volume"):
        df[c]=pd.to_numeric(df[c],errors="coerce")
    if df[["coin","timestamp"]].duplicated().any():
        raise ValueError("DUPLICATE_COIN_TIMESTAMP")
    if df[cols].isna().any().any():
        # Empty dex is permitted, missing dex was normalized for the venue filter.
        if df[["timestamp","coin","open","high","low","close","volume"]].isna().any().any():
            raise ValueError("NULL_REQUIRED_FIELD")
    if not (df[["open","high","low","close"]]>0).all().all() or not (df.volume>0).all():
        raise ValueError("INVALID_OHLCV")
    if ((df.low>df.high) | (df.open<df.low) | (df.open>df.high) |
        (df.close<df.low) | (df.close>df.high)).any():
        raise ValueError("INVALID_OHLC_BOUNDS")
    return df.sort_values(["coin","timestamp"]).reset_index(drop=True),receipts


def grouped_bars(df):
    return {c:{k:list(part[k]) for k in ("timestamp","open","high","low","close","volume")}
            for c,part in df.groupby("coin",sort=True)}


def after(b,t,tolerance_hours=2):
    i=bisect_left(b["timestamp"],t)
    if i>=len(b["timestamp"]) or b["timestamp"][i]>t+pd.Timedelta(hours=tolerance_hours):
        return None
    return i


def before(b,t,tolerance_hours=2):
    i=bisect_left(b["timestamp"],t+HOUR)-1
    if i<0 or b["timestamp"][i]<t-pd.Timedelta(hours=tolerance_hours):
        return None
    return i


def window_features(b, entry_t, pre_t):
    # Use the actual fill within one hour; only earlier bars enter features.
    e=after(b,entry_t,1)
    p=before(b,pre_t,2)
    if e is None or p is None or p>=e:
        return None
    prices=b["close"][p:e]
    if len(prices)<12:
        return None
    lr=[math.log(y/x) for x,y in zip(prices[:-1],prices[1:])]
    mu=sum(lr)/len(lr)
    vol=math.sqrt(sum((r-mu)**2 for r in lr)/len(lr))
    notional=sum(b["volume"][i]*b["close"][i] for i in range(p,e))
    return {"momentum":math.log(b["close"][e-1]/b["close"][p]),
            "vol":vol,"log_notional":math.log1p(notional)}


def score_path(b,entry_t,due_t):
    e=after(b,entry_t)
    x=after(b,due_t)
    if e is None or x is None or x<=e:
        return None
    # An exit cannot be synthesized from a much later trade or a stale mark.
    if b["timestamp"][e]>entry_t+HOUR or b["timestamp"][x]>due_t+HOUR:
        return None
    ep=b["open"][e]
    xp=b["open"][x]
    # Entry/exit are modeled at their respective hourly OPENs. The HIGH/LOW
    # inside the exit candle happen after that modeled exit and are not held.
    # Include the actual exit OPEN as a boundary, but not its future extrema.
    held_high=max([ep,xp]+b["high"][e:x])
    held_low=min([ep,xp]+b["low"][e:x])
    return {"entry":ep,"exit":xp,"return":xp/ep-1,
            "mae_short":held_high/ep-1,
            "mfe_short":1-held_low/ep,
            "entry_time":b["timestamp"][e].isoformat(),
            "exit_time":b["timestamp"][x].isoformat()}


def median(x):
    z=sorted(x)
    if not z: return None
    i=len(z)//2
    return float(z[i] if len(z)%2 else (z[i-1]+z[i])/2)


def matched_controls(coin,bars,firsts,entry_t,due_t,cf,k=5):
    choices=[]
    for old,b in bars.items():
        if old==coin or firsts[old]>entry_t-60*DAY:
            continue
        f=window_features(b,entry_t,entry_t-DAY)
        if f is None: continue
        # Selection uses only information known at entry, never future exit availability.
        d=abs(f["momentum"]-cf["momentum"])+5*abs(f["vol"]-cf["vol"])+0.08*abs(f["log_notional"]-cf["log_notional"])
        choices.append((d,old))
    choices.sort(key=lambda r:(r[0],r[1]))
    out=[]
    for d,old in choices[:k]:
        p=score_path(bars[old],entry_t,due_t)
        out.append({"coin":old,"distance":d,"status":"OK" if p else "CONTROL_EXIT_CENSORED",
                    "return":p["return"] if p else None})
    return out


def study(data, minimum_first="2025-07-09",latest_first="2026-09-29",
          fee_bps_roundtrip=10,slippage_bps_roundtrip=10,delay_days=0):
    bars=grouped_bars(data)
    firsts={c:b["timestamp"][0] for c,b in bars.items()}
    first_floor=min(firsts.values())
    observed_last=max(b["timestamp"][-1] for b in bars.values())
    start=max(pd.Timestamp(minimum_first,tz="UTC"),first_floor+45*DAY)
    last=min(pd.Timestamp(latest_first,tz="UTC"),observed_last-(32+delay_days)*DAY)
    rows=[]
    for coin,b in sorted(bars.items(),key=lambda kv:kv[1]["timestamp"][0]):
        first=firsts[coin]
        if not (start<=first<=last): continue
        entry_t=first.floor("D")+(2+delay_days)*DAY
        due_t=entry_t+30*DAY
        horizon={}
        for h in (1,3,7,14,30):
            p=score_path(b,entry_t,entry_t+h*DAY)
            horizon[str(h)]={"status":"OBSERVED" if p else "CENSORED",
                             "return":p["return"] if p else None,
                             "mae_short":p["mae_short"] if p else None}
        p=score_path(b,entry_t,due_t)
        row={"coin":coin,"first_observed_utc":first.isoformat(),
             "entry_target_utc":entry_t.isoformat(),"due_utc":due_t.isoformat(),
             "status":"OK" if p else "NO_EXECUTABLE_30D_EXIT",
             "source_label":"FIRST_OBSERVED_TRADE_PROXY_NOT_VERIFIED_LISTING",
             "horizons":horizon}
        if p:
            # Price outcome does not depend on whether controls can be matched.
            row.update(p)
            row["short_unit_net_ex_funding"]=-row["return"]-(fee_bps_roundtrip+slippage_bps_roundtrip)/10000
            f=window_features(b,entry_t,entry_t-DAY)
            if f is None:
                row["status"]="INSUFFICIENT_ENTRY_FEATURES"
            else:
                controls=matched_controls(coin,bars,firsts,entry_t,due_t,f)
                row["controls"]=controls
                good=[c["return"] for c in controls if c["return"] is not None]
                row["match_count"]=len(controls)
                row["control_exit_count"]=len(good)
                row["control_return"]=median(good)
                row["paired_excess"]=row["return"]-row["control_return"] if good else None
                # A preselected control that disappears later is still part of the fixed set.
                # Retain the partial descriptive result, but never call it a complete pair.
                row["complete_control_cohort"]=bool(controls) and len(good)==len(controls)
                row["paired_excess_complete"]=row["paired_excess"] if row["complete_control_cohort"] else None
        rows.append(row)
    usable=[r for r in rows if r.get("return") is not None]
    paired=[r for r in usable if r.get("paired_excess") is not None]
    paired_complete=[r for r in paired if r.get("complete_control_cohort",False)]
    control_partials=[r for r in paired if not r.get("complete_control_cohort",False)]
    months=defaultdict(list)
    for r in paired: months[r["first_observed_utc"][:7]].append(r["paired_excess"])
    ci=None
    if len(months)>=8:
        rng=random.Random(20261110)
        keys=sorted(months)
        draws=[]
        for _ in range(3000):
            sample=[v for _ in keys for v in months[rng.choice(keys)]]
            draws.append(median(sample))
        draws.sort()
        ci=[draws[75],draws[2924]]
    # Repeated month-block sensitivity on STRICT complete-control pairs only.
    complete_months=defaultdict(list)
    for r in paired_complete:
        complete_months[r["first_observed_utc"][:7]].append(r["paired_excess_complete"])
    complete_ci=None
    if len(complete_months)>=8:
        rng=random.Random(20261110)
        keys=sorted(complete_months)
        draws=[]
        for _ in range(3000):
            sample=[v for _ in keys for v in complete_months[rng.choice(keys)]]
            draws.append(median(sample))
        draws.sort()
        complete_ci=[draws[75],draws[2924]]
    hsummary={}
    for h in (1,3,7,14,30):
        rr=[r["horizons"][str(h)]["return"] for r in rows
            if r["horizons"][str(h)]["status"]=="OBSERVED"]
        hsummary[str(h)]={"observed":len(rr),"censored":len(rows)-len(rr),
                         "median_return":median(rr),
                         "fraction_falling":sum(v<0 for v in rr)/len(rr) if rr else None}
    return {
       "status":"RETROSPECTIVE_DESCRIPTIVE_FIRST_TRADE_PROXY_NO_TRADING_EDGE",
       "n_first_trade_candidates":len(rows),"n_30d_exit_observable":len(usable),
       "n_censored":len(rows)-len(usable),"n_paired":len(paired),
       "n_paired_complete_controls":len(paired_complete),
       "n_paired_partial_controls":len(control_partials),
       "n_missing_control_exits":sum(r["match_count"]-r["control_exit_count"] for r in rows if "match_count" in r),
       "n_month_clusters":len(months),
       "n_complete_month_clusters":len(complete_months),"horizon_days_summary":hsummary,
       "fall_fraction":sum(r["return"]<0 for r in usable)/len(usable) if usable else None,
       "median_30d_new_return":median([r["return"] for r in usable]),
       "median_paired_excess_new_minus_older":median([r["paired_excess"] for r in paired]),
       "paired_excess_legacy_scope":"DESCRIPTIVE_INCLUDES_PARTIAL_CONTROL_EXITS",
       "median_paired_excess_strict_complete_controls":median([r["paired_excess_complete"] for r in paired_complete]),
       "month_cluster_bootstrap_ci":ci,
       "month_cluster_bootstrap_ci_complete_controls":complete_ci,
       "median_short_unit_net_ex_funding":median([r["short_unit_net_ex_funding"] for r in usable]),
       "sensitivity":{"fee_bps_roundtrip":fee_bps_roundtrip,
                      "slippage_bps_roundtrip":slippage_bps_roundtrip,"delay_days":delay_days},
       "source_warning":"First observed trade is not proven listing. No funding, settlement, margin liquidation, execution depth or exact fill. Counts all censored exits.",
       "rows":rows}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--fee-bps",type=float,default=10)
    ap.add_argument("--slippage-bps",type=float,default=10)
    ap.add_argument("--delay-days",type=int,default=0,choices=[0,1,3,7])
    a=ap.parse_args()
    data,receipts=ingest(sorted(a.data_dir.glob("????-??.parquet")))
    result=study(data,fee_bps_roundtrip=a.fee_bps,
                 slippage_bps_roundtrip=a.slippage_bps,delay_days=a.delay_days)
    result["source_files"]=receipts
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("rows","source_files")},
                     sort_keys=True,indent=2))


if __name__=="__main__":main()
