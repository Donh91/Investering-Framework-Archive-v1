import importlib.util
import gzip
import io
import csv
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path

p=Path(__file__).resolve().parents[2]/"scripts/research/task2_archive_price_only_stress_v1.py"
spec=importlib.util.spec_from_file_location("task2_archive_stress",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
T=int(datetime(2020,9,1,tzinfo=timezone.utc).timestamp()*1000)

def tape(prices):
    return [(T+3600000*i,float(p)) for i,p in enumerate(prices)]

def fixture_csv(prices, *, wrong_timestamp=None, wrong_level=None, extra_gap=False):
    s=io.StringIO()
    w=csv.DictWriter(s,fieldnames=["timestamp_utc","continuity_segment_id","ew_index"])
    w.writeheader()
    for i,value in enumerate(prices):
        stamp=datetime.fromtimestamp((T/1000)+i*3600+(3600 if extra_gap and i==len(prices)-1 else 0),tz=timezone.utc)
        w.writerow({"timestamp_utc": wrong_timestamp if wrong_timestamp and i==0 else stamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "continuity_segment_id":0,"ew_index":wrong_level if wrong_level is not None and i==0 else value})
    return gzip.compress(s.getvalue().encode())

class Task2ArchiveResearchTests(unittest.TestCase):
    def test_frozen_grid_144_by_4_costs(self):
        self.assertEqual(len(m.fixture_grid()),576)
        self.assertEqual(len(set(m.fixture_grid())),576)
        self.assertEqual(set(c[-1] for c in m.fixture_grid()),set(m.COSTS))
    def test_flat_tape_no_claimed_sale(self):
        q=m.simulate_one(tape([100.0]*200),(.05,6,.25,24,.003))
        self.assertEqual(q["state"],"NO_SIGNAL")
        self.assertEqual(q["delta_vs_hold_pct_initial"],0)
    def test_trigger_never_fills_signal_candle(self):
        # Selling on the warning bar (index 3 at 90) instead of index 4
        # at 70 would inflate risk-protection benefit.
        q=m.simulate_one(tape([100,100,100,90,70,80,90,100,110,120]),(.05,2,.5,2,0))
        self.assertEqual(q["state"],"ONE_TRIM")
        self.assertTrue(q["reentered"])
        self.assertLess(q["delta_vs_hold_pct_initial"],0)
        self.assertTrue(q["not_live_executable"])
    def test_fees_never_create_fictitious_upside_on_flat_post_trigger(self):
        row=[100,100,100,90]+[90]*50
        a=m.simulate_one(tape(row),(.05,2,.5,6,0))
        b=m.simulate_one(tape(row),(.05,2,.5,6,.02))
        self.assertEqual(a["delta_vs_hold_pct_initial"],0)
        self.assertLess(b["delta_vs_hold_pct_initial"],0)
    def test_downside_can_help_synthetic_trim_but_not_certify_edge(self):
        row=[100,100,100,94,90,80,60,50]+[50]*40
        x=m.simulate_one(tape(row),(.05,2,.5,24,.003))
        self.assertEqual(x["state"],"ONE_TRIM")
        self.assertGreater(x["delta_vs_hold_pct_initial"],0)
    def test_no_anachronistic_reentry_if_horizon_ends(self):
        row=[100,100,100,92]+[90]*5
        x=m.simulate_one(tape(row),(.05,2,.5,168,.003))
        self.assertEqual(x["state"],"SKIP_INSUFFICIENT_CONTIGUOUS_HOURS")
    def test_non_utc_iso_rejected(self):
        with self.assertRaisesRegex(ValueError,"BAD_ARCHIVE_TIMESTAMP"):
            m.parse_hour_utc("2025-01-01T01:00:00+01:00")
    def test_duplicate_observation_rejected_before_any_strategy(self):
        # Override canonical row-count assertion temporarily only by testing
        # direct parser's earlier duplicate check.
        rows=fixture_csv([100,100,101])
        self.assertTrue(rows)
        with self.assertRaisesRegex(ValueError,"ARCHIVED_25506_ROW_COUNT_CHANGED"):
            m.load_price_segments(rows)
    def test_nan_archive_price_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"NONFINITE_INDEX_LEVEL"):
            m.load_price_segments(fixture_csv([1,2],wrong_level="nan"))
    def test_locked_price_archive_and_public_metadata_are_still_original(self):
        if m.PRICE.exists() and m.EPISODES.exists() and m.CFGI.exists():
            result=m.preflight()
            self.assertEqual(result["episode_counts"],{"ALTSEASON_2020_2021":45,"MODERN_ANALOGUE_2025_2026":1})
            self.assertEqual(result["cfgi"]["market_hourly_slots"],0)
            self.assertFalse(result["cfgi"]["original_vendor_first_publication_certified"])
            self.assertEqual(m.blob_sha(m.PRICE.read_bytes()),m.PRICE_BLOB)
    def test_unauthorized_blob_mutation_fails_before_market_analysis(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_DRIFT"):
            m.locked_read(Path(__file__),m.PRICE_BLOB)
    def test_invented_source_epoch_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNREGISTERED_ARCHIVE_ERA"):
            m.load_price_segments(fixture_csv([1,2,3],wrong_timestamp="2023-01-01T00:00:00Z"))
    def test_output_contains_no_winner_selection_or_trading_authority(self):
        self.assertEqual(m.STATUS,"EX_POST_PRICE_ONLY_ENGINEERING_STRESS_NOT_FORECAST_EDGE")

if __name__=="__main__":
    unittest.main()
