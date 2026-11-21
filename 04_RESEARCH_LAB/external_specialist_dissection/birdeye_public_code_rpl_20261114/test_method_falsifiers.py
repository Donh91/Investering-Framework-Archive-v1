"""Synthetic adversarial controls. Passing these does NOT establish alpha."""
import unittest
from method_falsifiers import (
    coverage_safe_hull, liquidity_path_diagnostics, first_known_gate,
    full_exit_capacity_gate,
)


class TestBirdeyeMethodFalsifiers(unittest.TestCase):
    def test_unknown_high_impact_score_cannot_be_safe(self):
        x = coverage_safe_hull([("activity", 0.2, 100, False), ("security", 0.8, None, True)])
        self.assertEqual(x["observed_mean"], 100)
        self.assertEqual(x["lower_bound"], 20)
        self.assertEqual(x["upper_bound"], 100)
        self.assertEqual(x["status"], "UNKNOWN_CRITICAL")

    def test_full_coverage_has_no_interval(self):
        x = coverage_safe_hull([("one", 0.5, 80, False), ("two", 0.5, 40, True)])
        self.assertEqual((x["lower_bound"], x["upper_bound"]), (60, 60))
        self.assertEqual(x["status"], "COMPLETE")

    def test_all_unknown_is_not_zero_observed(self):
        x = coverage_safe_hull([("security", 1, None, True)])
        self.assertIsNone(x["observed_mean"])
        self.assertEqual(x["upper_bound"], 100)

    def test_nan_cannot_pass(self):
        with self.assertRaises(ValueError):
            coverage_safe_hull([("bad", 1, float("nan"), True)])

    def test_monotonic_liquidity_increase_is_not_drawdown(self):
        x = liquidity_path_diagnostics([100, 150, 200])
        self.assertEqual(x["unordered_range_pct"], 50)
        self.assertEqual(x["temporal_max_drawdown_pct"], 0)
        self.assertEqual(x["current_from_peak_pct"], 0)

    def test_falling_liquidity_is_real_drawdown(self):
        x = liquidity_path_diagnostics([200, 150, 100])
        self.assertEqual(x["temporal_max_drawdown_pct"], 50)

    def test_recovery_uses_temporal_peak(self):
        x = liquidity_path_diagnostics([100, 200, 150, 190])
        self.assertEqual(x["temporal_max_drawdown_pct"], 25)
        self.assertEqual(x["current_from_peak_pct"], 5)

    def test_late_first_seen_prevents_retro_claim(self):
        self.assertEqual(first_known_gate(1000, 1000, 1200, 1100), "NOT_KNOWN_AT_CUTOFF")

    def test_missing_first_seen_abstains(self):
        self.assertEqual(first_known_gate(1000, 1000, None, 1100), "UNKNOWN_CLOCK")

    def test_as_of_data_is_eligible(self):
        self.assertEqual(first_known_gate(1000, 1010, 1020, 1100), "ELIGIBLE_AS_OF")

    def test_limited_exit_rejects_paper_ath(self):
        self.assertEqual(full_exit_capacity_gate(1000, 100, 1000, 1020), "CAPACITY_INSUFFICIENT")

    def test_stale_exit_quote_abstains(self):
        self.assertEqual(full_exit_capacity_gate(1000, 1000, 1000, 1200), "UNKNOWN_STALE_QUOTE")

    def test_missing_exit_route_abstains(self):
        self.assertEqual(full_exit_capacity_gate(1000, None, None, 1200), "UNKNOWN_ROUTE")


if __name__ == "__main__":
    unittest.main()
