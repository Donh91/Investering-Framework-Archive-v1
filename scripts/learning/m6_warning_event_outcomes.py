#!/usr/bin/env python3
"""Prospective M6 warning-event outcomes. Research-only, no action authority."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from datetime import datetime,timedelta,timezone
from pathlib import Path
from typing import Any

CONTRACT="M6_WARNING_EVENT_OUTCOME_v1"
INDEX_CONTRACT="M6_WARNING_EVENT_INDEX_v1"
INTEGRITY_REVISION="v1.2_POST_KNOWLEDGE_BAR_INTEGRITY"
FREEZE_CONTRACT="OFFICIAL_DAILY_COMPASS_v1"
PROTECTION_CONTRACT="COMPASS_PROTECTION_TRACKER_v1"
PRIMARY={"ELEVATED","HIGH","CONFIRMED"}
HORIZONS={"24h":24,"72h":72,"7d":168,"14d":336,"30d":720}
BARRIERS={"BTC":[-10.0,-15.0,-20.0],"ETH":[-15.0,-20.0,-30.0]}
HOURLY=Path("03_DAILY_CAPTURE_LOGS/hourly")
FREEZES=Path("04_MARKET_LEARNING/handlekompas/official/daily")

def parse(v):
    if not isinstance(v,str): return None
    try:d=datetime.fromisoformat(v.replace("Z","+00:00"))
    except ValueError:return None
    return d.astimezone(timezone.utc) if d.utcoffset() is not None else None

def finite_number(v):
    if isinstance(v,bool) or not isinstance(v,(int,float)):return None
    x=float(v);return x if math.isfinite(x) else None

def csv_number(v):
    if v in (None,""):return None
    try:
        x=float(v);return x if math.isfinite(x) else None
    except (TypeError,ValueError):return None

def pct(a,b):
    if a is None or b is None or a<=0:return None
    return (float(b)/float(a)-1)*100

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def z(d): return d.isoformat().replace("+00:00","Z") if d else None

def hourly_paths(start,end):
    d=start.date()-timedelta(days=1)
    while d<=end.date():
        yield HOURLY/f"{d:%Y/%m}/{d:%Y-%m-%d}.csv";d+=timedelta(days=1)

def load_tape(root,start,end):
    by_close={};bindings=[]
    for rel in hourly_paths(start,end):
        p=root/rel
        if not p.exists():continue
        bindings.append({"path":rel.as_posix(),"sha256":sha(p)})
        try:rows=csv.DictReader(io.StringIO(p.read_text(encoding="utf-8-sig")))
        except Exception:continue
        for r in rows:
            if r.get("spot_status")!="PASS":continue
            o=parse(r.get("timestamp_utc"))
            if o is None:continue
            close=o+timedelta(hours=1)
            if close<start or close>end:continue
            btc=csv_number(r.get("btc_close"));eth=csv_number(r.get("eth_close"))
            bh=csv_number(r.get("btc_high"));bl=csv_number(r.get("btc_low"))
            eh=csv_number(r.get("eth_high"));el=csv_number(r.get("eth_low"))
            if btc is None and eth is None:continue
            by_close[close]={"close":close,"btc":btc,"eth":eth,"btc_high":bh,"btc_low":bl,"eth_high":eh,"eth_low":el}
    return [by_close[k] for k in sorted(by_close)],bindings

def eligible_freezes(root):
    rows=[];base=root/FREEZES
    if not base.exists():return rows
    for p in sorted(base.rglob("CMP-*.json")):
        try:f=json.loads(p.read_text())
        except Exception:continue
        t=f.get("protection_tracker") or {};state=t.get("pullback_risk_state");issued=parse(f.get("issued_at_utc"));ref=f.get("market_reference") or {};obs=parse(ref.get("observation_open_utc"))
        knowledge=max(issued,obs+timedelta(hours=1)) if issued and obs else issued
        if (f.get("contract")==FREEZE_CONTRACT and t.get("contract")==PROTECTION_CONTRACT and t.get("data_quality")=="OK" and
            state in PRIMARY and issued and knowledge and finite_number(ref.get("btc_usdt")) is not None and finite_number(ref.get("eth_usdt")) is not None):
            rows.append({"path":p,"freeze":f,"tracker":t,"issued":issued,"knowledge":knowledge})
    # Family identity and first-warning weight must use actual knowledge time, not
    # filename / compass-id lexical order (which is not chronological).
    rows.sort(key=lambda row: (row['knowledge'], str(row['freeze'].get('compass_id') or '')))
    return rows

def cluster(rows):
    fam=[];current=None;last=None
    for r in rows:
        if last is None or (r["knowledge"]-last)>=timedelta(days=14):
            current="M6F-"+r["knowledge"].strftime("%Y%m%dT%H%M%SZ");idx=0
        else:idx+=1
        r["episode_family_id"]=current;r["episode_family_status"]="PROVISIONAL_OPEN_UNTIL_TROUGH_OBSERVED";r["within_family_warning_index"]=idx
        r["independent_family_weight"]=1.0 if idx==0 else 0.0;last=r["knowledge"];fam.append(r)
    return fam

def complete_tape(seg,start,end):
    if not seg:return False,{"reason":"NO_VALID_SPOT_ROWS"}
    closes=[x["close"] for x in seg]
    if closes[0]>start+timedelta(hours=1):return False,{"reason":"LATE_FIRST_CANDLE","first_close":z(closes[0])}
    if closes[-1]<end-timedelta(hours=1):return False,{"reason":"EARLY_LAST_CANDLE","last_close":z(closes[-1])}
    gaps=[(b-a).total_seconds()/3600 for a,b in zip(closes,closes[1:])]
    max_gap=max(gaps) if gaps else 0.0
    if max_gap>1.01:return False,{"reason":"INTERIOR_GAP","max_gap_hours":max_gap}
    return True,{"reason":"COMPLETE_HOURLY_CLOSE_GRID","first_close":z(closes[0]),"last_close":z(closes[-1]),"max_gap_hours":max_gap,"row_count":len(seg)}

def barrier_view(start,post_knowledge_low_observations,levels):
    """Low observations exclude any intrahour segment before warning knowledge."""
    out={}
    for level in levels:
        hit=next(((ts,pct(start,v)) for ts,v in post_knowledge_low_observations
            if pct(start,v) is not None and pct(start,v)<=level),None)
        out[str(level)]={"touched":bool(hit),"first_touch_timestamp":z(hit[0]) if hit else None,
            "basis":"FIRST_POST_WARNING_CLOSE_PLUS_FULL_POST_KNOWLEDGE_BAR_LOWS",
            "touch_time_semantics":"HOURLY_BAR_END_NOT_EXACT_LOW_TIME"}
    return out

def asset_view(seg,start_price,label,start):
    key="btc" if label=="BTC" else "eth";high_key=key+"_high";low_key=key+"_low"
    closes=[(r["close"],r.get(key)) for r in seg if isinstance(r.get(key),(int,float))]
    if len(closes)!=len(seg) or not closes:
        return {"state":"UNKNOWN_INCOMPLETE_ASSET_PATH","reason":"MISSING_ASSET_CLOSE"}
    # A bar ending after the warning can nevertheless contain its pre-warning
    # high/low. Use that bar's known closing price, but never its intrabar extrema.
    full_rows=[r for r in seg if r["close"]-timedelta(hours=1)>=start]
    if not full_rows:
        return {"state":"UNKNOWN_INCOMPLETE_ASSET_PATH","reason":"NO_FULL_POST_KNOWLEDGE_BAR"}
    for r in full_rows:
        c=r.get(key);hi=r.get(high_key);lo=r.get(low_key)
        if not all(isinstance(v,(int,float)) and math.isfinite(v) and v>0 for v in (c,hi,lo)):
            return {"state":"UNKNOWN_INCOMPLETE_ASSET_PATH","reason":"MISSING_FULL_BAR_OHLC"}
        if not (lo<=c<=hi):
            return {"state":"UNKNOWN_INCOMPLETE_ASSET_PATH","reason":"INCONSISTENT_FULL_BAR_OHLC"}
    # The close for the warning-straddling candle is a valid later observation.
    # Each full post-warning bar contributes its intrabar high and low.
    highs=closes+[(r["close"],r[high_key]) for r in full_rows]
    lows=closes+[(r["close"],r[low_key]) for r in full_rows]
    terminal=closes[-1];lo=min(lows,key=lambda x:x[1]);hi=max(highs,key=lambda x:x[1])
    post_anchor=closes[0]
    return {"state":"MATURED","reference_anchor":{"price":start_price,"semantics":"FREEZE_REFERENCE_CONTEXT_NOT_EXECUTION_PRICE",
            "terminal_return_pct":pct(start_price,terminal[1]),"mae_pct":pct(start_price,lo[1]),"mfe_pct":pct(start_price,hi[1]),
            "time_to_mae_hours":(lo[0]-start).total_seconds()/3600,"time_to_mfe_hours":(hi[0]-start).total_seconds()/3600,
            "extremum_timestamp_semantics":"HOURLY_CLOSE_OR_BAR_END_NOT_EXACT_TRADE_TIME"},
        "post_knowledge_close_anchor":{"timestamp":z(post_anchor[0]),"price":post_anchor[1],
            "semantics":"FIRST_HOURLY_CLOSE_AFTER_WARNING_KNOWLEDGE_NOT_EXECUTION_PRICE",
            "terminal_return_pct":pct(post_anchor[1],terminal[1]),"mae_pct":pct(post_anchor[1],lo[1]),
            "mfe_pct":pct(post_anchor[1],hi[1])},
        "terminal":{"timestamp":z(terminal[0]),"close":terminal[1]},
        "extrema_basis":"FIRST_POST_WARNING_CLOSE_PLUS_FULL_POST_KNOWLEDGE_BAR_HIGH_LOW",
        "excluded_straddling_bar_extrema":len(seg)-len(full_rows),
        "adverse_barriers":barrier_view(start_price,sorted(lows,key=lambda observation:observation[0]),BARRIERS[label])}

def build(root,now):
    warnings=cluster(eligible_freezes(root));events=[]
    for r in warnings:
        f,t=r["freeze"],r["tracker"];ref=f["market_reference"];start=r["knowledge"];max_end=min(now,start+timedelta(days=30));tape,bindings=load_tape(root,start,max_end)
        event_id="M6E-"+hashlib.sha256((str(f.get("compass_id"))+"|"+start.isoformat()).encode()).hexdigest()[:16]
        event={"contract":CONTRACT,"integrity_revision":INTEGRITY_REVISION,"event_id":event_id,"warning_state":t["pullback_risk_state"],
          "warning_timestamp":f.get("issued_at_utc"),"knowledge_timestamp":z(start),"source_path":r["path"].relative_to(root).as_posix(),"source_hash":sha(r["path"]),
          "compass_id":f.get("compass_id"),"data_health_state":t.get("data_quality"),"episode_family_id":r["episode_family_id"],
          "episode_family_status":r["episode_family_status"],"within_family_warning_index":r["within_family_warning_index"],"independent_family_weight":r["independent_family_weight"],
          "start_prices":{"BTC":finite_number(ref["btc_usdt"]),"ETH":finite_number(ref["eth_usdt"])},
          "reference_price_semantics":"FREEZE_REFERENCE_CONTEXT_NOT_EXECUTION_PRICE","outcome_tape_bindings":bindings,"horizons":{},
          "authority":{"research_only":True,"sell":False,"trim":False,"portfolio_action":False,"execution_anchor":False}}
        for name,hours in HORIZONS.items():
            end=start+timedelta(hours=hours)
            if now<end:
                event["horizons"][name]={"maturity_state":"PENDING","target_at_utc":z(end)};continue
            seg=[x for x in tape if start<=x["close"]<=end]
            complete,cov=complete_tape(seg,start,end)
            if not complete:
                event["horizons"][name]={"maturity_state":"UNKNOWN_INCOMPLETE_TAPE","target_at_utc":z(end),"coverage":cov};continue
            h={"maturity_state":"MATURED","target_at_utc":z(end),"coverage":cov}
            h["BTC"]=asset_view(seg,event["start_prices"]["BTC"],"BTC",start);h["ETH"]=asset_view(seg,event["start_prices"]["ETH"],"ETH",start)
            if h["BTC"]["state"]!="MATURED" or h["ETH"]["state"]!="MATURED":h["maturity_state"]="UNKNOWN_INCOMPLETE_ASSET_PATH"
            event["horizons"][name]=h
        events.append(event)
    return {"contract":INDEX_CONTRACT,"integrity_revision":INTEGRITY_REVISION,"generated_at_utc":z(now),"primary_warning_states":sorted(PRIMARY),
      "event_count":len(events),"provisional_independent_family_count":len({e["episode_family_id"] for e in events}),
      "warning_is_sell":False,"live_exit_rule":"NONE","economic_action_scoring_ready":False,"events":events}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo-root",type=Path,default=Path.cwd());ap.add_argument("--output",type=Path,required=True);ap.add_argument("--now-utc")
    a=ap.parse_args();now=parse(a.now_utc) if a.now_utc else datetime.now(timezone.utc).replace(microsecond=0)
    if now is None:raise ValueError("INVALID_NOW")
    report=build(a.repo_root,now);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"contract":report["contract"],"integrity_revision":report["integrity_revision"],"event_count":report["event_count"],"provisional_independent_family_count":report["provisional_independent_family_count"]}))
if __name__=="__main__":main()
