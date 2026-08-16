#!/usr/bin/env python3
"""Write a prospective evidence lifecycle receipt without inferring unavailable stages."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

TIME_FIELDS = [
    "observation_time", "source_available_time", "retrieval_start_time",
    "retrieval_complete_time", "normalization_time", "provenance_validation_time",
    "owner_grade_time", "framework_ingest_time", "framework_acceptance_time",
    "policy_evaluable_time", "decision_evaluation_time", "action_divergence_time",
]
VALID_STATUS = {"KNOWN", "DERIVED_WITH_RECEIPT", "UNAVAILABLE", "CONTRACT_BLOCKED", "NOT_APPLICABLE"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-run-id", required=True)
    ap.add_argument("--evidence-lane", required=True)
    ap.add_argument("--repo-head-sha", required=True)
    ap.add_argument("--source-lineage", default="")
    ap.add_argument("--artifact-hash", default="")
    ap.add_argument("--validator-run-id", default="")
    ap.add_argument("--timestamp", action="append", default=[], help="FIELD=ISO8601")
    ap.add_argument("--status", action="append", default=[], help="FIELD=STATUS")
    a = ap.parse_args()

    values = {field: None for field in TIME_FIELDS}
    statuses = {field: "UNAVAILABLE" for field in TIME_FIELDS}

    for item in a.timestamp:
        field, value = item.split("=", 1)
        if field not in values:
            raise SystemExit(f"unknown timestamp field: {field}")
        values[field] = value

    for item in a.status:
        field, status = item.split("=", 1)
        if field not in statuses:
            raise SystemExit(f"unknown timestamp field: {field}")
        if status not in VALID_STATUS:
            raise SystemExit(f"invalid status for {field}: {status}")
        statuses[field] = status

    for field in TIME_FIELDS:
        if values[field] is not None and statuses[field] == "UNAVAILABLE":
            statuses[field] = "KNOWN"
        if statuses[field] in {"UNAVAILABLE", "CONTRACT_BLOCKED", "NOT_APPLICABLE"}:
            values[field] = None

    body = {
        "contract": "EVIDENCE_LIFECYCLE_RECEIPT_v0_1",
        "contract_version": "0.1",
        "generated_at_utc": utc_now(),
        "source_run_id": a.source_run_id,
        "evidence_lane": a.evidence_lane,
        "repo_head_sha": a.repo_head_sha,
        "source_lineage": a.source_lineage,
        "artifact_hash": a.artifact_hash,
        "validator_run_id": a.validator_run_id,
        "timestamp_status": statuses,
        **values,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "path": str(a.output), "source_run_id": a.source_run_id}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
