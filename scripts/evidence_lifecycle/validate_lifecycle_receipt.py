#!/usr/bin/env python3
"""Validate EVIDENCE_LIFECYCLE_RECEIPT_v0_1 without inventing missing timestamps."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

CONTRACT = "EVIDENCE_LIFECYCLE_RECEIPT_v0_1"
STATUSES = {"KNOWN", "DERIVED_WITH_RECEIPT", "UNAVAILABLE", "CONTRACT_BLOCKED", "NOT_APPLICABLE"}
TIME_FIELDS = [
    "observation_time", "source_available_time", "retrieval_start_time",
    "retrieval_complete_time", "normalization_time", "provenance_validation_time",
    "owner_grade_time", "framework_ingest_time", "framework_acceptance_time",
    "policy_evaluable_time", "decision_evaluation_time", "action_divergence_time",
]
ORDER_PAIRS = [
    ("retrieval_start_time", "retrieval_complete_time"),
    ("retrieval_complete_time", "normalization_time"),
    ("normalization_time", "provenance_validation_time"),
    ("framework_ingest_time", "framework_acceptance_time"),
    ("framework_acceptance_time", "policy_evaluable_time"),
    ("policy_evaluable_time", "decision_evaluation_time"),
]


def parse_time(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("timestamp must be string or null")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt")
    args = ap.parse_args()
    data = json.loads(Path(args.receipt).read_text())
    errors = []

    if data.get("contract") != CONTRACT:
        errors.append(f"contract must equal {CONTRACT}")
    for required in ("source_run_id", "evidence_lane", "contract_version", "repo_head_sha"):
        if not data.get(required):
            errors.append(f"missing required field: {required}")

    status_map = data.get("timestamp_status", {})
    if not isinstance(status_map, dict):
        errors.append("timestamp_status must be an object")
        status_map = {}

    parsed = {}
    for field in TIME_FIELDS:
        status = status_map.get(field)
        value = data.get(field)
        if status not in STATUSES:
            errors.append(f"{field}: invalid or missing timestamp status")
            continue
        if status in {"UNAVAILABLE", "CONTRACT_BLOCKED", "NOT_APPLICABLE"} and value is not None:
            errors.append(f"{field}: {status} requires null timestamp")
        if status in {"KNOWN", "DERIVED_WITH_RECEIPT"} and value is None:
            errors.append(f"{field}: {status} requires timestamp")
        try:
            parsed[field] = parse_time(value)
        except ValueError as exc:
            errors.append(f"{field}: {exc}")

    if any(v == "DERIVED_WITH_RECEIPT" for v in status_map.values()) and not data.get("derivation_receipts"):
        errors.append("DERIVED_WITH_RECEIPT requires derivation_receipts")

    for earlier, later in ORDER_PAIRS:
        a, b = parsed.get(earlier), parsed.get(later)
        if a is not None and b is not None and a > b:
            errors.append(f"invalid ordering: {earlier} > {later}")

    result = {
        "contract": CONTRACT,
        "valid": not errors,
        "errors": errors,
        "missing_or_blocked": [
            f for f in TIME_FIELDS if status_map.get(f) in {"UNAVAILABLE", "CONTRACT_BLOCKED"}
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
