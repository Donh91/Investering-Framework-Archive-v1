import unittest
from scripts.research.cycle_navigator_calibration_controller import _coverage_v2, evaluate_v2_freezes


def row(window="weekly", asset="BTC", clock=1795427178, status="FROZEN_PROSPECTIVE"):
    return {"contract": "CN_FORWARD_RANGE_FREEZE_v2", "forecast_week": "2026-W48",
            "window": window, "asset": asset, "generated_unix": clock,
            "status": status, "forecast_low": 1.0, "forecast_high": 2.0}


class TestLiveLedger(unittest.TestCase):
    def test_windows_not_rows_or_assets(self):
        rows = [row(), row(asset="ETH"), row("day_1_2"), row("day_3_4"), row("day_5_7")]
        cov = _coverage_v2(rows)
        self.assertEqual(cov["raw_rows"], 5)
        self.assertEqual(cov["unique_recorded_freeze_clocks"], 1)
        self.assertEqual(cov["max_nonoverlapping_calendar_windows"], 3)
        self.assertEqual(cov["labelled_prospective_max_nonoverlapping_windows"], 3)
        self.assertFalse(cov["independence_attested"])

    def test_recovered_without_clock_separate(self):
        cov = _coverage_v2([row(clock=None, status="RECOVERED_FROM_IMMUTABLE_PROSPECTIVE_PUBLICATION")])
        self.assertEqual(cov["missing_freeze_clock_rows"], 1)
        self.assertEqual(cov["unique_recorded_freeze_clocks"], 0)
        self.assertEqual(cov["labelled_prospective_rows"], 0)

    def test_missing_clock_and_invalid_window_fail_closed(self):
        for bad in (row(clock=None), row(window="unknown"), row(clock=True)):
            with self.assertRaises(ValueError):
                _coverage_v2([bad])

    def test_freeze_never_promotes_injected_outcome(self):
        policy = {"research_escalation_floors": {"minimum_verified_rows_for_review": 1,
                  "minimum_verified_rows_for_persistent_pattern": 1, "recent_comparison_window_rows": 1}}
        injected = dict(row(), actual_low=1, actual_high=2, actual_verification_status="VERIFIED")
        result = evaluate_v2_freezes(policy, [injected])
        self.assertEqual(result["eligible_verified_row_n"], 0)
        self.assertEqual(result["selected_action"], "CONTINUE_CALIBRATION")
        self.assertFalse(result["canonical_effect"])


if __name__ == "__main__":
    unittest.main()
