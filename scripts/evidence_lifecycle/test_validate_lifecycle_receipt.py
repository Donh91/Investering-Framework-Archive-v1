#!/usr/bin/env python3
"""Bounded acceptance tests for lifecycle receipt semantics."""

import json
import subprocess
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_lifecycle_receipt.py")
TIME_FIELDS = [
    "observation_time", "source_available_time", "retrieval_start_time",
    "retrieval_complete_time", "normalization_time", "provenance_validation_time",
    "owner_grade_time", "framework_ingest_time", "framework_acceptance_time",
    "policy_evaluable_time", "decision_evaluation_time", "action_divergence_time",
]


def base_receipt():
    receipt = {
        "contract": "EVIDENCE_LIFECYCLE_RECEIPT_v0_1",
        "source_run_id": "test-run",
        "evidence_lane": "TEST_ONLY",
        "contract_version": "0.1",
        "repo_head_sha": "test-sha",
        "source_lineage": "test fixture",
        "artifact_hash": "test-hash",
        "validator_run_id": "test-validator",
        "timestamp_status": {},
    }
    for field in TIME_FIELDS:
        receipt[field] = None
        receipt["timestamp_status"][field] = "UNAVAILABLE"
    return receipt


def run(receipt):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "receipt.json"
        path.write_text(json.dumps(receipt))
        return subprocess.run(["python", str(VALIDATOR), str(path)], capture_output=True, text=True)


def main():
    valid = base_receipt()
    valid.update({
        "retrieval_start_time": "2026-08-16T09:00:00Z",
        "retrieval_complete_time": "2026-08-16T09:01:00Z",
        "framework_ingest_time": "2026-08-16T09:02:00Z",
        "framework_acceptance_time": "2026-08-16T09:03:00Z",
        "policy_evaluable_time": None,
    })
    valid["timestamp_status"].update({
        "retrieval_start_time": "KNOWN",
        "retrieval_complete_time": "KNOWN",
        "framework_ingest_time": "KNOWN",
        "framework_acceptance_time": "KNOWN",
        "policy_evaluable_time": "CONTRACT_BLOCKED",
    })
    assert run(valid).returncode == 0, "valid receipt should pass"

    bad_order = json.loads(json.dumps(valid))
    bad_order["retrieval_complete_time"] = "2026-08-16T08:59:00Z"
    assert run(bad_order).returncode != 0, "reversed timestamps must fail"

    false_precision = json.loads(json.dumps(valid))
    false_precision["policy_evaluable_time"] = "2026-08-16T09:04:00Z"
    assert run(false_precision).returncode != 0, "blocked timestamp must remain null"

    derived_without_receipt = json.loads(json.dumps(valid))
    derived_without_receipt["framework_acceptance_time"] = "2026-08-16T09:03:00Z"
    derived_without_receipt["timestamp_status"]["framework_acceptance_time"] = "DERIVED_WITH_RECEIPT"
    assert run(derived_without_receipt).returncode != 0, "derived timestamps require receipt"

    print("lifecycle receipt acceptance tests: PASS")


if __name__ == "__main__":
    main()
