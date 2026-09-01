#!/usr/bin/env python3
"""Fail-closed autonomous DATA PING state assembly from existing owners."""
from __future__ import annotations

import argparse, csv, hashlib, io, json, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from scripts.data_ping.truth_integrity import (
    FreshnessPolicy, GitCliSnapshot, IntegrityError, PointerContract,
    canonical_json, freshness_vector, normalized_sha256, resolve_pointer_chain,
)

CONTRACT="AUTO_MARKET_STATE_PACKET_v1"
LATEST_CONTRACT="AUTO_MARKET_STATE_LATEST_POINTER_v1"
CROSSCHECK_CONTRACT="DATA_PING_CROSSCHECK_CONTRACT_v1"
REPOSITORY="Donh91/Investering-Framework-Archive-v1"
OUTPUT_ROOT=Path("03_DAILY_CAPTURE_LOGS/autonomous_market_state")
CROSSCHECK_STATUSES={"AGREE","AGREE_WITH_EXPECTED_VENUE_BASIS","EXPLAINABLE_DEFINITION_DIFFERENCE","STALE_PRIMARY","STALE_CROSSCHECK","SCHEMA_MISMATCH","TRUE_CONFLICT","NOT_COMPARABLE"}
AUTHORITY={"binding":False,"canonical_market_state":False,"canonical_acceptance":False,"portfolio_action":False,"state_change":False,"interpretation":False}


def zulu(dt:datetime)->str: return dt.astimezone(timezone.utc).isoformat().replace("+00:00","Z")

def get(v:Any,*path:Any,default:Any=None)->Any:
    cur=v
    for key in path:
        if isinstance(key,int):
            if not isinstance(cur,Sequence) or isinstance(cur,(str,bytes)) or len(cur)<=key:return default
            cur=cur[key]
        else:
            if not isinstance(cur,Mapping) or key not in cur:return default
            cur=cur[key]
    return cur

def first(v:Mapping[str,Any],paths:Sequence[Sequence[Any]])->Any:
    for p in paths:
        x=get(v,*p,default=None)
        if x is not None:return x
    return None

def unavailable(reason:str)->dict[str,Any]: return {"availability":"UNAVAILABLE","value":None,"reason":reason}

def source(name:str,family:str,role:str,status:str,provenance:Any=None,freshness:Any=None,*,authority:str="EXISTING_OWNER_ONLY",required:bool=True,notes:Sequence[str]=())->dict[str,Any]:
    return {"name":name,"upstream_family":family,"role":role,"authority":authority,"status":status,"provenance":provenance,"freshness":freshness or {"status":"UNAVAILABLE"},"required_for_packet_health":required,"notes":list(notes)}

def classify_crosscheck(*,primary_family:str,crosscheck_family:str,comparable:bool,definition_compatible:bool,primary_fresh:bool|None=None,crosscheck_fresh:bool|None=None,exact_equal:bool|None=None,expected_venue_basis:bool=False)->str:
    if primary_fresh is False:return "STALE_PRIMARY"
    if crosscheck_fresh is False:return "STALE_CROSSCHECK"
    if not comparable:return "NOT_COMPARABLE"
    if not definition_compatible:return "EXPLAINABLE_DEFINITION_DIFFERENCE"
    if primary_family==crosscheck_family:return "NOT_COMPARABLE"
    if exact_equal is True:return "AGREE"
    if expected_venue_basis:return "AGREE_WITH_EXPECTED_VENUE_BASIS"
    if exact_equal is False:return "TRUE_CONFLICT"
    return "NOT_COMPARABLE"

def crosscheck_record(*,metric:str,primary_family:str,crosscheck_family:str,status:str,independent:bool,reason:str,primary_value:Any=None,crosscheck_value:Any=None)->dict[str,Any]:
    if status not in CROSSCHECK_STATUSES:raise ValueError("invalid crosscheck status")
    if primary_family==crosscheck_family and independent:raise ValueError("same upstream family cannot be independent corroboration")
    return {"contract":CROSSCHECK_CONTRACT,"metric":metric,"primary_upstream_family":primary_family,"crosscheck_upstream_family":crosscheck_family,"independent":independent,"status":status,"primary_value":primary_value,"crosscheck_value":crosscheck_value,"authority_switch_allowed":False,"reason":reason}


