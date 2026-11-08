from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.orchestration.build_framework_handoff_manifest import file_ref
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


def test_framework_handoff_file_ref_accepts_absolute_path_with_relative_repo_root() -> None:
    root = Path(".")
    target = (Path.cwd() / "scripts/orchestration/build_framework_handoff_manifest.py").resolve()

    ref = file_ref(target, root)

    assert ref is not None
    assert ref["path"] == "scripts/orchestration/build_framework_handoff_manifest.py"
    assert ref["sha256"] == _sha(target)


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



class MasterMondaySemanticReadinessShadowTests(unittest.TestCase):
    """Content usability is separate from a PASS byte-integrity receipt."""

    def _receipt(self, name: str, payload: dict, corrupt_sha: bool = False) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rel = "research/source/mm.json"
            target = root / rel
            _write_json(target, payload)
            manifest = _manifest(
                root, [name], {name: {
                    "path": rel,
                    "sha256": "0" * 64 if corrupt_sha else _sha(target),
                }},
            )
            return build_consumer_receipt(root, manifest, "TEST_CONSUMER", [name])

    def test_byte_verified_unavailable_scorecard_is_semantically_not_ready(self) -> None:
        value = self._receipt("MASTER_MONDAY_CALIBRATION_SCORECARD", {
            "status": "UNAVAILABLE_API_CONTRACT",
            "matured_outcome_count": 140,
            "experiment_registry_status": "AVAILABLE",
        })
        self.assertEqual(value["status"], "PASS")
        self.assertEqual(value["consumption_state"], "VERIFIED")
        self.assertEqual(value["semantic_readiness"]["status"], "NOT_READY")
        self.assertEqual(value["semantic_readiness"]["evidence_content_status"]
                         ["MASTER_MONDAY_CALIBRATION_SCORECARD"]["reason"],
                         "MM_CONTENT_UNAVAILABLE")

    def test_zero_maturity_pending_is_valid_pending_not_failure(self) -> None:
        value = self._receipt("MASTER_MONDAY_CALIBRATION_SCORECARD", {
            "status": "PENDING_MATURED_OUTCOMES",
            "matured_outcome_count": 0,
            "experiment_registry_status": "AVAILABLE",
        })
        self.assertEqual(value["status"], "PASS")
        self.assertEqual(value["semantic_readiness"]["status"], "PENDING_VALID")

    def test_inconsistent_pending_is_not_silently_accepted(self) -> None:
        value = self._receipt("MASTER_MONDAY_CALIBRATION_SCORECARD", {
            "status": "PENDING_MATURED_OUTCOMES",
            "matured_outcome_count": 3,
            "experiment_registry_status": "AVAILABLE",
        })
        self.assertEqual(value["semantic_readiness"]["status"], "NOT_READY")

    def test_ready_pointer_cannot_hide_unavailable_scorecard(self) -> None:
        value = self._receipt("MASTER_MONDAY_DELIVERY_POINTER", {
            "status": "READY",
            "scorecard_status": "UNAVAILABLE_API_CONTRACT",
            "operational_translation_status": "UNAVAILABLE_API_CONTRACT",
        })
        self.assertEqual(value["status"], "PASS")
        self.assertEqual(value["semantic_readiness"]["status"], "NOT_READY")

    def test_corrupt_hash_is_not_interpreted_as_semantic_ready(self) -> None:
        value = self._receipt("MASTER_MONDAY_OPERATIONAL_TRANSLATION", {
            "status": "READY",
        }, corrupt_sha=True)
        self.assertEqual(value["status"], "PARTIAL")
        self.assertEqual(value["semantic_readiness"]["status"], "UNKNOWN")
        self.assertEqual(value["semantic_readiness"]["evidence_content_status"]
                         ["MASTER_MONDAY_OPERATIONAL_TRANSLATION"]["reason"],
                         "EVIDENCE_NOT_BYTE_VERIFIED")

    def test_valid_translation_may_be_ready_without_changing_receipt(self) -> None:
        value = self._receipt("MASTER_MONDAY_OPERATIONAL_TRANSLATION", {
            "status": "PRODUCED",
        })
        self.assertEqual(value["status"], "PASS")
        self.assertEqual(value["semantic_readiness"]["status"], "READY")

    def test_unrelated_byte_receipts_are_not_treated_as_semantically_ready(self) -> None:
        value = self._receipt("A", {"status": "READY"})
        self.assertEqual(value["semantic_readiness"]["status"], "NOT_APPLICABLE")
        self.assertEqual(value["verified_evidence"]["A"]["path"],
                         "research/source/mm.json")


class ConsumerReceiptModuleFunctionCollectionTests(unittest.TestCase):
    """Unittest compatibility wrappers for the eight module-level tests above."""

    def run_with_tmp_path(self, fn) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fn(Path(directory))

    def test_consumer_receipt_passes_only_when_all_expected_inputs_are_verified_collected(self) -> None:
        self.run_with_tmp_path(test_consumer_receipt_passes_only_when_all_expected_inputs_are_verified)

    def test_consumer_receipt_is_partial_when_expected_input_is_not_declared_collected(self) -> None:
        self.run_with_tmp_path(test_consumer_receipt_is_partial_when_expected_input_is_not_declared)

    def test_consumer_receipt_is_partial_when_manifest_binding_is_stale_collected(self) -> None:
        self.run_with_tmp_path(test_consumer_receipt_is_partial_when_manifest_binding_is_stale)

    def test_consumer_receipt_degrades_when_handoff_snapshot_is_too_old_collected(self) -> None:
        self.run_with_tmp_path(test_consumer_receipt_degrades_when_handoff_snapshot_is_too_old)

    def test_consumer_receipt_is_unknown_when_manifest_is_unavailable_collected(self) -> None:
        self.run_with_tmp_path(test_consumer_receipt_is_unknown_when_manifest_is_unavailable)

    def test_stamp_target_recomputes_semantic_self_hash_after_receipt_collected(self) -> None:
        self.run_with_tmp_path(test_stamp_target_recomputes_semantic_self_hash_after_receipt)

    def test_framework_handoff_file_ref_accepts_absolute_path_with_relative_repo_root_collected(self) -> None:
        test_framework_handoff_file_ref_accepts_absolute_path_with_relative_repo_root()

    def test_framework_handoff_separates_receipt_consumers_from_routing_labels_collected(self) -> None:
        self.run_with_tmp_path(test_framework_handoff_separates_receipt_consumers_from_routing_labels)


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
