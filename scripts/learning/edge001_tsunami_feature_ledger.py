#!/usr/bin/env python3
"""EDGE-001 prospective point-in-time feature ledger. Research only."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,subprocess
from datetime import datetime,timedelta,timezone
from pathlib import Path

FREEZE_CONTRACT="OFFICIAL_DAILY_COMPASS_v1"
PROTECTION_CONTRACT="COMPASS_PROTECTION_TRACKER_v1"
PRIMARY={"ELEVATED","HIGH","CONFIRMED"}
CONTRACT="EDGE001_TSUNAMI_FEATURE_LEDGER_v1"
INTEGRITY_REVISION="v1.1_PIT_STRICT"
FREEZES=Path("04_MARKET_LEARNING/handlekompas/official/daily")
HOURLY=Path("03_DAILY_CAPTURE_LOGS/hourly")
BREADTH=Path("03_DAILY_CAPTURE_LOGS/breadth_rich")

def parse(v):
    if not isinstance(v,str): return None
    try:
        d=datetime.fromisoformat(v.replace("Z","+00:00"))
        return d.astimezone(timezone.utc) if d.utcoffset() is not None else None
    except ValueError:return None

def finite_number(v):
    if isinstance(v,bool) or not isinstance(v,(int,float)): return None
    x=float(v)
    return x if math.isfinite(x) else None

def csv_number(v):
    if v in (None,""): return None
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def z(d):return d.isoformat().replace("+00:00","Z") if d else None

def legal_knowledge(f):
    issued=parse(f.get("issued_at_utc"))
    if issued is None:return None
    ref=f.get("market_reference") or {}
    obs=parse(ref.get("observation_open_utc"))
    close=obs+timedelta(hours=1) if obs else issued
    return max(issued,close)

def eligible(root):
    out=[]
    base=root/FREEZES
    if not base.exists():return out
    for p in sorted(base.rglob("CMP-*.json")):
        try:f=json.loads(p.read_text())
        except Exception:continue
        t=f.get("protection_tracker") or {};ref=f.get("market_reference") or {};k=legal_knowledge(f)
        if (f.get("contract")==FREEZE_CONTRACT and t.get("contract")==PROTECTION_CONTRACT and
            t.get("data_quality")=="OK" and t.get("pullback_risk_state") in PRIMARY and k and
            finite_number(ref.get("btc_usdt")) is not None and finite_number(ref.get("eth_usdt")) is not None):
            out.append((p,f,t,k))
    return out

def _git_lines(root,rel,commit):
    try:
        raw=subprocess.check_output(["git","-C",str(root),"show",f"{commit}:{rel.as_posix()}"],stderr=subprocess.DEVNULL)
        return raw.decode("utf-8-sig",errors="replace")
    except Exception:return None

def first_commit_exact_csv_row(root,path,row):
    try:rel=path.relative_to(root)
    except ValueError:return {"status":"UNVERIFIED_PATH_OUTSIDE_ROOT"}
    try:
        log=subprocess.check_output(["git","-C",str(root),"log","--reverse","--format=%H|%cI","--",rel.as_posix()],text=True,stderr=subprocess.DEVNULL)
    except Exception:return {"status":"UNVERIFIED_NO_GIT_HISTORY"}
    target=json.dumps(row,sort_keys=True,separators=(",",":"))
    for line in log.splitlines():
        if "|" not in line:continue
        commit,when=line.split("|",1);content=_git_lines(root,rel,commit)
        if content is None:continue
        try:
            for candidate in csv.DictReader(io.StringIO(content)):
                if json.dumps(candidate,sort_keys=True,separators=(",",":"))==target:
                    return {"status":"FOUND","commit":commit,"commit_time_utc":z(parse(when))}
        except Exception:continue
    return {"status":"UNVERIFIED_EXACT_ROW_NOT_FOUND_IN_HISTORY"}

def first_commit_exact_file(root,path):
    try:rel=path.relative_to(root);target=path.read_bytes()
    except Exception:return {"status":"UNVERIFIED_PATH"}
    try:
        log=subprocess.check_output(["git","-C",str(root),"log","--reverse","--format=%H|%cI","--",rel.as_posix()],text=True,stderr=subprocess.DEVNULL)
    except Exception:return {"status":"UNVERIFIED_NO_GIT_HISTORY"}
    for line in log.splitlines():
        if "|" not in line:continue
        commit,when=line.split("|",1)
        try:raw=subprocess.check_output(["git","-C",str(root),"show",f"{commit}:{rel.as_posix()}"],stderr=subprocess.DEVNULL)
        except Exception:continue
        if raw==target:return {"status":"FOUND","commit":commit,"commit_time_utc":z(parse(when))}
    return {"status":"UNVERIFIED_EXACT_FILE_NOT_FOUND_IN_HISTORY"}

def hourly_row(root,k):
    candidates=[]
    for day in (k.date()-timedelta(days=1),k.date()):
        p=root/HOURLY/f"{day:%Y/%m}/{day:%Y-%m-%d}.csv"
        if not p.exists():continue
        try:rows=csv.DictReader(io.StringIO(p.read_text(encoding="utf-8-sig")))
        except Exception:continue
        for r in rows:
            o=parse(r.get("timestamp_utc"))
            if o is None:continue
            candle_close=o+timedelta(hours=1)
            source_end=parse(r.get("source_window_end_utc"))
            available=max(candle_close,source_end) if source_end else candle_close
            if available<=k:
                candidates.append((candle_close,available,p,r))
    if not candidates:return None,None,{"status":"UNKNOWN_NO_LEGAL_HOURLY_ROW"}
    candle_close,available,p,r=max(candidates,key=lambda x:(x[0],x[1]))
    hist=first_commit_exact_csv_row(root,p,r)
    commit_time=parse(hist.get("commit_time_utc"))
    pit_verified=hist.get("status")=="FOUND" and commit_time is not None and commit_time<=k
    age=(k-candle_close).total_seconds()/3600
    return r,p,{"status":"OBSERVED","row_timestamp_utc":r.get("timestamp_utc"),"candle_close_utc":z(candle_close),
        "source_window_end_utc":r.get("source_window_end_utc"),"legal_availability_utc":z(available),
        "age_hours_at_warning":age,"first_exact_main_commit":hist,
        "pit_status":"VERIFIED_FIRST_MAIN_COMMIT_PRE_OR_AT_KNOWLEDGE" if pit_verified else "PIT_UNVERIFIED",
        "point_in_time_feature_capture_eligible":pit_verified}

def breadth_context(root,k):
    candidates=[]
    base=root/BREADTH
    if base.exists():
        for p in base.rglob("*.json"):
            if p.name=="LATEST.json":continue
            try:j=json.loads(p.read_text())
            except Exception:continue
            if not isinstance(j,dict):continue
            obs=j.get("observation")
            if not isinstance(obs,dict):continue
            life=j.get("lifecycle")
            if not isinstance(life,dict):life={}
            times=[parse(obs.get("cutoff_utc")),parse(j.get("retrieved_at_utc")),parse(life.get("retrieval_complete_time"))]
            times=[x for x in times if x]
            if not times:continue
            availability=max(times)
            if availability<=k:candidates.append((availability,p,j))
    if not candidates:return {"status":"UNAVAILABLE","canonical_compatible":False,"scoring_eligible":False}
    availability,p,j=max(candidates,key=lambda x:x[0])
    sem=j.get("evidence_semantics")
    if not isinstance(sem,dict):sem={}
    hist=first_commit_exact_file(root,p);ct=parse(hist.get("commit_time_utc"))
    pit=hist.get("status")=="FOUND" and ct is not None and ct<=k
    return {"status":"CONTEXT_ONLY_PIT_VERIFIED" if pit else "CONTEXT_ONLY_PIT_UNVERIFIED",
        "path":p.relative_to(root).as_posix(),"source_hash":sha(p),"legal_availability_utc":z(availability),
        "first_exact_main_commit":hist,"canonical_compatible":bool(sem.get("canonical_compatible") is True),
        "evidence_role":sem.get("evidence_role"),"registered_threshold_compatibility":sem.get("registered_threshold_compatibility"),
        "scoring_eligible":False,"aggregate":j.get("aggregate")}

def frow(r,k,meta):
    if not r:return {"state":"UNKNOWN_NO_LEGAL_HOURLY_ROW","knowledge_cutoff_utc":z(k)}
    spot=r.get("spot_status");der=r.get("derivatives_status")
    spot_fields={x:csv_number(r.get(x)) for x in ("btc_close","eth_close","ethbtc_close","btc_taker_buy_quote_share","eth_taker_buy_quote_share","btc_return_1h_pct","eth_return_1h_pct","ethbtc_return_1h_pct")} if spot=="PASS" else None
    der_fields={x:csv_number(r.get(x)) for x in ("btc_oi_change_1h_pct","eth_oi_change_1h_pct","btc_funding_event_rate","eth_funding_event_rate","btc_long_short_ratio","eth_long_short_ratio")} if der=="PASS" else None
    state="OBSERVED" if spot=="PASS" or der=="PASS" else "UNKNOWN_HEALTH_GATES_FAILED"
    return {"state":state,"knowledge_cutoff_utc":z(k),"spot_status":spot,"derivatives_status":der,"spot":spot_fields,"derivatives":der_fields,
        "btc_price_oi_state":r.get("btc_price_oi_state") if der=="PASS" else None,
        "eth_price_oi_state":r.get("eth_price_oi_state") if der=="PASS" else None,
        "source_row_integrity":meta}

def build(root):
    rows=[]
    for p,f,t,k in eligible(root):
        hr,hp,hmeta=hourly_row(root,k);identity=str(f.get("compass_id"))+"|"+k.isoformat()
        rows.append({"feature_row_id":"TSUF-"+hashlib.sha256(identity.encode()).hexdigest()[:16],"compass_id":f.get("compass_id"),
            "warning_state":t.get("pullback_risk_state"),"warning_issued_at_utc":f.get("issued_at_utc"),"knowledge_timestamp":z(k),
            "source_freeze_path":p.relative_to(root).as_posix(),"source_freeze_hash":sha(p),
            "hourly_source_path":hp.relative_to(root).as_posix() if hp else None,"hourly_source_hash":sha(hp) if hp else None,
            "features":frow(hr,k,hmeta),"breadth_context":breadth_context(root,k),
            "labels":{"A0":"BLOCKED_BINARY","A1":"BLOCKED_BINARY","A2":"UNKNOWN_CANONICAL","A3":"CONTINUOUS_ONLY","M1":"CONTINUOUS_PARTIAL","M2":"CONTINUOUS","M3":"ACTIVE_FAIL_CLOSED"},
            "outcome_joined":False,"scoring_eligible":False})
    return {"contract":CONTRACT,"integrity_revision":INTEGRITY_REVISION,"row_count":len(rows),"collection_only":True,
        "outcome_joined":False,"scoring_ready":False,"warning_is_sell":False,"live_exit_rule":"NONE","rows":rows}

def main():
    a=argparse.ArgumentParser();a.add_argument("--repo-root",type=Path,default=Path.cwd());a.add_argument("--output",type=Path,required=True);x=a.parse_args()
    j=build(x.repo_root);x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(j,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"contract":j["contract"],"integrity_revision":j["integrity_revision"],"row_count":j["row_count"],"outcome_joined":j["outcome_joined"]}))
if __name__=="__main__":main()