def contracts()->dict[str,PointerContract]:
    return {
      "hourly":PointerContract(frozenset({"HOURLY_SEQUENCE_LATEST_POINTER_v2_2"}),frozenset({"HOURLY_SEQUENCE_CAPTURE_v2_2"}),("run_path",),exact_semantic_fields=("run_id","status","retrieved_at_utc"),timestamp_fields=("retrieved_at_utc",),retrieval_timestamp_field="retrieved_at_utc",pointer_timestamp_field="retrieved_at_utc"),
      "anchor":PointerContract(frozenset({"DAILY_LIVE_ANCHOR_LATEST_POINTER_v1"}),frozenset({"DAILY_LIVE_ANCHOR_INDEX_v3"}),("path",),exact_semantic_fields=("run_id","status","captured_at_utc"),timestamp_fields=("captured_at_utc",),retrieval_timestamp_field="captured_at_utc",pointer_timestamp_field="captured_at_utc"),
      "etf":PointerContract(frozenset({"DAILY_SETTLED_ETF_LATEST_POINTER_v2"}),frozenset({"DAILY_SETTLED_ETF_CALIBRATION_v2"}),("path",),exact_semantic_fields=("session_date",),timestamp_fields=("retrieved_at_utc",),retrieval_timestamp_field="retrieved_at_utc",pointer_timestamp_field="retrieved_at_utc"),
    }

def policies()->dict[str,FreshnessPolicy]:
    return {
      "hourly":FreshnessPolicy("HOURLY_OWNER_CADENCE_PLUS_GRACE_v1",retrieval_max_age=timedelta(hours=3),pointer_max_age=timedelta(hours=3)),
      "anchor":FreshnessPolicy("FOUR_HOUR_OWNER_CADENCE_PLUS_GRACE_v1",retrieval_max_age=timedelta(hours=6),pointer_max_age=timedelta(hours=6)),
      "etf":FreshnessPolicy("DAILY_OWNER_CADENCE_PLUS_GRACE_v1",retrieval_max_age=timedelta(hours=36),pointer_max_age=timedelta(hours=36)),
      "stable":FreshnessPolicy("DAILY_OWNER_CADENCE_PLUS_GRACE_v1",retrieval_max_age=timedelta(hours=36)),
      "entry":FreshnessPolicy("HOURLY_OWNER_CADENCE_PLUS_GRACE_v1",retrieval_max_age=timedelta(hours=3)),
    }

def read_optional(snapshot:GitCliSnapshot,path:str):
    try:
        v,p=snapshot.read_json(path);return v,p,None
    except IntegrityError as e:return None,None,f"{e.classification}:{e.detail}"

def read_pinned_bytes(root:Path,snapshot:GitCliSnapshot,path:str):
    pp=PurePosixPath(path)
    if not path or pp.is_absolute() or ".." in pp.parts:raise IntegrityError("GITHUB_POINTER_CONFLICT",f"unsafe_path:{path}")
    try:
        raw=subprocess.check_output(["git","show",f"{snapshot.commit_sha}:{path}"],cwd=root)
        blob=subprocess.check_output(["git","rev-parse","--verify",f"{snapshot.commit_sha}:{path}"],cwd=root,text=True).strip()
    except subprocess.CalledProcessError as e:raise IntegrityError("GITHUB_SOURCE_READ_FAIL",path) from e
    return raw,{"repository":REPOSITORY,"exact_commit_sha":snapshot.commit_sha,"exact_path":path,"git_blob_sha":blob,"raw_response_sha256":hashlib.sha256(raw).hexdigest(),"hash_semantics_contract":"DATA_PING_HASH_SEMANTICS_v1"}

def read_btc_d(root:Path,snapshot:GitCliSnapshot):
    path="03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv"
    try:
        raw,prov=read_pinned_bytes(root,snapshot,path);rows=list(csv.DictReader(io.StringIO(raw.decode())))
        if not rows:raise ValueError("empty csv")
        row=rows[-1];date=row.get("date") or row.get("Date") or row.get("timestamp") or row.get("time")
        value=row.get("btc_dominance") or row.get("BTC.D") or row.get("btc_d") or row.get("dominance") or row.get("value")
        if value is None:
            vals=[v for k,v in row.items() if k not in {"date","Date","timestamp","time"}];value=vals[-1] if vals else None
        return {"availability":"AVAILABLE","value_pct":float(value),"observation_date_utc":date,"source_convention":"CMC_DIRECT_SOURCE_CONVENTION","authority":"EXISTING_OWNER_EVIDENCE_ONLY"},prov,None
    except Exception as e:return unavailable(f"GITHUB_SOURCE_SCHEMA_FAIL:btc_d:{e}"),None,f"GITHUB_SOURCE_SCHEMA_FAIL:btc_d:{e}"

