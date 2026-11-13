"""Executable synthetic + existing archive guardrails for Task2 full historical CN replay."""
import json
import os
import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.research import task2_all_cn_historical_replay_v1 as r

def mk_market(w, low=90, high=110, close=100):
    start=date.fromisocalendar(2026,w,1)
    days=[{"date_utc":str(date.fromordinal(start.toordinal()+i)),
           "hour_count":24,"low":low,"high":high,"close":close,
           "open":close,"volume":1000} for i in range(7)]
    sym=lambda:{"completeness":"PASS","hour_count":168,"expected_hour_count":168,
                 "daily_ranges":days,"weekly_close":close,
                 "weekly_low":low,"weekly_high":high}
    return {"contract":"WEEKLY_MARKET_CLOSE_PACKAGE_v3",
            "iso_week":w,"iso_year":2026,"source":r.QUOTE,
            "final":True,"completeness":"COMPLETE",
            "symbols":{"BTCUSDT":sym(),"ETHUSDT":sym()}}

def put(root,path,data):
    f=root/path;f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")

class HistoricalReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for w in (38,39):
            put(self.root,r.ACTUAL/f"W{w:02d}"/"WEEKLY_MARKET_CLOSE_PACKAGE.json",
                mk_market(w,90 if w==38 else 91,110 if w==38 else 109,100))
        p=r.BASE/"W39"
        put(self.root,p/"CYCLE_NAVIGATOR_FORECAST_FREEZE.json",
            {"btc_range_low":92,"btc_range_high":108,
             "eth_range_low":93,"eth_range_high":107})
        put(self.root,p/"CYCLE_NAVIGATOR_DELIVERY_POINTER.json",
            {"issue_number":27,"status":"PASS","master_monday_pointer_sha256":"0"*64})
        put(self.root,p/"CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json",
            {"claims":[
                {"claim_id":"X","family":"intraday_day_1_2","alias_of":None,
                 "maturity_iso_week":39,"maturity_iso_year":2026,"horizon":"DAY_1_2",
                 "forecast":"BTC $92–$108; ETH $93–$107"},
                {"claim_id":"Z","family":"base_case_2_3_weeks","alias_of":None,
                 "maturity_iso_week":41,"horizon":"2_3_WEEKS","forecast":"UNKNOWN"}
            ]})
        legacy=r.LEGACY[0]/"CN_014_PUBLISHED_X_POST_2026-06-29.md"
        put(self.root,legacy,{"text":"Synthetic legacy CN without original timestamps"})

    def test_weekly_market_source_168h_grid_accept(self):
        ok,why=r.valid_observed_week(mk_market(39),39)
        self.assertTrue(ok,why)

    def test_hourly_gap_rejected_not_counted_as_week(self):
        p=mk_market(39);p["symbols"]["BTCUSDT"]["daily_ranges"][0]["hour_count"]=23
        ok,reason=r.valid_observed_week(p,39)
        self.assertFalse(ok)
        self.assertIn("INCOMPLETE",reason)

    def test_wrong_week_rejected(self):
        ok,reason=r.valid_observed_week(mk_market(39),40)
        self.assertFalse(ok)

    def test_both_issued_and_prior_week_band_match_properly(self):
        summary,rows,weekly,internal,windows,*_=r.build(self.root)
        self.assertEqual(summary["weeks_with_machine_cn"],1)
        self.assertEqual(summary["market_completed_week_packages"],2)
        self.assertEqual(len(rows),2)
        btc=next(x for x in rows if x["asset"]=="BTC")
        self.assertEqual(btc["forecast_full_path_covered"],0)
        self.assertEqual(btc["naive_full_path_covered"],1)
        self.assertEqual(btc["forecast_close_covered"],1)
        self.assertTrue(btc["prior_week_available"])
        self.assertEqual(summary["strict_prospective_skill_eligible_rows"],0)
        self.assertEqual(len(windows),2)

    def test_no_forward_claim_maturation(self):
        _,_,_,internal,*_=r.build(self.root)
        far=next(x for x in internal if x["claim_id"]=="Z")
        self.assertTrue(far["maturity_complete"] if far["maturity_iso_week"]<=45 else not far["maturity_complete"])
        self.assertEqual(far["scientific_status"],"SEMANTIC_CLAIM_NOT_MACHINE_SCORED")
        self.assertEqual(far["original_first_known_utc"],"UNKNOWN")

    def test_no_W46_final_outcome_even_with_provisional_file(self):
        p=r.BASE/"W46"
        put(self.root,p/"CYCLE_NAVIGATOR_FORECAST_FREEZE.json",
            {"btc_range_low":85,"btc_range_high":115,"eth_range_low":85,"eth_range_high":115})
        put(self.root,p/"CYCLE_NAVIGATOR_DELIVERY_POINTER.json",
            {"issue_number":34,"status":"DEGRADED"})
        put(self.root,r.ACTUAL/"W46"/"WEEKLY_MARKET_CLOSE_PACKAGE.json",mk_market(46))
        _,rows,_,_,_,*_=r.build(self.root)
        self.assertTrue(all(row["target_mature"] is False for row in rows if row["week"]==46))

    def test_interval_miss_and_width_are_not_scored_as_probability(self):
        z=r.check_interval(93,103,{"observed":{"low":90,"high":108,"close":100},"prev_close":100})
        self.assertEqual(z["full"],0)
        self.assertEqual(z["miss"],0.08)
        self.assertEqual(z["width"],0.10)
        self.assertNotIn("Brier",z)

    def test_legacy_text_does_not_claim_original_first_known(self):
        docs,_=r.legacy_documents(self.root)
        self.assertEqual(len(docs),1)
        self.assertFalse(docs[0]["issuer_original_time_verified"])
        self.assertEqual(docs[0]["first_known_utc"],"UNKNOWN")

    def test_real_repo_archives_visible_and_computation_is_non_empty(self):
        if not (r.ROOT/"05_CYCLE_NAVIGATOR/weekly/2026/W45").is_dir():
            self.skipTest("isolated test with synthetic root only")
        summary,*_=r.build(r.ROOT)
        self.assertGreaterEqual(summary["weeks_with_machine_cn"],11)
        self.assertGreaterEqual(summary["weeks_with_internal_freeze"],7)
        self.assertGreaterEqual(summary["legacy_cn_published_or_recovered_documents"],22)
        self.assertGreaterEqual(summary["market_completed_week_packages"],12)
        self.assertGreaterEqual(summary["weekly_price_rows_frozen_and_matured_with_prior_baseline"],8)
        self.assertEqual(summary["strict_prospective_skill_eligible_rows"],0)

if __name__=="__main__":
    unittest.main()
