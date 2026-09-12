from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "learning" / "outcome_censor_reason_summary.py"
_spec = importlib.util.spec_from_file_location("outcome_censor_reason_summary", SCRIPT)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
build_summary = _module.build_summary
classify_reason = _module.classify_reason


class OutcomeCensorReasonSummaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def write(self, name: str, value: dict) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n")

    def test_reason_counts_reconcile_and_preserve_exact_strings(self):
        self.write("legacy.json", {"contract": "MATURED_OUTCOME_v3", "status": "CENSORED", "reason": "LEGACY_V1_TARGET_UNIT_AMBIGUOUS"})
        self.write("availability.json", {"contract": "MATURED_OUTCOME_v3", "status": "CENSORED", "reason": "NO_EVIDENCE_WITHIN_MAX_LAG"})
        self.write("resolver.json", {"contract": "MATURED_OUTCOME_v3", "status": "CENSORED", "reason": "EVIDENCE_NAMESPACE_UNAVAILABLE"})
        self.write("matured.json", {"contract": "MATURED_OUTCOME_v3", "status": "MATURED", "result": "HIT"})
        result = build_summary(self.root)
        self.assertEqual(result["total_outcomes"], 4)
        self.assertEqual(result["censored_outcomes"], 3)
        self.assertEqual(result["reason_counts"], {
            "EVIDENCE_NAMESPACE_UNAVAILABLE": 1,
            "LEGACY_V1_TARGET_UNIT_AMBIGUOUS": 1,
            "NO_EVIDENCE_WITHIN_MAX_LAG": 1,
        })
        self.assertEqual(result["reason_class_counts"], {
            "DELIBERATE_LEGACY_QUARANTINE": 1,
            "EVIDENCE_AVAILABILITY": 1,
            "PROVENANCE_OR_RESOLVER": 1,
        })

    def test_unknown_reason_fails_closed(self):
        self.assertEqual(classify_reason("NEW_UNRECOGNIZED_REASON"), "UNCLASSIFIED_FAIL_CLOSED")
        self.write("unknown.json", {"contract": "MATURED_OUTCOME_v3", "status": "CENSORED", "reason": "NEW_UNRECOGNIZED_REASON"})
        result = build_summary(self.root)
        self.assertEqual(result["reason_counts"]["NEW_UNRECOGNIZED_REASON"], 1)
        self.assertEqual(result["reason_class_counts"]["UNCLASSIFIED_FAIL_CLOSED"], 1)

    def test_missing_reason_is_not_inferred(self):
        self.write("missing.json", {"contract": "MATURED_OUTCOME_v3", "status": "CENSORED"})
        result = build_summary(self.root)
        self.assertEqual(result["reason_counts"], {"MISSING_REASON": 1})
        self.assertEqual(result["reason_class_counts"], {"UNCLASSIFIED_FAIL_CLOSED": 1})

    def test_non_outcome_json_is_skipped(self):
        self.write("pointer.json", {"contract": "LATEST_POINTER_v1", "status": "CENSORED", "reason": "NO_EVIDENCE_WITHIN_MAX_LAG"})
        result = build_summary(self.root)
        self.assertEqual(result["total_outcomes"], 0)
        self.assertEqual(result["censored_outcomes"], 0)
        self.assertEqual(result["skipped_non_outcome_json"], 1)

    def test_summary_is_read_only(self):
        self.write("row.json", {"contract": "MATURED_OUTCOME_v3", "status": "CENSORED", "reason": "METRIC_UNAVAILABLE"})
        before = (self.root / "row.json").read_bytes()
        result = build_summary(self.root)
        after = (self.root / "row.json").read_bytes()
        self.assertEqual(before, after)
        self.assertTrue(result["authority"]["read_only"])
        self.assertFalse(result["authority"]["outcome_status_change"])
        self.assertFalse(result["authority"]["retrospective_uncensoring"])


if __name__ == "__main__":
    unittest.main()