def sections(anchor:Mapping[str,Any])->dict[str,Any]:
    # DAILY_LIVE_ANCHOR_INDEX_v3 stores normalized owner metrics under `metrics`.
    # Keep limited legacy fallbacks only for older replayable packets, never as a hidden source switch.
    metrics=anchor.get("metrics") if isinstance(anchor.get("metrics"),Mapping) else anchor
    return {
      "derivatives":first(metrics,(("derivatives",),("okx_derivatives",),("owners","okx"))) or {},
      "breadth":first(metrics,(("breadth",),("market_breadth",),("owners","breadth"))) or {},
      "sentiment":first(metrics,(("sentiment",),("cfgi",),("owners","cfgi"))) or {},
      "rotation":first(metrics,(("rotation_context",),("altseason",),("owners","rotation_context"))) or {},
      "macro":first(metrics,(("macro",),("fred_macro",),("owners","fred"))) or {},
      "micro":first(metrics,(("microstructure",),("binance_microstructure",),("owners","binance_microstructure"))) or {},
    }

def latest_nonempty_capture(root:Path,snapshot:GitCliSnapshot,section_name:str,max_candidates:int=48):
    try:paths=subprocess.check_output(["git","ls-tree","-r","--name-only",snapshot.commit_sha,"--","03_DAILY_CAPTURE_LOGS/captures"],cwd=root,text=True).splitlines()
    except subprocess.CalledProcessError:return None,None,"GITHUB_SOURCE_READ_FAIL:capture_enumeration"
    paths=[p for p in paths if p.endswith(".json") and not p.endswith("/LATEST.json")]
    for path in sorted(paths,reverse=True)[:max_candidates]:
        payload,prov,err=read_optional(snapshot,path)
        if err or not payload:continue
        value=sections(payload).get(section_name)
        if value:return {"owner_payload":value,"source_capture_path":path,"source_capture_timestamp_utc":payload.get("captured_at_utc"),"fallback_semantics":"SAME_OWNER_PRIOR_SAMPLE_NOT_HIDDEN_FALLBACK"},prov,None
    return None,None,f"NO_NONEMPTY_{section_name.upper()}_SAMPLE_WITHIN_{max_candidates}_CAPTURES"

def live_prices(hourly:Mapping[str,Any])->dict[str,Any]:
    obs=get(hourly,"directional_summary","latest_observations",default=[]);x=obs[-1] if isinstance(obs,list) and obs else {}
    return {"observation_timestamp_utc":x.get("timestamp_utc"),"btc_usd":x.get("btc_close"),"eth_usd":x.get("eth_close"),"eth_btc":x.get("ethbtc_close"),"btc_return_1h_pct":x.get("btc_return_1h_pct"),"eth_return_1h_pct":x.get("eth_return_1h_pct"),"eth_minus_btc_return_1h_pp":x.get("eth_minus_btc_return_1h_pp"),"ethbtc_return_1h_pct":x.get("ethbtc_return_1h_pct")}

def normalize_stable(v:Mapping[str,Any]|None)->dict[str,Any]:
    if not v:return unavailable("OWNER_PAYLOAD_UNAVAILABLE")
    return {"availability":v.get("availability","AVAILABLE"),"owner_contract":v.get("contract"),"evidence_semantics":v.get("evidence_semantics"),"global_supply":first(v,(("global_supply",),("metrics","global_supply"),("supply","global"))),"change_1d_pct":first(v,(("change_1d_pct",),("metrics","change_1d_pct"))),"change_7d_pct":first(v,(("change_7d_pct",),("metrics","change_7d_pct"))),"change_30d_pct":first(v,(("change_30d_pct",),("metrics","change_30d_pct"))),"deployment_inference":"NOT_PERFORMED"}

def normalize_etf(v:Mapping[str,Any])->dict[str,Any]:
    return {"session_date":v.get("session_date"),"status":v.get("status"),"btc":first(v,(("assets","BTC"),("btc",),("settled","BTC"))),"eth":first(v,(("assets","ETH"),("eth",),("settled","ETH"))),"owner_contract":v.get("contract")}

