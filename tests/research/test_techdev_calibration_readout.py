import json
from pathlib import Path
import tempfile
import unittest

from scripts.research.techdev_calibration_readout import OWNERS, build_readout

ROOT = Path(__file__).resolve().parents[2]


class TechDevCalibrationReadoutTests(unittest.TestCase):
    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for path in OWNERS.values():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / path).read_bytes())
        return root

    def test_current_owner_reconciles_without_rewriting_or_promoting_history(self):
        root = self.fixture()
        before = {path: (root / path).read_bytes() for path in OWNERS.values()}
        report = build_readout(root)
        history = report["historical_calibration"]
        self.assertEqual((history["source_claim_rows"], history["anchor_rows"], history["outcome_eligible_anchors"]), (257, 50, 44))
        self.assertEqual(report["historical_ledger_counts_preserved"]["scored_rows"], 0)
        self.assertEqual(report["historical_ledger_counts_preserved"]["source_backed_claim_rows"], 186)
        self.assertFalse(history["full_corpus_exhaustive_scoring_claimed"])
        self.assertEqual(history["historical_rows_promoted_to_prospective_evidence"], 0)
        self.assertEqual(history["eligibility_counts"]["SOURCE_BLOCKED"], 2)
        self.assertEqual(history["category_verdicts_as_published"]["FRAMEWORK_ACTION_IMPACT"], "NOT_EVALUABLE")
        revisions = report["first_call_and_revision_channels"]
        self.assertEqual(revisions[1]["original_result"], "NOT_SUPPORTED")
        self.assertEqual(revisions[1]["latest_result"], "SUPPORTED_POST_EVENT")
        self.assertTrue(revisions[1]["revision_cost"])
        self.assertEqual(before, {path: (root / path).read_bytes() for path in OWNERS.values()})

    def test_missing_anchor_owner_is_not_empty_or_zero_evidence(self):
        root = self.fixture()
        (root / OWNERS["anchors"]).unlink()
        with self.assertRaises(FileNotFoundError):
            build_readout(root)

    def test_duplicate_anchor_cannot_inflate_calibration(self):
        root = self.fixture()
        path = root / OWNERS["anchors"]
        lines = path.read_text().splitlines()
        path.write_text("\n".join(lines + [lines[1]]) + "\n")
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            build_readout(root)

    def test_dropped_anchor_fails_count_reconciliation(self):
        root = self.fixture()
        path = root / OWNERS["anchors"]
        path.write_text("\n".join(path.read_text().splitlines()[:-1]) + "\n")
        with self.assertRaisesRegex(ValueError, "ANCHOR_COUNT"):
            build_readout(root)

    def test_category_count_drift_is_explicit(self):
        root = self.fixture()
        path = root / OWNERS["categories"]
        path.write_text(path.read_text().replace("BOTTOM_SIGNAL,0,0,1,1", "BOTTOM_SIGNAL,0,0,2,2"))
        with self.assertRaisesRegex(ValueError, "CATEGORY_ELIGIBLE_COUNTS"):
            build_readout(root)

    def test_commit_binding_rejects_mutated_owner(self):
        from unittest.mock import patch
        root = self.fixture()
        with patch("scripts.research.techdev_calibration_readout.subprocess.run") as command:
            command.return_value.stdout = b"different owner bytes"
            with self.assertRaisesRegex(ValueError, "COMMIT_BYTES_MISMATCH"):
                build_readout(root, "a" * 40)


if __name__ == "__main__":
    unittest.main()
