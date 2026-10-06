#!/usr/bin/env python3
"""Prospective M6 warning-event outcomes. Research-only, no action authority."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math
from datetime import datetime,timedelta,timezone
from pathlib import Path
from typing import Any

CONTRACT="M6_WARNING_EVENT_OUTCOME_v1"
INDEX_CONTRACT="M6_WARNING_EVENT_INDEX_v1"
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

def pct(a,b):
    if not isinstance(a,(int,float)) or isinstance(a,bool) or not isinstance(b,(int,float)) or isinstance(b,bool) or not math.isfinite(float(a)) or not math.isfinite(float(b)) or float(a)<=0:return None
    return (float(b)/float(a)-1)*100

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def hourly_paths(start,end):
    d=start.date()
    while d<=end.date():
        yield HOURLY/f"{d:%Y/%m}/{d:%Y-%m-%d}.csv"; d+=timedelta(days=1)

def load_tape(root,start,end):
    out=[]
    for rel in hourly_paths(start,end):
        p=root/rel
        if not p.exists(): continue
        try:
            for r in csv.DictReader(io.StringIO(p.read_text(encoding="utf-8-sig"))):
                o=parse(r.get("timestamp_utc"))
                if o is None: continue
                close=parse(r.get("source_window_end_utc")) or o+timedelta(hours=1)
                if close<start or close>end: continue
                def f(k):
                    try:return float(r[k]) if r.get(k) not in (None,"") else None
                    except:return None
                out.append({"close":close,"btc":f("btc_close"),"eth":f("eth_close")})
        except Exception: continue
    return sorted(out,key=lambda x:x["close"])

def eligible_freezes(root):
    rows=[]
    base=root/FREEZES
    if not base.exists(): return rows
    for p in sorted(base.rglob("CMP-*.json")):
        try:f=json.loads(p.read_text())
        except:continue
        t=f.get("protection_tracker") or {}
        state=t.get("pullback_risk_state")
        issued=parse(f.get("issued_at_utc"))
        ref=f.get("market_reference") or {}
        obs=parse(ref.get("observation_open_utc"))
        knowledge=(obs+timedelta(hours=1)) if obs else issued
        if (f.get("contract")==FREEZE_CONTRACT and t.get("contract")==PROTECTION_CONTRACT and
            t.get("data_quality")=="OK" and state in PRIMARY and issued and knowledge and
            isinstance(ref.get("btc_usdt"),(int,float)) and isinstance(ref.get("eth_usdt"),(int,float))):
            rows.append({"path":p,"freeze":f,"tracker":t,"issued":issued,"knowledge":max(issued,knowledge)})
    return rows

def cluster(rows):
    # Prospective conservative family assignment. Until a family trough is known,
    # warnings <14d apart remain in the same open family; this cannot inflate N.
    fam=[]; current=None; last=None; idx=0
    for r in rows:
        if last is None or (r["knowledge"]-last)>=timedelta(days=14):
            current="M6F-"+r["knowledge"].strftime("%Y%m%dT%H%M%SZ"); idx=0
        else: idx+=1
        r["episode_family_id"]=current; r["within_family_warning_index"]=idx
        r["independent_family_weight"]=1.0 if idx==0 else 0.0
        last=r["knowledge"]; fam.append(r)
    return fam

def barrier_view(start,tape,key,levels,horizon_end):
    vals=[(r["close"],r[key]) for r in tape if r["close"]<=horizon_end and isinstance(r.get(key),(int,float))]
    out={}
    for level in levels:
        hit=next(((ts,pct(start,v)) for ts,v in vals if pct(start,v) is not None and pct(start,v)<=level),None)
        out[str(level)]={"touched":bool(hit),"first_touch_timestamp":hit[0].isoformat().replace("+00:00","Z") if hit else None}
    return out

def build(root,now):
    warnings=cluster(eligible_freezes(root)); events=[]
    for r in warnings:
        f,t=r["freeze"],r["tracker"]; ref=f["market_reference"]; start=r["knowledge"]
        event_id="M6E-"+hashlib.sha256((str(f.get("compass_id"))+"|"+start.isoformat()).encode()).hexdigest()[:16]
        max_end=min(now,start+timedelta(days=30)); tape=load_tape(root,start,max_end)
        event={"contract":CONTRACT,"event_id":event_id,"warning_state":t["pullback_risk_state"],
          "warning_timestamp":f.get("issued_at_utc"),"knowledge_timestamp":start.isoformat().replace("+00:00","Z"),
          "source_path":r["path"].relative_to(root).as_posix(),"source_hash":sha(r["path"]),
          "compass_id":f.get("compass_id"),"data_health_state":t.get("data_quality"),
          "episode_family_id":r["episode_family_id"],"within_family_warning_index":r["within_family_warning_index"],
          "independent_family_weight":r["independent_family_weight"],"start_prices":{"BTC":ref["btc_usdt"],"ETH":ref["eth_usdt"]},
          "horizons":{},"authority":{"research_only":True,"sell":False,"trim":False,"portfolio_action":False}}
        for name,hours in HORIZONS.items():
            end=start+timedelta(hours=hours)
            if now<end:
                event["horizons"][name]={"maturity_state":"PENDING","target_at_utc":end.isoformat().replace("+00:00","Z")};continue
            seg=[x for x in tape if start<=x["close"]<=end]
            if not seg or seg[-1]["close"]<end-timedelta(hours=1):
                event["horizons"][name]={"maturity_state":"UNKNOWN_INCOMPLETE_TAPE","target_at_utc":end.isoformat().replace("+00:00","Z")};continue
            h={"maturity_state":"MATURED","target_at_utc":end.isoformat().replace("+00:00","Z")}
            for label,key in (("BTC","btc"),("ETH","eth")):
                vals=[(x["close"],x[key]) for x in seg if isinstance(x.get(key),(int,float))]
                changes=[(ts,pct(ref["btc_usdt"] if label=="BTC" else ref["eth_usdt"],v)) for ts,v in vals]
                changes=[x for x in changes if x[1] is not None]
                if not changes: h[label]={"state":"UNKNOWN"};continue
                lo=min(changes,key=lambda x:x[1]); hi=max(changes,key=lambda x:x[1]); terminal=changes[-1]
                h[label]={"terminal_return_pct":terminal[1],"mae_pct":lo[1],"mfe_pct":hi[1],
                  "time_to_mae_hours":(lo[0]-start).total_seconds()/3600,"time_to_mfe_hours":(hi[0]-start).total_seconds()/3600,
                  "adverse_barriers":barrier_view(ref["btc_usdt"] if label=="BTC" else ref["eth_usdt"],seg,key,BARRIERS[label],end)}
            event["horizons"][name]=h
        events.append(event)
    return {"contract":INDEX_CONTRACT,"generated_at_utc":now.isoformat().replace("+00:00","Z"),"primary_warning_states":sorted(PRIMARY),
      "event_count":len(events),"independent_family_count":len({e["episode_family_id"] for e in events}),
      "warning_is_sell":False,"live_exit_rule":"NONE","events":events}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo-root",type=Path,default=Path.cwd());ap.add_argument("--output",type=Path,required=True);ap.add_argument("--now-utc")
    a=ap.parse_args();now=parse(a.now_utc) if a.now_utc else datetime.now(timezone.utc).replace(microsecond=0)
    if now is None: raise ValueError("INVALID_NOW")
    report=build(a.repo_root,now);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"contract":report["contract"],"event_count":report["event_count"],"independent_family_count":report["independent_family_count"]}))
if __name__=="__main__":main()
