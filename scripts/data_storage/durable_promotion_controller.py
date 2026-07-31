#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

REQUIRED=("artifact_id","artifact_digest","dataset_id","partition_id","source_run_id","schema_version","row_count","member_manifest_sha256","durable_pointer","durable_sha256","independent_readback")
AUTHORITY={"framework_state_change":False,"portfolio_action":False,"enumeration_authorized":False,"outcome_access":False}

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def validate(entry:dict)->list[str]:
    errors=[f"missing:{k}" for k in REQUIRED if k not in entry]
    if entry.get("independent_readback")!="PASS": errors.append("readback_not_pass")
    if not str(entry.get("artifact_digest","")).startswith("sha256:"): errors.append("artifact_digest_invalid")
    if len(str(entry.get("durable_sha256","")))!=64: errors.append("durable_sha256_invalid")
    if entry.get("deletion_authorized") is True and errors: errors.append("unsafe_deletion_authorization")
    return errors

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("ledger",type=Path); ap.add_argument("--output",type=Path); a=ap.parse_args()
    doc=json.loads(a.ledger.read_text()); results=[]
    for entry in doc.get("entries",[]):
        errors=validate(entry); results.append({"dataset_id":entry.get("dataset_id"),"partition_id":entry.get("partition_id"),"status":"PASS" if not errors else "BLOCKED","errors":errors,"deletion_authorized":not errors})
    out={"contract":"DURABLE_PROMOTION_VALIDATION_v1","status":"PASS" if all(x["status"]=="PASS" for x in results) else "BLOCKED","results":results,"authority":AUTHORITY}
    if a.output: a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True)); return 0 if out["status"]=="PASS" else 2
if __name__=="__main__": raise SystemExit(main())
