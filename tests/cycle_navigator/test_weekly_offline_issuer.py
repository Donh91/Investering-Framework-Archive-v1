"""Offline source-bound seven-day CN publisher regression and adversarial guards."""
import copy
import unittest
from scripts.cycle_navigator.weekly_offline_issuer import build_offline_value, METHOD
from scripts.cycle_navigator.daily_price_journey import validate_daily_path, validate_daily_range_plan, daily_product_acceptance
from datetime import datetime, timezone


def fixtures():
    prior = {
        "contract": "CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1", "issue_number": 33,
        "forecast_freeze": {
            "btc_range_low": 72000, "btc_range_high": 84000,
            "eth_range_low": 2000, "eth_range_high": 2500,
            "ethbtc_condition": "weak", "breadth_condition": "not confirmed",
            "structural_calls": ["a", "b", "c", "d", "e"],
            "intraday_map": {"day_1_2":"BTC $72000–$84000; ETH $2000–$2500",
                             "day_3_4":"BTC $72000–$84000; ETH $2000–$2500",
                             "day_5_7":"BTC $72000–$84000; ETH $2000–$2500"},
        },
        "decision_projection": {
            "next_21_30d": {"scenarios":[]}, "weeks_4_8": {},
            "protection": {"public_explanation":{
                "contract":"CN_PUBLIC_PROTECTION_COPY_v1",
                "summary":"Volatility remains elevated and source confirmation incomplete.",
                "watch_for":"Watch whether price holds and participation broadens.",
                "weakens_if":"Risk eases if price resilience and breadth recover together.",
                "onset_start_day":None,"onset_end_day":None
            }}
        }}
    weekly = {
        "contract":"WEEKLY_RAW_CALIBRATION_PACK_v3","readiness":"READY",
        "iso_year":2026,"iso_week":45,
        "source_capture_paths":["03_DAILY_CAPTURE_LOGS/captures/2026/W45/real.json"],
        "hourly_gap_diagnostics":{"observed_hours":168,"missing_hour_count":0},
        "hourly_sequence":{
            "btc":{"week_range":{"open":78354.01,"high":81196.01,"low":73510,"close":74851.44}},
            "eth":{"week_range":{"open":2275.3,"high":2450,"low":2060,"close":2127.46}}}}
    baseline = {
        "status":"READY","target_iso_year":2026,"target_iso_week":46,
        "anchor_contiguous":True,
        "assets":{"BTC":{"status":"READY","low":71200,"high":76200},
                  "ETH":{"status":"READY","low":1960,"high":2180}}}
    context={"completed_week_hourly_capture":weekly,"master_monday_pointer":{"iso_year":2026,"iso_week":45}}
    return context, baseline, prior


class OfflineIssuerTest(unittest.TestCase):
    def test_source_week_generates_seven_independent_btc_eth_points(self):
        v=build_offline_value(*fixtures(),2026,46,34,33)
        self.assertEqual(v["issue_number"],34)
        self.assertEqual(v["status"],"DEGRADED")
        self.assertEqual(len(v["evaluation"]["parameter_scores"]),12)
        self.assertEqual(v["evaluation"]["structural_score"],None)
        f=v["forecast_freeze"]
        validate_daily_path(f["daily_price_path"],f,2026,46)
        validate_daily_range_plan(f["daily_range_plan"],f,2026,46)
        for a in ("BTC","ETH"):
            path=f["daily_price_path"][a]["points"]
            range_=f["daily_range_plan"][a]["points"]
            self.assertEqual(len(path),7)
            self.assertEqual(len(range_),7)
            self.assertEqual([p["day"] for p in path],list(range(1,8)))
            self.assertGreater(len(set(p["expected_close"] for p in path)),3)
            self.assertEqual([(x["low"],x["high"]) for x in path],[(x["low"],x["high"]) for x in range_])
        receipt=daily_product_acceptance(f,2026,46,datetime(2026,11,9,10,0,tzinfo=timezone.utc))
        self.assertEqual(receipt["status"],"COMPLETE")
        self.assertIn("2026-11-15",v["readable_markdown"])
        self.assertIn(METHOD,v["readable_markdown"])

    def test_not_backdated_and_source_contract_mismatch_fails_closed(self):
        c,b,p=fixtures()
        p_before=copy.deepcopy(p)
        build_offline_value(c,b,p,2026,46,34,33)
        self.assertEqual(p,p_before)
        bad=copy.deepcopy(c);bad["completed_week_hourly_capture"]["hourly_gap_diagnostics"]["observed_hours"]=167
        with self.assertRaisesRegex(ValueError,"CN_OFFLINE_SOURCE_UNQUALIFIED"):
            build_offline_value(bad,b,p,2026,46,34,33)
        bad=copy.deepcopy(c);bad["master_monday_pointer"]["iso_week"]=44
        with self.assertRaisesRegex(ValueError,"CN_OFFLINE_SOURCE_UNQUALIFIED"):
            build_offline_value(bad,b,p,2026,46,34,33)

    def test_week_and_quote_boundary_cannot_be_faked(self):
        c,b,p=fixtures()
        b=copy.deepcopy(b);b["target_iso_week"]=45
        with self.assertRaisesRegex(ValueError,"CN_OFFLINE_BASELINE_UNQUALIFIED"):
            build_offline_value(c,b,p,2026,46,34,33)
        c,b,p=fixtures()
        b=copy.deepcopy(b);b["assets"]["BTC"]["low"]=-1
        with self.assertRaisesRegex(ValueError,"CN_OFFLINE_NONFINITE_OR_INCONSISTENT"):
            build_offline_value(c,b,p,2026,46,34,33)
        v=build_offline_value(*fixtures(),2026,46,34,33)
        # Even complete week forecast cannot be backdated after day-one settlement.
        late=daily_product_acceptance(v["forecast_freeze"],2026,46,datetime(2026,11,10,0,1,tzinfo=timezone.utc))
        self.assertEqual(late["status"],"INCOMPLETE")

if __name__=="__main__":
    unittest.main()
