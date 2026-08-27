from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists(): return {}
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except Exception: return {}
    return value if isinstance(value,dict) else {}


def parse_ts(value: Any) -> datetime | None:
    if not value: return None
    try: return datetime.fromisoformat(str(value).replace("Z","+00:00")).astimezone(timezone.utc)
    except Exception: return None


def age_hours(value: Any, now: datetime) -> float | None:
    parsed=parse_ts(value)
    return None if parsed is None else round(max(0.0,(now-parsed).total_seconds()/3600.0),3)


def file_sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() and path.is_file() else None


def pointer_summary(root: Path, pointer_path: str) -> dict[str, Any]:
    pointer=load_json(root/pointer_path); target_path=pointer.get("path"); declared=pointer.get("sha256"); target=root/str(target_path) if target_path else None; actual=file_sha256(target) if target else None
    return {"path":pointer_path,"target_path":target_path,"declared_sha256":declared,"actual_sha256":actual,"hash_status":"MATCH" if declared and actual and declared==actual else "MISMATCH" if declared or actual else "UNAVAILABLE"}


def verified_weekly_target(root: Path, pointer_path: str) -> dict[str, Any]:
    pointer=load_json(root/pointer_path); target_path=pointer.get("path"); declared=pointer.get("sha256")
    if not target_path: return {"pointer_path":pointer_path,"target_path":None,"declared_sha256":declared,"actual_sha256":None,"hash_status":"UNAVAILABLE","hash_mode":"SEMANTIC_PACKAGE_HASH","target":{}}
    target_file=root/str(target_path); target=load_json(target_file); semantic_sha=target.get("package_sha256") if isinstance(target,dict) else None; contract_ok=target.get("contract")=="MASTER_MONDAY_MACHINE_PACKAGE_v1" if isinstance(target,dict) else False; match=bool(declared and semantic_sha and declared==semantic_sha and contract_ok)
    return {"pointer_path":pointer_path,"target_path":target_path,"declared_sha256":declared,"actual_sha256":semantic_sha,"raw_file_sha256":file_sha256(target_file),"hash_status":"MATCH" if match else "MISMATCH" if declared or semantic_sha else "UNAVAILABLE","hash_mode":"SEMANTIC_PACKAGE_HASH","contract_status":"MATCH" if contract_ok else "MISMATCH","target":target}


def latest_director(root: Path):
    candidates=sorted((root/"research/api_agent/outputs/daily").glob("**/DAILY_DIRECTOR_OUTPUT.json"))
    if not candidates: return None,{},{}
    path=candidates[-1]; return path,load_json(path),load_json(path.with_name("DAILY_DIRECTOR_RECEIPT.json"))


def latest_remediation(root: Path):
    latest=root/"research/remediation/LATEST_REMEDIATION_QUEUE.json"
    if latest.exists(): return latest,load_json(latest)
    candidates=sorted((root/"research/remediation").glob("**/REMEDIATION_QUEUE.json"))
    if not candidates: return None,{}
    path=candidates[-1]; return path,load_json(path)


def count_receipts(root: Path) -> dict[str,Any]:
    total=0; cost=0.0; input_tokens=0; output_tokens=0; latest_ts=None; latest_row={}; month=datetime.now(timezone.utc).strftime("%Y-%m")
    for path in (root/"research/api_agent/outputs").glob("**/*RECEIPT.json"):
        row=load_json(path); created=row.get("completed_at_utc") or row.get("generated_at_utc") or row.get("created_at_utc"); ts=parse_ts(created)
        if ts is None:
            try: ts=datetime.fromtimestamp(path.stat().st_mtime,tz=timezone.utc)
            except Exception: ts=None
        if ts and ts.strftime("%Y-%m")!=month: continue
        total+=1; cost+=float(row.get("cost_usd") or row.get("estimated_cost_usd") or 0.0); input_tokens+=int(row.get("input_tokens") or 0); output_tokens+=int(row.get("output_tokens") or 0)
        if ts and (latest_ts is None or ts>latest_ts): latest_ts=ts; latest_row={"path":str(path.relative_to(root)),"task":row.get("task"),"model":row.get("model"),"status":row.get("status"),"completed_at_utc":created,"cost_usd":row.get("cost_usd") or row.get("estimated_cost_usd")}
    return {"month":month,"receipt_count":total,"cost_usd":round(cost,6),"input_tokens":input_tokens,"output_tokens":output_tokens,"latest":latest_row}


