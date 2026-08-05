#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, itertools, json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC=timezone.utc
KINDS={"SENSOR_COMBINATION","FORECAST_TEST","SEQUENCE_TEST","DATA_QUALITY_TEST"}
OPS={"GT","LT","DELTA_PCT_GT","DELTA_PCT_LT","POSITIVE","NEGATIVE","AVAILABLE","CHANGED"}


def canon(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(",",":"))+"\n").encode()
def sha(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def read(p:Path)->Any:return json.loads(p.read_text())
def dt(v:Any)->datetime:
    x=datetime.fromisoformat(str(v).replace("Z","+00:00"));return (x if x.tzinfo else x.replace(tzinfo=UTC)).astimezone(UTC)
def iso(x:datetime)->str:return x.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00","Z")
def at(v:Any,path:str)->Any:
    for part in path.split("."):
        if not isinstance(v,dict):return None
        v=v.get(part)
    return v
def rel(root:Path,p:Path)->str:return str(p.resolve().relative_to(root.resolve()))
def write_new(p:Path,v:dict[str,Any])->bool:
    if p.exists():return False
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(canon(v));return True


def component(raw:dict[str,Any])->dict[str,Any]:
    path=str(raw.get("metric_path") or "").strip();op=str(raw.get("operator") or "").upper();thr=raw.get("threshold")
    if not path or op not in OPS:raise ValueError("invalid_component")
    if op in {"GT","LT","DELTA_PCT_GT","DELTA_PCT_LT"} and not isinstance(thr,(int,float)):raise ValueError("threshold_required")
    return {"metric_path":path,"operator":op,"threshold":float(thr) if isinstance(thr,(int,float)) else None}


def normalize(raw:dict[str,Any])->dict[str,Any]:
    kind=str(raw.get("kind") or "SENSOR_COMBINATION").upper();direction=str(raw.get("target_direction") or "NONE").upper()
    if kind not in KINDS or direction not in {"UP","DOWN","RANGE","NONE"}:raise ValueError("invalid_kind_or_direction")
    title=str(raw.get("title") or "").strip();hyp=str(raw.get("hypothesis") or "").strip();fals=str(raw.get("falsifier") or "").strip();h=int(raw.get("horizon_days") or 0)
    if not title or not hyp or not fals or not 1<=h<=365:raise ValueError("invalid_identity_or_horizon")
    target=str(raw.get("target_metric_path") or "").strip() or None;thr=raw.get("target_threshold_pct");lo=raw.get("target_range_lower_pct");hi=raw.get("target_range_upper_pct")
    if direction in {"UP","DOWN"} and (not target or not isinstance(thr,(int,float)) or float(thr)<=0):raise ValueError("invalid_directional_target")
    if direction=="RANGE" and (not target or not isinstance(lo,(int,float)) or not isinstance(hi,(int,float)) or float(lo)>=float(hi)):raise ValueError("invalid_range_target")
    if direction=="NONE":target=thr=lo=hi=None
    return {"kind":kind,"title":title,"hypothesis":hyp,"falsifier":fals,"horizon_days":h,"components":[component(x) for x in raw.get("components",[]) if isinstance(x,dict)],"target_metric_path":target,"target_direction":direction,"target_threshold_pct":float(thr) if isinstance(thr,(int,float)) else None,"target_range_lower_pct":float(lo) if isinstance(lo,(int,float)) else None,"target_range_upper_pct":float(hi) if isinstance(hi,(int,float)) else None,"regime_dependency":str(raw.get("regime_dependency") or "REGIME_AGNOSTIC"),"novelty_reason":str(raw.get("novelty_reason") or "UNSPECIFIED"),"revisit_conditions":[str(x) for x in raw.get("revisit_conditions",[])],"evidence_basis":[str(x) for x in raw.get("evidence_basis",[])]}


def identity_spec(spec:dict[str,Any])->dict[str,Any]:
    return {k:spec[k] for k in ("kind","title","hypothesis","falsifier","horizon_days","components","target_metric_path","target_direction","target_threshold_pct","target_range_lower_pct","target_range_upper_pct","regime_dependency")}


def placebo(event_window_id:str)->str:
    return ("UP","DOWN","RANGE")[int(event_window_id[0],16)%3]


def from_forecast(x:dict[str,Any],latest:dict[str,Any])->dict[str,Any]|None:
    direction=str(x.get("direction") or "").upper();path=str(x.get("metric_path") or "");h=x.get("horizon_days");start=at(latest,path)
    if direction not in {"UP","DOWN","RANGE"} or not path or not isinstance(h,int):return None
    out={"kind":"FORECAST_TEST","title":f"Prospective {path} {direction}","hypothesis":str(x.get("rationale") or "Prospective forecast candidate"),"falsifier":"The fixed target is not satisfied at the fixed horizon.","horizon_days":h,"components":[],"target_metric_path":path,"target_direction":direction,"target_threshold_pct":None,"target_range_lower_pct":None,"target_range_upper_pct":None,"regime_dependency":"CURRENT_OBSERVED_REGIME","novelty_reason":"DAILY_DIRECTOR_FORECAST","revisit_conditions":[],"evidence_basis":[str(x.get("rationale") or "")]}
    if direction in {"UP","DOWN"}:
        if not isinstance(x.get("threshold"),(int,float)) or float(x["threshold"])<=0:return None
        out["target_threshold_pct"]=float(x["threshold"])
    else:
        lo=x.get("range_low");hi=x.get("range_high")
        if not isinstance(start,(int,float)) or not isinstance(lo,(int,float)) or not isinstance(hi,(int,float)) or float(lo)>=float(hi):return None
        out["target_range_lower_pct"]=(float(lo)/float(start)-1)*100;out["target_range_upper_pct"]=(float(hi)/float(start)-1)*100
    return out


def emergent_pairs(context:dict[str,Any],latest:dict[str,Any],limit:int=6)->list[dict[str,Any]]:
    rows=[]
    for x in context.get("metric_deltas",[]):
        if not isinstance(x,dict) or not isinstance(x.get("percentage_change"),(int,float)):continue
        path=str(x.get("metric") or "");change=float(x["percentage_change"])
        if not path or abs(change)<0.05 or any(k in path.lower() for k in ("timestamp","time_ms","retrieval")):continue
        rows.append((abs(change),path,change))
    rows=sorted(rows,reverse=True)[:6];target="spot.BTCUSDT.close" if isinstance(at(latest,"spot.BTCUSDT.close"),(int,float)) else None
    out=[]
    if not target:return out
    for (_,a,da),(_,b,db) in itertools.combinations(rows,2):
        same=da*db>0;direction="UP" if same and da>0 else "DOWN" if same else "RANGE"
        out.append({"kind":"SENSOR_COMBINATION","title":f"Emergent pair: {a} + {b}","hypothesis":f"The coincident direction of {a} and {b} may contain forward information for BTC over seven days.","falsifier":"The pair fails to beat its fixed directional or range target across prospective independent windows.","horizon_days":7,"components":[{"metric_path":a,"operator":"DELTA_PCT_GT" if da>0 else "DELTA_PCT_LT","threshold":0.0},{"metric_path":b,"operator":"DELTA_PCT_GT" if db>0 else "DELTA_PCT_LT","threshold":0.0}],"target_metric_path":target,"target_direction":direction,"target_threshold_pct":1.0 if direction in {"UP","DOWN"} else None,"target_range_lower_pct":-1.5 if direction=="RANGE" else None,"target_range_upper_pct":1.5 if direction=="RANGE" else None,"regime_dependency":"DISCOVERED_IN_CURRENT_DELTA_REGIME","novelty_reason":"AUTOMATIC_COINCIDENCE_DISCOVERY","revisit_conditions":["Re-evaluate whenever both metrics are comparable."],"evidence_basis":[f"{a} delta={da:.8f}%",f"{b} delta={db:.8f}%"]})
        if len(out)>=limit:break
    return out


def legacy(path:Path|None)->list[dict[str,Any]]:
    if not path or not path.exists():return []
    v=read(path);out=[]
    for p in v.get("pairs",[]):
        a=str(p.get("sensor_a") or "UNKNOWN");b=str(p.get("sensor_b") or "UNKNOWN");pid=str(p.get("pair_id") or "UNKNOWN")
        out.append({"kind":"SENSOR_COMBINATION","title":f"Legacy sensor pair {pid}: {a} + {b}","hypothesis":f"The frozen combination {a} and {b} may add marginal value when machine-mappable.","falsifier":"After prospective mapping and sufficient independent windows, the pair fails to beat the best single-sensor control.","horizon_days":7,"components":[],"target_metric_path":None,"target_direction":"NONE","target_threshold_pct":None,"target_range_lower_pct":None,"target_range_upper_pct":None,"regime_dependency":"WAITING_FOR_MACHINE_SENSOR_MAPPING","novelty_reason":f"PRESERVE_FROZEN_SENSOR_PAIR_{pid}","revisit_conditions":[f"Map {a} to source-backed metrics",f"Map {b} to source-backed metrics","Create a new linked measurable candidate without rewriting this concept"],"evidence_basis":[f"legacy_test_id={v.get('test_id')}",f"pair_id={pid}"]})
    return out


def delta(latest:Any,previous:Any)->float|None:
    if not isinstance(latest,(int,float)) or not isinstance(previous,(int,float)) or previous==0:return None
    return (float(latest)/float(previous)-1)*100
def evaluate(c:dict[str,Any],latest:dict[str,Any],previous:dict[str,Any])->dict[str,Any]:
    l=at(latest,c["metric_path"]);p=at(previous,c["metric_path"]);d=delta(l,p);op=c["operator"];t=c.get("threshold")
    if l is None or (op.startswith("DELTA_") and d is None):m=None
    elif op=="AVAILABLE":m=True
    elif op=="GT":m=isinstance(l,(int,float)) and float(l)>float(t)
    elif op=="LT":m=isinstance(l,(int,float)) and float(l)<float(t)
    elif op=="DELTA_PCT_GT":m=d is not None and d>float(t)
    elif op=="DELTA_PCT_LT":m=d is not None and d<float(t)
    elif op=="POSITIVE":m=isinstance(l,(int,float)) and float(l)>0
    elif op=="NEGATIVE":m=isinstance(l,(int,float)) and float(l)<0
    else:m=p is not None and l!=p
    return {**c,"latest":l,"previous":p,"delta_pct":round(d,8) if d is not None else None,"matched":m}


def jsons(root:Path,contract:str)->list[tuple[Path,dict[str,Any]]]:
    out=[]
    for p in root.rglob("*.json") if root.exists() else []:
        try:v=read(p)
        except Exception:continue
        if v.get("contract")==contract:out.append((p,v))
    return out


def registry(candidate_root:Path,obs_root:Path,forecast_root:Path,outcome_root:Path,receipt_root:Path,now:str)->dict[str,Any]:
    candidates=[v for _,v in jsons(candidate_root,"EXPERIMENT_CANDIDATE_v1")];obs={};candidate_forecasts={};outcomes={};receipts={}
    for _,v in jsons(obs_root,"EXPERIMENT_OBSERVATION_v1"):obs.setdefault(v["candidate_id"],[]).append(v)
    for _,v in jsons(forecast_root,"FROZEN_FORECAST_v1"):
        cid=v.get("source_candidate_id");fid=v.get("forecast_id")
        if cid and fid:candidate_forecasts.setdefault(cid,[]).append(fid)
    for p in outcome_root.rglob("*.json") if outcome_root.exists() else []:
        try:v=read(p)
        except Exception:continue
        if v.get("forecast_id"):outcomes[v["forecast_id"]]=v
    for _,v in jsons(receipt_root,"EXPERIMENT_EXECUTION_RECEIPT_v1"):receipts.setdefault(v.get("candidate_id"),[]).append(v.get("replication_status"))
    rows=[];counts={}
    for c in candidates:
        cid=c["candidate_id"];o=sorted(obs.get(cid,[]),key=lambda x:x.get("observed_at_utc",""));last=o[-1] if o else None;fos=candidate_forecasts.get(cid,[]);mature=[outcomes[x] for x in fos if x in outcomes]
        if any(x.get("status")=="MATURED" and x.get("result")=="HIT" for x in mature):state="MATURED_SUPPORTED"
        elif any(x.get("status")=="MATURED" and x.get("result")=="MISS" for x in mature):state="MATURED_NOT_SUPPORTED"
        elif mature:state="MATURED_INCONCLUSIVE"
        elif fos:state="WAITING_FOR_MATURITY"
        elif last and last.get("evaluation_status")=="WAITING_FOR_MAPPING":state="WAITING_FOR_MAPPING"
        elif last and last.get("evaluation_status")=="WAITING_FOR_DATA":state="WAITING_FOR_DATA"
        elif last and last.get("evaluation_status")=="FIRED_NO_TARGET":state="FIRED_NO_TARGET"
        elif o:state="INCUBATING"
        else:state="PROPOSED"
        counts[state]=counts.get(state,0)+1;rows.append({"candidate_id":cid,"title":c["spec"]["title"],"kind":c["spec"]["kind"],"state":state,"created_at_utc":c["created_at_utc"],"observation_count":len(o),"forecast_ids":fos,"matured_outcome_count":len(mature),"replication_receipts":sorted(set(x for x in receipts.get(cid,[]) if x)),"automatic_age_expiry":False})
    return {"contract":"EXPERIMENT_LIFECYCLE_REGISTRY_v1","generated_at_utc":now,"authority":"SHADOW_ONLY_NO_AUTOMATIC_PROMOTION","candidate_count":len(rows),"state_counts":counts,"candidates":rows,"rules":{"idea_bank_capacity":"UNBOUNDED_WITH_SEMANTIC_DEDUPLICATION","automatic_age_expiry":False,"max_new_forecasts_per_run_default":5,"promotion_requires_governance_review":True}}


def main()->None:
    p=argparse.ArgumentParser()
    for name in ("repo-root","daily-output","daily-context","daily-receipt","candidate-root","observation-root","dispatch-root","forecast-root","outcome-root","receipt-root","registry-output","manifest-output"):p.add_argument(f"--{name}",type=Path,required=True)
    p.add_argument("--legacy-sensor-catalog",type=Path);p.add_argument("--repository",default="Donh91/Investering-Framework-Archive-v1");p.add_argument("--branch",default="main");p.add_argument("--max-new-forecasts",type=int,default=5);a=p.parse_args()
    root=a.repo_root.resolve();output=read(a.daily_output);context=read(a.daily_context);receipt=read(a.daily_receipt);latest=((context.get("latest_capture") or {}).get("market_metrics") or {});previous=((context.get("previous_capture") or {}).get("market_metrics") or {});captured=(context.get("latest_capture") or {}).get("captured_at_utc") or iso(datetime.now(UTC));when=dt(captured);now=iso(datetime.now(UTC));source={"daily_output_sha256":sha(output),"daily_context_sha256":sha(context),"daily_receipt_sha256":sha(receipt),"source_run_id":(context.get("latest_capture") or {}).get("run_id")}
    raw=[x for x in output.get("experiment_candidates",[]) if isinstance(x,dict)]+legacy(a.legacy_sensor_catalog)+emergent_pairs(context,latest)
    for x in output.get("forecast_candidates",[]):
        if isinstance(x,dict):
            y=from_forecast(x,latest)
            if y:raw.append(y)
    new_ids=set();rejected=[]
    for x in raw:
        try:
            spec=normalize(x);cid="EC-"+sha(identity_spec(spec))[:20];value={"contract":"EXPERIMENT_CANDIDATE_v1","candidate_id":cid,"created_at_utc":captured,"registered_at_utc":now,"spec":spec,"source":{**source,"daily_output_path":rel(root,a.daily_output),"daily_context_path":rel(root,a.daily_context),"daily_receipt_path":rel(root,a.daily_receipt)},"dormancy_policy":{"automatic_age_expiry":False,"retain_until":"FALSIFIED_OR_GOVERNANCE_CLOSED"},"authority":{"canonical_promotion":False,"framework_state_change":False,"model_weight_change":False,"portfolio_action":False}}
            if write_new(a.candidate_root/when.strftime("%Y/%m")/f"{cid}.json",value):new_ids.add(cid)
        except Exception as e:rejected.append({"title":str(x.get("title") or "UNKNOWN"),"error":str(e)})
    new_forecasts=dispatch=0
    candidate_rows=jsons(a.candidate_root,"EXPERIMENT_CANDIDATE_v1")
    candidate_rows.sort(key=lambda item:(0 if item[1].get("spec",{}).get("kind")=="FORECAST_TEST" else 1,str(item[1].get("candidate_id") or "")))
    for spec_path,c in candidate_rows:
        spec=c["spec"];results=[evaluate(x,latest,previous) for x in spec["components"]];mapping=not spec["components"] and spec["kind"]!="FORECAST_TEST";missing=any(x["matched"] is None for x in results);fired=(not mapping and ((not spec["components"] and spec["kind"]=="FORECAST_TEST") or (results and not missing and all(x["matched"] for x in results))))
        status="WAITING_FOR_MAPPING" if mapping else "WAITING_FOR_DATA" if missing else "FIRED_NO_TARGET" if fired and spec["target_direction"]=="NONE" else "FIRED" if fired else "OBSERVED_NOT_FIRED";oid="EO-"+sha({"candidate_id":c["candidate_id"],"captured":captured,"source":source})[:20];ob={"contract":"EXPERIMENT_OBSERVATION_v1","observation_id":oid,"candidate_id":c["candidate_id"],"observed_at_utc":captured,"evaluation_status":status,"component_results":results,"source":source,"authority":"SHADOW_ONLY"};op=a.observation_root/c["candidate_id"]/f"{oid}.json";is_new=False if mapping and c["candidate_id"] not in new_ids else write_new(op,ob)
        fid=None;start=at(latest,spec.get("target_metric_path") or "") if spec.get("target_metric_path") else None
        if fired and spec["target_direction"]!="NONE" and isinstance(start,(int,float)) and new_forecasts<a.max_new_forecasts:
            window=sha({"run":source["source_run_id"],"captured":captured})[:20];fid="EXP-FC-"+sha({"candidate_id":c["candidate_id"],"window":window})[:20];fc={"contract":"FROZEN_FORECAST_v1","forecast_id":fid,"source_candidate_id":c["candidate_id"],"source_observation_id":oid,"frozen_at_utc":captured,"outcome_due_utc":iso(when+timedelta(days=spec["horizon_days"])),"metric_path":spec["target_metric_path"],"direction":spec["target_direction"],"start_value":float(start),"threshold_pct":spec["target_threshold_pct"],"range_lower_pct":spec["target_range_lower_pct"],"range_upper_pct":spec["target_range_upper_pct"],"causal_event_window_id":window,"experimental_only":True,"controls":{"always_wait":"ALWAYS_WAIT","single_component_specs":spec["components"],"deterministic_placebo_direction":placebo(window),"control_freeze_time_utc":captured},"authority":{"portfolio_action":False,"framework_state_change":False,"model_weight_change":False,"canonical_promotion":False}}
            if write_new(a.forecast_root/when.strftime("%Y/%m")/f"{fid}.json",fc):new_forecasts+=1
        if is_new and (c["candidate_id"] in new_ids or fired):
            rid="ER-"+sha({"candidate_id":c["candidate_id"],"observation_id":oid})[:20];req={"contract":"EXPERIMENT_REQUEST_v1","request_id":rid,"candidate_id":c["candidate_id"],"created_at_utc":now,"request_type":"SENSOR_FIRE_REPLICATION" if fired else "SPEC_REGISTRATION","spec":spec,"embedded_observation":ob,"local_frozen_forecast_id":fid,"source_spec_path":rel(root,spec_path),"source_spec_sha256":sha(c),"authority":{"automatic_trade":False,"canonical_promotion":False,"portfolio_action":False}}
            dispatch+=int(write_new(a.dispatch_root/when.strftime("%Y/%m/%d")/f"{rid}.json",req))
    reg=registry(a.candidate_root,a.observation_root,a.forecast_root,a.outcome_root,a.receipt_root,now);a.registry_output.parent.mkdir(parents=True,exist_ok=True);a.registry_output.write_bytes(canon(reg));requests=[]
    for path,v in jsons(a.dispatch_root,"EXPERIMENT_REQUEST_v1"):
        rp=rel(root,path);requests.append({"request_id":v["request_id"],"candidate_id":v["candidate_id"],"path":rp,"sha256":sha(v),"raw_url":f"https://raw.githubusercontent.com/{a.repository}/{a.branch}/{rp}"})
    manifest={"contract":"EXPERIMENT_DISPATCH_MANIFEST_v1","generated_at_utc":now,"source_repository":a.repository,"source_branch":a.branch,"request_count":len(requests),"requests":sorted(requests,key=lambda x:x["request_id"]),"authority":"SHADOW_ONLY_CROSS_REPO_DISPATCH"};a.manifest_output.parent.mkdir(parents=True,exist_ok=True);a.manifest_output.write_bytes(canon(manifest));print(json.dumps({"candidate_count":reg["candidate_count"],"new_candidate_count":len(new_ids),"new_forecasts":new_forecasts,"dispatch_created":dispatch,"rejected":rejected},sort_keys=True))

if __name__=="__main__":main()
