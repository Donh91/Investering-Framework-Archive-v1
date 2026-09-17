import csv
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.learning.compass_outcomes import action_quality, mature_one


class CompassOutcomeTest(unittest.TestCase):
    def freeze(self):
        return {
            "contract": "OFFICIAL_DAILY_COMPASS_v1",
            "compass_id": "CMP-20260916-test",
            "compass_sha256": "frozen-sha",
            "issued_at_utc": "2026-09-16T12:00:00Z",
            "market_reference": {"btc_usdt": 100.0, "eth_usdt": 50.0, "ethbtc": 0.5},
            "horizons": {
                "NEXT_12H": {
                    "expected_direction": "DOWN",
                    "action_posture": "HOLD",
                    "eta": "0-12h",
                    "confirmation_trigger": {"type": "ACTION_STATE", "states": ["PREPARE"]},
                    "invalidation_trigger": {"type": "ACTION_STATE", "states": ["HOLD_DEFENSIVE_WAIT"]},
                },
                "NEXT_1_3D": {"expected_direction": "MIXED", "action_posture": "WAIT", "eta": "24-72h"},
                "NEXT_5_7D": {"expected_direction": "SIDEWAYS", "action_posture": "PREPARE", "eta": "120-168h"},
            },
            "evidence_snapshot": {"selected_features": []},
        }

    def write_hourly(self, root: Path):
        path = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-17.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "btc_close", "eth_close", "ethbtc_close"])
            writer.writeheader()
            writer.writerow({"timestamp_utc": "2026-09-17T00:00:00Z", "btc_close": "95", "eth_close": "47", "ethbtc_close": "0.4947"})

    def test_cannot_score_before_maturity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(json.dumps(self.freeze()))
            original = freeze_path.read_bytes()
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 16, 23, 59, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertIsNone(result)
            self.assertEqual(original, freeze_path.read_bytes())

    def test_mature_outcome_is_separate_and_forecast_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(json.dumps(self.freeze()))
            original = freeze_path.read_bytes()
            self.write_hourly(root)
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 17, 0, 30, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "MATURED")
            outcome_path = root / result["path"]
            outcome = json.loads(outcome_path.read_text())
            self.assertEqual(outcome["direction_accuracy"]["btc"]["result"], "CORRECT")
            self.assertEqual(outcome["action_utility"]["action"], "HOLD")
            self.assertEqual(original, freeze_path.read_bytes())

    def test_action_quality_is_horizon_action_not_hardwired_to_12h(self):
        self.assertEqual(action_quality("WAIT", -2.0, -3.0)["action"], "WAIT")
        self.assertEqual(action_quality("PREPARE", 2.0, -1.0)["action"], "PREPARE")

    def test_missing_target_observation_stays_pending_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(json.dumps(self.freeze()))
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 17, 1, 0, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            self.assertEqual(result["status"], "PENDING_TARGET_EVIDENCE")
            self.assertFalse((root / result["path"]).exists())

    def test_excursion_stops_at_frozen_horizon(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            freeze_path = root / "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-test.json"
            freeze_path.parent.mkdir(parents=True, exist_ok=True)
            freeze_path.write_text(json.dumps(self.freeze()))
            path = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-17.csv"
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "btc_close", "eth_close", "ethbtc_close"])
                writer.writeheader()
                writer.writerow({"timestamp_utc": "2026-09-17T00:00:00Z", "btc_close": "95", "eth_close": "47", "ethbtc_close": "0.4947"})
                writer.writerow({"timestamp_utc": "2026-09-17T01:00:00Z", "btc_close": "150", "eth_close": "75", "ethbtc_close": "0.5"})
            result = mature_one(root, freeze_path, "12h", datetime(2026, 9, 17, 2, 0, tzinfo=timezone.utc), Path("04_MARKET_LEARNING/handlekompas/official"))
            outcome = json.loads((root / result["path"]).read_text())
            self.assertAlmostEqual(outcome["realized"]["btc_mfe_pct"], -5.0)


if __name__ == "__main__":
    unittest.main()
