"""Fail-closed, synthetic-only tests for Research Lab scientific conversion preflight."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.research.research_lab_evidence_conversion_preflight_v1 import audit


def write(root: Path, relative: str, content: object) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        content if isinstance(content, str) else json.dumps(content),
        encoding="utf-8",
    )


def fixture(root: Path) -> None:
    write(root, "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json", {
        "candidate_count": 2, "candidates": [
            {"candidate_id": "a", "matured_outcome_count": 3,
             "scientific_score_eligible_outcome_count": 0,
             "scientific_score_nonadmission_counts_v1": {"FORECAST_SOURCE_ANCHOR_REJECTED": 3}},
            {"candidate_id": "b", "matured_outcome_count": 0,
             "scientific_score_eligible_outcome_count": 0,
             "scientific_score_nonadmission_counts_v1": {}},
        ],
    })
    write(root, "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json", {
        "candidate_count": 2, "status_counts": {
            "QUALIFIED_FOR_FORWARD_TEST": 1, "SEMANTIC_DUPLICATE_KEEP_SHADOW": 1
        },
        "candidates": [{"candidate_id": "a", "status": "QUALIFIED_FOR_FORWARD_TEST"},
                       {"candidate_id": "b", "status": "SEMANTIC_DUPLICATE_KEEP_SHADOW"}],
    })
    write(root, "06_RESEARCH_LAB/shared_row_model_tournament_v1/NEXT_ACTION_STATE.json", {
        "primary_action": "INVESTIGATE_DIVERGENCE",
        "terminal_verdict": "INSUFFICIENT_EVIDENCE",
        "evidence_summary": {"eligible_rows_total": 45, "matured_rows": {"7d": 32}},
    })
    write(root, "06_RESEARCH_LAB/shared_row_model_tournament_v1/RUNTIME_STATUS.json", {
        "eligible_prospective_rows": 0,
    })
    write(root, "research/framework_memory/fnp_forward_rows/LATEST.json", {
        "status": "PASS_NO_ELIGIBLE_INPUT", "current_source_row_count": 0,
        "source_receipts_ignored_nondivergence_or_other_contract": 5,
        "authoritative_fnp_evaluator_available": False,
    })
    write(root, "05_CYCLE_NAVIGATOR/autonomous_calibration_v1/STATE.json", {
        "eligible_verified_row_n": 0,
    })
    write(root, "05_CYCLE_NAVIGATOR/forward_range_ledger/FORWARD_RANGE_LEDGER_v0_1.csv",
          "forecast_id,notes\nCNxx_EXAMPLE_BTC,EXAMPLE_ONLY\n")
    write(root, "scripts/experiments/source_git_anchor.py",
          "# No authenticated server-side acceptance clock exists\n"
          "if accepted_before is not None or accepted_after is not None:\n"
          "    return False\n")


class EvidenceConversionPreflightTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_rejected_outcomes_are_not_skill(self):
        report = audit(self.root)
        self.assertEqual(report["status"], "DIAGNOSTIC_ONLY_NOT_SCIENTIFIC_ADMISSION")
        self.assertEqual(report["experiment"]["matured_outcome_count_candidate_summed_nonindependent"], 3)
        self.assertEqual(report["experiment"]["scientific_score_eligible_candidate_summed_nonindependent"], 0)
        self.assertEqual(report["experiment"]["nonadmission_reason_counts"], {
            "FORECAST_SOURCE_ANCHOR_REJECTED": 3
        })
        self.assertFalse(report["experiment"]["timed_anchor_correction_authorized"])
        self.assertFalse(report["authority"]["scientific_promotion"])
        self.assertEqual(report["cycle_navigator"]["legacy_baseline_ledger_real_rows"], 0)

    def test_shared_row_mismatch_is_not_automatically_a_writer_bug(self):
        report = audit(self.root)
        self.assertEqual(report["shared_row"]["runtime_eligible_rows"], 0)
        self.assertEqual(report["shared_row"]["next_action_reported_eligible_rows"], 45)
        self.assertIn("RECONCILE_ROW_GRAIN", report["shared_row"]["semantics"])
        self.assertEqual(report["shared_row"]["terminal_verdict"], "INSUFFICIENT_EVIDENCE")

    def test_source_gate_change_never_implies_new_eligibility(self):
        write(self.root, "scripts/experiments/source_git_anchor.py", "# changed source gate")
        report = audit(self.root)
        self.assertEqual(report["experiment"]["timed_git_anchor_policy"],
                         "NOT_ATTESTED_SOURCE_CHANGED")
        self.assertEqual(report["experiment"]["scientific_score_eligible_candidate_summed_nonindependent"], 0)

    def test_invalid_candidate_count_fails_closed(self):
        path = "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"
        value = json.loads((self.root / path).read_text())
        value["candidate_count"] = 999
        write(self.root, path, value)
        with self.assertRaisesRegex(ValueError, "REGISTRY_COUNT_DRIFT"):
            audit(self.root)

    def test_admission_status_drift_fails_closed(self):
        path = "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"
        value = json.loads((self.root / path).read_text())
        value["status_counts"] = {"QUALIFIED_FOR_FORWARD_TEST": 2}
        write(self.root, path, value)
        with self.assertRaisesRegex(ValueError, "ADMISSION_STATUS_COUNT_DRIFT"):
            audit(self.root)

    def test_missing_provenance_file_fails_closed(self):
        (self.root / "scripts/experiments/source_git_anchor.py").unlink()
        with self.assertRaisesRegex(ValueError, "SOURCE_GATE_UNAVAILABLE"):
            audit(self.root)

    def test_admission_duplicate_id_with_unchanged_status_counts_fails_closed(self):
        path = "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"
        value = json.loads((self.root / path).read_text())
        value["candidates"][1]["candidate_id"] = "a"
        write(self.root, path, value)
        with self.assertRaisesRegex(ValueError, "ADMISSION_CANDIDATE_ID_DRIFT"):
            audit(self.root)

    def test_admission_replaced_id_with_unchanged_status_counts_fails_closed(self):
        path = "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"
        value = json.loads((self.root / path).read_text())
        value["candidates"][1]["candidate_id"] = "not-in-original-registry"
        write(self.root, path, value)
        with self.assertRaisesRegex(ValueError, "ADMISSION_CANDIDATE_ID_DRIFT"):
            audit(self.root)

    def test_external_csv_symlink_is_rejected(self):
        path = self.root / "05_CYCLE_NAVIGATOR/forward_range_ledger/FORWARD_RANGE_LEDGER_v0_1.csv"
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "external.csv"
            external.write_text("forecast_id,notes\\nFAKE,EXAMPLE_ONLY\\n")
            path.unlink()
            path.symlink_to(external)
            with self.assertRaisesRegex(ValueError, "SOURCE_MISSING_OR_UNTRUSTED"):
                audit(self.root)

    def test_parent_directory_symlink_is_rejected(self):
        folder = self.root / "scripts/experiments"
        actual = self.root / "scripts/real_gate"
        folder.rename(actual)
        folder.symlink_to(actual, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "SOURCE_GATE_UNAVAILABLE"):
            audit(self.root)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO support required")
    def test_nonregular_fifo_csv_is_rejected_before_open(self):
        path = self.root / "05_CYCLE_NAVIGATOR/forward_range_ledger/FORWARD_RANGE_LEDGER_v0_1.csv"
        path.unlink()
        os.mkfifo(path)
        with self.assertRaisesRegex(ValueError, "SOURCE_MISSING_OR_UNTRUSTED"):
            audit(self.root)

    def test_modified_temporal_guard_body_cannot_be_attested(self):
        path = "scripts/experiments/source_git_anchor.py"
        value = (self.root / path).read_text()
        self.assertIn("return False", value)
        write(self.root, path, value.replace("return False", "return True"))
        self.assertEqual(audit(self.root)["experiment"]["timed_git_anchor_policy"],
                         "NOT_ATTESTED_SOURCE_CHANGED")


if __name__ == "__main__":
    unittest.main()
