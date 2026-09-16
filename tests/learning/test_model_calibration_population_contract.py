from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "scripts" / "learning" / "build_model_calibration_ledger.py"


class ModelCalibrationPopulationContractTests(unittest.TestCase):
    def run_builder(self, root: Path):
        frozen = root / "forecast_candidates" / "FROZEN"
        matured = root / "forecast_candidates" / "MATURED"
        output = root / "MODEL_CALIBRATION_LEDGER.csv"
        eligibility = root / "MODEL_CALIBRATION_SETTLEMENT_ELIGIBILITY.json"
        result = subprocess.run(
            [
                sys.executable,
                str(LEDGER),
                "--forecast-root",
                str(frozen),
                "--outcome-root",
                str(matured),
                "--output",
                str(output),
                "--eligibility-output",
                str(eligibility),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout), json.loads(eligibility.read_text()), output

    def test_no_ratified_cohort_is_explicit_not_generic_success(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "forecast_candidates" / "PENDING").mkdir(parents=True)
            (root / "forecast_candidates" / "PENDING" / "candidate.json").write_text("{}")
            summary, eligibility, output = self.run_builder(root)

            self.assertEqual(summary["cohort_status"], "NO_FROZEN_RATIFIED_COHORT")
            self.assertEqual(eligibility["cohort_status"], "NO_FROZEN_RATIFIED_COHORT")
            self.assertEqual(eligibility["settlement_eligibility_status"], "NO_FROZEN_RATIFIED_COHORT")
            self.assertEqual(eligibility["population_id"], "API_AGENT_RATIFIED_T13")
            self.assertEqual(eligibility["candidate_count"], 1)
            self.assertEqual(eligibility["frozen_count"], 0)
            self.assertFalse(eligibility["direct_framework_memory_import_allowed"])
            self.assertFalse(eligibility["historical_schema_backfill_by_inference_allowed"])
            self.assertEqual(len(output.read_text().splitlines()), 1)

    def test_ratified_forecast_without_outcome_reports_awaiting_outcomes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "forecast_candidates" / "FROZEN"
            frozen.mkdir(parents=True)
            (frozen / "f.json").write_text(
                json.dumps(
                    {
                        "contract": "FROZEN_FORECAST_v1",
                        "forecast_id": "F-1",
                        "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
                    }
                )
            )
            summary, eligibility, _ = self.run_builder(root)
            self.assertEqual(summary["cohort_status"], "COHORT_PRESENT_AWAITING_OUTCOMES")
            self.assertEqual(eligibility["frozen_count"], 1)
            self.assertEqual(eligibility["outcome_record_count"], 0)

    def test_noneligible_outcome_is_distinct_from_empty_cohort(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "forecast_candidates" / "FROZEN"
            matured = root / "forecast_candidates" / "MATURED"
            frozen.mkdir(parents=True)
            matured.mkdir(parents=True)
            (frozen / "f.json").write_text(
                json.dumps(
                    {
                        "contract": "FROZEN_FORECAST_v1",
                        "forecast_id": "F-1",
                        "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
                    }
                )
            )
            (matured / "o.json").write_text(
                json.dumps(
                    {
                        "contract": "MATURED_OUTCOME_v3",
                        "forecast_id": "F-1",
                        "status": "MATURED",
                        "result": "MISS",
                        "scientific_score_eligible": False,
                    }
                )
            )
            summary, eligibility, _ = self.run_builder(root)
            self.assertEqual(summary["cohort_status"], "COHORT_PRESENT_NO_SETTLEMENT_ELIGIBLE_OUTCOMES")
            self.assertEqual(eligibility["row_count"], 1)
            self.assertEqual(eligibility["settlement_eligible_count"], 0)

    def test_settlement_eligible_rows_present_does_not_grant_skill_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "forecast_candidates" / "FROZEN"
            matured = root / "forecast_candidates" / "MATURED"
            frozen.mkdir(parents=True)
            matured.mkdir(parents=True)
            (frozen / "f.json").write_text(
                json.dumps(
                    {
                        "contract": "FROZEN_FORECAST_v1",
                        "forecast_id": "F-1",
                        "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
                    }
                )
            )
            (matured / "o.json").write_text(
                json.dumps(
                    {
                        "contract": "MATURED_OUTCOME_v3",
                        "forecast_id": "F-1",
                        "status": "MATURED",
                        "result": "HIT",
                        "scientific_score_eligible": True,
                    }
                )
            )
            summary, eligibility, _ = self.run_builder(root)
            self.assertEqual(summary["cohort_status"], "SETTLEMENT_ELIGIBLE_ROWS_PRESENT")
            self.assertFalse(eligibility["scientific_skill_authority"])
            self.assertFalse(eligibility["authority"]["model_weight_change"])
            self.assertFalse(eligibility["authority"]["automatic_path_repoint"])


if __name__ == "__main__":
    unittest.main()
