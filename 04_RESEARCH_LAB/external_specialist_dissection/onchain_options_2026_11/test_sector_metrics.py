"""Synthetic negative controls for REA options metrics. No live-source or edge proof."""
import unittest
from datetime import date, timedelta

from sector_metrics import premium_hhi, weekly_comparison

CUTOFF = "2026-11-01T00:00:00Z"
END = date(2026, 10, 31)


def cohort():
    out = []
    for i in range(14):
        d = END - timedelta(days=13-i)
        out.append({
            "venue": "Demo",
            "day_utc": d.isoformat(),
            "source_id": "SYNTHETIC",
            "source_available_at_utc": f"{(d + timedelta(days=1)).isoformat()}T00:00:00Z",
            "period_final": True,
            "options_only_verified": True,
            "premium_usd": 100 if i < 7 else 200,
            "notional_usd": 1000,
            "fee_scope": "OPTIONS_ONLY",
            "fees_usd": 10,
        })
    return out


class MetricTests(unittest.TestCase):
    def test_weekly_growth_and_ratio(self):
        x = weekly_comparison(cohort(), "Demo", END.isoformat(), CUTOFF)
        self.assertEqual(x["status"], "DESCRIPTIVE_ONLY")
        self.assertEqual(x["current_7d_premium_usd"], 1400)
        self.assertEqual(x["previous_7d_premium_usd"], 700)
        self.assertEqual(x["premium_growth_7d_vs_prior_7d"], 1)
        self.assertEqual(x["premium_to_notional"], 0.2)
        self.assertEqual(x["options_only_fees_to_premium"], 0.05)
        self.assertIsNone(x["tokenholder_capture"])
        self.assertEqual(x["predictive_edge"], "UNTESTED")

    def test_missing_day_is_not_zero(self):
        x = weekly_comparison(cohort()[:-1], "Demo", END.isoformat(), CUTOFF)
        self.assertEqual(x["status"], "UNKNOWN")
        self.assertEqual(x["reason"], "INCOMPLETE_14_DAY_COHORT")

    def test_duplicate_day_is_rejected(self):
        rows = cohort()
        rows.append(dict(rows[-1]))
        x = weekly_comparison(rows, "Demo", END.isoformat(), CUTOFF)
        self.assertEqual(x["reason"], "DUPLICATE_VENUE_DAY")

    def test_future_known_at_rejected(self):
        rows = cohort()
        rows[3]["source_available_at_utc"] = "2026-11-02T00:00:00Z"
        x = weekly_comparison(rows, "Demo", END.isoformat(), CUTOFF)
        self.assertEqual(x["reason"], "FUTURE_AVAILABLE_DATA")

    def test_incomplete_current_period_rejected(self):
        rows = cohort()
        rows[-1]["period_final"] = False
        x = weekly_comparison(rows, "Demo", END.isoformat(), CUTOFF)
        self.assertEqual(x["reason"], "IN_PROGRESS_PERIOD")

    def test_mixed_product_volume_rejected(self):
        rows = cohort()
        rows[-1]["options_only_verified"] = False
        x = weekly_comparison(rows, "Demo", END.isoformat(), CUTOFF)
        self.assertEqual(x["reason"], "OPTIONS_ONLY_UNVERIFIED")

    def test_fee_scope_mismatch_not_fabricated(self):
        rows = cohort()
        rows[-1]["fee_scope"] = "ALL_MARKETS"
        x = weekly_comparison(rows, "Demo", END.isoformat(), CUTOFF)
        self.assertEqual(x["status"], "DESCRIPTIVE_ONLY")
        self.assertIsNone(x["options_only_fees_to_premium"])

    def test_zero_prior_period_does_not_invent_growth(self):
        rows = cohort()
        for row in rows[:7]:
            row["premium_usd"] = 0
        x = weekly_comparison(rows, "Demo", END.isoformat(), CUTOFF)
        self.assertIsNone(x["premium_growth_7d_vs_prior_7d"])

    def test_concentration_with_complete_census(self):
        rows = [
            dict(cohort()[-1], venue="Demo", premium_usd=90),
            dict(cohort()[-1], venue="Other", premium_usd=10),
        ]
        x = premium_hhi(rows, END.isoformat(), CUTOFF, {"Demo", "Other"})
        self.assertEqual(x["status"], "DESCRIPTIVE_ONLY")
        self.assertAlmostEqual(x["premium_hhi"], 0.82)

    def test_concentration_requires_full_denominator(self):
        rows = [cohort()[-1]]
        x = premium_hhi(rows, END.isoformat(), CUTOFF, {"Demo", "Other"})
        self.assertEqual(x["reason"], "INCOMPLETE_VENUE_CENSUS")


if __name__ == "__main__":
    unittest.main()
