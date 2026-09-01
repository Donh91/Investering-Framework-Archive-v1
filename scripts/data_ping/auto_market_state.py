#!/usr/bin/env python3
"""Non-binding automated market-state assembly from existing GitHub owners."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,subprocess
from datetime import datetime,timedelta,timezone
from pathlib import Path
from typing import Any,Mapping
from scripts.data_ping import truth_integrity as ti

REPO="Donh91/Investering-Framework-Archive-v1"; REPOSITORY=REPO
CONTRACT="AUTO_MARKET_STATE_PACKET_v1"; POINTER="AUTO_MARKET_STATE_LATEST_POINTER_v1"
SCORE="MANUAL_DATA_PING_REPLACEMENT_SCORE_v1"
REGISTRY="02_DATA_PING/source_integrations/2026-09-01__auto-market-state-source-admission-v1.json"
REPLAY="02_DATA_PING/development_validation/2026-09-01__auto-market-state-replay-report-v1.json"
DEFAULT_ROOT=Path("04_MARKET_LEARNING/entry_signals/auto_market_state")
AUTH={"binding":False,"canonical_acceptance":False,"canonical_market_state":False,"state_change":False,"portfolio_action":False,"model_weight_change":False,"market_threshold_change":False,"purpose":"AUTOMATED_NON_BINDING_STATE_ASSEMBLY_AND_QA"}
AUTHORITY=AUTH
LANES=("hourly_market","live_anchor","btc_dominance","derivatives","breadth","settled_etf","stablecoin_liquidity","macro_risk","sentiment","altseason_context","catalyst_context","entry_signal_reference")

def canon(v): return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)+"\n").encode()
def h(v): return hashlib.sha256(v).hexdigest()
def iso(d): return d.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def num(v):
    if isinstance(v,bool) or not isinstance(v,(int,float)): return None
    x=float(v); return x if math.isfinite(x) else None
def ptime(v):
    if not isinstance(v,str): return None
    try: d=datetime.fromisoformat(v.replace("Z","+00:00")); return d.astimezone(timezone.utc) if d.utcoffset() is not None else None
    except ValueError: return None
def nested(v,*ks):
    for k in ks:
        if not isinstance(v,Mapping): return None
        v=v.get(k)
    return v

def read_json(snap,path):
    try:
        v,p=snap.read_json(path); return v,{"status":"PASS","path":path,"provenance":p}
    except Exception as e:
        return None,{"status":"UNAVAILABLE","path":path,"classification":getattr(e,"classification",type(e).__name__),"detail":getattr(e,"detail",str(e))}

def resolve(snap,path,contract,now,max_age):
    try:
        policy=ti.FreshnessPolicy("AUTO_STATE_v1",retrieval_max_age=max_age,source_observation_max_age=max_age,pointer_max_age=max_age,coverage_max_lag=max_age)
        r=ti.resolve_pointer_chain(snap,path,contract,now_utc=now,freshness_policy=policy)
        status="PASS" if r["freshness"]["status"]=="PASS" else "DEGRADED"
        return r,{"status":status,"classification":r["classification"],"freshness":r["freshness"],"pointer_path":r["pointer_path"],"target_path":r["target_path"],"provenance":r["provenance"]}
    except Exception as e:
        return None,{"status":"FAIL","classification":getattr(e,"classification",type(e).__name__),"detail":getattr(e,"detail",str(e)),"pointer_path":path}

def git_bytes(root,sha,path):
    raw=subprocess.check_output(["git","show",f"{sha}:{path}"],cwd=root)
    blob=subprocess.check_output(["git","rev-parse","--verify",f"{sha}:{path}"],cwd=root,text=True).strip()
    return raw,{"repository":REPO,"exact_commit_sha":sha,"exact_path":path,"git_blob_sha":blob,"raw_response_sha256":h(raw)}

def hourly_row(root,sha,res):
    end=ptime(nested(res,"target","window_end_utc"))
    if not end:return None,{"status":"UNAVAILABLE","classification":"HOURLY_WINDOW_END_UNAVAILABLE"}
    op=end-timedelta(hours=1); path=f"03_DAILY_CAPTURE_LOGS/hourly/{op:%Y/%m/%Y-%m-%d}.csv"
    try:
        raw,prov=git_bytes(root,sha,path); want=iso(op)
        row=next((r for r in reversed(list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))) if r.get("timestamp_utc")==want),None)
        if not row:return None,{"status":"UNAVAILABLE","classification":"HOURLY_EXACT_ROW_MISSING","expected":want,"provenance":prov}
        return row,{"status":"PASS","classification":"HOURLY_EXACT_ROW_BOUND","timestamp_utc":want,"provenance":prov}
    except Exception as e:return None,{"status":"UNAVAILABLE","classification":type(e).__name__,"detail":str(e),"path":path}

def btc_d(root,sha,now):
    path="03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv"
    try:
        raw,prov=git_bytes(root,sha,path); rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        ok=[r for r in rows if r.get("data_quality")=="PASS" and r.get("source_status")=="PUBLIC_SOURCE_BACKED" and ptime(r.get("source_timestamp")) and ptime(r["source_timestamp"])<=now]
        if not ok:return None,{"status":"UNAVAILABLE","classification":"BTC_D_NO_ELIGIBLE_ROW"}
        r=max(ok,key=lambda x:x["source_timestamp"]); age=(now-ptime(r["source_timestamp"])).total_seconds()
        return {"value_pct":float(r["btc_d_close"]),"date_utc":r["date_utc"],"source_timestamp":r["source_timestamp"],"source_provider":r["source_provider"],"source_convention":r["source_convention"]},{"status":"PASS" if age<=172800 else "DEGRADED","classification":"BTC_D_LATEST_ELIGIBLE_SETTLED_ROW","age_seconds":age,"provenance":prov}
    except Exception as e:return None,{"status":"UNAVAILABLE","classification":type(e).__name__,"detail":str(e)}

def stablecoin(v):
    if not isinstance(v,Mapping) or v.get("contract")!="DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1":return None,{"status":"UNAVAILABLE","classification":"STABLECOIN_CONTRACT_UNAVAILABLE"}
    g=v.get("global") or {}; sem=v.get("evidence_semantics") or {}; auth=v.get("authority") or {}
    if num(g.get("total_usd")) is None:return None,{"status":"UNAVAILABLE","classification":"STABLECOIN_NON_NORMALIZABLE_GLOBAL"}
    if sem.get("evidence_role")!="SUPPLY_LIQUIDITY" or sem.get("deployment_confirmation")!="NOT_ESTABLISHED":return None,{"status":"FAIL","classification":"STABLECOIN_SEMANTICS_ESCALATED"}
    if any(auth.get(k) is True for k in ("binding","canonical_acceptance","state_change","portfolio_action")):return None,{"status":"FAIL","classification":"STABLECOIN_AUTHORITY_ESCALATION"}
    return {"total_usd":num(g.get("total_usd")),"change_1d_pct":num(g.get("change_1d_pct")),"change_7d_pct":num(g.get("change_7d_pct")),"change_30d_pct":num(g.get("change_30d_pct")),"evidence_role":"SUPPLY_LIQUIDITY","deployment_confirmation":"NOT_ESTABLISHED"},{"status":"PASS","classification":"STABLECOIN_SUPPLY_LIQUIDITY_NORMALIZED"}

def etf(v):
    if not isinstance(v,Mapping) or v.get("contract")!="DAILY_SETTLED_ETF_CALIBRATION_v2":return None,{"status":"UNAVAILABLE","classification":"ETF_CONTRACT_UNAVAILABLE"}
    rows={r.get("asset"):r for r in v.get("rows",[]) if isinstance(r,Mapping)}
    if not all(a in rows and rows[a].get("session_final") is True and rows[a].get("total_parity") is True and num(rows[a].get("reported_total")) is not None for a in ("BTC","ETH")):return None,{"status":"UNAVAILABLE","classification":"ETF_FINALITY_OR_PARITY_UNAVAILABLE"}
    return {"session_date":v.get("session_date"),"btc_reported_total_musd":num(rows["BTC"]["reported_total"]),"eth_reported_total_musd":num(rows["ETH"]["reported_total"]),"session_final":True,"total_parity":True},{"status":"PASS","classification":"ETF_SETTLED_FINAL_PARITY"}

def crosscheck(a,b,fam_a,fam_b,comparable=True,tol_pct=.25,stale_a=False,stale_b=False):
    base={"primary_family":fam_a,"crosscheck_family":fam_b,"independent_source_family":fam_a!=fam_b,"comparable":comparable,"owner_switch_permitted":False,"market_interpretation":"NONE"}
    if stale_a:return {**base,"status":"STALE_PRIMARY"}
    if stale_b:return {**base,"status":"STALE_CROSSCHECK"}
    if not comparable:return {**base,"status":"NOT_COMPARABLE"}
    if a is None or b is None:return {**base,"status":"SCHEMA_MISMATCH"}
    try: d=abs(float(a)-float(b))/max(abs(float(a)),1e-12)*100
    except Exception:return {**base,"status":"SCHEMA_MISMATCH"}
    return {**base,"status":"AGREE" if d<=tol_pct else "TRUE_CONFLICT","relative_difference_pct":d}

def read_json_lane(snap,path): return read_json(snap,path)
def normalize_stablecoin(v,*,now_utc=None):
    out,health=stablecoin(v)
    if out is not None: out={**out,"evidence_semantics":{"evidence_role":"SUPPLY_LIQUIDITY","deployment_confirmation":"NOT_ESTABLISHED"}}
    return out,health
def normalize_crosscheck(a,b,*,primary_family,crosscheck_family,comparable=True,tolerance_pct=.25):
    base={"primary_family":primary_family,"crosscheck_family":crosscheck_family,"independent":primary_family!=crosscheck_family,"independent_source_family":primary_family!=crosscheck_family,"comparable":comparable,"owner_switch_permitted":False,"market_interpretation":"NONE","difference_pct":None}
    if a is None:return {**base,"status":"STALE_PRIMARY"}
    if b is None:return {**base,"status":"STALE_CROSSCHECK"}
    if not comparable:return {**base,"status":"NOT_COMPARABLE"}
    try:d=abs(float(a)-float(b))/max(abs(float(a)),1e-12)*100
    except Exception:return {**base,"status":"SCHEMA_MISMATCH"}
    return {**base,"status":"AGREE" if d<=tolerance_pct else "TRUE_CONFLICT","difference_pct":d,"relative_difference_pct":d}
def normalize_etf(result,*,now_utc=None):
    v=result.get("target") if isinstance(result,Mapping) and isinstance(result.get("target"),Mapping) else result
    out,health=etf(v)
    if out is None and isinstance(v,Mapping) and v.get("contract")=="DAILY_SETTLED_ETF_CALIBRATION_v2":
        rows={r.get("asset"):r for r in v.get("rows",[]) if isinstance(r,Mapping)}
        if any(rows.get(a,{}).get("session_final") is not True for a in ("BTC","ETH")): health={"status":"UNAVAILABLE","classification":"ETF_SESSION_NOT_FINAL"}
    return out,health
def replacement_score(registry,health,replay):
    entries=(registry or {}).get("sources",[]) if isinstance(registry,Mapping) else []
    by={e.get("manual_replacement_lane"):e for e in entries if isinstance(e,Mapping)}; total=len(LANES)
    acq=sum(bool(by.get(x,{}).get("unattended_git_owner")) for x in LANES); norm=sum(bool(by.get(x,{}).get("normalization_contract")) for x in LANES); ready=sum(health.get(x,{}).get("status")=="PASS" for x in LANES)
    parity=(replay or {}).get("packet_parity_pct") if isinstance(replay,Mapping) else None; packets=(replay or {}).get("packets_replayed",0) if isinstance(replay,Mapping) else 0; fields=(replay or {}).get("comparable_fields",0) if isinstance(replay,Mapping) else 0
    A=round(acq/total*100,2); B=round(norm/total*100,2); D=round(ready/total*100,2); E=round((total-acq)/total*100,2)
    return {"contract":SCORE,"denominator":{"functional_lanes":total,"lanes":list(LANES)},"acquisition_automation_pct":A,"normalization_validation_automation_pct":B,"packet_parity_pct":parity,"packet_parity_evidence":{"status":"MEASURED" if isinstance(parity,(int,float)) else "UNMEASURED_LINEAGE_GAP","packets":packets,"comparable_fields":fields},"decision_context_readiness_pct":D,"manual_input_residual_pct":E,"A_acquisition_automation_pct":A,"B_normalization_validation_pct":B,"C_packet_parity_pct":parity,"D_decision_context_readiness_pct":D,"E_manual_input_residual_pct":E,"no_blended_marketing_score":True,"blended_marketing_score":"NOT_COMPUTED"}

def prior_packet(snap):
    ptr,_=read_json(snap,"04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
    if not ptr:return None,{"status":"NOT_AVAILABLE_FIRST_PACKET"}
    p,_=read_json(snap,ptr.get("packet_path","")); return p,{"status":"AVAILABLE" if p else "UNAVAILABLE","packet_sha256":ptr.get("packet_sha256")}
def delta(a,b):
    if num(a) is None or num(b) is None:return None
    av=float(a); bv=float(b); return {"absolute":av-bv,"pct":None if bv==0 else (av/bv-1)*100}

def assemble(repo_root=Path.cwd(),now_utc=None):
    now=(now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc); snap=ti.GitCliSnapshot.open_repo(repo_root,repository=REPO,ref="HEAD"); H={}
    live,lh=resolve(snap,"03_DAILY_CAPTURE_LOGS/captures/LATEST.json",ti.DAILY_POINTER,now,timedelta(hours=8)); H["live_anchor"]=lh
    hourly,hh=resolve(snap,"03_DAILY_CAPTURE_LOGS/hourly/LATEST.json",ti.HOURLY_POINTER,now,timedelta(hours=3)); row,rh=hourly_row(repo_root,snap.commit_sha,hourly or {}); H["hourly_market"]={**hh,"row":rh,"status":"PASS" if hh.get("status")=="PASS" and rh.get("status")=="PASS" else hh.get("status")}
    mm=nested(live,"target","market_metrics") or {}; deriv=mm.get("derivatives") or {}; breadth=mm.get("breadth") or {}; sentiment=mm.get("sentiment") or {}; alt=mm.get("altseason_context") or mm.get("rotation_context") or {}; macro=mm.get("macro") or {}
    H["derivatives"]={"status":"PASS" if isinstance(deriv,Mapping) and deriv else "UNAVAILABLE","classification":"LIVE_ANCHOR_DERIVATIVES"}
    try:
        br=ti.validate_breadth_owner_interface(breadth); H["breadth"]={"status":"PASS","classification":br["classification"],"evidence_role":br["evidence_role"]}
    except Exception as e:H["breadth"]={"status":"UNAVAILABLE","classification":getattr(e,"classification",type(e).__name__)}
    H["sentiment"]={"status":"PASS" if sentiment else "UNAVAILABLE","classification":"LIVE_ANCHOR_SENTIMENT"}; H["altseason_context"]={"status":"PASS" if alt else "UNAVAILABLE","classification":"LIVE_ANCHOR_ALTSEASON_CONTEXT"}; H["macro_risk"]={"status":"PASS" if macro else "UNAVAILABLE","classification":"LIVE_ANCHOR_MACRO_CONTEXT"}
    bd,bdh=btc_d(repo_root,snap.commit_sha,now); H["btc_dominance"]=bdh
    ep,erh=read_json(snap,"03_DAILY_CAPTURE_LOGS/etf/LATEST.json"); ev=None
    if ep and isinstance(ep.get("path"),str): ev,evh=read_json(snap,ep["path"]); er,enh=etf(ev); H["settled_etf"]={**erh,"target":evh,"normalization":enh,"status":"PASS" if erh.get("status")==evh.get("status")==enh.get("status")=="PASS" else enh.get("status")}
    else: er=None; H["settled_etf"]={"status":"UNAVAILABLE","classification":"ETF_POINTER_UNAVAILABLE"}
    sv,srh=read_json(snap,"03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json"); st,snh=stablecoin(sv); H["stablecoin_liquidity"]={**srh,"normalization":snh,"status":"PASS" if srh.get("status")==snh.get("status")=="PASS" else snh.get("status")}
    cat,ch=read_json(snap,"03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json")
    H["catalyst_context"]={**ch,"status":"PASS" if cat and cat.get("authority")=="RESEARCH_ONLY_NON_CANONICAL" and cat.get("run_status")=="PASS" else "DEGRADED" if cat and cat.get("authority")=="RESEARCH_ONLY_NON_CANONICAL" else "UNAVAILABLE","classification":"CATALYST_DISCOVERY_ONLY_REFERENCE"}
    ent,eh=read_json(snap,"04_MARKET_LEARNING/entry_signals/LATEST.json"); H["entry_signal_reference"]={**eh,"status":"PASS" if ent and ent.get("contract")=="ENTRY_SIGNAL_LATEST_v1" and nested(ent,"authority","portfolio_execution") is False else "UNAVAILABLE","classification":"ENTRY_SIGNAL_REFERENCE_NON_BINDING"}
    registry,_=read_json(snap,REGISTRY); replay,_=read_json(snap,REPLAY)
    market=None
    if row:
        market={"observation_open_utc":row.get("timestamp_utc"),"observation_semantics":"COMPLETED_1H_CANDLE_CLOSE_VALUE_ON_CANDLE_OPEN_LABEL","btc_usdt":float(row["btc_close"]) if row.get("btc_close") else None,"eth_usdt":float(row["eth_close"]) if row.get("eth_close") else None,"ethbtc":float(row["ethbtc_close"]) if row.get("ethbtc_close") else None}
    H["derivatives"]["hourly_status"]="PASS" if row and row.get("btc_open_interest") and row.get("eth_open_interest") else "UNAVAILABLE"
    vals={"btc_usdt":nested(market,"btc_usdt"),"eth_usdt":nested(market,"eth_usdt"),"ethbtc":nested(market,"ethbtc"),"btc_dominance_pct":nested(bd,"value_pct"),"breadth_advance_ratio":nested(breadth,"aggregate","advance_ratio"),"stablecoin_total_usd":nested(st,"total_usd"),"btc_etf_musd":nested(er,"btc_reported_total_musd"),"eth_etf_musd":nested(er,"eth_reported_total_musd")}
    prior,pstat=prior_packet(snap); pvals=nested(prior,"normalized_state","scalar_values") or {}; deltas={k:delta(v,pvals.get(k)) for k,v in vals.items()}
    derived=None if not market or not market.get("btc_usdt") or not market.get("eth_usdt") else market["eth_usdt"]/market["btc_usdt"]
    x={"ethbtc_direct_vs_derived_same_binance_family":normalize_crosscheck(nested(market,"ethbtc"),derived,primary_family="BINANCE_SPOT",crosscheck_family="BINANCE_SPOT")}
    score=replacement_score(registry,H,replay); critical=any(H[x].get("status")=="FAIL" for x in ("hourly_market","live_anchor")); nonpass=any(H[x].get("status")!="PASS" for x in LANES); status="FAIL" if critical else "DEGRADED" if nonpass else "PASS"
    packet={"contract":CONTRACT,"packet_generated_at_utc":iso(now),"source_snapshot":{"repository":REPO,"exact_commit_sha":snap.commit_sha,"ref_resolution_count":snap.resolution_count,"consistency":snap.consistency()},"source_registry_path":REGISTRY,"replay_report_path":REPLAY,"source_health":H,"normalized_state":{"live_market":market,"btc_dominance":bd,"derivatives":{"live_anchor":deriv,"hourly":{"btc_open_interest":float(row["btc_open_interest"]) if row and row.get("btc_open_interest") else None,"eth_open_interest":float(row["eth_open_interest"]) if row and row.get("eth_open_interest") else None}},"breadth":breadth,"settled_etf":er,"stablecoin_liquidity":st,"macro_risk":macro or None,"sentiment":sentiment or None,"altseason_context":alt or None,"catalyst_context":cat,"entry_signal_reference":None if not ent else {"contract":ent.get("contract"),"generated_at_utc":ent.get("generated_at_utc"),"state":ent.get("state"),"observer_state":ent.get("observer_state"),"authority":ent.get("authority")},"scalar_values":vals},"crosschecks":x,"predecessor":pstat,"deltas_since_prior_auto_packet":deltas,"replacement_score":score,"blockers":[x for x in LANES if H[x].get("status")!="PASS"],"validation_status":status,"missingness_policy":"MISSING_IS_UNKNOWN_DEGRADED_OR_UNAVAILABLE_NEVER_BEARISH","fallback_policy":"NO_SILENT_FALLBACK_NO_OWNER_SWITCH_FROM_CROSSCHECK","authority":AUTH}
    packet["packet_sha256"]=h(canon({k:v for k,v in packet.items() if k!="packet_sha256"})); return packet

def write_packet(packet,root):
    d=ptime(packet["packet_generated_at_utc"]) or datetime.now(timezone.utc); r=root/"runs"/d.strftime("%Y/%m/%d"); r.mkdir(parents=True,exist_ok=True); path=r/f"{d:%H%M%S}_{packet['packet_sha256'][:12]}.json"; path.write_bytes(canon(packet)); root.mkdir(parents=True,exist_ok=True)
    ptr={"contract":POINTER,"packet_path":path.as_posix(),"packet_sha256":packet["packet_sha256"],"packet_generated_at_utc":packet["packet_generated_at_utc"],"source_snapshot_commit_sha":nested(packet,"source_snapshot","exact_commit_sha"),"validation_status":packet["validation_status"],"manual_input_residual_pct":nested(packet,"replacement_score","manual_input_residual_pct"),"authority":AUTH}; (root/"LATEST.json").write_bytes(canon(ptr)); return {"packet_path":path.as_posix(),"pointer_path":(root/"LATEST.json").as_posix(),"packet_sha256":packet["packet_sha256"],"validation_status":packet["validation_status"]}
def assemble_and_write(repo_root=Path.cwd(),output_root=DEFAULT_ROOT,now_utc=None):
    p=assemble(repo_root,now_utc); return {**write_packet(p,output_root),"replacement_score":p["replacement_score"],"blockers":p["blockers"]}
def main():
    a=argparse.ArgumentParser(); a.add_argument("--repo-root",type=Path,default=Path.cwd()); a.add_argument("--output-root",type=Path,default=DEFAULT_ROOT); a.add_argument("--now-utc"); a.add_argument("--no-write",action="store_true"); z=a.parse_args(); now=ti.parse_utc(z.now_utc,"now_utc") if z.now_utc else datetime.now(timezone.utc); p=assemble(z.repo_root,now); print(json.dumps(p if z.no_write else {**write_packet(p,z.output_root),"replacement_score":p["replacement_score"],"blockers":p["blockers"]},sort_keys=True)); raise SystemExit(2 if p["validation_status"]=="FAIL" else 0)
if __name__=="__main__": main()
