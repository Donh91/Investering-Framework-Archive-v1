#!/usr/bin/env python3
"""Deterministic negative/positive fixtures for RQS research-only diagnostics."""
import unittest
from datetime import datetime, timedelta, timezone
from scripts.research.rebound_quality_shadow import assess


def fixture(*, oi_trend=-8.0, remove_derivatives=False):
    t = datetime(2026, 10, 30, tzinfo=timezone.utc)
    # Prior peak -> meaningful drop, then a 3-hour bounce.
    btc = [100, 101, 100, 99, 98, 97, 96, 95, 95, 95, 95, 96, 96, 97, 98, 99]
    result = []
    for i, value in enumerate(btc):
        ts = t + timedelta(hours=i)
        result.append({
            "timestamp_utc": ts.isoformat().replace("+00:00", "Z"),
            "source_window_end_utc": (ts + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
            "btc_close": str(value), "btc_quote_volume": "1000",
            "btc_taker_buy_quote_volume": "550", "ethbtc_close": str(0.030 + 0.00001 * i),
            "btc_open_interest": str(1000 + oi_trend * i),
            "spot_status": "PASS", "derivatives_status": "FAIL" if remove_derivatives else "PASS",
        })
    return result


class ReboundQualityTest(unittest.TestCase):
    def test_candidate_is_research_only_and_not_short_covering_proof(self):
        rows = fixture()
        out = assess(rows, rows[-1]["source_window_end_utc"])
        self.assertEqual(out["status"], "REPLAY_CANDIDATE_RESEARCH_ONLY")
        self.assertTrue(out["evidence"]["candidate"])
        self.assertEqual(out["evidence"]["oi_pattern"], "PRICE_UP_OI_DOWN_SIDE_UNIDENTIFIED")
        self.assertIsNone(out["score_0_100"])
        self.assertFalse(out["short_covering_proven"])
        self.assertEqual(out["trade_permission"], "NONE")
        self.assertFalse(out["first_known_verified"])

    def test_leverage_pattern_not_a_bullish_signal(self):
        rows = fixture(oi_trend=8)
        out = assess(rows, rows[-1]["source_window_end_utc"])
        self.assertEqual(out["evidence"]["oi_pattern"], "PRICE_UP_OI_UP_LEVERAGE_POSSIBLE")
        self.assertIsNone(out["bull_trap_probability"])

    def test_missing_derivatives_do_not_become_zero(self):
        rows = fixture(remove_derivatives=True)
        out = assess(rows, rows[-1]["source_window_end_utc"])
        self.assertIsNone(out["evidence"]["btc_open_interest_last_3h_change_pct"])
        self.assertFalse(out["family_independence"]["DERIVATIVES_OI"])

    def test_future_bars_excluded_and_gap_denied(self):
        rows = fixture()
        before = assess(rows, "2026-10-30T15:00:00Z")
        self.assertEqual(before["reason"], "NEEDS_16_CONTIGUOUS_COMPLETED_HOURS")
        rows.pop(5)
        out = assess(rows, (datetime(2026, 10, 31, tzinfo=timezone.utc)).isoformat())
        self.assertEqual(out["reason"], "NEEDS_16_CONTIGUOUS_COMPLETED_HOURS")

    def test_conflicting_duplicate_denied(self):
        rows = fixture()
        dup = dict(rows[1]); dup["btc_close"] = "12345"
        with self.assertRaisesRegex(ValueError, "conflicting_duplicate_candle"):
            assess(rows + [dup], rows[-1]["source_window_end_utc"])

    def test_stale_denied(self):
        rows = fixture()
        result = assess(rows, "2026-10-31T10:00:00Z")
        self.assertEqual(result["reason"], "OWNER_DATA_STALE")

    def test_repeated_collection_end_is_not_duplicate_candle(self):
        rows = fixture()
        for r in rows:
            r["source_window_end_utc"] = "2026-10-30T16:00:00Z"
        out = assess(rows, "2026-10-30T16:00:00Z")
        self.assertEqual(out["status"], "REPLAY_CANDIDATE_RESEARCH_ONLY")

    def test_run_coverage_earlier_than_candle_end_fails(self):
        rows = fixture()
        rows[-1]["source_window_end_utc"] = "2026-10-30T13:00:00Z"
        with self.assertRaisesRegex(ValueError, "source_coverage_ends_before_candle"):
            assess(rows, "2026-10-30T16:00:00Z")

    def test_hourly_gap_cannot_be_filled(self):
        rows = fixture() + [{**fixture()[0], "timestamp_utc": "2026-10-30T19:00:00Z", "source_window_end_utc": "2026-10-30T20:00:00Z"}]
        out = assess(rows, "2026-10-30T20:00:00Z")
        self.assertEqual(out["reason"], "HOURLY_GAP_NO_FORWARD_FILL")


if __name__ == "__main__":
    unittest.main()
