#!/usr/bin/env python3
"""Validate planning/receipt contracts for the repository-local Research Parallel Lanes skill.

This is a static deterministic guard. It does NOT dispatch GitHub jobs, authenticate
agents, authorize API spend or certify that a cited run actually happened.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

HEX40=re.compile(r"[0-9a-f]{40}\Z")
HEX64=re.compile(r"[0-9a-f]{64}\Z")
LANE=re.compile(r"L[0-9]{2}\Z")
VALID_STATUS={"PLANNED","RUNNING","COMPLETE_VERIFIED","FAILED_EVIDENCED",
              "BLOCKED","NOT_EXECUTED"}
KINDS={"GITHUB_JOB","READ_ONLY_TOOL","EXISTING_AI_AGENT"}
ELIGIBILITY={"HISTORICAL_TRUTH_ONLY","ORIGINAL_PIT_VERIFIED","UNKNOWN"}
LENGTH_FIELDS=("name","question","hypothesis","baseline","falsifier",
               "source_ref","output_path")

def validate(data: dict) -> list[str]:
    errors=[]
    if not isinstance(data,dict):
        return ["top-level value must be an object"]
    for k,val in (("contract","RESEARCH_PARALLEL_LANES_V1"),
                  ("status","PLANNING_ONLY_EXAMPLE")):
        if data.get(k)!=val: errors.append(f"{k} requires {val}")
    if not isinstance(data.get("mission_id"),str) or not data.get("mission_id"):
        errors.append("mission_id required")
    owner=data.get("original_owner_issue","")
    if not (isinstance(owner,str) and re.fullmatch(
        r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[0-9]+",owner)):
        errors.append("original_owner_issue must be native exact GitHub issue URL")
    if not HEX40.fullmatch(str(data.get("source_snapshot_sha",""))):
        errors.append("source_snapshot_sha must be a 40-hex commit")
    if data.get("source_eligibility") not in ELIGIBILITY:
        errors.append("source_eligibility invalid")
    if data.get("data_classification") not in {"PUBLIC_ONLY","RESTRICTED_REFERENCES_ONLY"}:
        errors.append("data_classification invalid")
    manifest=data.get("source_manifest_path")
    if not isinstance(manifest,str) or not manifest or ".." in Path(manifest).parts or manifest.startswith("/"):
        errors.append("source_manifest_path must be safe repository-relative path")
    for k in ("no_new_scheduler","no_new_agent_identity","no_trading_authority"):
        if data.get(k) is not True:
            errors.append(f"{k} must be true")
    cap=data.get("parallel_job_cap")
    if type(cap)!=int or not (1<=cap<=10):
        errors.append("parallel_job_cap must be integer in 1..10")
    budget=data.get("approved_budget_usd")
    if type(budget) not in (int,float) or not (0<=budget<=10000):
        errors.append("approved_budget_usd invalid")
        budget=0
    lanes=data.get("lanes")
    if not isinstance(lanes,list) or not (2<=len(lanes)<=10):
        return errors+["lanes must contain 2..10 independently falsifiable tracks"]
    names=[]
    total=0.0
    paths=[]
    for i,lane in enumerate(lanes):
        prefix=f"lanes[{i}]"
        if not isinstance(lane,dict):
            errors.append(prefix+": object required")
            continue
        lid=lane.get("id")
        if not isinstance(lid,str) or not LANE.fullmatch(lid):
            errors.append(prefix+": lane id must match L##")
        else:names.append(lid)
        for k in LENGTH_FIELDS:
            value=lane.get(k)
            if not isinstance(value,str) or len(value.strip())<8:
                errors.append(prefix+f": {k} must be informative")
        ref=lane.get("output_path")
        if isinstance(ref,str):
            if ref.startswith("/") or ".." in Path(ref).parts or ref.startswith("Donh91/secrets/"):
                errors.append(prefix+": output_path must remain repository-relative and nonrestricted")
            paths.append(ref)
        mode=lane.get("executor_kind")
        if mode not in KINDS:
            errors.append(prefix+": unknown executor_kind")
        state=lane.get("status")
        if state not in VALID_STATUS:
            errors.append(prefix+": unknown status")
        deps=lane.get("depends_on")
        if not isinstance(deps,list) or any(not isinstance(x,str) or not LANE.fullmatch(x) for x in deps):
            errors.append(prefix+": depends_on must be a list of L##")
        mins=lane.get("max_minutes")
        if type(mins)!=int or mins<=0 or mins>90:
            errors.append(prefix+": max_minutes must be 1..90")
        usd=lane.get("budget_usd")
        if type(usd) not in (int,float) or usd<0:
            errors.append(prefix+": invalid budget_usd")
        else:
            total+=usd
        proof=lane.get("run_evidence")
        if not isinstance(proof,dict):
            errors.append(prefix+": run_evidence object required")
            proof={}
        if state=="COMPLETE_VERIFIED":
            # Schema evidence completeness is NOT proof that the external run exists.
            if mode=="GITHUB_JOB":
                for k in ("workflow_run_id","job_id","artifact_id"):
                    if type(proof.get(k))!=int or proof[k]<=0:
                        errors.append(prefix+f": verified job requires positive {k}")
                if not HEX40.fullmatch(str(proof.get("exact_head_sha",""))):
                    errors.append(prefix+": verified job needs exact_head_sha")
                if not HEX64.fullmatch(str(proof.get("artifact_sha256",""))):
                    errors.append(prefix+": verified job needs artifact_sha256")
                if proof.get("conclusion")!="success":
                    errors.append(prefix+": completed GitHub job conclusion must be success")
            elif mode=="EXISTING_AI_AGENT":
                if not proof.get("native_agent_run_id") or not proof.get("native_result_receipt"):
                    errors.append(prefix+": verified AI agent needs native execution and result receipt")
            elif mode=="READ_ONLY_TOOL":
                if not proof.get("tool_call_id") or not proof.get("source_readback"):
                    errors.append(prefix+": verified tool lane needs observed call+readback")
        if state=="FAILED_EVIDENCED" and not proof.get("failure_receipt"):
            errors.append(prefix+": failed lane requires a specific failure receipt")
        if state in {"PLANNED","NOT_EXECUTED"} and proof.get("conclusion")=="success":
            errors.append(prefix+": planning-only lane cannot assert success")
    if len(names)!=len(set(names)):
        errors.append("duplicate lane id")
    if len(paths)!=len(set(paths)):
        errors.append("duplicate output_path risks parallel write conflict")
    by_id={lane.get("id"):lane for lane in lanes if isinstance(lane,dict)}
    for lid,lane in by_id.items():
        deps=lane.get("depends_on",[])
        if not isinstance(deps,list):continue
        for dep in deps:
            if dep==lid or dep not in by_id:
                errors.append(f"{lid}: unknown/self dependency {dep}")
            if (lane.get("status")=="COMPLETE_VERIFIED" and
                    dep in by_id and by_id[dep].get("status")!="COMPLETE_VERIFIED"):
                errors.append(f"{lid}: dependency {dep} not verified")
        seen=set()
        def walk(x:str)->bool:
            if x in seen:return True
            seen.add(x)
            for y in by_id.get(x,{}).get("depends_on",[]):
                if y==lid:return True
                if y in by_id and walk(y):return True
            seen.discard(x)
            return False
        if lid and walk(lid):errors.append(f"{lid}: dependency cycle detected")
    if total>budget:
        errors.append("sum of lane model budgets exceeds approved_budget_usd")
    return errors

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("manifest",type=Path)
    args=p.parse_args()
    data=json.loads(args.manifest.read_text(encoding="utf8"))
    errors=validate(data)
    print(json.dumps({"contract":"RESEARCH_PARALLEL_LANES_STATIC_QA_V1",
                      "manifest":str(args.manifest),"lanes":len(data.get("lanes",[])),
                      "status":"PASS_SCHEMA_ONLY" if not errors else "FAIL",
                      "does_not_dispatch_agents_or_jobs":True,
                      "errors":errors},indent=2))
    return 1 if errors else 0
if __name__=="__main__":sys.exit(main())
