from __future__ import annotations

import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.learning.shadow_compass_v2_outcomes import mature_one


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class ShadowCompassV2OutcomeTests(unittest.TestCase):
    def fixture(self, root: Path, *, direction: str = "UP") -> Path:
        issued = datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc)
        auto_rel = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json")
        write_json(root / auto_rel, {
            "contract": "AUTO_MARKET_STATE_PACKET_v1",
            "packet_sha256": "auto-sha",
            "normalized_state": {
                "live_market": {"btc_usdt": 100.0, "eth_usdt": 50.0, "ethbtc": 0.5},
            },
            "deltas_since_prior_auto_packet": {"btc_usdt": {"pct": 1.0}},
        })
        row = {
            "direction": direction,
            "confidence": "MEDIUM",
            "pullback_risk": "NORMAL",
            "transmission_state": "WEAK",
            "expected_path": "test",
            "supporting_evidence": ["x"],
            "contradicting_evidence": [],
            "missing_evidence": [],
            "falsification_conditions": ["y"],
        }
        forecast_rel = Path("04_MARKET_LEARNING/handlekompas/shadow_v2/forecasts/2026/09/01/SCV2-test.json")
        write_json(root / forecast_rel, {
            "contract": "SHADOW_COMPASS_V2_FORECAST_v1",
            "forecast_id": "SCV2-test",
            "forecast_sha256": "forecast-sha",
            "issued_at_utc": issued.isoformat().replace("+00:00", "Z"),
            "model_id": "gpt-6.1-sol",
            "reasoner_version": "test-v1",
            "source_bindings": {
                "auto_market_state": {"packet_path": auto_rel.as_posix(), "packet_sha256": "auto-sha"},
            },
            "model_output": {
                "horizons": {"12h": row, "72h": row, "168h": row},
            },
        })
        day = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-01.csv"
        day.parent.mkdir(parents=True, exist_ok=True)
        fields = ["timestamp_utc", "btc_close", "eth_close", "ethbtc_close"]
        rows = []
        for hour in range(15):
            t = issued + timedelta(hours=hour)
            rows.append({
                "timestamp_utc": t.isoformat().replace("+00:00", "Z"),
                "btc_close": 100.0 + hour,
                "eth_close": 50.0 + hour / 2,
                "ethbtc_close": 0.5,
            })
        with day.open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return root / forecast_rel

    def test_cannot_mature_before_horizon(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            forecast = self.fixture(root)
            out = mature_one(root, forecast, "12h", datetime(2026, 9, 1, 11, 59, tzinfo=timezone.utc))
            self.assertIsNone(out)

    def test_matured_shadow_uses_same_direction_tolerance_contract(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            forecast = self.fixture(root, direction="UP")
            out = mature_one(root, forecast, "12h", datetime(2026, 9, 1, 13, tzinfo=timezone.utc))
            self.assertEqual(out["status"], "MATURED")
            value = json.loads((root / out["path"]).read_text())
            self.assertEqual(value["contract"], "SHADOW_COMPASS_V2_OUTCOME_v1")
            self.assertEqual(value["scoring_contract"], "SHADOW_COMPASS_V2_SCORING_v1")
            self.assertTrue(value["direction_accuracy"]["btc"]["correct"])
            self.assertTrue(value["direction_accuracy"]["eth"]["correct"])
            self.assertEqual(value["comparison_metadata"]["sideways_tolerance_pct"], 1.5)
            self.assertFalse(value["authority"]["automatic_promotion"])
            self.assertEqual(value["baselines"]["persistence"]["prediction"], "UP")

    def test_sideways_uses_official_tolerance(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            forecast = self.fixture(root, direction="SIDEWAYS")
            # overwrite endpoint with +1%, within 12h ±1.5% tolerance
            day = root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09/2026-09-01.csv"
            rows = list(csv.DictReader(day.open()))
            rows[12]["btc_close"] = "101.0"
            rows[12]["eth_close"] = "50.5"
            with day.open("w", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            out = mature_one(root, forecast, "12h", datetime(2026, 9, 1, 13, tzinfo=timezone.utc))
            value = json.loads((root / out["path"]).read_text())
            self.assertTrue(value["direction_accuracy"]["btc"]["correct"])
            self.assertEqual(value["direction_accuracy"]["btc"]["sideways_tolerance_pct"], 1.5)

    def test_source_sha_mismatch_fails_without_writing_outcome(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            forecast = self.fixture(root)
            auto = root / "04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json"
            value = json.loads(auto.read_text())
            value["packet_sha256"] = "tampered"
            auto.write_text(json.dumps(value))
            out = mature_one(root, forecast, "12h", datetime(2026, 9, 1, 13, tzinfo=timezone.utc))
            self.assertEqual(out["status"], "SOURCE_INTEGRITY_FAIL")
            self.assertFalse((root / "04_MARKET_LEARNING/handlekompas/shadow_v2/outcomes").exists())


if __name__ == "__main__":
    unittest.main()