def source_health(rows:Sequence[Mapping[str,Any]])->dict[str,Any]:
    counts={};fail=[]
    for r in rows:
        st=str(r.get("status","UNKNOWN"));counts[st]=counts.get(st,0)+1
        if r.get("required_for_packet_health",True) and st not in {"PASS","AVAILABLE"}:fail.append(str(r.get("name")))
    return {"status":"DEGRADED" if fail else "PASS","counts":counts,"required_failures":fail,"missing_is_market_evidence":False,"collector_failure_is_market_evidence":False}

def delta(a:Any,b:Any):
    if isinstance(a,bool) or isinstance(b,bool) or not isinstance(a,(int,float)) or not isinstance(b,(int,float)):return unavailable("NUMERIC_PAIR_REQUIRED")
    return {"availability":"AVAILABLE","value":a-b}

def compute_deltas(cur:Mapping[str,Any],prev:Mapping[str,Any]|None):
    if not prev:return {"availability":"UNAVAILABLE","reason":"NO_PRIOR_PACKET","fields":{}}
    return {"availability":"AVAILABLE","fields":{k:delta(get(cur,"market","live",k),get(prev,"market","live",k)) for k in ("btc_usd","eth_usd","eth_btc")}}


def assemble_packet(*,repo_root:Path,snapshot:GitCliSnapshot,now_utc:datetime,previous_packet:Mapping[str,Any]|None=None)->dict[str,Any]:
    cs,ps=contracts(),policies();sources=[];blockers=[]
    def chain(name,path,family,role):
        try:
            r=resolve_pointer_chain(snapshot,path,cs[name],now_utc=now_utc,freshness_policy=ps[name]);st="PASS" if get(r,"freshness","status") in {"PASS","UNCONFIRMED_POLICY"} else "DEGRADED"
            sources.append(source(name,family,role,st,r.get("provenance"),r.get("freshness")))
            if st!="PASS":blockers.append({"source":name,"classification":"SOURCE_FRESHNESS_DEGRADED","market_effect":"NONE"})
            return r
        except IntegrityError as e:
            sources.append(source(name,family,role,"FAIL",notes=(f"{e.classification}:{e.detail}",)));blockers.append({"source":name,"classification":e.classification,"detail":e.detail,"market_effect":"NONE"});return None
    hourly=chain("hourly","03_DAILY_CAPTURE_LOGS/hourly/LATEST.json","BINANCE_SPOT_PLUS_OKX_DERIVATIVES","OWNER_EVIDENCE")
    anchor=chain("anchor","03_DAILY_CAPTURE_LOGS/captures/LATEST.json","MULTI_OWNER_LIVE_ANCHOR","OWNER_INDEX")
    etf=chain("etf","03_DAILY_CAPTURE_LOGS/etf/LATEST.json","FARSIDE","SETTLED_OWNER_EVIDENCE")
    stable,stable_prov,stable_err=read_optional(snapshot,"03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json")
    stable_ts=first(stable or {},(("retrieved_at_utc",),("lifecycle","retrieved_at_utc"),("captured_at_utc",)))
    stable_fr=freshness_vector(now_utc=now_utc,policy=ps["stable"],retrieval_timestamp=stable_ts) if stable else None
    stable_st="PASS" if stable and get(stable_fr or {},"status") in {"PASS","UNCONFIRMED_POLICY"} else ("DEGRADED" if stable else "FAIL")
    sources.append(source("stablecoin_liquidity","DEFILLAMA","SUPPLY_LIQUIDITY_OWNER",stable_st,stable_prov,stable_fr,authority="EXISTING_NON_CANONICAL_OWNER",notes=((stable_err,) if stable_err else ())))
    if stable_st!="PASS":blockers.append({"source":"stablecoin_liquidity","classification":stable_err or "SOURCE_FRESHNESS_DEGRADED","market_effect":"NONE"})
    entry,entry_prov,entry_err=read_optional(snapshot,"04_MARKET_LEARNING/entry_signals/LATEST.json");entry_ts=first(entry or {},(("generated_at_utc",),("observed_at_utc",),("captured_at_utc",),("timestamp_utc",)))
    entry_fr=freshness_vector(now_utc=now_utc,policy=ps["entry"],retrieval_timestamp=entry_ts) if entry else None
    sources.append(source("entry_signal_reference","DERIVED_EXISTING_OWNERS","READ_ONLY_DECISION_SUPPORT_REFERENCE","PASS" if entry else "UNAVAILABLE",entry_prov,entry_fr,authority="NO_MARKET_OR_PORTFOLIO_AUTHORITY",required=False,notes=((entry_err,) if entry_err else ())))
    hp=hourly.get("target",{}) if hourly else {};ap=anchor.get("target",{}) if anchor else {};sec=sections(ap) if anchor else {k:{} for k in ("derivatives","breadth","sentiment","rotation","macro","micro")};live=live_prices(hp) if hourly else {"btc_usd":None,"eth_usd":None,"eth_btc":None}
    btc_d,btc_prov,btc_err=read_btc_d(repo_root,snapshot);sources.append(source("btc_dominance","COINMARKETCAP","DIRECT_SOURCE_DAILY_OWNER","PASS" if btc_d.get("availability")=="AVAILABLE" else "FAIL",btc_prov,{"status":"OWNER_DAILY_COMPLETENESS_VALIDATED"},authority="EXISTING_OWNER_EVIDENCE_ONLY",notes=((btc_err,) if btc_err else ())))
    if btc_err:blockers.append({"source":"btc_dominance","classification":btc_err,"market_effect":"NONE"})
    macro=sec["macro"] or None;macro_note=None
    if not macro:
        macro,macro_prov,macro_note=latest_nonempty_capture(repo_root,snapshot,"macro")
        if macro:sources.append(source("macro_risk_prior_sample","FRED","SAME_OWNER_PRIOR_SAMPLE","PASS",macro_prov,{"status":"POLICY_UNAVAILABLE"},authority="EXISTING_OWNER_EVIDENCE_ONLY",notes=("same owner prior sample; timestamp retained",)))
        else:blockers.append({"source":"macro_risk","classification":macro_note or "UNAVAILABLE","market_effect":"NONE"})
    catalyst,cat_prov,cat_err=read_optional(snapshot,"03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json");cat=unavailable("DISCOVERY_ONLY_OWNER_UNAVAILABLE") if not catalyst else {"availability":"AVAILABLE","contract":catalyst.get("contract"),"authority":catalyst.get("authority"),"run_status":catalyst.get("run_status"),"daily_result":catalyst.get("daily_result"),"observation_date_utc":catalyst.get("observation_date_utc"),"shared_row_tournament_eligible":catalyst.get("shared_row_tournament_eligible"),"production_critical":False}
    sources.append(source("catalyst_context","SITUATION_ROOM_MULTI_SOURCE","DISCOVERY_ONLY",catalyst.get("run_status","AVAILABLE") if catalyst else "UNAVAILABLE",cat_prov,{"status":"POLICY_UNAVAILABLE"},authority="RESEARCH_ONLY_NON_CANONICAL",required=False,notes=((cat_err,) if cat_err else ())))
    checks=[crosscheck_record(metric="ALTSEASON_CONTEXT",primary_family="BLOCKCHAINCENTER",crosscheck_family="COINMARKETCAP",independent=True,status="EXPLAINABLE_DEFINITION_DIFFERENCE",reason="PUBLISHED_METHODOLOGIES_AND_UNIVERSES_DIFFER;CONTEXT_ONLY")]
    anchor_btc=first(sec["micro"],(("BTC","midpoint"),("btc","midpoint"),("BTCUSDT","midpoint"),("btc_midpoint",)))
    if live.get("btc_usd") is not None and anchor_btc is not None:checks.insert(0,crosscheck_record(metric="BTC_USD_SPOT_SANITY",primary_family="BINANCE",crosscheck_family="BINANCE",independent=False,status="NOT_COMPARABLE",reason="SAME_UPSTREAM_FAMILY_AND_DIFFERENT_OBSERVATION_TIME;SANITY_ONLY",primary_value=live.get("btc_usd"),crosscheck_value=anchor_btc))
    packet={"contract":CONTRACT,"generated_at_utc":zulu(now_utc),"freeze":{"repository":REPOSITORY,"exact_commit_sha":snapshot.commit_sha,"all_source_reads_pinned_to_snapshot":True,"manual_input_count":0,"chatgpt_automation_slots_added":0},"authority":dict(AUTHORITY),"market":{"live":{**live,"availability":"AVAILABLE" if any(v is not None for k,v in live.items() if k!="observation_timestamp_utc") else "UNAVAILABLE"},"btc_dominance":btc_d,"derivatives":sec["derivatives"] or unavailable("LIVE_ANCHOR_SECTION_UNAVAILABLE"),"breadth":sec["breadth"] or unavailable("LIVE_ANCHOR_SECTION_UNAVAILABLE"),"etf":normalize_etf(etf.get("target",{})) if etf else unavailable("ETF_OWNER_UNAVAILABLE"),"stablecoin_liquidity":normalize_stable(stable),"macro_risk":macro or unavailable(macro_note or "MACRO_OWNER_UNAVAILABLE"),"sentiment":sec["sentiment"] or unavailable("LIVE_ANCHOR_SECTION_UNAVAILABLE"),"altseason_context":sec["rotation"] or unavailable("LIVE_ANCHOR_SECTION_UNAVAILABLE"),"catalyst_context":cat},"crosschecks":checks,"entry_signal_reference":{"availability":"AVAILABLE" if entry else "UNAVAILABLE","path":"04_MARKET_LEARNING/entry_signals/LATEST.json" if entry else None,"contract":entry.get("contract") if entry else None,"state":first(entry or {},(("state",),("entry_signal",),("signal","state"))),"authority":"READ_ONLY_DECISION_SUPPORT_ONLY"},"blockers":blockers,"validation":{"interpretation_performed":False,"portfolio_action_performed":False,"hidden_fallback_used":False,"crosscheck_can_switch_owner":False,"proxy_promoted_to_canonical":False,"snapshot_consistency":snapshot.consistency()}}
    packet["deltas_vs_prior"]=compute_deltas(packet,previous_packet);packet["source_health"]=source_health(sources);packet["validation"]["status"]="PASS" if packet["source_health"]["status"]=="PASS" else "DEGRADED";packet["sources"]=sources;packet["packet_normalized_sha256"]=normalized_sha256({k:v for k,v in packet.items() if k!="packet_normalized_sha256"});return packet


