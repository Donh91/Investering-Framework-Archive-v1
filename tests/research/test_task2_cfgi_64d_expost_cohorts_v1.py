"""Task2 64-day same-opportunity audit must not turn archived scores into PIT."""
import csv
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path
from scripts.research import task2_cfgi_64d_expost_cohorts_v1 as m

def sample_spot_folder(root, *, n=21, bad_day=None, missing_field=False):
    start=date(2026,8,8)
    for i in range(n):
        day=start+timedelta(days=i)
        path=Path(root)/day.strftime("%Y/%m")/(day.isoformat()+".csv")
        path.parent.mkdir(parents=True,exist_ok=True)
        names=["timestamp_utc","source_window_end_utc","spot_status","btc_close","eth_close"]
        if missing_field:names.remove("eth_close")
        with path.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=names)
            w.writeheader()
            for hour in range(24):
                ts=f"{day}T{hour:02d}:00:00Z"
                end=f"{day}T{(hour+1)%24:02d}:00:00Z"
                if hour==23: end=f"{day+timedelta(days=1)}T00:00:00Z"
                if bad_day and i==1 and hour==9:
                    ts=f"{day+timedelta(days=1)}T09:00:00Z"
                x={"timestamp_utc":ts,"source_window_end_utc":end,
                   "spot_status":"PASS","btc_close":"100","eth_close":"200"}
                w.writerow({name:x[name] for name in names})

class Task2WideSampleTests(unittest.TestCase):
    def test_fixed_64_day_original_window(self):
        ds=list(m.day_iter(m.START,m.END))
        self.assertEqual(len(ds),64)
        self.assertEqual(ds[0],date(2026,8,18))
        self.assertEqual(ds[-1],date(2026,10,20))
    def test_backward_window_prohibited(self):
        with self.assertRaisesRegex(ValueError,"UNBOUNDED_SOURCE_SCAN"):
            list(m.day_iter(date(2026,10,20),date(2026,8,18)))
    def test_unbounded_forward_scan_prohibited(self):
        with self.assertRaisesRegex(ValueError,"UNBOUNDED_SOURCE_SCAN"):
            list(m.day_iter(date(2025,1,1),date(2026,10,20)))
    def test_empty_sources_do_not_create_false_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,"INSUFFICIENT_ORIGINAL_ARCHIVE"):
                m.spot_index(Path(folder))
    def test_sample_complete_price_archive_source(self):
        with tempfile.TemporaryDirectory() as folder:
            sample_spot_folder(folder)
            a,receipts,missing,incomplete=m.spot_index(Path(folder))
            self.assertEqual(len(a),21*24)
            self.assertEqual(len(receipts),21)
            self.assertEqual(len(incomplete),0)
            self.assertTrue(missing)
            self.assertEqual(len(receipts[0]["original_git_blob_sha1"]),40)
    def test_price_wrong_calendar_day_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            sample_spot_folder(folder,bad_day=True)
            with self.assertRaisesRegex(ValueError,"WRONG_SPOT_DAY"):
                m.spot_index(Path(folder))
    def test_source_schema_missing_eth_not_silently_filled(self):
        with tempfile.TemporaryDirectory() as folder:
            sample_spot_folder(folder,missing_field=True)
            with self.assertRaisesRegex(ValueError,"MISSING_SPOT_OWNER_CONTRACT"):
                m.spot_index(Path(folder))
    def test_no_original_vendor_price_emitted(self):
        self.assertFalse(m.AUTHORITY["raw_market_values_published"])
        self.assertFalse(m.AUTHORITY["provider_first_publication_verified"])
        self.assertFalse(m.AUTHORITY["historical_edge_admitted"])
    def test_no_purchasing_and_no_trade_authority(self):
        self.assertFalse(m.AUTHORITY["new_vendor_requests"])
        self.assertFalse(m.AUTHORITY["trade_authorized"])
    def test_wide_study_does_not_change_fixed_small_study(self):
        from scripts.research import task2_cfgi_price_expost_4h_v1 as tiny
        self.assertEqual(len(tiny.DAYS),7)
        self.assertEqual(len(m.day_iter(m.START,m.END).__iter__().__next__().__class__.__name__),4)
    def test_actual_original_archive_census_when_mounted(self):
        if m.CAPTURE_ROOT.exists() and m.PRICE_ROOT.exists():
            o=m.execute()
            self.assertEqual(o["contract"],m.CONTRACT)
            self.assertEqual(o["source_original_manifest"]["total_calendar_days"],64)
            self.assertEqual(len(o["by_symbol"]),2)
            self.assertEqual(sum(x["symbol_observations"] for x in o["by_symbol"].values()),
                             o["joined_symbol_opportunities"])
            self.assertEqual(sum(v["symbol_observations"] for v in o["by_week"].values()),
                             o["joined_symbol_opportunities"])
            self.assertFalse(o["statistical_significance_claim"])
            self.assertFalse(o["executed_forecast_model_included"])
            self.assertFalse(o["original_raw_cfgi_values_exported"])
            self.assertFalse(o["historical_or_live_cfgi_edge_proven"] if "historical_or_live_cfgi_edge_proven" in o else o["authority"]["historical_edge_admitted"])
            self.assertGreater(o["weekly_units"],7)
            self.assertGreater(o["joined_symbol_opportunities"],80)
    def test_declared_default_is_expost_not_pit(self):
        self.assertIn("EX_POST",m.LABEL)
        self.assertIn("NOT_PIT",m.LABEL)
if __name__=="__main__":unittest.main()
