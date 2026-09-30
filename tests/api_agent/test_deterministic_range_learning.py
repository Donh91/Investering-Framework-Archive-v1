from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent.build_weekly_calibration_context import load_deterministic_range_learning


def write_score(root: Path, year: int, week: int, *, btc_contained: bool = True) -> None:
    path = root / f"05_CYCLE_NAVIGATOR/range_baselines/scores/{year}/W{week:02d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "contract": "CN_DETERMINISTIC_RANGE_BASELINE_SCORE_v1",
        "target_iso_year": year,
        "target_iso_week": week,
        "baseline_sha256": f"sha-{year}-{week}",
        "assets": {
            "BTC": {"status": "SCORED", "full_range_contained": btc_contained, "predicted_width_pct_of_actual_open": 10.0, "midpoint_error_pct_of_actual_open": 1.0},
            "ETH": {"status": "SCORED", "full_range_contained": True, "predicted_width_pct_of_actual_open": 12.0, "midpoint_error_pct_of_actual_open": 1.5},
        },
    }))


class DeterministicRangeLearningTests(unittest.TestCase):
    def test_only_matured_scores_through_completed_week_are_loaded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_score(root, 2026, 38)
            write_score(root, 2026, 39, btc_contained=False)
            write_score(root, 2026, 40)  # future relative to completed W39
            out = load_deterministic_range_learning(root, 2026, 39)
            self.assertEqual(out["contract"], "MASTER_MONDAY_DETERMINISTIC_RANGE_LEARNING_v1")
            self.assertEqual(out["score_count"], 2)
            self.assertEqual(
                [(row["target_iso_year"], row["target_iso_week"]) for row in out["recent_scores"]],
                [(2026, 38), (2026, 39)],
            )
            self.assertEqual(out["current_completed_week_score"]["target_iso_week"], 39)
            self.assertFalse(out["current_completed_week_score"]["assets"]["BTC"]["full_range_contained"])
            self.assertEqual(out["authority"], "CALIBRATION_EVIDENCE_ONLY")

    def test_limit_keeps_most_recent_rows_without_auto_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for week in range(30, 40):
                write_score(root, 2026, week)
            out = load_deterministic_range_learning(root, 2026, 39, limit=3)
            self.assertEqual([row["target_iso_week"] for row in out["recent_scores"]], [37, 38, 39])
            self.assertTrue(any("Do not auto-promote" in rule for rule in out["rules"]))

    def test_missing_score_is_explicitly_unavailable(self):
        with tempfile.TemporaryDirectory() as td:
            out = load_deterministic_range_learning(Path(td), 2026, 39)
            self.assertEqual(out["score_count"], 0)
            self.assertEqual(out["current_completed_week_score"]["status"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
