"""Task2 W45 source and clock regression, research-only."""
import tempfile
import unittest
from pathlib import Path
from scripts.research import task2_cn_w45_postfreeze_paired_v1 as w45


class Task2W45PostissueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = w45.build()

    def test_original_first_issue_and_postissue_denominators(self):
        o = self.out
        self.assertEqual(o["original_first_issue_commit"], w45.FIRST_COMMIT)
        self.assertEqual(o["issue_utc"], "2026-11-02T08:19:08Z")
        self.assertEqual(o["complete_hourly_source_n"], 168)
        self.assertEqual(o["postfreeze_closed_endpoint_n"], 160)
        self.assertEqual(o["whole_candles_opening_after_issue_n"], 159)

    def test_original_pair_both_assets_real_extrema(self):
        for asset, expected in (("BTC", [73510.0, 81196.01]),
                                ("ETH", [2060.0, 2450.0])):
            r = self.out["results"][asset]
            self.assertEqual(r["observed_whole_candle_low_high_USDT"], expected)
            self.assertTrue(r["CN_original_USD_vs_USDT_proxy"]["joint_full_low_and_high_contained"])
            self.assertFalse(r["B1_original_vs_USDT_proxy"]["joint_full_low_and_high_contained"])
            self.assertGreater(r["CN_to_B1_width_ratio"], 2)

    def test_no_fake_PIT_quoted_currency_or_model_winner(self):
        o = self.out
        self.assertFalse(o["quote_USD_USDT_equivalence_proven"])
        self.assertFalse(o["vendor_original_first_known_proven"])
        self.assertFalse(o["user_delivery_proven"])
        self.assertFalse(o["statistically_proven_CN_edge"])
        self.assertFalse(o["portfolio_or_trading_authority"])
        self.assertEqual(o["independent_future_market_regime_n"], 0)

    def test_source_missing_or_replaced_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with self.assertRaisesRegex(ValueError, "MISSING_OR_UNSAFE_SOURCE"):
                w45.read_locked(root, "cn")
            p = root / w45.SOURCES["cn"][0]
            p.parent.mkdir(parents=True)
            p.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SOURCE_GIT_BLOB_DRIFT"):
                w45.read_locked(root, "cn")

    def test_strict_utc_and_invalid_candle_batch(self):
        with self.assertRaisesRegex(ValueError, "STRICT_UTC_Z_REQUIRED"):
            w45.utc("2026-11-02T08:19:08+01:00")
        with self.assertRaisesRegex(ValueError, "INVALID_COLLECTOR_BATCH_WINDOW_SPAN"):
            w45.validated_hourly_candle_clocks({
                "timestamp_utc": "2026-11-02T09:00:00Z",
                "source_window_end_utc": "2026-11-02T09:00:00Z",
            })


if __name__ == "__main__":
    unittest.main()
