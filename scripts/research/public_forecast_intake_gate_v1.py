#!/usr/bin/env python3
"""Offline, fail-closed structure check for external public forecast research.

This is NOT a forecast issuer, proof authenticator, outcome scorer or admission
authority. A syntactically valid claimant-supplied receipt is not independent
first-known evidence. No network, wallet, GitHub or production-side effects.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import urlparse

CONTRACT = "PUBLIC_FORECAST_RESEARCH_INTAKE_V1"
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
HEX_RE = re.compile(r"^[a-fA-F0-9]{64}$")
CLAIM_TYPES = {"direction", "target", "range", "exact_bottom", "conditional"}
AUTHORITIES = {"RESEARCH_ONLY"}
REQUIRED = (
    "case_id", "authority", "source_uri", "claim_type", "asset",
    "source_issued_at_utc", "first_machine_observed_at_utc",
    "frozen_at_utc", "outcome_window_start_utc",
    "source_content_sha256", "original_source_receipt_ref",
)

def parse_utc(value: object) -> datetime | None:
    if not isinstance(value, str) or not UTC_RE.fullmatch(value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo == timezone.utc else None
    except ValueError:
        return None

def audit_case(row: object) -> dict:
    if not isinstance(row, dict):
        return {"status": "REJECTED_SCHEMA", "problems": ["NOT_AN_OBJECT"],
                "scientific_admitted": False, "scorable": False}
    problems = []
    for key in REQUIRED:
        if key not in row:
            problems.append("MISSING_" + key.upper())
    if not isinstance(row.get("authority"), str) or row.get("authority") not in AUTHORITIES:
        problems.append("AUTHORITY_NOT_RESEARCH_ONLY")
    if not isinstance(row.get("claim_type"), str) or row.get("claim_type") not in CLAIM_TYPES:
        problems.append("INVALID_CLAIM_TYPE")
    if not isinstance(row.get("case_id"), str) or not row.get("case_id", "").strip():
        problems.append("INVALID_CASE_ID")
    if not isinstance(row.get("asset"), str) or row.get("asset") not in {"BTC", "ETH", "SOL"}:
        problems.append("ASSET_NOT_WHITELISTED")
    uri = row.get("source_uri")
    if not isinstance(uri, str) or urlparse(uri).scheme != "https" or not urlparse(uri).netloc:
        problems.append("SOURCE_URI_NOT_HTTPS")
    digest = row.get("source_content_sha256")
    if digest is not None and (not isinstance(digest, str) or not HEX_RE.fullmatch(digest)):
        problems.append("MALFORMED_SOURCE_HASH")
    clocks = {k: parse_utc(row.get(k)) for k in (
        "source_issued_at_utc", "first_machine_observed_at_utc",
        "frozen_at_utc", "outcome_window_start_utc"
    )}
    for key, value in clocks.items():
        if row.get(key) is not None and value is None:
            problems.append("MALFORMED_" + key.upper())
    if all(v is not None for v in clocks.values()):
        issued, seen, frozen, start = clocks.values()
        if not (issued <= seen <= frozen < start):
            problems.append("NONCAUSAL_CLOCK_ORDER")
    if problems:
        return {"case_id": row.get("case_id"), "status": "REJECTED_SCHEMA",
                "problems": sorted(set(problems)), "scientific_admitted": False,
                "scorable": False}
    missing_proof = [k for k in (
        "source_issued_at_utc", "first_machine_observed_at_utc",
        "frozen_at_utc", "outcome_window_start_utc",
        "source_content_sha256", "original_source_receipt_ref"
    ) if not row.get(k)]
    status = ("CONTEXT_ONLY_MISSING_PROOF" if missing_proof
              else "STRUCTURAL_ONLY_INDEPENDENT_PROOF_UNVERIFIED")
    return {"case_id": row["case_id"], "status": status,
            "problems": ["MISSING_PROOF:" + ",".join(missing_proof)] if missing_proof else
                        ["NO_INDEPENDENT_RECEIPT_AUTHENTICATION"],
            "scientific_admitted": False, "scorable": False}

def audit_manifest(manifest: object) -> dict:
    if not isinstance(manifest, dict) or manifest.get("contract") != CONTRACT:
        raise ValueError("MANIFEST_CONTRACT_MISMATCH")
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        raise ValueError("CASES_NOT_ARRAY")
    ids = [c.get("case_id") for c in cases if isinstance(c, dict)]
    if len([x for x in ids if isinstance(x, str)]) != len(set(x for x in ids if isinstance(x, str))):
        raise ValueError("DUPLICATE_CASE_ID")
    results = [audit_case(c) for c in cases]
    return {"contract": CONTRACT, "rows": results, "row_count": len(results),
            "scientific_admitted_count": 0, "forecast_scores_created": 0,
            "authority": "RESEARCH_ONLY"}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Read-only JSON manifest")
    args = parser.parse_args()
    result = audit_manifest(json.loads(args.manifest.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
