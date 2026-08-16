#!/usr/bin/env python3
"""Bounded acceptance tests for lifecycle receipt semantics."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = Path(__file__).with_name("validate_lifecycle_receipt.py")
STAMPER = Path(__file__).with_name("stamp_acceptance_receipt.py")
BRIDGE = ROOT / "scripts/data_ping/accepted_data_ping_bridge.py"
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


def test_validator_guards():
    valid = base_receipt()
    valid.update({
        "retrieval_start_time": "2026-08-16T09:00:00Z",
        "retrieval_complete_time": "2026-08-16T09:01:00Z",
        "framework_acceptance_time": "2026-08-16T09:03:00Z",
        "acceptance_attestation": {
            "acceptance_contract": "TEST_ACCEPTANCE_v1",
            "acceptance_run_id": "test-acceptance",
            "accepted_artifact": "fixture.json",
        },
    })
    valid["timestamp_status"].update({
        "retrieval_start_time": "KNOWN",
        "retrieval_complete_time": "KNOWN",
        "framework_ingest_time": "UNAVAILABLE",
        "framework_acceptance_time": "KNOWN",
        "policy_evaluable_time": "CONTRACT_BLOCKED",
    })
    assert run(valid).returncode == 0, "acceptance may be known while ingest remains unavailable"

    bad_order = json.loads(json.dumps(valid))
    bad_order["retrieval_complete_time"] = "2026-08-16T08:59:00Z"
    assert run(bad_order).returncode != 0, "reversed timestamps must fail"

    false_precision = json.loads(json.dumps(valid))
    false_precision["policy_evaluable_time"] = "2026-08-16T09:04:00Z"
    assert run(false_precision).returncode != 0, "blocked timestamp must remain null"

    missing_acceptance_attestation = json.loads(json.dumps(valid))
    missing_acceptance_attestation.pop("acceptance_attestation")
    assert run(missing_acceptance_attestation).returncode != 0, "acceptance requires explicit attestation"

    policy_without_evaluator = json.loads(json.dumps(valid))
    policy_without_evaluator["policy_evaluable_time"] = "2026-08-16T09:04:00Z"
    policy_without_evaluator["timestamp_status"]["policy_evaluable_time"] = "KNOWN"
    assert run(policy_without_evaluator).returncode != 0, "policy evaluability requires frozen contract and evaluator receipt"

    policy_valid = json.loads(json.dumps(valid))
    policy_valid["policy_evaluable_time"] = "2026-08-16T09:04:00Z"
    policy_valid["timestamp_status"]["policy_evaluable_time"] = "KNOWN"
    policy_valid["policy_contract_id"] = "TEST_POLICY_v1"
    policy_valid["policy_evaluator_receipt"] = "test-policy-evaluator.json"
    assert run(policy_valid).returncode == 0, "fully attested policy evaluability should pass"

    decision_without_policy = json.loads(json.dumps(valid))
    decision_without_policy["decision_evaluation_time"] = "2026-08-16T09:05:00Z"
    decision_without_policy["timestamp_status"]["decision_evaluation_time"] = "KNOWN"
    decision_without_policy["decision_evaluator_id"] = "TEST_DECISION_EVALUATOR"
    decision_without_policy["decision_evaluator_receipt"] = "test-decision.json"
    assert run(decision_without_policy).returncode != 0, "decision evaluation requires prior policy evaluability"

    decision_valid = json.loads(json.dumps(policy_valid))
    decision_valid["decision_evaluation_time"] = "2026-08-16T09:05:00Z"
    decision_valid["timestamp_status"]["decision_evaluation_time"] = "KNOWN"
    decision_valid["decision_evaluator_id"] = "TEST_DECISION_EVALUATOR"
    decision_valid["decision_evaluator_receipt"] = "test-decision.json"
    assert run(decision_valid).returncode == 0, "fully attested decision evaluation should pass"

    divergence_without_row = json.loads(json.dumps(decision_valid))
    divergence_without_row["action_divergence_time"] = "2026-08-16T09:06:00Z"
    divergence_without_row["timestamp_status"]["action_divergence_time"] = "KNOWN"
    assert run(divergence_without_row).returncode != 0, "action divergence requires decision row id"

    divergence_valid = json.loads(json.dumps(decision_valid))
    divergence_valid["action_divergence_time"] = "2026-08-16T09:06:00Z"
    divergence_valid["timestamp_status"]["action_divergence_time"] = "KNOWN"
    divergence_valid["decision_row_id"] = "TEST_ROW_001"
    assert run(divergence_valid).returncode == 0, "fully attested action divergence should pass"

    derived_without_receipt = json.loads(json.dumps(valid))
    derived_without_receipt["framework_acceptance_time"] = "2026-08-16T09:03:00Z"
    derived_without_receipt["timestamp_status"]["framework_acceptance_time"] = "DERIVED_WITH_RECEIPT"
    assert run(derived_without_receipt).returncode != 0, "derived timestamps require receipt"


def test_acceptance_stamper_does_not_infer_ingest():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        receipt_path = root / "receipt.json"
        artifact_path = root / "accepted.json"
        receipt_path.write_text(json.dumps(base_receipt()))
        artifact_path.write_text("{}\n")
        subprocess.run([
            "python", str(STAMPER),
            "--receipt", str(receipt_path),
            "--accepted-artifact", str(artifact_path),
            "--acceptance-contract", "TEST_ACCEPTANCE_v1",
            "--acceptance-run-id", "test-run",
        ], check=True, capture_output=True, text=True)
        stamped = json.loads(receipt_path.read_text())
        assert stamped["framework_ingest_time"] is None
        assert stamped["timestamp_status"]["framework_ingest_time"] == "UNAVAILABLE"
        assert stamped["framework_acceptance_time"] is not None
        assert stamped["timestamp_status"]["framework_acceptance_time"] == "KNOWN"
        assert stamped["acceptance_attestation"]["framework_ingest_not_inferred"] is True
        assert subprocess.run(["python", str(VALIDATOR), str(receipt_path)], capture_output=True).returncode == 0


def run_bridge(packet: dict, root: Path, snapshot_id: str) -> dict:
    inbox = root / f"inbox-{snapshot_id}"; accepted = root / f"accepted-{snapshot_id}"; rejected = root / f"rejected-{snapshot_id}"
    inbox.mkdir()
    (inbox / "packet.json").write_text(json.dumps(packet))
    subprocess.run([
        "python", str(BRIDGE),
        "--inbox", str(inbox),
        "--accepted-root", str(accepted),
        "--rejected-root", str(rejected),
        "--run-id", "test-bridge",
    ], check=True, capture_output=True, text=True)
    stored_paths = list(accepted.rglob(f"{snapshot_id}.json"))
    assert len(stored_paths) == 1
    return json.loads(stored_paths[0].read_text())["bridge_receipt"]


def packet(snapshot_id: str) -> dict:
    return {
        "contract": "ACCEPTED_DATA_PING_PACKET_v1",
        "snapshot_id": snapshot_id,
        "freeze_utc": "2026-08-16T10:00:00Z",
        "source_health": {},
        "market_metrics": {},
        "framework_interpretation": "TEST_ONLY",
        "acceptance_status": "ACCEPTED",
        "authority": {"portfolio_action": False, "model_weight_change": False, "canonical_promotion": False},
    }


def test_data_ping_bridge_acceptance_semantics():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        body = packet("TEST_SNAPSHOT_001")
        bridge = run_bridge(body, root, body["snapshot_id"])
        assert bridge["framework_acceptance_time"] is not None
        assert bridge["framework_acceptance_status"] == "KNOWN"
        assert bridge["framework_ingest_time"] is None
        assert bridge["framework_ingest_status"] == "UNAVAILABLE"
        assert bridge["policy_evaluable_time"] is None
        assert bridge["decision_evaluation_time"] is None
        assert bridge["action_divergence_time"] is None
        assert bridge["framework_ingest_not_inferred"] is True
        assert bridge["upstream_lifecycle_refs"] == []
        assert bridge["upstream_lifecycle_link_status"] == "UNAVAILABLE"
        assert bridge["upstream_lifecycle_link_method"] == "PACKET_SUPPLIED_ONLY_NO_TEMPORAL_INFERENCE"

        linked = packet("TEST_SNAPSHOT_002")
        linked["lifecycle_receipts"] = [
            {"source_run_id": "gh-123-1", "path": "03_DAILY_CAPTURE_LOGS/evidence_lifecycle/example.json"}
        ]
        bridge = run_bridge(linked, root, linked["snapshot_id"])
        assert bridge["upstream_lifecycle_link_status"] == "EXPLICIT"
        assert bridge["upstream_lifecycle_refs"] == linked["lifecycle_receipts"]


def main():
    test_validator_guards()
    test_acceptance_stamper_does_not_infer_ingest()
    test_data_ping_bridge_acceptance_semantics()
    print("lifecycle receipt acceptance tests: PASS")


if __name__ == "__main__":
    main()
