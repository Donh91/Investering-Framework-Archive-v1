from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.orchestration.consumer_receipt import build_consumer_receipt, canonical, stamp_target


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest(root: Path, expected: list[str], evidence: dict[str, dict], *, generated_at_utc: str = "2026-09-15T00:00:00Z") -> Path:
    path = root / "research/framework_handoffs/LATEST_FRAMEWORK_HANDOFF_MANIFEST.json"
    _write_json(path, {
        "contract": "FRAMEWORK_HANDOFF_MANIFEST_v2",
        "generated_at_utc": generated_at_utc,
        "consumers": {"TEST_CONSUMER": expected},
        "evidence": evidence,
    })
    return path


def test_consumer_receipt_passes_only_when_all_expected_inputs_are_verified(tmp_path: Path) -> None:
    evidence_path = tmp_path / "research/source/a.json"
    _write_json(evidence_path, {"value": 1})
    manifest = _manifest(tmp_path, ["A"], {"A": {"path": "research/source/a.json", "sha256": _sha(evidence_path)}})

    receipt = build_consumer_receipt(
        tmp_path,
        manifest,
        "TEST_CONSUMER",
        ["A"],
        consumed_at_utc="2026-09-15T00:05:00Z",
        max_manifest_age_seconds=900,
    )

    assert receipt["status"] == "PASS"
    assert receipt["consumption_state"] == "VERIFIED"
    assert receipt["manifest_freshness_status"] == "PASS"
    assert receipt["manifest_age_seconds"] == 300.0
    assert receipt["manifest_sha256"] == _sha(manifest)
    assert receipt["missing_expected_evidence"] == []
    assert receipt["stale_declared_evidence"] == []
    assert set(receipt["verified_evidence"]) == {"A"}


def test_consumer_receipt_is_partial_when_expected_input_is_not_declared(tmp_path: Path) -> None:
    a = tmp_path / "research/source/a.json"
    b = tmp_path / "research/source/b.json"
    _write_json(a, {"value": "a"})
    _write_json(b, {"value": "b"})
    manifest = _manifest(tmp_path, ["A", "B"], {
        "A": {"path": "research/source/a.json", "sha256": _sha(a)},
        "B": {"path": "research/source/b.json", "sha256": _sha(b)},
    })

    receipt = build_consumer_receipt(tmp_path, manifest, "TEST_CONSUMER", ["A"])

    assert receipt["status"] == "PARTIAL"
    assert receipt["consumption_state"] == "DEGRADED"
    assert receipt["missing_expected_evidence"] == ["B"]
    assert set(receipt["verified_evidence"]) == {"A"}


def test_consumer_receipt_is_partial_when_manifest_binding_is_stale(tmp_path: Path) -> None:
    evidence_path = tmp_path / "research/source/a.json"
    _write_json(evidence_path, {"value": 1})
    manifest = _manifest(tmp_path, ["A"], {"A": {"path": "research/source/a.json", "sha256": "0" * 64}})

    receipt = build_consumer_receipt(tmp_path, manifest, "TEST_CONSUMER", ["A"])

    assert receipt["status"] == "PARTIAL"
    assert receipt["consumption_state"] == "DEGRADED"
    assert receipt["stale_declared_evidence"] == ["A"]
    assert receipt["verified_evidence"] == {}


def test_consumer_receipt_degrades_when_handoff_snapshot_is_too_old(tmp_path: Path) -> None:
    evidence_path = tmp_path / "research/source/a.json"
    _write_json(evidence_path, {"value": 1})
    manifest = _manifest(
        tmp_path,
        ["A"],
        {"A": {"path": "research/source/a.json", "sha256": _sha(evidence_path)}},
        generated_at_utc="2026-09-15T00:00:00Z",
    )

    receipt = build_consumer_receipt(
        tmp_path,
        manifest,
        "TEST_CONSUMER",
        ["A"],
        consumed_at_utc="2026-09-15T01:00:00Z",
        max_manifest_age_seconds=900,
    )

    assert receipt["status"] == "PARTIAL"
    assert receipt["consumption_state"] == "DEGRADED"
    assert receipt["manifest_freshness_status"] == "STALE"
    assert receipt["manifest_age_seconds"] == 3600.0
    assert "HANDOFF_MANIFEST_STALE" in receipt["reasons"]


