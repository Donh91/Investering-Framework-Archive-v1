from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.learning.build_model_calibration_ledger import outcome_matches_frozen_forecast
from scripts.learning.forecast_ratification_freezer import digest, validate_frozen_forecast_record

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "scripts" / "learning" / "build_model_calibration_ledger.py"


class ModelCalibrationPopulationContractTests(unittest.TestCase):
    @staticmethod
    def valid_forecast(forecast_id: str = "F-1") -> dict:
        return {
            "contract": "FROZEN_FORECAST_v1",
            "model": "test-model",
            "task": "test-task",
            "prompt_sha256": "a" * 64,
            "forecast_id": forecast_id,
            "metric_path": "metrics.test",
            "horizon_days": 1,
            "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
        }

    def run_builder(self, root: Path):
        population_root = root / "research" / "api_agent" / "forecast_candidates"
        frozen = population_root / "FROZEN"
        matured = population_root / "MATURED"
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
            pending = root / "research" / "api_agent" / "forecast_candidates" / "PENDING"
            pending.mkdir(parents=True)
            (pending / "candidate.json").write_text("{}")
            summary, eligibility, output = self.run_builder(root)

            self.assertEqual(summary["cohort_status"], "NO_FROZEN_RATIFIED_COHORT")
            self.assertEqual(eligibility["cohort_status"], "NO_FROZEN_RATIFIED_COHORT")
            self.assertEqual(eligibility["settlement_eligibility_status"], "NO_FROZEN_RATIFIED_COHORT")
            self.assertEqual(eligibility["population_id"], "NONCANONICAL_FIXTURE")
            self.assertEqual(eligibility["canonical_population_id"], "API_AGENT_RATIFIED_T13")
            self.assertEqual(eligibility["execution_mode"], "NONCANONICAL_FIXTURE")
            self.assertFalse(eligibility["canonical_population_identity"])
            self.assertEqual(eligibility["candidate_count"], 1)
            self.assertEqual(eligibility["frozen_count"], 0)
            self.assertFalse(eligibility["direct_framework_memory_import_allowed"])
            self.assertFalse(eligibility["historical_schema_backfill_by_inference_allowed"])
            self.assertEqual(len(output.read_text().splitlines()), 1)

    def test_ratified_forecast_without_outcome_reports_awaiting_outcomes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "research" / "api_agent" / "forecast_candidates" / "FROZEN"
            frozen.mkdir(parents=True)
            (frozen / "f.json").write_text(json.dumps(self.valid_forecast()))
            summary, eligibility, _ = self.run_builder(root)
            self.assertEqual(summary["cohort_status"], "COHORT_PRESENT_AWAITING_OUTCOMES")
            self.assertEqual(eligibility["frozen_count"], 1)
            self.assertEqual(eligibility["outcome_record_count"], 0)

    def test_noneligible_outcome_is_distinct_from_empty_cohort(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            population_root = root / "research" / "api_agent" / "forecast_candidates"
            frozen = population_root / "FROZEN"
            matured = population_root / "MATURED"
            frozen.mkdir(parents=True)
            matured.mkdir(parents=True)
            (frozen / "f.json").write_text(json.dumps(self.valid_forecast()))
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
            population_root = root / "research" / "api_agent" / "forecast_candidates"
            frozen = population_root / "FROZEN"
            matured = population_root / "MATURED"
            frozen.mkdir(parents=True)
            matured.mkdir(parents=True)
            (frozen / "f.json").write_text(json.dumps(self.valid_forecast()))
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
            self.assertEqual(summary["scientific_scored_count"], 0)
            self.assertTrue(eligibility["rows"][0]["settlement_score_eligible"])
            self.assertFalse(eligibility["rows"][0]["scientific_score_eligible"])
            self.assertEqual(eligibility["rows"][0]["scientific_score_exclusion_reason"], "NONCANONICAL_FIXTURE_NO_SCIENTIFIC_AUTHORITY")

    def test_orphan_eligible_outcome_is_quarantined(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            matured = root / "research" / "api_agent" / "forecast_candidates" / "MATURED"
            matured.mkdir(parents=True)
            (matured / "orphan.json").write_text(
                json.dumps(
                    {
                        "contract": "MATURED_OUTCOME_v3",
                        "forecast_id": "ORPHAN",
                        "status": "MATURED",
                        "result": "HIT",
                        "scientific_score_eligible": True,
                    }
                )
            )

            summary, eligibility, output = self.run_builder(root)

            self.assertEqual(summary["cohort_status"], "NO_FROZEN_RATIFIED_COHORT")
            self.assertEqual(summary["orphan_outcome_count"], 1)
            self.assertEqual(eligibility["outcome_record_count"], 0)
            self.assertEqual(eligibility["settlement_eligible_count"], 0)
            self.assertEqual(len(output.read_text().splitlines()), 1)

    def test_incomplete_frozen_forecast_is_quarantined(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "research" / "api_agent" / "forecast_candidates" / "FROZEN"
            frozen.mkdir(parents=True)
            (frozen / "incomplete.json").write_text(
                json.dumps(
                    {
                        "contract": "FROZEN_FORECAST_v1",
                        "forecast_id": "F-INCOMPLETE",
                        "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
                    }
                )
            )

            summary, eligibility, _ = self.run_builder(root)

            self.assertEqual(summary["cohort_status"], "NO_FROZEN_RATIFIED_COHORT")
            self.assertEqual(summary["invalid_frozen_forecast_count"], 1)
            self.assertEqual(eligibility["frozen_count"], 0)

    def test_refuses_roots_outside_declared_population(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "research" / "framework_memory" / "forecast_memory"
            matured = root / "research" / "framework_memory" / "outcome_memory"
            frozen.mkdir(parents=True)
            matured.mkdir(parents=True)
            output = root / "MODEL_CALIBRATION_LEDGER.csv"
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
                ],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("POPULATION_ROOT_MISMATCH", result.stderr)
            self.assertFalse(output.exists())


    def test_suffix_shaped_external_fixture_cannot_write_repository_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "research" / "api_agent" / "forecast_candidates" / "FROZEN"
            matured = root / "research" / "api_agent" / "forecast_candidates" / "MATURED"
            frozen.mkdir(parents=True)
            matured.mkdir(parents=True)
            repository_output = ROOT / "research" / "api_agent" / "_SHOULD_NOT_WRITE_STAGE2_TEST.csv"
            repository_eligibility = ROOT / "research" / "api_agent" / "_SHOULD_NOT_WRITE_STAGE2_TEST.json"
            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(LEDGER),
                        "--forecast-root",
                        str(frozen),
                        "--outcome-root",
                        str(matured),
                        "--output",
                        str(repository_output),
                        "--eligibility-output",
                        str(repository_eligibility),
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("POPULATION_ROOT_MISMATCH", result.stderr)
                self.assertFalse(repository_output.exists())
                self.assertFalse(repository_eligibility.exists())
            finally:
                repository_output.unlink(missing_ok=True)
                repository_eligibility.unlink(missing_ok=True)

    @staticmethod
    def canonical_frozen() -> dict:
        return {
            "contract": "FROZEN_FORECAST_v1",
            "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
            "forecast_id": "ff_test",
            "candidate_id": "candidate-test",
            "model": "test-model",
            "task": "test-task",
            "prompt_sha256": "a" * 64,
            "candidate_sha256": "b" * 64,
            "ratification_sha256": "c" * 64,
            "baseline_evidence_sha256": "d" * 64,
            "frozen_at_utc": "2026-09-10T00:00:00Z",
            "outcome_due_utc": "2026-09-11T00:00:00Z",
            "ratification_decision_at_utc": "2026-09-10T00:00:00Z",
            "baseline_evidence_observed_at_utc": "2026-09-09T23:59:00Z",
            "horizon_days": 1,
            "metric_path": "spot.BTCUSDT.close",
            "ratification_contract": "FORECAST_RATIFICATION_PACKET_v2",
            "ratification_authority": "CHATGPT_FRAMEWORK_OWNER",
            "ratification_outcome_blind": True,
            "baseline_evidence_path": "evidence/baseline.json",
            "direction": "UP",
            "start_value": 100.0,
            "target_mode": "PCT_MOVE",
            "threshold_pct": 1.0,
            "authority": {
                "portfolio_action": False,
                "model_weight_change": False,
                "canonical_promotion": False,
                "framework_state_change": False,
            },
        }

    def test_canonical_owner_validator_rejects_semantically_invalid_freeze(self):
        valid = self.canonical_frozen()
        validate_frozen_forecast_record(valid)
        for key, bad in (("prompt_sha256", "bad"), ("horizon_days", -1), ("metric_path", {"bad": True})):
            with self.subTest(key=key):
                row = dict(valid)
                row[key] = bad
                with self.assertRaises(ValueError):
                    validate_frozen_forecast_record(row)

    def test_outcome_forecast_hash_binding_is_byte_deterministic(self):
        frozen = self.canonical_frozen()
        good = {"forecast_sha256": digest(frozen)}
        self.assertTrue(outcome_matches_frozen_forecast(good, frozen))
        self.assertFalse(outcome_matches_frozen_forecast({}, frozen))
        self.assertFalse(outcome_matches_frozen_forecast({"forecast_sha256": "0" * 64}, frozen))



if __name__ == "__main__":
    unittest.main()
