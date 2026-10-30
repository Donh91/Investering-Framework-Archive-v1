#!/usr/bin/env python3
"""Deterministic negative/positive fixtures for RQS research-only diagnostics."""
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from scripts.research.rebound_quality_shadow import assess, replay_census, read_public_owner, due_only_outcome_preview


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
    def test_due_only_outcome_preview_no_future_lookahead(self):
        rows = fixture()
        asof = "2026-10-30T16:00:00Z"
        out = due_only_outcome_preview(rows, "2026-10-30T09:00:00Z", asof)
        self.assertEqual(out["horizons"]["6h"]["status"], "DESCRIPTIVE_EXPOST_ONLY")
        self.assertEqual(out["horizons"]["24h"]["status"], "PENDING_NOT_MATURE")
        self.assertEqual(out["horizons"]["72h"]["status"], "PENDING_NOT_MATURE")
        self.assertFalse(out["prediction_or_skill_scored"])
        self.assertFalse(out["first_known_verified"])
        self.assertEqual(out["trade_permission"], "NONE")

    def test_due_only_outcome_preview_missing_hour_fails_closed(self):
        rows = fixture()
        rows = [r for r in rows if r["timestamp_utc"] != "2026-10-30T11:00:00Z"]
        out = due_only_outcome_preview(rows, "2026-10-30T09:00:00Z",
                                       "2026-10-30T16:00:00Z")
        self.assertEqual(out["horizons"]["6h"]["status"],
                         "UNAVAILABLE_MISSING_OR_INVALID_HOURLY_SOURCE")
        self.assertIsNone(out["horizons"]["6h"]["btc_close_return_pct"])

    def test_due_only_outcome_preview_future_collection_ineligible(self):
        rows = fixture()
        rows[11]["source_window_end_utc"] = "2026-10-31T00:00:00Z"
        out = due_only_outcome_preview(rows, "2026-10-30T09:00:00Z",
                                       "2026-10-30T16:00:00Z")
        self.assertEqual(out["horizons"]["6h"]["status"],
                         "UNAVAILABLE_MISSING_OR_INVALID_HOURLY_SOURCE")

    def test_census_no_recycled_old_window_at_three_lagged_hours(self):
        rows = fixture()
        report = replay_census(rows, "2026-10-30T19:00:00Z")
        self.assertEqual(report["evaluated_cutoffs"], 168)
        self.assertEqual(report["eligible_complete_cutoffs"], 1)
        self.assertEqual(report["raw_rebound_candidate_cutoffs"], 1)
        self.assertEqual(report["excluded_cutoffs_by_reason"]["NO_NEW_COMPLETED_CANDLE_AT_CUTOFF"], 3)

    def test_source_candle_with_half_hour_offset_is_rejected(self):
        rows = fixture()
        for r in rows:
            r["timestamp_utc"] = (datetime.fromisoformat(
                r["timestamp_utc"].replace("Z", "+00:00")) + timedelta(minutes=30)
                ).isoformat().replace("+00:00", "Z")
            r["source_window_end_utc"] = (datetime.fromisoformat(
                r["source_window_end_utc"].replace("Z", "+00:00")) + timedelta(minutes=30)
                ).isoformat().replace("+00:00", "Z")
        with self.assertRaisesRegex(ValueError, "candle_open_not_utc_hour_aligned"):
            assess(rows, "2026-10-30T17:00:00Z")
        with self.assertRaisesRegex(ValueError, "candle_open_not_utc_hour_aligned"):
            replay_census(rows, "2026-10-30T17:00:00Z")

    def test_volume_baseline_is_immediately_preceding_12_hours(self):
        rows = fixture()
        volumes = [1] + [100]*6 + [1000]*6 + [100]*3
        self.assertEqual(len(rows), len(volumes))
        for row, volume in zip(rows, volumes):
            row["btc_quote_volume"] = str(volume)
            row["btc_taker_buy_quote_volume"] = str(volume * 0.5)
        result = assess(rows, "2026-10-30T16:00:00Z")
        self.assertAlmostEqual(result["evidence"]["btc_last_3h_quote_volume_vs_prior_12h_median"],
                               100.0/550.0, places=6)
        rows[12]["btc_quote_volume"] = ""
        missing = assess(rows, "2026-10-30T16:00:00Z")
        self.assertIsNone(missing["evidence"]["btc_last_3h_quote_volume_vs_prior_12h_median"])
        self.assertFalse(missing["family_independence"]["SPOT_PRICE_FLOW"])

    def test_real_public_hourly_owner_readback_no_trade(self):
        """Integration smoke against existing public 29-30 October Hourly files."""
        files = [Path("03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-29.csv"),
                 Path("03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-30.csv")]
        rows = read_public_owner(Path("."), files)
        result = assess(rows, "2026-10-30T21:00:00Z")
        self.assertEqual(result["status"], "NO_CANDIDATE_RESEARCH_ONLY")
        self.assertEqual(result["evidence"]["window_end_utc"], "2026-10-30T21:00:00Z")
        self.assertFalse(result["first_known_verified"])
        self.assertFalse(result["short_covering_proven"])
        self.assertIsNone(result["score_0_100"])
        self.assertEqual(result["trade_permission"], "NONE")

    def test_real_public_hourly_replay_never_claims_backtest_edge(self):
        files = [Path("03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-29.csv"),
                 Path("03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-30.csv")]
        rows = read_public_owner(Path("."), files)
        report = replay_census(rows, "2026-10-30T21:00:00Z")
        self.assertGreater(report["eligible_complete_cutoffs"], 0)
        self.assertFalse(report["performance_backtest"])
        self.assertFalse(report["first_known_verified"])
        self.assertIsNone(report["directional_accuracy"])
        self.assertIsNone(report["after_cost_edge"])
        self.assertEqual(report["official_action_permission"], "NONE")

    def test_missing_hour_stays_in_census_denominator(self):
        rows = fixture()
        report_complete = replay_census(rows, "2026-10-30T16:00:00Z")
        rows = [r for r in rows if r["timestamp_utc"] != "2026-10-30T08:00:00Z"]
        report_with_gap = replay_census(rows, "2026-10-30T16:00:00Z")
        self.assertEqual(report_with_gap["evaluated_cutoffs"],
                         report_complete["evaluated_cutoffs"])
        self.assertLess(report_with_gap["eligible_complete_cutoffs"],
                        report_complete["eligible_complete_cutoffs"])
        self.assertGreater(sum(report_with_gap["excluded_cutoffs_by_reason"].values()), 0)

    def test_empty_source_does_not_invent_candidate(self):
        report = replay_census([], "2026-10-30T16:00:00Z")
        self.assertEqual(report["raw_rebound_candidate_cutoffs"], 0)
        self.assertFalse(report["first_known_verified"])
        self.assertIsNone(report["after_cost_edge"])

    def test_cutoff_with_minutes_is_rounded_to_completed_utc_hour(self):
        rows = fixture()
        report = replay_census(rows, "2026-10-30T16:17:30Z")
        self.assertEqual(report["asof_utc"], "2026-10-30T16:17:30Z")
        self.assertEqual(report["raw_rebound_candidate_cutoffs"], 1)

    def test_episode_census_never_promotes_quality_to_accuracy(self):
        rows = fixture()
        report = replay_census(rows, "2026-10-30T16:00:00Z")
        self.assertGreaterEqual(report["raw_rebound_candidate_cutoffs"], 1)
        self.assertFalse(report["performance_backtest"])
        self.assertFalse(report["first_known_verified"])
        self.assertIsNone(report["after_cost_edge"])
        self.assertEqual(report["official_action_permission"], "NONE")
        self.assertEqual(report["cluster_sensitivity_NOT_CHOSEN_OR_CALIBRATED"]["6h"]["cluster_count"], 1)

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

    def test_later_collection_run_cannot_be_replayed_as_earlier_evidence(self):
        rows = fixture()
        rows[-1]["source_window_end_utc"] = "2026-10-30T17:00:00Z"
        out = assess(rows, "2026-10-30T16:00:00Z")
        self.assertEqual(out["reason"], "NEEDS_16_CONTIGUOUS_COMPLETED_HOURS")
        self.assertFalse(out["first_known_verified"])

    def test_incomplete_spot_volume_is_not_independent_evidence(self):
        rows = fixture()
        rows[-1]["btc_quote_volume"] = ""
        out = assess(rows, "2026-10-30T16:00:00Z")
        self.assertIsNone(out["evidence"]["btc_last_3h_taker_buy_quote_share"])
        self.assertFalse(out["family_independence"]["SPOT_PRICE_FLOW"])
        self.assertIsNone(out["score_0_100"])

    def test_run_coverage_earlier_than_candle_end_fails(self):
        rows = fixture()
        rows[-1]["source_window_end_utc"] = "2026-10-30T13:00:00Z"
        with self.assertRaisesRegex(ValueError, "source_coverage_ends_before_candle"):
            assess(rows, "2026-10-30T16:00:00Z")

    def test_hourly_gap_cannot_be_filled(self):
        rows = fixture() + [{**fixture()[0], "timestamp_utc": "2026-10-30T19:00:00Z", "source_window_end_utc": "2026-10-30T20:00:00Z"}]
        out = assess(rows, "2026-10-30T20:00:00Z")
        self.assertEqual(out["reason"], "HOURLY_GAP_NO_FORWARD_FILL")


    def test_fixed_168h_census_includes_source_free_prefix_and_empty_window(self):
        end = "2026-10-30T16:00:00Z"
        sparse = fixture()
        short = replay_census(sparse, end)
        none = replay_census([], end)
        self.assertEqual(short["evaluated_cutoffs"], 168)
        self.assertEqual(none["evaluated_cutoffs"], 168)
        self.assertEqual(short["eligible_complete_cutoffs"], 1)
        self.assertEqual(none["eligible_complete_cutoffs"], 0)
        self.assertEqual(none["raw_rebound_candidate_cutoffs"], 0)
        self.assertEqual(sum(none["excluded_cutoffs_by_reason"].values()), 168)
        self.assertEqual(
            sum(short["excluded_cutoffs_by_reason"].values()) +
            short["eligible_complete_cutoffs"], 168)
        self.assertFalse(none["first_known_verified"])
        self.assertIsNone(none["after_cost_edge"])

    def test_fixed_168h_census_with_pregrid_warmup_scores_168_not_169(self):
        base = datetime(2026, 10, 30, tzinfo=timezone.utc)
        rows = []
        for i in range(200):
            ts = base + timedelta(hours=i)
            row = {
                "timestamp_utc": ts.isoformat().replace("+00:00", "Z"),
                "source_window_end_utc":
                    (ts + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
                "btc_close": "100", "btc_quote_volume": "1000",
                "btc_taker_buy_quote_volume": "500",
                "ethbtc_close": "0.030", "btc_open_interest": "1000",
                "spot_status": "PASS", "derivatives_status": "PASS",
            }
            rows.append(row)
        end = base + timedelta(hours=200)
        report = replay_census(rows, end.isoformat().replace("+00:00", "Z"))
        self.assertEqual(report["evaluated_cutoffs"], 168)
        self.assertEqual(report["eligible_complete_cutoffs"], 168)
        self.assertEqual(report["excluded_cutoffs_by_reason"], {})
        self.assertEqual(report["raw_rebound_candidate_cutoffs"], 0)
        self.assertFalse(report["performance_backtest"])
        self.assertIsNone(report["after_cost_edge"])
        self.assertEqual(report["official_action_permission"], "NONE")

    def test_fixed_denominator_survives_midnight_and_partial_hour_cutoff(self):
        rows = fixture()
        at_midnight = replay_census(rows, "2026-10-31T00:00:00Z")
        at_minutes = replay_census(rows, "2026-10-30T16:17:30Z")
        for item in (at_midnight, at_minutes):
            self.assertEqual(item["evaluated_cutoffs"], 168)
            self.assertEqual(
                item["eligible_complete_cutoffs"] +
                sum(item["excluded_cutoffs_by_reason"].values()), 168)
            self.assertFalse(item["first_known_verified"])


if __name__ == "__main__":
    unittest.main()
