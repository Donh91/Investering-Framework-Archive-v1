#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

CONTRACT="RESEARCH_SOURCE_RECEIPT_VALIDATOR_v1"
FORBIDDEN_TRUE=("binding","canonical_acceptance","state_change","portfolio_action","automatic_promotion")
SHA256_RE=re.compile(r"^[0-9a-f]{64}$")

class ValidationError(ValueError): pass

def validate(doc:Any)->dict[str,Any]:
    if not isinstance(doc,dict): raise ValidationError("receipt_not_object")
    for k in ("contract","source","payload_sha256","payload_bytes","raw_persisted","authority"):
        if k not in doc: raise ValidationError(f"missing_{k}")
    if not isinstance(doc["contract"],str) or not doc["contract"]: raise ValidationError("bad_contract")
    if not isinstance(doc["source"],str) or not doc["source"]: raise ValidationError("bad_source")
    if not isinstance(doc["payload_sha256"],str) or not SHA256_RE.fullmatch(doc["payload_sha256"]):
        raise ValidationError("bad_payload_sha256")
    if not isinstance(doc["payload_bytes"],int) or doc["payload_bytes"] < 1: raise ValidationError("bad_payload_bytes")
    if doc["raw_persisted"] is not False: raise ValidationError("raw_persistence_forbidden")
    authority=doc["authority"]
    if not isinstance(authority,dict): raise ValidationError("authority_not_object")
    for k in FORBIDDEN_TRUE:
        if authority.get(k) is not False: raise ValidationError(f"authority_not_false_{k}")
    return {
        "contract":CONTRACT,
        "status":"PASS",
        "source":doc["source"],
        "input_contract":doc["contract"],
        "payload_sha256":doc["payload_sha256"],
        "raw_persisted":False,
        "authority_ceiling":"RESEARCH_ONLY",
    }

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("receipt",type=Path)
    a=ap.parse_args()
    try: doc=json.loads(a.receipt.read_text())
    except json.JSONDecodeError as e: raise SystemExit(f"FAIL invalid_json: {e}") from e
    try: result=validate(doc)
    except ValidationError as e: raise SystemExit(f"FAIL {e}") from e
    print(json.dumps(result,sort_keys=True,separators=(",",":")))
    return 0

if __name__=="__main__": raise SystemExit(main())