def load_previous(snapshot:GitCliSnapshot):
    latest,_,err=read_optional(snapshot,str(OUTPUT_ROOT/"LATEST.json"))
    if not latest or err or not isinstance(latest.get("path"),str):return None
    previous,_,_=read_optional(snapshot,latest["path"]);return previous

def write_packet(root:Path,packet:Mapping[str,Any]):
    generated=str(packet["generated_at_utc"]).replace(":","").replace("-","");day=generated[:8];tm=generated[9:15];run_id=f"AUTO_STATE_{day}T{tm}Z_{packet['freeze']['exact_commit_sha'][:12]}";out=root/OUTPUT_ROOT/"runs"/day[:4]/day[4:6]/day[6:8];out.mkdir(parents=True,exist_ok=True);run=out/f"{tm}_{run_id}.json";run.write_bytes(canonical_json(packet));rel=run.relative_to(root).as_posix();latest={"contract":LATEST_CONTRACT,"generated_at_utc":packet["generated_at_utc"],"path":rel,"source_freeze_commit_sha":packet["freeze"]["exact_commit_sha"],"packet_normalized_sha256":packet["packet_normalized_sha256"],"validation_status":get(packet,"validation","status")};lp=root/OUTPUT_ROOT/"LATEST.json";lp.parent.mkdir(parents=True,exist_ok=True);lp.write_bytes(canonical_json(latest));return run,lp

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--repo-root",default=".");p.add_argument("--ref",required=True);p.add_argument("--now-utc");p.add_argument("--write",action="store_true");a=p.parse_args();root=Path(a.repo_root).resolve();now=datetime.fromisoformat(a.now_utc.replace("Z","+00:00")) if a.now_utc else datetime.now(timezone.utc);snap=GitCliSnapshot.open_repo(root,repository=REPOSITORY,ref=a.ref);packet=assemble_packet(repo_root=root,snapshot=snap,now_utc=now,previous_packet=load_previous(snap))
    if a.write:
        run,lp=write_packet(root,packet);print(json.dumps({"status":packet["validation"]["status"],"run_path":str(run),"latest_path":str(lp),"freeze_commit":snap.commit_sha},sort_keys=True))
    else:print(canonical_json(packet).decode(),end="")
    return 0
if __name__=="__main__":raise SystemExit(main())
