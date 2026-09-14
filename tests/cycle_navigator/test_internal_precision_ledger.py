from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "internal_precision_ledger",
    ROOT / "scripts/cycle_navigator/internal_precision_ledger.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


class InternalPrecisionLedgerTests(unittest.TestCase):
    def test_family_scores_cover_core_cn_dimensions(self):
        rows = [
            {"parameter_id": "ethbtc_condition", "score": 100},
            {"parameter_id": "breadth_condition", "score": 100},
            {"parameter_id": "structural_call_1", "score": 100},
            {"parameter_id": "structural_call_2", "score": 100},
            {"parameter_id": "structural_call_3", "score": 100},
            {"parameter_id": "structural_call_4", "score": 50},
            {"parameter_id": "structural_call_5", "score": 100},
        ]
        scores = MOD.build_family_scores(rows)
        self.assertEqual(scores["regime"], 100.0)
        self.assertEqual(scores["ethbtc"], 100.0)
        self.assertEqual(scores["breadth"], 100.0)
        self.assertEqual(scores["rotation"], 75.0)
        self.assertEqual(scores["altseason"], 100.0)
        self.assertIsNone(scores["btc_range"])
        self.assertIsNone(scores["intraday_day_1_2"])

    def test_forecast_inventory_freezes_intraday_and_long_horizons(self):
        machine = {
            "forecast_freeze": {
                "btc_range_low": 70,
                "btc_range_high": 80,
                "eth_range_low": None,
                "eth_range_high": None,
                "ethbtc_condition": "ETH/BTC non-negative",
                "breadth_condition": "Breadth remains weak",
                "structural_calls": ["regime", "ethbtc", "rotation", "no transmission", "altseason inactive"],
                "intraday_map": {"day_1_2": "pullback", "day_3_4": "UNAVAILABLE", "day_5_7": "stabilize"},
            },
            "base_case_this_week": "volatile consolidation",
            "base_case_2_3_weeks": "selective rotation",
            "base_case_4_8_weeks": "conditional expansion",
        }
        rows = MOD.freeze_inventory_rows(machine, 27, 2026, 39)
        ids = [row["parameter_id"] for row in rows]
        self.assertIn("btc_range", ids)
        self.assertNotIn("eth_range", ids)
        self.assertIn("intraday_day_1_2", ids)
        self.assertNotIn("intraday_day_3_4", ids)
        self.assertIn("intraday_day_5_7", ids)
        self.assertIn("base_case_2_3_weeks", ids)
        self.assertIn("base_case_4_8_weeks", ids)

    def test_precision_box_is_compact(self):
        evaluation = {
            "weekly_structural_score": 90.0,
            "family_scores": {
                "regime": 100.0, "ethbtc": 100.0, "breadth": 100.0,
                "rotation": 75.0, "altseason": 100.0,
                "btc_range": None, "eth_range": None,
                "intraday_day_1_2": None, "intraday_day_3_4": None, "intraday_day_5_7": None,
            },
            "coverage": {"accounted": 7, "expected": 7, "pct": 100.0},
            "self_critique": ["miss one", "miss two"],
        }
        box = MOD.precision_box(37, evaluation, 10, "PUBLIC_FREEZE_ONLY_PRE_ACTIVATION")
        self.assertLessEqual(len(box.splitlines()), 8)
        self.assertIn("Weekly 90%", box)
        self.assertIn("Rotation 75%", box)
        self.assertIn("hindsight edits 0", box)

    def test_immutable_write_fails_on_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "frozen.json"
            self.assertEqual(MOD.write_immutable_json(path, {"a": 1}), "CREATED")
            self.assertEqual(MOD.write_immutable_json(path, {"a": 1}), "UNCHANGED")
            with self.assertRaises(SystemExit):
                MOD.write_immutable_json(path, {"a": 2})


if __name__ == "__main__":
    unittest.main()
