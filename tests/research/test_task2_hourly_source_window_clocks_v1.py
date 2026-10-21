"""Task2 CSV source batch vs candle clocks: no false publication authority."""
import csv
import io
import unittest
from datetime import datetime,timezone,timedelta
from scripts.research import task2_hourly_source_window_clocks_v1 as m
T=datetime(2026,10,18,tzinfo=timezone.utc)
def iso(d):return d.strftime('%Y-%m-%dT%H:%M:%SZ')
def data(lags=None):
    if lags is None:lags=[1]*24
    out=io.StringIO()
    w=csv.DictWriter(out,fieldnames=["timestamp_utc","source_window_end_utc","spot_status","derivatives_status","btc_close","eth_close"])
    w.writeheader()
    for i in range(24):
        t=T+timedelta(hours=i)
        w.writerow({"timestamp_utc":iso(t),"source_window_end_utc":iso(t+timedelta(hours=lags[i])),
                    "spot_status":"PASS","derivatives_status":"PASS","btc_close":"777777.66","eth_close":"888888.55"})
    return out.getvalue().encode()
class HourlyBatchClockTests(unittest.TestCase):
    def test_canonical_24_complete(self):
        x=m.audit_day(data(),18)
        self.assertEqual(x["source_batch_end_equals_nominal_candle_end"],24)
        self.assertEqual(x["source_batch_end_after_nominal_candle_end"],0)
        self.assertNotIn("777777.66",str(x))
        self.assertNotIn("888888.55",str(x))
        self.assertNotIn("btc_close",str(x))
    def test_all_batch_stamped_different(self):
        x=m.audit_day(data([6]*24),18)
        self.assertEqual(x["source_batch_end_after_nominal_candle_end"],24)
        self.assertEqual(x["max_batch_window_end_minus_start_hours"],6)
    def test_missing_hour_fail_closed(self):
        s=data().decode().splitlines()
        with self.assertRaisesRegex(ValueError,"MISSING_OR_DUPLICATE"):
            m.audit_day(("\n".join(s[:-1])+"\n").encode(),18)
    def test_duplicate_or_displaced_hour_fail_closed(self):
        s=data().decode().splitlines();s[3]=s[2]
        with self.assertRaisesRegex(ValueError,"NONCANONICAL"):
            m.audit_day(("\n".join(s)+"\n").encode(),18)
    def test_non_integral_request_window_rejected(self):
        s=data().decode().replace("2026-10-18T01:00:00Z","2026-10-18T01:15:00Z",1)
        with self.assertRaisesRegex(ValueError,"NONINTEGRAL"):
            m.audit_day(s.encode(),18)
    def test_future_window_end_zero_span_rejected(self):
        s=data().decode().replace("2026-10-18T01:00:00Z","2026-10-18T00:00:00Z",1)
        with self.assertRaisesRegex(ValueError,"INVALID_BATCH_WINDOW"):
            m.audit_day(s.encode(),18)
    def test_blob_change_rejected(self):
        with self.assertRaisesRegex(ValueError,"ORIGINAL_HOURLY_BLOB_DRIFT"):
            m.audit_day(data(),18,expected_blob="a"*40)
    def test_unknown_era_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNREGISTERED_FROZEN_DAY"):
            m.audit_day(data(),1)
    def test_bad_timezone_rejected(self):
        with self.assertRaisesRegex(ValueError,"CLOCK_NOT_EXPLICIT_UTC"):
            m.utc("2026-10-18T00:00:00+00:00")
    def test_declaration_never_infers_data_available(self):
        self.assertIn("BATCH REQUEST WINDOW END",m.__doc__)
    def test_source_frozen_full_week(self):
        if m.SOURCE.exists():
            result=m.execute()
            self.assertEqual(result["original_hour_rows"],168)
            self.assertEqual(result["batch_end_after_candle_end_count"],104)
            self.assertEqual(result["batch_end_equals_candle_end_count"],64)
            self.assertEqual(result["max_batch_end_minus_hour_start_hours"],6)
            self.assertFalse(result["before_batch_end_data_available_proven"])
            self.assertFalse(result["after_batch_end_data_unavailable_proven"])
            self.assertFalse(result["cfgi_or_compass_edge_tested"])
            self.assertFalse(result["values_disclosed"])
if __name__=="__main__":unittest.main()
