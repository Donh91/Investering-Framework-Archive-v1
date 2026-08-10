import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "api_agent" / "build_weekly_calibration_context.py"


class WeeklyExperimentContextTest(unittest.TestCase):
    def test_compacts_active_and_newly_matured_experiment_learning(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            weekly = root / "weekly.json"
            freeze = root / "freeze.json"
            daily = root / "daily"
            registry = root / "registry.json"
            outcomes = root / "outcomes"
            output = root / "context.json"
            daily.mkdir()
            outcomes.mkdir()
            weekly.write_text(json.dumps({"contract": "WEEKLY_CAPTURE_PACK_TEST"}))
            freeze.write_text(json.dumps({
                "iso_year": 2026,
                "iso_week": 32,
                "window_start_utc": "2026-08-03T00:00:00Z",
                "window_end_utc": "2026-08-10T00:00:00Z",
                "freeze_sha256": "abc123",
            }))
            registry.write_text(json.dumps({
                "contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1",
                "generated_at_utc": "2026-08-06T03:00:00Z",
                "candidate_count": 2,
                "state_counts": {"WAITING_FOR_MATURITY": 1, "WAITING_FOR_MAPPING": 1},
                "candidates": [
                    {
                        "candidate_id": "EC-active",
                        "title": "Active experiment",
                        "kind": "FORECAST_TEST",
                        "state": "WAITING_FOR_MATURITY",
                        "created_at_utc": "2026-08-04T10:00:00Z",
                        "forecast_ids": ["EXP-FC-1"],
                    },
                    {
                        "candidate_id": "EC-latent",
                        "title": "Odd dormant sensor",
                        "kind": "SENSOR_COMBINATION",
                        "state": "WAITING_FOR_MAPPING",
                        "created_at_utc": "2026-08-04T10:00:00Z",
                        "forecast_ids": [],
                    },
                ],
            }))
            (outcomes / "EXP-FC-1.json").write_text(json.dumps({
                "contract": "MATURED_OUTCOME_v2",
                "forecast_id": "EXP-FC-1",
                "status": "MATURED",
                "result": "HIT",
                "return_pct": 2.4,
                "evidence_lag_hours": 0.5,
                "created_at_utc": "2026-08-07T10:00:00Z",
            }))
            subprocess.run([
                sys.executable,
                str(SCRIPT),
                "--weekly-pointer", str(weekly),
                "--daily-output-root", str(daily),
                "--freeze-file", str(freeze),
                "--experiment-registry", str(registry),
                "--experiment-outcome-root", str(outcomes),
                "--output", str(output),
            ], check=True)
            value = json.loads(output.read_text())
            self.assertEqual(value["contract"], "WEEKLY_API_CALIBRATION_CONTEXT_v6")
            learning = value["experiment_learning"]
            self.assertEqual(learning["candidate_count"], 2)
            self.assertEqual(learning["latent_candidate_count"], 1)
            self.assertEqual(len(learning["active_candidates"]), 1)
            self.assertEqual(learning["active_candidates"][0]["candidate_id"], "EC-active")
            self.assertEqual(len(learning["new_matured_outcomes"]), 1)
            self.assertEqual(learning["new_matured_outcomes"][0]["result"], "HIT")


if __name__ == "__main__":
    unittest.main()
