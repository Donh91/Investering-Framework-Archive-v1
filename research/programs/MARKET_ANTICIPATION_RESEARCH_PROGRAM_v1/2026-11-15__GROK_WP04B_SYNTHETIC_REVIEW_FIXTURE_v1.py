#!/usr/bin/env python3
"""Research-only synthetic review controls for Bridge Grok #195.
These tests demonstrate failure classes in excerpts of the reported scripts.
They DO NOT import Grok's code, replay public raw data, or verify historical counts.
No production writer, model, portfolio, API or trade authority.
Run: python 2026-11-15__GROK_WP04B_SYNTHETIC_REVIEW_FIXTURE_v1.py
"""
import unittest

import numpy as np
import pandas as pd


class ClockReviewFixtures(unittest.TestCase):
    def test_equal_release_dates_need_value_date_tiebreak(self):
        # Adversarial large tie group: same release but different value dates.
        data = pd.DataFrame(
            {
                "value_date": pd.date_range("2026-01-01", periods=100),
                "available_at": [pd.Timestamp("2026-05-26")] * 100,
                "z": np.arange(100),
            }
        )
        shuffled = data.sample(frac=1, random_state=0).reset_index(drop=True)
        unsafe = int(
            shuffled.sort_values("available_at")
            .groupby("available_at").last()["z"].iloc[0]
        )
        fixed = int(
            shuffled.sort_values(
                ["available_at", "value_date"], kind="stable"
            ).groupby("available_at").last()["z"].iloc[0]
        )
        self.assertEqual(fixed, 99)
        self.assertNotEqual(unsafe, fixed)

    def test_dollar_only_publication_needs_union_of_source_days(self):
        release = pd.Timestamp("2026-05-26")
        macro = pd.DataFrame(
            {"avail_ust_vix": [pd.NaT], "avail_dtw": [release]},
            index=[pd.Timestamp("2026-05-22")],
        )
        days = pd.date_range("2026-05-24", "2026-05-29")
        legacy = pd.Series(
            days.isin(pd.DatetimeIndex(macro["avail_ust_vix"].dropna().unique())),
            index=days,
        )
        fixed = pd.Series(False, index=days)
        for k in ("avail_ust_vix", "avail_dtw"):
            fixed |= pd.Series(
                days.isin(pd.DatetimeIndex(macro[k].dropna().unique())),
                index=days,
            )
        self.assertFalse(bool(legacy.loc[release]))
        self.assertTrue(bool(fixed.loc[release]))

    def test_eight_hour_funding_is_not_an_hourly_2160_window(self):
        # 2160 funding settlement observations span 720d at 8h spacing.
        # 2160 hourly observations span 90d. These are not same contract.
        self.assertEqual(2160 * 8 // 24, 720)
        self.assertEqual(2160 // 24, 90)
        self.assertNotEqual(2160 * 8 // 24, 2160 // 24)

    def test_cluster_24_hours_does_not_independize_72_hour_labels(self):
        # Two accepted events separated by 25h have 47h of common horizon.
        self.assertGreater(25, 24)
        self.assertEqual(72 - 25, 47)
        self.assertGreater(72 - 25, 0)


if __name__ == "__main__":
    unittest.main()
