#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

LEDGER = Path("05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl")
MISSION = "RL-CN-SKILL-BASELINE-003"
WEEKS = {"2026-W39", "2026-W40"}
SYMBOLS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}
SOURCE = "https://data-api.binance.vision/api/v3/klines"
HISTORY_START = "2025-12-01"
RESEARCH_ONLY = True


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso_week_bounds(label: str) -> tuple[date, date]:
    year_s, week_s = label.split("-W")
    monday = date.fromisocalendar(int(year_s), int(week_s), 1)
    return monday, monday + timedelta(days=6)


def round_half_up(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def fetch_daily(symbol: str, start: date, end: date) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start_ms = int(datetime(start.year,start.month,start.day,tzinfo=timezone.utc).timestamp()*1000)
    end_exclusive = end + timedelta(days=1)
    end_ms = int(datetime(end_exclusive.year,end_exclusive.month,end_exclusive.day,tzinfo=timezone.utc).timestamp()*1000)-1
    params = {
        "symbol": symbol,
        "interval": "1d",
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1000,
    }
    url = SOURCE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":"Investering-Research-Lab/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    payload = json.loads(raw)
    if not isinstance(payload, list):
        raise ValueError(f"unexpected_binance_payload:{symbol}")
    rows=[]
    for x in payload:
        if not isinstance(x,list) or len(x)<7:
            continue
        open_time=datetime.fromtimestamp(int(x[0])/1000, timezone.utc)
        close_time=datetime.fromtimestamp(int(x[6])/1000, timezone.utc)
        rows.append({
            "date": open_time.date().isoformat(),
            "open_time_utc": open_time.isoformat().replace("+00:00","Z"),
            "close_time_utc": close_time.isoformat().replace("+00:00","Z"),
            "open": float(x[1]), "high": float(x[2]), "low": float(x[3]), "close": float(x[4]),
        })
    receipt={
        "provider":"BINANCE_PUBLIC_DATA_MIRROR",
        "endpoint":SOURCE,
        "symbol":symbol,
        "interval":"1d",
        "start":start.isoformat(),
        "end":end.isoformat(),
        "row_count":len(rows),
        "response_sha256":sha256(raw),
        "url_query":params,
    }
    return rows,receipt


def true_ranges(rows: list[dict[str,Any]]) -> list[float]:
    out=[]
    prev=None
    for r in rows:
        if prev is None:
            tr=r["high"]-r["low"]
        else:
            tr=max(r["high"]-r["low"],abs(r["high"]-prev),abs(r["low"]-prev))
        out.append(tr)
        prev=r["close"]
    return out


def wilder_atr14(rows: list[dict[str,Any]]) -> list[float|None]:
    trs=true_ranges(rows)
    vals:[float|None]=[None]*len(rows)
    if len(trs)<14:
        return vals
    atr=sum(trs[:14])/14.0
    vals[13]=atr
    for i in range(14,len(trs)):
        atr=((atr*13)+trs[i])/14.0
        vals[i]=atr
    return vals


def jaccard(low:float,high:float,actual_low:float,actual_high:float)->float:
    overlap=max(0.0,min(high,actual_high)-max(low,actual_low))
    union=max(high,actual_high)-min(low,actual_low)
    return overlap/union if union>0 else 0.0


def winkler(low:float,high:float,actual_low:float,actual_high:float,anchor:float,alpha:float=.10)->float:
    penalty=(high-low)+(2/alpha)*max(0.0,low-actual_low)+(2/alpha)*max(0.0,actual_high-high)
    return penalty/anchor*100.0


def score_range(low:float,high:float,actual_rows:list[dict[str,Any]],anchor:float)->dict[str,Any]:
    actual_low=min(r["low"] for r in actual_rows)
    actual_high=max(r["high"] for r in actual_rows)
    breach=sum(1 for r in actual_rows if r["low"]<low or r["high"]>high)
    actual_width=actual_high-actual_low
    return {
        "low":round(low,6),"high":round(high,6),
        "actual_low":actual_low,"actual_high":actual_high,
        "jaccard":round(jaccard(low,high,actual_low,actual_high),6),
        "winkler_a10":round(winkler(low,high,actual_low,actual_high,anchor,.10),6),
        "daily_containment_pct":round((len(actual_rows)-breach)/len(actual_rows)*100,4),
        "breach_days":breach,
        "width_ratio":round((high-low)/actual_width,6) if actual_width else None,
    }


def load_weekly_freezes(root:Path)->list[dict[str,Any]]:
    rows=[]
    for line in (root/LEDGER).read_text().splitlines():
        if not line.strip():
            continue
        obj=json.loads(line)
        if obj.get("forecast_week") in WEEKS and obj.get("window")=="weekly" and obj.get("asset") in SYMBOLS:
            rows.append(obj)
    grouped={}
    for r in rows:
        key=(r["forecast_week"],r["asset"])
        grouped.setdefault(key,[]).append(r)
    out=[]
    for key,items in sorted(grouped.items()):
        ranges={(float(x["forecast_low"]),float(x["forecast_high"]),int(x["generated_unix"])) for x in items}
        if len(ranges)!=1:
            raise ValueError(f"conflicting_weekly_freezes:{key}:{ranges}")
        # prefer the highest public issue identity when lineage-corrected duplicates exist
        chosen=sorted(items,key=lambda x:(int(x.get("public_issue_number") or -1),bool(x.get("lineage_correction"))))[-1]
        out.append(chosen)
    if len(out)!=4:
        raise ValueError(f"expected_four_week_asset_freezes_got:{len(out)}")
    return out


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root",type=Path,default=Path("."))
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    root=args.repo_root
    freezes=load_weekly_freezes(root)

    # Long warmup deliberately exceeds protocol minimum because E1X found ~120 candles
    # are needed for sub-dollar convergence of recursive Wilder ATR.
    fetch_start=date.fromisoformat(HISTORY_START)
    fetch_end=date(2026,10,4)
    market={}
    receipts={}
    for asset,symbol in SYMBOLS.items():
        rows,receipt=fetch_daily(symbol,fetch_start,fetch_end)
        atrs=wilder_atr14(rows)
        for r,a in zip(rows,atrs):
            r["atr14"]=a
        market[asset]=rows
        receipts[asset]=receipt

    results=[]
    for fr in freezes:
        asset=fr["asset"]
        cutoff=datetime.fromtimestamp(int(fr["generated_unix"]),timezone.utc)
        rows=market[asset]
        eligible=[r for r in rows if dt(r["close_time_utc"]) <= cutoff]
        if len(eligible)<120:
            raise ValueError(f"insufficient_warmup:{fr['forecast_week']}:{asset}:{len(eligible)}")
        anchor=eligible[-1]
        if anchor["atr14"] is None:
            raise ValueError("atr_missing")
        atr_raw=float(anchor["atr14"])
        atr_whole=round_half_up(atr_raw)
        anchor_close=float(anchor["close"])
        dumb15=(round_half_up(anchor_close-1.5*atr_whole),round_half_up(anchor_close+1.5*atr_whole))
        dumb20=(round_half_up(anchor_close-2.0*atr_whole),round_half_up(anchor_close+2.0*atr_whole))

        week_start,week_end=iso_week_bounds(fr["forecast_week"])
        actual=[r for r in rows if week_start.isoformat() <= r["date"] <= week_end.isoformat()]
        if len(actual)!=7:
            raise ValueError(f"expected_7_actual_days:{fr['forecast_week']}:{asset}:{len(actual)}")

        official=(float(fr["forecast_low"]),float(fr["forecast_high"]))
        result={
            "forecast_week":fr["forecast_week"],
            "asset":asset,
            "freeze_generated_unix":fr["generated_unix"],
            "freeze_generated_utc":cutoff.isoformat().replace("+00:00","Z"),
            "freeze_source":fr["source"],
            "public_issue_number":fr.get("public_issue_number"),
            "anchor_date":anchor["date"],
            "anchor_close":anchor_close,
            "atr14_raw_long_warmup":round(atr_raw,8),
            "atr14_whole_usd":atr_whole,
            "history_rows_available_pre_freeze":len(eligible),
            "reconstruction_status":"RESEARCH_RECONSTRUCTED_EX_ANTE_INPUTS_NOT_ORIGINALLY_FROZEN",
            "scores":{
                "CN":score_range(*official,actual,anchor_close),
                "DUMB15":score_range(*dumb15,actual,anchor_close),
                "DUMB20":score_range(*dumb20,actual,anchor_close),
            },
        }
        results.append(result)

    pairwise={"CN_vs_DUMB15":{"jaccard_wins":0,"jaccard_losses":0,"winkler_wins":0,"winkler_losses":0},
              "CN_vs_DUMB20":{"jaccard_wins":0,"jaccard_losses":0,"winkler_wins":0,"winkler_losses":0}}
    for r in results:
        cn=r["scores"]["CN"]
        for base in ("DUMB15","DUMB20"):
            b=r["scores"][base]
            key=f"CN_vs_{base}"
            if cn["jaccard"]>b["jaccard"]: pairwise[key]["jaccard_wins"]+=1
            elif cn["jaccard"]<b["jaccard"]: pairwise[key]["jaccard_losses"]+=1
            if cn["winkler_a10"]<b["winkler_a10"]: pairwise[key]["winkler_wins"]+=1
            elif cn["winkler_a10"]>b["winkler_a10"]: pairwise[key]["winkler_losses"]+=1

    means={}
    for model in ("CN","DUMB15","DUMB20"):
        means[model]={
            "mean_jaccard":round(sum(r["scores"][model]["jaccard"] for r in results)/len(results),6),
            "mean_winkler_a10":round(sum(r["scores"][model]["winkler_a10"] for r in results)/len(results),6),
            "mean_containment_pct":round(sum(r["scores"][model]["daily_containment_pct"] for r in results)/len(results),4),
        }

    output={
        "contract":"CN_RESEARCH_RECONSTRUCTED_BASELINE_TOURNAMENT_v1",
        "mission_id":MISSION,
        "status":"RESEARCH_ONLY_NOT_CANONICAL_SCORE",
        "purpose":"Current-era no-outcome-input mechanical comparison for exact weekly W39-W40 BTC/ETH freezes.",
        "method":{
            "baseline":"anchor close +/- 1.5x and 2.0x Wilder ATR14",
            "atr_seed":"SMA first 14 TR then Wilder recursive update",
            "warmup":"all available Binance daily bars from 2025-12-01; minimum 120 pre-freeze bars enforced",
            "rounding":"ATR and baseline bounds rounded to whole USD, half-up",
            "knowledge_rule":"only daily klines whose close_time <= forecast freeze generated_unix",
            "actual_window":"ISO forecast week Monday-Sunday, same provider for all compared ranges",
        },
        "critical_boundary":"These DUMB baselines were reconstructed after the fact from pre-freeze market inputs. Outcomes were not used to form them, but they were not committed at original publication and MUST NOT be represented as original frozen protocol baselines.",
        "provider_receipts":receipts,
        "rows":results,
        "means":means,
        "pairwise":pairwise,
        "limitations":[
            "N=4 asset-week rows across only two weeks.",
            "BTC and ETH rows within a week are correlated.",
            "Binance BTCUSDT/ETHUSDT is a research provider and may differ slightly from the original CN/FMP/Kraken source basis.",
            "No statistical significance or promotion decision is implied.",
            "W36-W38 are excluded because the v2 ledger does not expose exact comparable weekly-window freezes for those weeks.",
        ],
        "authority":{"canonical_score_rewrite":False,"public_surface_effect":False,"framework_state_change":False,"portfolio_action":False}
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","means":means,"pairwise":pairwise,"rows":[{"week":r["forecast_week"],"asset":r["asset"],"scores":r["scores"]} for r in results]},sort_keys=True))


if __name__=="__main__":
    main()
