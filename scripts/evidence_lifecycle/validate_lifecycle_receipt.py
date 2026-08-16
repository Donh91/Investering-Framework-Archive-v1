#!/usr/bin/env python3
"""Validate EVIDENCE_LIFECYCLE_RECEIPT_v0_1 without inventing missing timestamps."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

CONTRACT = "EVIDENCE_LIFECYCLE_RECEIPT_v0_1"
STATUSES = {"KNOWN", "DERIVED_WITH_RECEIPT", "UNAVAILABLE", "CONTRACT_BLOCKED", "NOT_APPLICABLE"}
OBSERVED = {"KNOWN", "DERIVED_WITH_RECEIPT"}
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
    ("decision_evaluation_time", "action_divergence_time"),
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
        if status in OBSERVED and value is None:
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

    def observed(field):
        return status_map.get(field) in OBSERVED and parsed.get(field) is not None

    # Acceptance is an explicit framework event, not an inferred consequence of
    # retrieval, storage or report generation.
    if observed("framework_acceptance_time") and not isinstance(data.get("acceptance_attestation"), dict):
        errors.append("framework_acceptance_time requires acceptance_attestation")

    # Policy evaluability may exist only after an observed framework acceptance
    # and must identify the already-existing frozen contract and evaluator receipt.
    if observed("policy_evaluable_time"):
        if not observed("framework_acceptance_time"):
            errors.append("policy_evaluable_time requires observed framework_acceptance_time")
        if not data.get("policy_contract_id"):
            errors.append("policy_evaluable_time requires policy_contract_id")
        if not data.get("policy_evaluator_receipt"):
            errors.append("policy_evaluable_time requires policy_evaluator_receipt")

    # A decision timestamp is not the same as context generation or research
    # analysis. It requires a prior policy-evaluable event plus an explicit
    # decision-evaluator attestation.
    if observed("decision_evaluation_time"):
        if not observed("policy_evaluable_time"):
            errors.append("decision_evaluation_time requires observed policy_evaluable_time")
        if not data.get("decision_evaluator_id"):
            errors.append("decision_evaluation_time requires decision_evaluator_id")
        if not data.get("decision_evaluator_receipt"):
            errors.append("decision_evaluation_time requires decision_evaluator_receipt")

    if observed("action_divergence_time"):
        if not observed("decision_evaluation_time"):
            errors.append("action_divergence_time requires observed decision_evaluation_time")
        if not data.get("decision_row_id"):
            errors.append("action_divergence_time requires decision_row_id")

    # Contract blocking is not latency. A blocked stage cannot have a later
    # observed decision/action timestamp in the same lifecycle receipt.
    if status_map.get("policy_evaluable_time") == "CONTRACT_BLOCKED":
        if observed("decision_evaluation_time") or observed("action_divergence_time"):
            errors.append("CONTRACT_BLOCKED policy_evaluable_time forbids later observed stages")
    if status_map.get("decision_evaluation_time") == "CONTRACT_BLOCKED" and observed("action_divergence_time"):
        errors.append("CONTRACT_BLOCKED decision_evaluation_time forbids action_divergence_time")

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