def incident_summary(root: Path) -> dict[str,Any]:
    open_paths=[]
    for path in sorted((root/"09_SOURCE_QA/incidents").glob("INCIDENT_*.md")):
        text=path.read_text(encoding="utf-8",errors="replace")
        if "status: CLOSED" not in text and "Status: CLOSED" not in text: open_paths.append(str(path.relative_to(root)))
    return {"open_count":len(open_paths),"paths":open_paths[-20:]}


def freshness_status(age: float|None, *, green: float, amber: float):
    if age is None: return "RED","TIMESTAMP_UNAVAILABLE"
    if age<=green: return "GREEN","FRESH"
    if age<=amber: return "AMBER","DELAYED"
    return "RED","STALE"


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--repo-root",type=Path,default=Path(".")); parser.add_argument("--output",type=Path,default=Path("LATEST_OPERATIONS_DASHBOARD.json")); args=parser.parse_args(); root=args.repo_root.resolve(); now=datetime.now(timezone.utc)
    architecture=load_json(root/"research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json"); automation=load_json(root/"research/architecture_health/LATEST_AUTOMATION_HEALTH.json"); handoff=load_json(root/"LATEST_HANDOFF.json")
    capture_pointer=pointer_summary(root,"03_DAILY_CAPTURE_LOGS/captures/LATEST.json"); capture_target=load_json(root/str(capture_pointer.get("target_path"))) if capture_pointer.get("target_path") else {}
    director_path,director,director_receipt=latest_director(root); weekly_verified=verified_weekly_target(root,"research/api_agent/outputs/weekly/2026/W34/MASTER_MONDAY_DELIVERY_POINTER.json"); weekly_path=root/str(weekly_verified.get("target_path")) if weekly_verified.get("target_path") else None; weekly=weekly_verified.get("target") if isinstance(weekly_verified.get("target"),dict) else {}
    remediation_path,remediation=latest_remediation(root); experiment=load_json(root/"research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"); receipt_sync=load_json(root/"research/experiment_lifecycle/LATEST_EXPERIMENT_RECEIPT_SYNC.json")
    capture_ts=capture_target.get("captured_at_utc") or capture_target.get("capture_timestamp_utc"); director_ts=director_receipt.get("completed_at_utc") or director_receipt.get("generated_at_utc") or director_receipt.get("created_at_utc"); weekly_ts=weekly.get("generated_at_utc"); remediation_ts=remediation.get("generated_at_utc"); experiment_ts=experiment.get("generated_at_utc"); receipt_sync_ts=receipt_sync.get("generated_at_utc")
    capture_age=age_hours(capture_ts,now); director_age=age_hours(director_ts,now); weekly_age=age_hours(weekly_ts,now); remediation_age=age_hours(remediation_ts,now); experiment_age=age_hours(experiment_ts,now); receipt_sync_age=age_hours(receipt_sync_ts,now)
    capture_status,capture_reason=freshness_status(capture_age,green=8,amber=12); director_status,director_reason=freshness_status(director_age,green=8,amber=24); weekly_status,weekly_reason=freshness_status(weekly_age,green=192,amber=240); remediation_status,remediation_reason=freshness_status(remediation_age,green=24,amber=48); experiment_status,experiment_reason=freshness_status(experiment_age,green=8,amber=24); receipt_sync_status,receipt_sync_reason=freshness_status(receipt_sync_age,green=8,amber=24)
    if capture_pointer["hash_status"]!="MATCH": capture_status,capture_reason="RED","POINTER_HASH_MISMATCH"
    if weekly_verified["hash_status"]!="MATCH": weekly_status,weekly_reason="RED","TARGET_HASH_MISMATCH"
    arch_status="GREEN" if architecture.get("status")=="GREEN" else "RED" if architecture.get("status")=="RED" else "AMBER"; auto_status="GREEN" if automation.get("status")=="GREEN" else "RED" if automation.get("status")=="RED" else "AMBER"
    systems={"architecture_health":{"status":arch_status,"generated_at_utc":architecture.get("generated_at_utc"),"blockers":architecture.get("blockers",[]),"input_error":architecture.get("input_error")},"automation_health":{"status":auto_status,"generated_at_utc":automation.get("generated_at_utc"),"blockers":automation.get("blockers",[]),"red_count":automation.get("red_count"),"amber_count":automation.get("amber_count")},"daily_capture":{"status":capture_status,"reason":capture_reason,"age_hours":capture_age,"timestamp_utc":capture_ts,"pointer":capture_pointer},"openai_daily_director":{"status":director_status,"reason":director_reason,"age_hours":director_age,"timestamp_utc":director_ts,"path":str(director_path.relative_to(root)) if director_path else None,"receipt_path":str(director_path.with_name("DAILY_DIRECTOR_RECEIPT.json").relative_to(root)) if director_path else None,"semantic_status":director.get("status")},"weekly_output":{"status":weekly_status,"reason":weekly_reason,"age_hours":weekly_age,"timestamp_utc":weekly_ts,"path":str(weekly_path.relative_to(root)) if weekly_path else None,"target_path":weekly_verified.get("target_path"),"target_hash_status":weekly_verified.get("hash_status"),"hash_mode":weekly_verified.get("hash_mode"),"pointer":{"path":weekly_verified.get("pointer_path"),"declared_sha256":weekly_verified.get("declared_sha256"),"actual_sha256":weekly_verified.get("actual_sha256"),"raw_file_sha256":weekly_verified.get("raw_file_sha256"),"hash_status":weekly_verified.get("hash_status")}},"remediation_maturation":{"status":remediation_status,"reason":remediation_reason,"age_hours":remediation_age,"timestamp_utc":remediation_ts,"path":str(remediation_path.relative_to(root)) if remediation_path else None},"experiment_lifecycle":{"status":experiment_status,"reason":experiment_reason,"age_hours":experiment_age,"timestamp_utc":experiment_ts,"path":"research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"},"experiment_receipt_sync":{"status":receipt_sync_status,"reason":receipt_sync_reason,"age_hours":receipt_sync_age,"timestamp_utc":receipt_sync_ts,"path":"research/experiment_lifecycle/LATEST_EXPERIMENT_RECEIPT_SYNC.json"}}
    priority={"RED":3,"AMBER":2,"GREEN":1}; overall=max((row["status"] for row in systems.values()),key=lambda value:priority.get(value,0)); required_actions=[]
    if auto_status=="RED": required_actions.append({"priority":"P0","system":"automation_health","reason":automation.get("blockers",[])})
    if weekly_status=="RED": required_actions.append({"priority":"P0","system":"weekly_output","reason":weekly_reason})
    if capture_status=="RED": required_actions.append({"priority":"P0","system":"daily_capture","reason":capture_reason})
    if director_status in {"AMBER","RED"}: required_actions.append({"priority":"P1","system":"openai_daily_director","reason":director_reason})
    state_counts=experiment.get("state_counts") if isinstance(experiment.get("state_counts"),dict) else {}
    dashboard={"contract":"OPERATIONS_DASHBOARD_v1_2","authority":"OPERATIONAL_OBSERVABILITY_ONLY","generated_at_utc":now.isoformat().replace("+00:00","Z"),"overall_status":overall,"systems":systems,"agent_activity":{"openai_api":count_receipts(root),"experiments":{"candidate_count":experiment.get("candidate_count",0),"state_counts":state_counts,"dispatch_request_count":experiment.get("dispatch_request_count",0)},"remediation":{"codex_ready":remediation.get("summary",{}).get("codex_ready",0),"needs_more_evidence":remediation.get("summary",{}).get("needs_more_evidence",0),"automatic_code_write":False,"automatic_merge":False},"pending_forecast_candidates":len(remediation.get("items",[])) if isinstance(remediation.get("items"),list) else 0},"incidents":incident_summary(root),"required_actions":required_actions,"source_status":{"architecture_health":"PASS" if architecture else "MISSING","automation_health":"PASS" if automation else "MISSING","latest_handoff":"PASS" if handoff else "MISSING"}}
    payload=json.dumps(dashboard,sort_keys=True,separators=(",",":"))+"\n"; dashboard["dashboard_sha256"]=hashlib.sha256(payload.encode()).hexdigest(); args.output.write_text(json.dumps(dashboard,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8"); print(json.dumps({"status":overall,"output":str(args.output),"required_actions":required_actions},sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
