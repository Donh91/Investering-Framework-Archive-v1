import unittest
from datetime import datetime,timezone,timedelta
from scripts.research.cn_mm_task2_comparator_readback_v1 import point_panel
class Task2ComparatorTests(unittest.TestCase):
    def test_matched_day_and_no_unpaired_day(self):
        start=datetime(2026,11,16,tzinfo=timezone.utc)
        bars={start+timedelta(hours=i):{"BTC":(110.,111.,109.)} for i in range(24)}
        issued={"assets":{"BTC":{"P0":100.,"days":[{"day":1,"scored_from_utc":start.isoformat(),
            "end_utc":(start+timedelta(days=1)).isoformat()}]}}}
        freeze={"daily_price_path":{"BTC":{"points":[{"day":1,"expected_close":105.}]}}}
        score={"rows":[{"asset":"BTC","day":1,"CN_interval_score":1.}],"paired_rows":1}
        result=point_panel(issued,freeze,bars,score)
        self.assertEqual(result["all"]["n"],1)
        self.assertAlmostEqual(result["all"]["c0_mean_abs_error_fraction"],0.05)
        self.assertAlmostEqual(result["all"]["c1_mean_abs_error_fraction"],0.1)
        score["paired_rows"]=2
        with self.assertRaisesRegex(ValueError,"DUPLICATE_PAIR"):
            point_panel(issued,freeze,bars,score)
    def test_empty_panel_is_null(self):
        result=point_panel({"assets":{}},{},{},{"rows":[],"paired_rows":0})
        self.assertIsNone(result["all"]["c0_mean_abs_error_fraction"])
