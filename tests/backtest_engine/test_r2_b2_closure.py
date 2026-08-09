from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.daily_capture.materialize_blind_dual_run import (
    B2_EXPERIMENT_ID,
    B2_EXPERIMENT_STATUS,
    R2_TERMINAL_VERDICT,
    apply_r2_closed_identity_overlay,
)


class R2B2ClosureTests(unittest.TestCase):
    def test_closed_identity_cannot_report_b2_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "COVERAGE_LATEST.json"
            original = {
                "schema_version": "PROSPECTIVE_B2_COVERAGE_MONITOR_v2",
                "b2_analysis_authorized": False,
                "readiness_basis": "IDENTIFYING_OPPORTUNITY_ONLY",
                "per_lane": {
                    "ROTATION_PERMISSION": {
                        "b2_coverage_ready": True,
                        "coverage_band": "COVERAGE_READY",
                        "occupied_identifying_windows": 31,
                        "elapsed_identifying_weeks": 13.0,
                    }
                },
            }
            path.write_text(json.dumps(original) + "\n")
            out = apply_r2_closed_identity_overlay(path)
            lane = out["per_lane"]["ROTATION_PERMISSION"]
            self.assertTrue(lane["identifying_coverage_threshold_met"])
            self.assertFalse(lane["b2_coverage_ready"])
            self.assertEqual(lane["coverage_band"], "B2_CLOSED_NON_TESTABLE")
            self.assertEqual(out["experiment_identity"], B2_EXPERIMENT_ID)
            self.assertEqual(out["experiment_status"], B2_EXPERIMENT_STATUS)
            self.assertEqual(out["terminal_research_verdict"], R2_TERMINAL_VERDICT)
            self.assertEqual(out["evidence_class"], "NON_B2_EVIDENCE")
            self.assertEqual(out["evidence_purpose"], "HEALTH_ONLY")
            self.assertFalse(out["b2_analysis_authorized"])
            self.assertFalse(out["r3_authorized"])

    def test_nonidentifying_engineering_counters_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "COVERAGE_LATEST.json"
            original = {
                "per_lane": {
                    "ROTATION_PERMISSION": {
                        "b2_coverage_ready": False,
                        "coverage_band": "EARLY_ACCUMULATION",
                        "pair_execution_valid_rows": 9,
                        "identifying_opportunity_rows": 0,
                        "occupied_pair_execution_windows": 4,
                        "occupied_identifying_windows": 0,
                    }
                }
            }
            path.write_text(json.dumps(original) + "\n")
            out = apply_r2_closed_identity_overlay(path)
            lane = out["per_lane"]["ROTATION_PERMISSION"]
            self.assertEqual(lane["pair_execution_valid_rows"], 9)
            self.assertEqual(lane["occupied_pair_execution_windows"], 4)
            self.assertEqual(lane["identifying_opportunity_rows"], 0)
            self.assertFalse(lane["identifying_coverage_threshold_met"])
            self.assertFalse(lane["b2_coverage_ready"])


if __name__ == "__main__":
    unittest.main()
