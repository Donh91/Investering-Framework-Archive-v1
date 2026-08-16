#!/usr/bin/env python3
"""Stamp an existing lifecycle receipt at a real framework acceptance event.

This utility is intentionally narrow. It may record framework_ingest_time and
framework_acceptance_time only when an authoritative caller has actually
accepted the referenced evidence. It never infers policy_evaluable_time or
later decision stages.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--accepted-artifact", type=Path, required=True)
    ap.add_argument("--acceptance-contract", required=True)
    ap.add_argument("--acceptance-run-id", required=True)
    a = ap.parse_args()

    body = json.loads(a.receipt.read_text())
    if body.get("contract") != "EVIDENCE_LIFECYCLE_RECEIPT_v0_1":
        raise SystemExit("wrong lifecycle receipt contract")
    if not a.accepted_artifact.exists():
        raise SystemExit("accepted artifact does not exist")

    statuses = body.setdefault("timestamp_status", {})
    if body.get("framework_acceptance_time") is not None:
        raise SystemExit("framework_acceptance_time already stamped")

    now = utc_now()
    # The acceptance caller has the artifact in hand at this point. If no
    # earlier ingest event was recorded, acceptance itself is the first
    # receipt-backed framework-ingest event, not a reconstructed earlier time.
    if body.get("framework_ingest_time") is None:
        body["framework_ingest_time"] = now
        statuses["framework_ingest_time"] = "KNOWN"
    body["framework_acceptance_time"] = now
    statuses["framework_acceptance_time"] = "KNOWN"

    # Do not infer later lifecycle stages from acceptance.
    if body.get("policy_evaluable_time") is None and statuses.get("policy_evaluable_time") not in {"CONTRACT_BLOCKED", "NOT_APPLICABLE"}:
        statuses["policy_evaluable_time"] = "UNAVAILABLE"
    if body.get("decision_evaluation_time") is None:
        statuses["decision_evaluation_time"] = "UNAVAILABLE"
    if body.get("action_divergence_time") is None:
        statuses["action_divergence_time"] = "UNAVAILABLE"

    body["acceptance_attestation"] = {
        "acceptance_contract": a.acceptance_contract,
        "acceptance_run_id": a.acceptance_run_id,
        "accepted_artifact": str(a.accepted_artifact),
        "stamped_at_utc": now,
        "no_policy_evaluability_inferred": True,
    }
    a.receipt.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "receipt": str(a.receipt), "framework_acceptance_time": now}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
