from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.cycle_navigator.deterministic_range_baseline import build_baseline, score_baseline


def weekly_pack(year: int, week: int, btc: tuple[float, float, float, float], eth: tuple[float, float, float, float]) -> dict:
    def row(values):
        o, h, l, c = values
        return {"week_range": {"open": o, "high": h, "low": l, "close": c}}
    return {
        "contract": "WEEKLY_RAW_CALIBRATION_PACK_v3",
        "iso_year": year,
        "iso_week": week,
        "readiness": "READY",
        "hourly_gap_diagnostics": {"observed_hours": 168},
        "hourly_sequence": {"btc": row(btc), "eth": row(eth)},
    }


class DeterministicRangeBaselineTests(unittest.TestCase):
    def fixture_repo(self, root: Path) -> None:
        packs = {
            35: weekly_pack(2026, 35, (100, 110, 95, 105), (50, 55, 46, 52)),
            36: weekly_pack(2026, 36, (105, 115.5, 99.75, 110), (52, 57.2, 49.4, 54)),
            37: weekly_pack(2026, 37, (110, 121, 104.5, 115), (54, 59.4, 51.3, 56)),
            38: weekly_pack(2026, 38, (115, 126.5, 109.25, 120), (56, 61.6, 53.2, 58)),
        }
        for week, value in packs.items():
            path = root / f"03_DAILY_CAPTURE_LOGS/weekly/2026/W{week:02d}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value))

    def test_baseline_uses_only_prior_complete_weeks_and_is_independent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture_repo(root)
            out = build_baseline(root, target_year=2026, target_week=39)
            self.assertEqual(out["contract"], "CN_DETERMINISTIC_RANGE_BASELINE_v1")
            self.assertEqual(out["source_weeks"], ["2026-W35", "2026-W36", "2026-W37", "2026-W38"])
            self.assertEqual(out["lookback_weeks_used"], 4)
            self.assertTrue(out["independence"]["generated_without_cycle_navigator_model_output"])
            self.assertFalse(out["independence"]["llm_forecast_input"])
            self.assertFalse(out["authority"]["official_range_override"])
            self.assertEqual(out["assets"]["BTC"]["anchor_price"], 120)
            self.assertAlmostEqual(out["assets"]["BTC"]["median_up_excursion_pct"], 10.0)
            self.assertAlmostEqual(out["assets"]["BTC"]["median_down_excursion_pct"], 5.0)
            self.assertAlmostEqual(out["assets"]["BTC"]["low"], 114.0)
            self.assertAlmostEqual(out["assets"]["BTC"]["high"], 132.0)
            self.assertTrue(all(not row["source_path"].startswith("/") for row in out["assets"]["BTC"]["samples"]))

    def test_scoring_reports_containment_and_width_without_composite_score(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture_repo(root)
            baseline = build_baseline(root, target_year=2026, target_week=39)
            actual = weekly_pack(2026, 39, (120, 130, 115, 125), (58, 63, 55, 60))
            score = score_baseline(baseline, actual)
            self.assertEqual(score["contract"], "CN_DETERMINISTIC_RANGE_BASELINE_SCORE_v1")
            self.assertTrue(score["assets"]["BTC"]["full_range_contained"])
            self.assertEqual(score["assets"]["BTC"]["lower_miss_pct_of_actual_open"], 0.0)
            self.assertEqual(score["assets"]["BTC"]["upper_miss_pct_of_actual_open"], 0.0)
            self.assertNotIn("accuracy", score)
            self.assertFalse(score["authority"]["automatic_promotion"])

    def test_target_week_cannot_leak_into_its_own_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture_repo(root)
            target = root / "03_DAILY_CAPTURE_LOGS/weekly/2026/W39.json"
            target.write_text(json.dumps(weekly_pack(2026, 39, (120, 240, 60, 180), (58, 116, 29, 87))))
            out = build_baseline(root, target_year=2026, target_week=39)
            self.assertNotIn("2026-W39", out["source_weeks"])
            self.assertLess(out["assets"]["BTC"]["high"], 200)

    def test_mismatched_actual_week_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture_repo(root)
            baseline = build_baseline(root, target_year=2026, target_week=39)
            with self.assertRaisesRegex(ValueError, "baseline_actual_week_mismatch"):
                score_baseline(baseline, weekly_pack(2026, 40, (1, 2, 0.5, 1.5), (1, 2, 0.5, 1.5)))


if __name__ == "__main__":
    unittest.main()
