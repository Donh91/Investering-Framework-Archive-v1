#!/usr/bin/env python3
from __future__ import annotations

import csv, json, statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path("04_MARKET_LEARNING/intraday_execution")
OBS = ROOT / "observations"
EVENTS = ROOT / "events"
LATEST = ROOT / "LATEST.json"
STATE = ROOT / "STATE.json"
SUMMARY = ROOT / "EVENT_SUMMARY.json"
CONFIG = ROOT / "config.json"
ENTRY = Path("04_MARKET_LEARNING/entry_signals/LATEST.json")
PULLBACK = Path("04_MARKET_LEARNING/pullback_learning/STATE.json")
BREADTH = Path("03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json")
HOURLY_POINTER = Path("03_DAILY_CAPTURE_LOGS/hourly/LATEST.json")


def now_utc(): return datetime.now(timezone.utc)
def parse_utc(v): return datetime.fromisoformat(v.replace("Z", "+00:00"))
def read_json(p):
    try: return json.loads(Path(p).read_text())
    except Exception: return None

def write_json(p, obj):
    p=Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n")

def f(row, key):
    v=row.get(key)
    if v in (None, ""): return None
    try: return float(v)
    except Exception: return None

def percentile_rank(values, x):
    vals=[float(v) for v in values if v is not None]
    if not vals or x is None: return None
    return 100.0*sum(v <= x for v in vals)/len(vals)

