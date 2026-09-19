#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

HEX64=set("0123456789abcdef")

def load(path: Path) -> dict[str, Any]:
    value=json.loads(path.read_text())
    if not isinstance(value,dict):
        raise SystemExit("ROW_NOT_OBJECT")
    return value

def parse_ts(value: Any) -> datetime:
    if not isinstance(value,str):
        raise ValueError("timestamp_missing")
    return datetime.fromisoformat(value.replace("Z","+00:00"))

def sha_ok(value: Any) -> bool:
    return isinstance(value,str) and len(value)==64 and all(c in HEX64 for c in value.lower())

def require(row: dict[str,Any], fields: list[str], errors: list[str]) -> None:
    for field in fields:
        if field not in row or row[field] is None or row[field]=="":
            errors.append("MISSING:"+field)

def validate(row: dict[str,Any], contract: dict[str,Any]) -> dict[str,Any]:
    errors: list[str]=[]
    warnings: list[str]=[]
    if row.get("test_id") != contract.get("test_id"):
        errors.append("TEST_ID_MISMATCH")
    experiment=row.get("experiment_id")
    experiments=contract.get("experiment_contracts") or {}
    experiment_contract=next((v for v in experiments.values() if v.get("experiment_id")==experiment),None)
    if not experiment_contract:
        errors.append("EXPERIMENT_NOT_REGISTERED")
        experiment_contract={}

    row_type=row.get("row_type")
    if row_type not in {"FROZEN_INPUT_ROW","OUTCOME_ROW","CORRECTION_ROW"}:
        errors.append("ROW_TYPE_INVALID")

    common=["row_id","test_id","experiment_id","prereg_id"]
    require(row,common,errors)

    if row_type=="FROZEN_INPUT_ROW":
        require(row,[
            "frozen_at_utc","window_start_utc","window_end_utc","spec_sha256","source_code_sha",
            "eligibility_manifest_sha256","metric_definition_sha256","benchmark_definition_sha256",
            "kill_condition_sha256"
        ],errors)
        require(row,list(experiment_contract.get("required_frozen_fields") or []),errors)
        for field in ["spec_sha256","eligibility_manifest_sha256","metric_definition_sha256","benchmark_definition_sha256","kill_condition_sha256"]:
            if field in row and not sha_ok(row.get(field)):
                errors.append("HASH_INVALID:"+field)
        try:
            frozen=parse_ts(row.get("frozen_at_utc"))
            start=parse_ts(row.get("window_start_utc"))
            end=parse_ts(row.get("window_end_utc"))
            if not frozen < start < end:
                errors.append("CAUSAL_WINDOW_INVALID")
        except Exception:
            errors.append("TIMESTAMP_INVALID")
        forbidden=set(contract.get("mutable_outcome_fields") or [])
        leaked=sorted(field for field in forbidden if field in row and row[field] not in (None,"",{},[]))
        if leaked:
            errors.append("OUTCOME_PRESENT_AT_FREEZE:"+",".join(leaked))

    if row_type=="OUTCOME_ROW":
        require(row,[
            "input_row_id","observed_at_utc","data_health","requested_coverage","returned_coverage",
            "provider_identity","source_content_sha256","source_commit_receipt","eligibility","machine_verdict"
        ],errors)
        require(row,list(experiment_contract.get("required_outcome_fields") or []),errors)
        if row.get("data_health") not in {"PASS","DEGRADED","UNKNOWN"}:
            errors.append("DATA_HEALTH_INVALID")
        if row.get("machine_verdict") not in set(contract.get("machine_verdicts") or []):
            errors.append("MACHINE_VERDICT_INVALID")
        if row.get("eligibility") not in {"ELIGIBLE","EXCLUDED","UNKNOWN"}:
            errors.append("ELIGIBILITY_INVALID")
        if "source_content_sha256" in row and not sha_ok(row.get("source_content_sha256")):
            errors.append("HASH_INVALID:source_content_sha256")
        requested=row.get("requested_coverage")
        returned=row.get("returned_coverage")
        if isinstance(requested,(int,float)) and isinstance(returned,(int,float)):
            if returned < 0 or requested < 0 or returned > requested:
                errors.append("COVERAGE_INVALID")
            if returned < requested and row.get("data_health")=="PASS":
                errors.append("PARTIAL_COVERAGE_CANNOT_PASS")
        else:
            warnings.append("COVERAGE_NOT_NUMERIC")
        if row.get("data_health")!="PASS" and row.get("machine_verdict")=="PROSPECTIVE_PASS":
            errors.append("DEGRADED_DATA_CANNOT_PASS")
        metrics=row.get("metrics")
        if isinstance(metrics,dict):
            for key,value in metrics.items():
                if value==0 and str(row.get("metric_missingness",{}).get(key,"")).upper() in {"UNKNOWN","MISSING","FAILED"}:
                    errors.append("MISSING_TO_ZERO:"+key)

    if row_type=="CORRECTION_ROW":
        require(row,["original_row_id","correction_reason","corrected_fields","observed_at_utc","source_content_sha256"],errors)
        if not sha_ok(row.get("source_content_sha256")):
            errors.append("HASH_INVALID:source_content_sha256")

    result={
        "contract":"ALPHA_LAB_PROSPECTIVE_EDGE_ROW_VALIDATION_v1",
        "test_id":row.get("test_id"),
        "experiment_id":experiment,
        "row_id":row.get("row_id"),
        "row_type":row_type,
        "valid":not errors,
        "errors":errors,
        "warnings":warnings,
        "promotion_authority":False,
        "portfolio_authority":False,
    }
    return result

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--row",type=Path,required=True)
    p.add_argument("--contract",type=Path,default=Path("06_RESEARCH_LAB/alpha_lab/ALPHA_LAB_PROSPECTIVE_EDGE_EXPERIMENTS_v1.json"))
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=validate(load(a.row),load(a.contract))
    text=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(text)
    print(text,end="")
    return 0 if result["valid"] else 2

if __name__=="__main__":
    raise SystemExit(main())
