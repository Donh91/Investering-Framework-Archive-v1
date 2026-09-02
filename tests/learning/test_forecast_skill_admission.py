from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "learning"))

from build_forecast_replication_eligibility import build as build_replication  # noqa: E402
from build_forecast_skill_admission import build as build_skill  # noqa: E402

LEDGER = ROOT / "scripts" / "learning" / "build_model_calibration_ledger.py"


def settlement_doc(count: int = 1):
    return {
        "contract": "MODEL_CALIBRATION_SETTLEMENT_ELIGIBILITY_v1",
        "eligibility_scope": "SETTLEMENT_TIMING_ONLY",
        "settlement_eligible_count": count,
        "scientific_scored_count": count,
        "scientific_skill_status": "NOT_ASSESSED_SETTLEMENT_TIMING_ONLY",
        "scientific_skill_authority": False,
        "rows": [
            {
                "forecast_id": f"fc-{i}",
                "settlement_score_eligible": True,
                "scientific_score_eligible": True,
                "eligibility_scope": "SETTLEMENT_TIMING_ONLY",
                "scientific_skill_eligible": False,
            }
            for i in range(count)
        ],
    }


def evidence_audit():
    return {
        "contract": "FORECAST_EVIDENCE_CLASS_BOUNDARY_AUDIT_v1",
        "status": "PASS",
        "cross_evidence_class_pooling_allowed": False,
        "forecast_skill_authority": False,
        "violations": [],
    }


def replication_pass(count: int = 20):
    return {
        "contract": "FORECAST_REPLICATION_ELIGIBILITY_v1",
        "status": "PASS",
        "scientific_skill_authority": False,
        "independently_assessed_forecast_count": count,
        "disagreement_rate": 0.0,
        "max_disagreement_rate": 0.05,
    }


class ForecastSkillAdmissionTests(unittest.TestCase):
    def test_calibration_sidecar_explicitly_limits_itself_to_settlement_timing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "FROZEN"; matured = root / "MATURED"
            frozen.mkdir(); matured.mkdir()
            (frozen / "fc.json").write_text(json.dumps({
                "contract": "FROZEN_FORECAST_v1",
                "forecast_id": "fc",
                "candidate_id": "c",
                "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
            }))
            (matured / "fc.json").write_text(json.dumps({
                "contract": "MATURED_OUTCOME_v3",
                "forecast_id": "fc",
                "status": "MATURED",
                "result": "HIT",
                "scientific_score_eligible": True,
                "settlement_contract_version": "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
            }))
            ledger = root / "ledger.csv"; sidecar = root / "sidecar.json"
            proc = subprocess.run([
                sys.executable, str(LEDGER),
                "--forecast-root", str(frozen),
                "--outcome-root", str(matured),
                "--output", str(ledger),
                "--eligibility-output", str(sidecar),
            ], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            doc = json.loads(sidecar.read_text())
            self.assertEqual(doc["eligibility_scope"], "SETTLEMENT_TIMING_ONLY")
            self.assertEqual(doc["scientific_skill_status"], "NOT_ASSESSED_SETTLEMENT_TIMING_ONLY")
            self.assertFalse(doc["scientific_skill_authority"])
            self.assertEqual(doc["settlement_eligible_count"], 1)
            self.assertTrue(doc["rows"][0]["settlement_score_eligible"])
            self.assertFalse(doc["rows"][0]["scientific_skill_eligible"])

    def test_legacy_replicated_fired_receipt_without_independent_verification_does_not_count(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); receipts = root / "receipts"; receipts.mkdir()
            (receipts / "legacy.json").write_text(json.dumps({
                "contract": "EXPERIMENT_EXECUTION_RECEIPT_v1",
                "local_frozen_forecast_id": "fc-0",
                "replication_status": "REPLICATED_FIRED",
            }))
            result = build_replication(settlement_doc(1), receipts, 1, 0.05)
            self.assertEqual(result["status"], "BLOCKED_INSUFFICIENT_INDEPENDENT_REPLICATION")
            self.assertEqual(result["independently_assessed_forecast_count"], 0)
            self.assertEqual(result["agreement_forecast_count"], 0)

    def test_replication_requires_real_independent_data_verification_and_recompute(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); receipts = root / "receipts"; receipts.mkdir()
            for i in range(20):
                (receipts / f"r-{i}.json").write_text(json.dumps({
                    "contract": "EXPERIMENT_EXECUTION_RECEIPT_v1",
                    "local_frozen_forecast_id": f"fc-{i}",
                    "replication_status": "REPLICATED_FIRED",
                    "component_recompute_performed": True,
                    "independent_data_verification_performed": True,
                }))
            result = build_replication(settlement_doc(20), receipts, 20, 0.05)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["independently_assessed_forecast_count"], 20)
            self.assertEqual(result["disagreement_rate"], 0.0)
            self.assertFalse(result["scientific_skill_authority"])

    def test_disagreement_above_five_percent_blocks_replication_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); receipts = root / "receipts"; receipts.mkdir()
            for i in range(20):
                status = "REPLICATION_MISMATCH" if i < 2 else "REPLICATED_FIRED"
                (receipts / f"r-{i}.json").write_text(json.dumps({
                    "contract": "EXPERIMENT_EXECUTION_RECEIPT_v1",
                    "local_frozen_forecast_id": f"fc-{i}",
                    "replication_status": status,
                    "component_recompute_performed": True,
                    "independent_data_verification_performed": True,
                }))
            result = build_replication(settlement_doc(20), receipts, 20, 0.05)
            self.assertEqual(result["status"], "FAIL_DISAGREEMENT_RATE")
            self.assertAlmostEqual(result["disagreement_rate"], 0.1)

    def test_skill_admission_stays_blocked_when_power_and_calibration_are_not_assessed(self):
        result = build_skill(settlement_doc(20), replication_pass(), evidence_audit(), None, None, 20.0)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["forecast_skill_established"])
        self.assertIn("EFFECTIVE_N:NOT_ASSESSED_NO_CANONICAL_POWER_AUDIT", result["blockers"])
        self.assertIn("CALIBRATION_BASELINE:NOT_ASSESSED_NO_PREREGISTERED_CALIBRATION_AUDIT", result["blockers"])
        self.assertFalse(result["historical_replay_can_increase_prospective_n"])

    def test_even_full_gate_pass_only_admits_future_skill_analysis_not_skill_claim(self):
        power = {"contract": "FORECAST_EFFECTIVE_N_AUDIT_v1", "status": "PASS", "effective_n": 24.0, "method": "PREREGISTERED_FIXTURE"}
        calibration = {"contract": "FORECAST_CALIBRATION_AUDIT_v1", "status": "PASS", "prospective_only": True, "baseline": "PREREGISTERED_FIXTURE"}
        result = build_skill(settlement_doc(20), replication_pass(), evidence_audit(), power, calibration, 20.0)
        self.assertEqual(result["status"], "ELIGIBLE_FOR_PREREGISTERED_SKILL_ANALYSIS")
        self.assertFalse(result["forecast_skill_established"])
        self.assertTrue(result["skill_analysis_admission_only"])
        self.assertEqual(result["blockers"], [])


if __name__ == "__main__":
    unittest.main()
