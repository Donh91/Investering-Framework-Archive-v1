from __future__ import annotations

import unittest

from scripts.cycle_navigator.range_skill_shadow_v1 import evaluate_week


def sample() -> dict:
    return dict(
        target_iso_year=2026, target_iso_week=39, asset="BTC",
        forecast_quote="USDT", realized_quote="USDT",
        first_issued_at_utc="2026-09-20T23:00:00Z",
        prior_close_first_known_at_utc="2026-09-20T22:00:00Z",
        realized_final_at_utc="2026-09-28T00:15:00Z",
        realized_hours=168, realized_final=True,
        forecast_source_sha256="a" * 64, realized_source_sha256="b" * 64,
        first_issue_commit_sha="c" * 40,
        prior_week_close=100.0, cn_low=90.0, cn_high=120.0,
        realized_low=92.0, realized_high=118.0,
    )


class RangeSkillShadowTests(unittest.TestCase):
    def test_cn_can_outperform_same_width_placement_in_fixture(self) -> None:
        outcome = evaluate_week(sample())
        self.assertEqual(outcome["claim_class"], "PIT_CLOCK_COMPATIBLE_SOURCE_UNVERIFIED")
        self.assertTrue(outcome["cn"]["both_extrema_contained"])
        self.assertFalse(outcome["matched_width_naive"]["both_extrema_contained"])
        self.assertFalse(outcome["naive_is_independent_width_forecast"])
        self.assertFalse(outcome["scientific_admission"])

    def test_late_issue_is_never_relabelled_full_week_prospective(self) -> None:
        row = sample()
        row["first_issued_at_utc"] = "2026-09-21T08:00:00Z"
        self.assertEqual(evaluate_week(row)["claim_class"], "DESCRIPTIVE_ONLY_LATE_ISSUE")

    def test_quote_mismatch_fails_closed(self) -> None:
        row = sample()
        row["forecast_quote"] = "USD"
        with self.assertRaisesRegex(ValueError, "EXACT_QUOTE_MATCH_REQUIRED"):
            evaluate_week(row)

    def test_incomplete_week_fails_closed(self) -> None:
        row = sample()
        row["realized_hours"] = 167
        with self.assertRaisesRegex(ValueError, "FULL_168H_FINAL_SOURCE_REQUIRED"):
            evaluate_week(row)

    def test_nonfinite_boolean_and_nonpositive_prices_fail_closed(self) -> None:
        for value in (float("nan"), float("inf"), True, 0):
            row = sample()
            row["cn_low"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate_week(row)

    def test_invalid_source_identity_fails_closed(self) -> None:
        row = sample()
        row["first_issue_commit_sha"] = "unknown"
        with self.assertRaisesRegex(ValueError, "IMMUTABLE_HASH_REQUIRED"):
            evaluate_week(row)

    def test_future_known_prior_close_fails_closed(self) -> None:
        row = sample()
        row["prior_close_first_known_at_utc"] = "2026-09-21T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "PRIOR_CLOSE_NOT_KNOWN_AT_ISSUE"):
            evaluate_week(row)

    def test_unmatured_outcome_fails_closed(self) -> None:
        row = sample()
        row["realized_final_at_utc"] = "2026-09-24T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "REALIZED_WEEK_NOT_MATURE"):
            evaluate_week(row)

    def test_missing_source_clock_and_reversed_band_fail_closed(self) -> None:
        row = sample()
        del row["first_issued_at_utc"]
        with self.assertRaisesRegex(ValueError, "OFFSET_TIMESTAMP_REQUIRED"):
            evaluate_week(row)
        row = sample()
        row["cn_low"] = 130
        with self.assertRaisesRegex(ValueError, "ORDERED_BAND_REQUIRED"):
            evaluate_week(row)

    def test_alpha_is_explicit_and_not_probabilistic_calibration(self) -> None:
        for alpha in (-1, 0, 1, float("nan"), True):
            with self.subTest(alpha=alpha), self.assertRaisesRegex(ValueError, "ALPHA_OUT_OF_RANGE"):
                evaluate_week(sample(), alpha=alpha)

    def test_metrics_are_descriptive_and_never_trading_authority(self) -> None:
        outcome = evaluate_week(sample())
        self.assertGreaterEqual(outcome["cn"]["jaccard"], 0)
        self.assertLessEqual(outcome["cn"]["jaccard"], 1)
        self.assertEqual(
            outcome["loss_kind"], "CUSTOM_EXTREME_ENVELOPE_NOT_PROPER_QUANTILE_SCORE")
        self.assertFalse(outcome["portfolio_authority"])


if __name__ == "__main__":
    unittest.main()
