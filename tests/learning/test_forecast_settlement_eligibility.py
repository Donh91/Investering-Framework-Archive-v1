from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "scripts" / "learning" / "outcome_maturation_engine.py"
LEDGER = ROOT / "scripts" / "learning" / "build_model_calibration_ledger.py"


class ForecastSettlementEligibilityTest(unittest.TestCase):
    def _forecast(self, forecast_id: str, due: str, *, settlement_contract: str | None = None):
        row = {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": forecast_id,
            "candidate_id": f"candidate-{forecast_id}",
            "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
            "direction": "UP",
            "threshold_pct": 1.0,
            "start_value": 100.0,
            "metric_path": "price",
            "frozen_at_utc": "2026-01-01T00:00:00Z",
            "outcome_due_utc": due,
        }
        if settlement_contract:
            row["settlement_contract_version"] = settlement_contract
        return row

    def _run_engine(self, root: Path, now: str):
        result = subprocess.run(
            [
                sys.executable,
                str(ENGINE),
                "--forecast-root", str(root / "FROZEN"),
                "--evidence-root", str(root / "evidence"),
                "--output-root", str(root / "MATURED"),
                "--now-utc", now,
                "--max-evidence-lag-hours", "24",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_legacy_first_capture_outcome_is_visible_but_never_skill_eligible(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("FROZEN", "evidence", "MATURED"):
                (root / name).mkdir()
            forecast = self._forecast("legacy", "2026-01-02T00:00:00Z")
            (root / "FROZEN/legacy.json").write_text(json.dumps(forecast))
            (root / "evidence/late.json").write_text(json.dumps({
                "captured_at_utc": "2026-01-02T02:00:00Z",
                "price": 103.0,
            }))
            summary = self._run_engine(root, "2026-01-03T02:00:00Z")
            row = json.loads((root / "MATURED/legacy.json").read_text())
            self.assertEqual(row["status"], "MATURED")
            self.assertEqual(row["settlement_contract_version"], "LEGACY_FIRST_CAPTURE_AFTER_DUE_v0")
            self.assertEqual(row["settlement_offset_seconds"], 7200.0)
            self.assertFalse(row["scientific_score_eligible"])
            self.assertEqual(row["scientific_score_exclusion_reason"], "LEGACY_POST_DUE_CAPTURE_SETTLEMENT")
            self.assertEqual(summary["scientific_score_eligible"], 0)
            self.assertEqual(summary["scientific_score_excluded"], 1)

    def test_exact_target_time_contract_scores_only_exact_observation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("FROZEN", "evidence", "MATURED"):
                (root / name).mkdir()
            forecast = self._forecast(
                "exact",
                "2026-01-02T00:00:00Z",
                settlement_contract="FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
            )
            (root / "FROZEN/exact.json").write_text(json.dumps(forecast))
            (root / "evidence/exact.json").write_text(json.dumps({
                "captured_at_utc": "2026-01-02T00:00:00Z",
                "price": 102.0,
            }))
            (root / "evidence/late.json").write_text(json.dumps({
                "captured_at_utc": "2026-01-02T02:00:00Z",
                "price": 90.0,
            }))
            summary = self._run_engine(root, "2026-01-03T02:00:00Z")
            row = json.loads((root / "MATURED/exact.json").read_text())
            self.assertEqual(row["status"], "MATURED")
            self.assertEqual(row["end_value"], 102.0)
            self.assertEqual(row["settlement_offset_seconds"], 0.0)
            self.assertTrue(row["scientific_score_eligible"])
            self.assertIsNone(row["scientific_score_exclusion_reason"])
            self.assertEqual(summary["scientific_score_eligible"], 1)

    def test_exact_target_time_contract_never_substitutes_late_capture(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("FROZEN", "evidence", "MATURED"):
                (root / name).mkdir()
            forecast = self._forecast(
                "exact-missing",
                "2026-01-02T00:00:00Z",
                settlement_contract="FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
            )
            (root / "FROZEN/exact.json").write_text(json.dumps(forecast))
            (root / "evidence/late.json").write_text(json.dumps({
                "captured_at_utc": "2026-01-02T00:01:00Z",
                "price": 105.0,
            }))
            summary = self._run_engine(root, "2026-01-03T02:00:00Z")
            row = json.loads((root / "MATURED/exact-missing.json").read_text())
            self.assertEqual(row["status"], "CENSORED")
            self.assertEqual(row["reason"], "NO_EXACT_TARGET_TIME_EVIDENCE_WITHIN_PUBLICATION_GRACE")
            self.assertIsNone(row["settlement_observation_utc"])
            self.assertFalse(row["scientific_score_eligible"])
            self.assertEqual(summary["matured"], 0)
            self.assertEqual(summary["censored"], 1)

    def test_calibration_ledger_fails_closed_on_legacy_outcomes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frozen = root / "FROZEN"; matured = root / "MATURED"
            frozen.mkdir(); matured.mkdir()
            legacy_forecast = self._forecast("legacy", "2026-01-02T00:00:00Z")
            exact_forecast = self._forecast("exact", "2026-01-02T00:00:00Z", settlement_contract="FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1")
            (frozen / "legacy.json").write_text(json.dumps(legacy_forecast))
            (frozen / "exact.json").write_text(json.dumps(exact_forecast))
            common = {
                "contract": "MATURED_OUTCOME_v3",
                "status": "MATURED",
                "result": "HIT",
                "created_at_utc": "2026-01-03T00:00:00Z",
                "return_pct": 2.0,
            }
            (matured / "legacy.json").write_text(json.dumps({**common, "forecast_id": "legacy"}))
            (matured / "exact.json").write_text(json.dumps({
                **common,
                "forecast_id": "exact",
                "scientific_score_eligible": True,
                "settlement_contract_version": "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
                "settlement_target_utc": "2026-01-02T00:00:00Z",
                "settlement_observation_utc": "2026-01-02T00:00:00Z",
                "settlement_offset_seconds": 0.0,
            }))
            output = root / "ledger.csv"
            result = subprocess.run(
                [sys.executable, str(LEDGER), "--forecast-root", str(frozen), "--outcome-root", str(matured), "--output", str(output)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(result.stdout)
            with output.open() as handle:
                rows = {row["forecast_id"]: row for row in csv.DictReader(handle)}
            self.assertEqual(summary["scored_count"], 1)
            self.assertEqual(summary["matured_unscorable_count"], 1)
            self.assertEqual(rows["exact"]["hit"], "1")
            self.assertEqual(rows["legacy"]["hit"], "")
            self.assertEqual(rows["legacy"]["scientific_score_exclusion_reason"], "LEGACY_OUTCOME_WITHOUT_EXPLICIT_SETTLEMENT_ELIGIBILITY")


if __name__ == "__main__":
    unittest.main()