def test_consumer_receipt_is_unknown_when_manifest_is_unavailable(tmp_path: Path) -> None:
    missing = tmp_path / "research/framework_handoffs/missing.json"
    receipt = build_consumer_receipt(
        tmp_path,
        missing,
        "TEST_CONSUMER",
        ["A"],
        consumed_at_utc="2026-09-15T01:00:00Z",
        max_manifest_age_seconds=900,
    )

    assert receipt["status"] == "UNAVAILABLE"
    assert receipt["consumption_state"] == "UNKNOWN"
    assert receipt["reason"] == "HANDOFF_MANIFEST_UNAVAILABLE"


def test_stamp_target_recomputes_semantic_self_hash_after_receipt(tmp_path: Path) -> None:
    evidence_path = tmp_path / "research/source/a.json"
    _write_json(evidence_path, {"value": 1})
    manifest = _manifest(tmp_path, ["A"], {"A": {"path": "research/source/a.json", "sha256": _sha(evidence_path)}})
    target = tmp_path / "output.json"
    _write_json(target, {"contract": "OUTPUT_v1", "payload": 7, "package_sha256": "old"})

    receipt = stamp_target(tmp_path, manifest, "TEST_CONSUMER", target, ["A"], "package_sha256")
    stamped = json.loads(target.read_text())
    declared_hash = stamped.pop("package_sha256")

    assert receipt["status"] == "PASS"
    assert stamped["consumer_receipt"]["contract"] == "CONSUMER_RECEIPT_v1"
    assert declared_hash == hashlib.sha256(canonical(stamped)).hexdigest()


def test_framework_handoff_separates_receipt_consumers_from_routing_labels(tmp_path: Path) -> None:
    output = tmp_path / "handoff.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/orchestration/build_framework_handoff_manifest.py",
            "--repo-root",
            str(tmp_path),
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    manifest = json.loads(output.read_text())

    assert set(manifest["consumers"]) == {"MASTER_MONDAY", "CYCLE_NAVIGATOR", "OPERATIONS_DASHBOARD"}
    assert manifest["consumer_receipt_policy"]["receipt_required_for"] == ["CYCLE_NAVIGATOR", "MASTER_MONDAY", "OPERATIONS_DASHBOARD"]
    assert manifest["consumer_receipt_policy"]["routing_targets_are_consumers"] is False
    assert manifest["consumer_receipt_policy"]["producer_success_requires_verified_consumer_receipt"] is True
    for label in ("RAW_WEEKLY_CALIBRATION", "FORECAST_LEDGER", "EXPERIMENT_LEARNING", "ASTRA_RESEARCH_ROUTING", "CODEX_DELIVERY_ROUTING"):
        assert label not in manifest["consumers"]


class ConsumerReceiptInvariantGateTest(unittest.TestCase):
    def test_runtime_consumer_topology_is_receipt_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "handoff.json"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/orchestration/build_framework_handoff_manifest.py",
                    "--repo-root",
                    str(root),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            manifest = json.loads(output.read_text())
            self.assertEqual(set(manifest["consumers"]), {"MASTER_MONDAY", "CYCLE_NAVIGATOR", "OPERATIONS_DASHBOARD"})
            self.assertEqual(manifest["consumer_receipt_policy"]["receipt_required_for"], ["CYCLE_NAVIGATOR", "MASTER_MONDAY", "OPERATIONS_DASHBOARD"])
            self.assertFalse(manifest["consumer_receipt_policy"]["routing_targets_are_consumers"])
            self.assertTrue(manifest["consumer_receipt_policy"]["producer_success_requires_verified_consumer_receipt"])
            for label in ("RAW_WEEKLY_CALIBRATION", "FORECAST_LEDGER", "EXPERIMENT_LEARNING", "ASTRA_RESEARCH_ROUTING", "CODEX_DELIVERY_ROUTING"):
                self.assertNotIn(label, manifest["consumers"])


if __name__ == "__main__":
    unittest.main()
