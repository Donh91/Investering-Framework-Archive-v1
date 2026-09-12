import importlib.util
import json
import math
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "factor_test_at_hyp_0019.py"


def load_module():
    spec = importlib.util.spec_from_file_location("factor_test_at_hyp_0019", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FactorTest0019Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def fixture_rows(self):
        rows = []
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        for symbol, base in (("BTC", 100000.0), ("ETH", 3500.0)):
            for episode in range(2):
                episode_start = start + timedelta(days=episode * 40)
                price = base * (1.0 + episode * 0.1)
                for index in range(100):
                    score = 50.0 + 20.0 * math.sin(index / 8.0) + (5.0 if symbol == "BTC" else -3.0)
                    price *= 1.0 + (0.0005 * (score - 50.0) / 50.0) + 0.0001 * math.sin(index)
                    rows.append({
                        "classification": "Neutral",
                        "score": score,
                        "real_price": price,
                        "symbol": symbol,
                        "timestamp": (episode_start + timedelta(hours=index)).isoformat().replace("+00:00", "Z"),
                    })
        return rows

    def write_fixture(self, directory: Path) -> Path:
        path = directory / "fixture.jsonl"
        path.write_text("\n".join(json.dumps(row) for row in self.fixture_rows()) + "\n")
        return path

    def test_pre_registered_design_is_deterministic_and_research_only(self):
        with tempfile.TemporaryDirectory() as td:
            report = self.mod.run(self.write_fixture(Path(td)))
        self.assertEqual(report["experiment_id"], "AT-E3-0019")
        self.assertEqual(report["theory_id"], "AT-HYP-0019")
        self.assertEqual(report["trial_accounting"]["proposal_trial_n"], 2)
        self.assertEqual(report["pre_registered_design"]["transforms"], ["RAW", "ROLLING_PERCENTILE", "ZSCORE", "DISTANCE_FROM_EXTREMA"])
        self.assertFalse(report["authority"]["portfolio_execution"])
        self.assertFalse(report["adjudication"]["promotion_authorized"])

    def test_all_transforms_are_right_truncation_clean(self):
        with tempfile.TemporaryDirectory() as td:
            report = self.mod.run(self.write_fixture(Path(td)))
        self.assertTrue(report["temporal_integrity"]["all_transforms_clean"])
        self.assertTrue(all(report["temporal_integrity"]["right_truncation_invariance"].values()))

    def test_large_timestamp_gap_creates_separate_segments(self):
        with tempfile.TemporaryDirectory() as td:
            report = self.mod.run(self.write_fixture(Path(td)))
        self.assertEqual(report["data_summary"]["segments_by_symbol"], {"BTC": 2, "ETH": 2})

    def test_oos_rows_exist_for_both_symbols(self):
        with tempfile.TemporaryDirectory() as td:
            report = self.mod.run(self.write_fixture(Path(td)))
        self.assertGreaterEqual(report["data_summary"]["oos_rows_by_symbol"]["BTC"], self.mod.MIN_TEST_ROWS_PER_SYMBOL)
        self.assertGreaterEqual(report["data_summary"]["oos_rows_by_symbol"]["ETH"], self.mod.MIN_TEST_ROWS_PER_SYMBOL)

    def test_naive_timestamp_fails_closed(self):
        rows = self.fixture_rows()
        rows[0]["timestamp"] = "2025-01-01T00:00:00"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
            with self.assertRaises(self.mod.FactorTestError):
                self.mod.run(path)

    def test_result_contains_no_raw_row_export(self):
        with tempfile.TemporaryDirectory() as td:
            report = self.mod.run(self.write_fixture(Path(td)))
        encoded = json.dumps(report)
        self.assertNotIn('"classification"', encoded)
        self.assertFalse(report["source_binding"]["raw_values_exported_to_public_result"])


if __name__ == "__main__":
    unittest.main()
