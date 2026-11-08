"""Task2 source-locked W44 CN vs B1, no preissue, no source-ineligible alpha."""
from __future__ import annotations
import math
import tempfile
import unittest
from pathlib import Path
from scripts.research import task2_cn_w44_postfreeze_paired_v1 as w44

ROOT=Path(__file__).resolve().parents[2]

class Task2W44PostfreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.replay=w44.build(ROOT)

    def test_162_complete_postfreeze_hours_and_exact_original_issuer(self):
        out=self.replay
        self.assertEqual(out["contract"],w44.CONTRACT)
        self.assertEqual(out["full_week_completed_hours"],168)
        self.assertEqual(out["postfreeze_eligible_hours"],162)
        self.assertEqual(out["postfreeze_first_eligible_hour_utc"],"2026-10-26T07:00:00+00:00")
        self.assertEqual(out["issue_at_utc"],"2026-10-26T06:57:49+00:00")
        self.assertEqual(out["last_eligible_complete_hour_end_utc"],"2026-11-02T00:00:00+00:00")
        self.assertEqual(out["original_publishing_git_commit"],w44.ISSUE_COMMIT)

    def test_full_postissue_ohlc_sensitivity_keeps_original_162_unchanged(self):
        out=self.replay
        self.assertEqual(out["postfreeze_eligible_hours"],162)
        self.assertEqual(out["whole_candle_postissue_hours"],161)
        self.assertTrue(out["first_retained_completed_candle_opened_preissue"])
        self.assertEqual(out["first_whole_candle_postissue_open_utc"],
                         "2026-10-26T07:00:00+00:00")
        for symbol in ("BTC","ETH"):
            original=out["results"][symbol]["postfreeze_hourly_extrema"]
            sensitivity=out["results"][symbol]["whole_candle_postissue_sensitivity"]
            self.assertEqual(sensitivity["hours"],161)
            self.assertGreaterEqual(sensitivity["low"],original["low"])
            self.assertLessEqual(sensitivity["high"],original["high"])
            self.assertEqual(sensitivity["min_changed_from_locked_162"],
                             sensitivity["low"]!=original["low"])
            self.assertEqual(sensitivity["max_changed_from_locked_162"],
                             sensitivity["high"]!=original["high"])
            self.assertFalse(sensitivity["same_quote_or_vendor_first_known_proven"])
            self.assertFalse(sensitivity["statistical_edge_admitted"])

    def test_both_frozen_original_cn_contain_and_narrower_b1_miss(self):
        out=self.replay["results"]
        for symbol in ("BTC","ETH"):
            row=out[symbol]
            self.assertTrue(row["CN"]["joint_full_low_and_high_contained"])
            self.assertFalse(row["ORIGINAL_PREISSUED_B1"]["joint_full_low_and_high_contained"])
            self.assertTrue(row["CN_contained_B1_missed_and_B1_jaccard_higher"])
            self.assertGreater(row["CN_width_over_B1_width"],1)
            self.assertGreater(row["ORIGINAL_PREISSUED_B1"]["jaccard_overlap"],row["CN"]["jaccard_overlap"])

    def test_btc_and_eth_exact_small_source_negative_controls(self):
        btc=self.replay["results"]["BTC"]
        eth=self.replay["results"]["ETH"]
        self.assertEqual(btc["postfreeze_hourly_extrema"],{"low":76325.98,"high":81971.0})
        self.assertEqual(eth["postfreeze_hourly_extrema"],{"low":2174.08,"high":2391.55})
        self.assertEqual(btc["CN"]["predicted_low"],75000)
        self.assertEqual(btc["ORIGINAL_PREISSUED_B1"]["predicted_low"],76840.30681173655)
        self.assertEqual(eth["CN"]["predicted_high"],2550)
        self.assertEqual(eth["ORIGINAL_PREISSUED_B1"]["predicted_high"],2388.010739126768)

    def test_positive_alphas_and_market_edge_not_inferred(self):
        p=self.replay
        self.assertIn("USDT",p["currency_semantics"])
        self.assertFalse(p["original_vendor_first_known_proven"])
        self.assertIsNone(p["independent_market_event_families"])
        self.assertFalse(p["joint_probabilistic_interval_skill_proven"])
        self.assertFalse(p["confirmed_incremental_forecast_edge"])
        self.assertFalse(p["trading_or_public_score_change"])
        self.assertFalse(p["round3_analysis_performed"])
        self.assertTrue(p["no_model_selection_or_parameter_tuning"])

    def test_actual_55_batch_window_ends_are_not_fake_hourly_candle_closes(self):
        result=self.replay
        self.assertEqual(result["batch_window_after_candle_end_rows"],55)
        self.assertEqual(result["time_series_clock"],
            "TIMESTAMP_UTC_CANONICAL_CANDLE_OPEN_PLUS_ONE_COMPLETED_HOUR")
        self.assertTrue(result["batch_request_end_is_not_first_known"])
        self.assertFalse(result["original_vendor_first_known_proven"])
        self.assertEqual(result["postfreeze_eligible_hours"],162)

    def test_two_distinct_nominal_hours_share_batch_end_legitimately(self):
        a,first_end,late_a=w44.validated_hourly_candle_clocks({
            "timestamp_utc":"2026-10-26T01:00:00Z",
            "source_window_end_utc":"2026-10-26T05:00:00Z"})
        b,second_end,late_b=w44.validated_hourly_candle_clocks({
            "timestamp_utc":"2026-10-26T02:00:00Z",
            "source_window_end_utc":"2026-10-26T05:00:00Z"})
        self.assertNotEqual(a,b)
        self.assertNotEqual(first_end,second_end)
        self.assertEqual((second_end-first_end).total_seconds(),3600)
        self.assertTrue(late_a)
        self.assertTrue(late_b)

    def test_invalid_batch_window_and_noncanonical_candle_fail_closed(self):
        for start,end,error in (
            ("2026-10-26T07:00:00Z","2026-10-26T07:00:00Z",
             "INVALID_COLLECTOR_BATCH_WINDOW_SPAN"),
            ("2026-10-26T07:00:00Z","2026-10-27T08:00:00Z",
             "INVALID_COLLECTOR_BATCH_WINDOW_SPAN"),
            ("2026-10-26T07:30:00Z","2026-10-26T09:00:00Z",
             "NON_HOURLY_CANONICAL_SOURCE_CLOCK"),
            ("2026-10-26T07:00:00Z","2026-10-26T09:30:00Z",
             "NON_HOURLY_CANONICAL_SOURCE_CLOCK"),
        ):
            with self.assertRaisesRegex(ValueError,error):
                w44.validated_hourly_candle_clocks({
                    "timestamp_utc":start,"source_window_end_utc":end})

    def test_inverted_missing_or_nonfinite_range_fails_closed(self):
        for vals in ((100,99,90,110,100),(10,20,30,29,100),
                     (float("nan"),20,3,15,100),(0,10,3,9,100)):
            with self.assertRaisesRegex(ValueError,"INVALID_W44_ORIGINAL_BAND|NONFINITE_W44_RANGE"):
                w44.joint_score(*vals)

    def test_frozen_git_blob_mutation_not_silent(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            rel=w44.SOURCES["original_cn"][0]
            path=root/rel
            path.parent.mkdir(parents=True)
            path.write_bytes(b'{"tampered":true}')
            with self.assertRaisesRegex(ValueError,"ORIGINAL_GIT_BLOB_DRIFT"):
                w44.locked_read(root,"original_cn")

if __name__=="__main__":
    unittest.main()