def mean(xs):
    xs=[x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None

def median(xs):
    xs=[x for x in xs if x is not None]
    return statistics.median(xs) if xs else None

def pct(a,b):
    return None if a in (None,0) or b is None else (b/a-1.0)*100.0


def hourly_rows():
    ptr=read_json(HOURLY_POINTER)
    if not ptr or ptr.get("status") != "COMPLETE": raise RuntimeError("hourly pointer missing/incomplete")
    end=parse_utc(ptr["window_end_utc"])
    rows=[]
    for d in {end.date(), (end-timedelta(days=1)).date(), (end-timedelta(days=2)).date()}:
        p=Path(f"03_DAILY_CAPTURE_LOGS/hourly/{d:%Y/%m/%Y-%m-%d}.csv")
        if not p.exists(): continue
        with p.open(newline="") as fh:
            for r in csv.DictReader(fh):
                if r.get("spot_status") != "PASS": continue
                ts=parse_utc(r["timestamp_utc"])
                if ts <= end: rows.append((ts,r))
    rows=sorted({ts:r for ts,r in rows}.items())
    if len(rows) < 6: raise RuntimeError("insufficient hourly rows")
    return ptr, rows


def asset_features(asset, pairs):
    latest_ts, latest=pairs[-1]
    pref=asset.lower()
    close=f(latest,f"{pref}_close")
    today=[r for ts,r in pairs if ts.date()==latest_ts.date()]
    prevday=[r for ts,r in pairs if ts.date()==(latest_ts-timedelta(days=1)).date()]
    trailing=[r for ts,r in pairs[-24:]]
    qv=[f(r,f"{pref}_quote_volume") for r in today]
    bv=[f(r,f"{pref}_volume") for r in today]
    q=sum(x for x in qv if x is not None); b=sum(x for x in bv if x is not None)
    vwap=q/b if b else None
    prior_vol=[f(r,f"{pref}_quote_volume") for r in pairs[-25:-1]]
    rel_vol=None
    med=median(prior_vol)
    cur_q=f(latest,f"{pref}_quote_volume")
    if med not in (None,0) and cur_q is not None: rel_vol=cur_q/med
    pdh=max([f(r,f"{pref}_high") for r in prevday if f(r,f"{pref}_high") is not None], default=None)
    pdl=min([f(r,f"{pref}_low") for r in prevday if f(r,f"{pref}_low") is not None], default=None)
    first2=today[:2]
    orh=max([f(r,f"{pref}_high") for r in first2 if f(r,f"{pref}_high") is not None], default=None)
    orl=min([f(r,f"{pref}_low") for r in first2 if f(r,f"{pref}_low") is not None], default=None)
    h24=max([f(r,f"{pref}_high") for r in trailing if f(r,f"{pref}_high") is not None], default=None)
    l24=min([f(r,f"{pref}_low") for r in trailing if f(r,f"{pref}_low") is not None], default=None)
    ret1=f(latest,f"{pref}_return_1h_pct")
    close4=f(pairs[-5][1],f"{pref}_close") if len(pairs)>=5 else None
    ret4=pct(close4,close)
    prior3=[f(r,f"{pref}_return_1h_pct") for _,r in pairs[-4:-1]]
    accel=None if ret1 is None or mean(prior3) is None else ret1-mean(prior3)
    taker=f(latest,f"{pref}_taker_buy_quote_share")
    prior_taker=[f(r,f"{pref}_taker_buy_quote_share") for _,r in pairs[-4:-1]]
    taker_delta=None if taker is None or mean(prior_taker) is None else taker-mean(prior_taker)
    funding=None
    for _,r in reversed(pairs[-24:]):
        x=f(r,f"{pref}_funding_event_rate")
        if x is not None: funding=x; break
    return {
        "close":close,"session_vwap":vwap,"vwap_deviation_pct":pct(vwap,close),
        "rolling_relative_quote_volume":rel_vol,"previous_day_high":pdh,"previous_day_low":pdl,
        "above_previous_day_high":None if pdh is None else close>pdh,"below_previous_day_low":None if pdl is None else close<pdl,
        "opening_range_high_2h":orh,"opening_range_low_2h":orl,
        "above_opening_range_high":None if orh is None else close>orh,"below_opening_range_low":None if orl is None else close<orl,
        "distance_from_24h_high_pct":pct(h24,close),"distance_from_24h_low_pct":pct(l24,close),
        "return_1h_pct":ret1,"return_4h_pct":ret4,"momentum_acceleration_1h_vs_prior3h_pp":accel,
        "taker_buy_quote_share":taker,"taker_buy_share_delta_vs_prior3h":taker_delta,
        "oi_change_1h_pct":f(latest,f"{pref}_oi_change_1h_pct"),"funding_event_rate_latest":funding,
    }


def ethbtc_features(pairs):
    ts,r=pairs[-1]; close=f(r,"ethbtc_close")
    close4=f(pairs[-5][1],"ethbtc_close") if len(pairs)>=5 else None
    highs=[f(x,"ethbtc_high") for _,x in pairs[-24:] if f(x,"ethbtc_high") is not None]
    return {"close":close,"return_1h_pct":f(r,"ethbtc_return_1h_pct"),"return_4h_pct":pct(close4,close),
            "distance_from_24h_high_pct":pct(max(highs) if highs else None,close)}


def recent_observations(limit):
    rows=[]
    if OBS.exists():
        for p in sorted(OBS.rglob("*.json"))[-limit:]:
            d=read_json(p)
            if d: rows.append(d)
    return rows


def build_snapshot(cfg):
    entry=read_json(ENTRY) or {}; pull=read_json(PULLBACK) or {}; breadth=read_json(BREADTH) or {}
    agg=breadth.get("aggregate",breadth)
    ptr,pairs=hourly_rows(); ts,_=pairs[-1]
    constituents={str(x.get("asset_id")):float(x["price_usd"]) for x in breadth.get("constituents",[]) if x.get("asset_id") and x.get("price_usd") not in (None,0)}
    br=agg.get("advance_ratio")
    if br is None and agg.get("advancer_pct") is not None: br=float(agg["advancer_pct"])/100.0
    return {
      "captured_at_utc":now_utc().isoformat(),"price_observation_utc":ts.isoformat(),"hourly_sequence_run_id":ptr.get("run_id"),
      "entry_state":entry.get("state"),"pullback_research_state":pull.get("research_state"),
      "btc":asset_features("btc",pairs),"eth":asset_features("eth",pairs),"ethbtc":ethbtc_features(pairs),
      "breadth":{"advance_ratio":br,"advancer_pct":agg.get("advancer_pct"),"equal_weight_mean_return_24h_pct":agg.get("equal_weight_mean_return_24h_pct"),
                 "median_return_24h_pct":agg.get("median_return_24h_pct"),"outperforming_btc_count":agg.get("outperforming_btc_count"),
                 "outperforming_eth_count":agg.get("outperforming_eth_count"),"membership_hash":agg.get("membership_hash")},
      "constituents":constituents,
      "limitations":cfg["explicit_limitations"],
    }


def classify(cfg,recent,obs,prev_state):
    n=len(recent)
    if obs.get("entry_state") != "GRADUATED_ALTCOIN_TOPUP_ACTIVE": return "REGIME_NOT_ACTIVE",{"observation_count":n}
    if n < cfg["warmup_observations"]: return "LEARNING_WARMUP",{"observation_count":n,"minimum_required":cfg["warmup_observations"]}
    def hist(path):
        out=[]
        a,b=path
        for o in recent:
            v=(o.get(a) or {}).get(b)
            if v is not None: out.append(v)
        return out
    metrics={
      "btc_vwap_rank":percentile_rank(hist(("btc","vwap_deviation_pct")),obs["btc"]["vwap_deviation_pct"]),
      "eth_vwap_rank":percentile_rank(hist(("eth","vwap_deviation_pct")),obs["eth"]["vwap_deviation_pct"]),
      "btc_rvol_rank":percentile_rank(hist(("btc","rolling_relative_quote_volume")),obs["btc"]["rolling_relative_quote_volume"]),
      "eth_rvol_rank":percentile_rank(hist(("eth","rolling_relative_quote_volume")),obs["eth"]["rolling_relative_quote_volume"]),
      "btc_ret4_rank":percentile_rank(hist(("btc","return_4h_pct")),obs["btc"]["return_4h_pct"]),
      "eth_ret4_rank":percentile_rank(hist(("eth","return_4h_pct")),obs["eth"]["return_4h_pct"]),
      "btc_accel_rank":percentile_rank(hist(("btc","momentum_acceleration_1h_vs_prior3h_pp")),obs["btc"]["momentum_acceleration_1h_vs_prior3h_pp"]),
      "eth_accel_rank":percentile_rank(hist(("eth","momentum_acceleration_1h_vs_prior3h_pp")),obs["eth"]["momentum_acceleration_1h_vs_prior3h_pp"]),
      "breadth_rank":percentile_rank([o.get("breadth",{}).get("advance_ratio") for o in recent],obs["breadth"]["advance_ratio"]),
    }
    prev=recent[-1] if recent else None
    breadth_delta=None
    if prev and prev.get("breadth",{}).get("advance_ratio") is not None and obs["breadth"]["advance_ratio"] is not None:
        breadth_delta=obs["breadth"]["advance_ratio"]-prev["breadth"]["advance_ratio"]
    metrics["breadth_delta_vs_prior_observation"]=breadth_delta
    high4=max([x for x in [metrics["btc_ret4_rank"],metrics["eth_ret4_rank"]] if x is not None],default=None)
    highv=max([x for x in [metrics["btc_vwap_rank"],metrics["eth_vwap_rank"]] if x is not None],default=None)
    highr=max([x for x in [metrics["btc_rvol_rank"],metrics["eth_rvol_rank"]] if x is not None],default=None)
    weak_taker=(obs["btc"].get("taker_buy_quote_share") or .5)<.48 and (obs["eth"].get("taker_buy_quote_share") or .5)<.48
    overheat=highv is not None and highr is not None and highv>=90 and highr>=80
    decel=(metrics["btc_accel_rank"] is not None and metrics["btc_accel_rank"]<=30) or (metrics["eth_accel_rank"] is not None and metrics["eth_accel_rank"]<=30)
    breadth_soft=breadth_delta is not None and breadth_delta<=-0.08
    if overheat and decel and (weak_taker or breadth_soft): return "LOCAL_TRIM_WATCH_RESEARCH",metrics
    if overheat and (decel or breadth_soft): return "OVERHEAT_WATCH_RESEARCH",metrics
    if high4 is not None and high4>=85 and (metrics["breadth_rank"] or 0)>=70: return "MOMENTUM_EXPANSION_RESEARCH",metrics
    pull_state=obs.get("pullback_research_state")
    if pull_state in {"PULLBACK_ACTIVE_RESEARCH","PULLBACK_RISK_RESEARCH"}: return "PULLBACK_ACTIVE_RESEARCH",metrics
    if prev_state=="PULLBACK_ACTIVE_RESEARCH" and (metrics["btc_accel_rank"] or 0)>=60 and (metrics["eth_accel_rank"] or 0)>=60 and (metrics["breadth_rank"] or 0)>=50:
        return "RELOAD_WATCH_RESEARCH",metrics
    if prev_state=="RELOAD_WATCH_RESEARCH" and (metrics["breadth_rank"] or 0)>=50: return "CONTINUATION_RESEARCH",metrics
    return "NORMAL",metrics


def event_paths(): return sorted(EVENTS.glob("*.json")) if EVENTS.exists() else []
def mature_events(obs, now):
    for p in event_paths():
        e=read_json(p)
        if not e or e.get("status")!="OPEN": continue
        opened=parse_utc(e["price_observation_utc"])
        hrs=(parse_utc(obs["price_observation_utc"])-opened).total_seconds()/3600
        if hrs < 24: continue
        start=e.get("constituents",{}); cur=obs.get("constituents",{})
        vals=[]
        for k,p0 in start.items():
            p1=cur.get(k)
            if p0 and p1: vals.append((p1/p0-1)*100)
        e["status"]="MATURED_24H"; e["matured_at_utc"]=now.isoformat(); e["matched_constituent_count_24h"]=len(vals)
        e["median_matched_return_24h_pct"]=median(vals); e["mean_matched_return_24h_pct"]=mean(vals)
        write_json(p,e)

def open_event(state,obs,now,prev_state):
    if state not in {"OVERHEAT_WATCH_RESEARCH","LOCAL_TRIM_WATCH_RESEARCH","RELOAD_WATCH_RESEARCH"}: return
    if prev_state==state: return
    ts=parse_utc(obs["price_observation_utc"]); eid=f"{ts:%Y%m%dT%H%M%SZ}_{state.lower()}"
    p=EVENTS/f"{eid}.json"
    if p.exists(): return
    write_json(p,{"contract":"INTRADAY_EXECUTION_EVENT_v1","event_id":eid,"status":"OPEN","research_state":state,
                  "previous_research_state":prev_state,"opened_at_utc":now.isoformat(),"price_observation_utc":obs["price_observation_utc"],
                  "snapshot":{k:v for k,v in obs.items() if k!="constituents"},"constituents":obs.get("constituents",{}),
                  "authority":{"research_only":True,"portfolio_execution":False,"automatic_rule_changes":False}})

def event_summary(now):
    rows=[read_json(p) for p in event_paths()]; rows=[x for x in rows if x]
    matured=[x for x in rows if x.get("status")=="MATURED_24H"]
    by={}
    for s in ["OVERHEAT_WATCH_RESEARCH","LOCAL_TRIM_WATCH_RESEARCH","RELOAD_WATCH_RESEARCH"]:
        vals=[x.get("median_matched_return_24h_pct") for x in matured if x.get("research_state")==s and x.get("median_matched_return_24h_pct") is not None]
        by[s]={"matured_count":len(vals),"median_of_median_return_24h_pct":median(vals),"mean_of_median_return_24h_pct":mean(vals)}
    out={"contract":"INTRADAY_EXECUTION_EVENT_SUMMARY_v1","generated_at_utc":now.isoformat(),"event_count":len(rows),"matured_24h_count":len(matured),"by_state":by,
         "governance":{"research_only":True,"automatic_rule_changes":False,"promotion_requires_separate_review":True}}
    write_json(SUMMARY,out); return out


def main():
    now=now_utc(); cfg=read_json(CONFIG)
    if not cfg or cfg.get("contract")!="INTRADAY_EXECUTION_RESEARCH_CONFIG_v1": raise RuntimeError("config missing/invalid")
    obs=build_snapshot(cfg); recent=recent_observations(cfg["trailing_observations"])
    prev_state=(read_json(STATE) or {}).get("research_state")
    if recent and recent[-1].get("price_observation_utc")==obs["price_observation_utc"]:
        mature_events(obs,now); summary=event_summary(now); latest=read_json(LATEST) or {}; latest["generated_at_utc"]=now.isoformat(); latest["duplicate_price_observation_skipped"]=True; latest["event_summary"]=summary; write_json(LATEST,latest); print(json.dumps(latest,sort_keys=True)); return
    state,evidence=classify(cfg,recent,obs,prev_state); obs["contract"]="INTRADAY_EXECUTION_OBSERVATION_v1"; obs["research_state"]=state; obs["adaptive_evidence"]=evidence
    ts=parse_utc(obs["price_observation_utc"]); write_json(OBS/f"{ts:%Y/%m/%d}/{ts:%Y%m%dT%H%M%SZ}.json",obs)
    mature_events(obs,now); open_event(state,obs,now,prev_state); summary=event_summary(now)
    auth=cfg["authority"]
    write_json(STATE,{"contract":"INTRADAY_EXECUTION_STATE_v1","updated_at_utc":now.isoformat(),"research_state":state,"previous_research_state":prev_state,"observation_count":len(recent)+1,"adaptive_evidence":evidence,"authority":auth})
    latest={"contract":"INTRADAY_EXECUTION_LATEST_v1","generated_at_utc":now.isoformat(),"research_state":state,"previous_research_state":prev_state,
            "market_snapshot":{k:v for k,v in obs.items() if k!="constituents"},"adaptive_evidence":evidence,"event_summary":summary,
            "data_ping_bridge":{"display_line":f"EXECUTION RESEARCH: {state} | BTC vwap={obs['btc']['vwap_deviation_pct'] if obs['btc']['vwap_deviation_pct'] is not None else 'NA'}% | ETH vwap={obs['eth']['vwap_deviation_pct'] if obs['eth']['vwap_deviation_pct'] is not None else 'NA'}% | breadth={(obs['breadth']['advance_ratio'] or 0)*100:.0f}% | sample={len(recent)+1}"},
            "authority":auth}
    write_json(LATEST,latest); print(json.dumps(latest,sort_keys=True))

if __name__=="__main__": main()
