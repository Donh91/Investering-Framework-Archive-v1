from __future__ import annotations
import csv,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("m6",ROOT/"scripts/learning/m6_warning_event_outcomes.py")
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

class M6WarningEventTests(unittest.TestCase):
    def freeze(self,root,state,btc=85000.0,eth=2700.0,issued="2026-10-06T16:14:15Z"):
        p=root/"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/06"/f"CMP-{state}.json";p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({"contract":"OFFICIAL_DAILY_COMPASS_v1","compass_id":f"CMP-{state}","issued_at_utc":issued,
          "market_reference":{"btc_usdt":btc,"eth_usdt":eth,"observation_open_utc":"2026-10-06T15:00:00Z"},
          "protection_tracker":{"contract":"COMPASS_PROTECTION_TRACKER_v1","data_quality":"OK","pullback_risk_state":state}}))

    def write_hourly(self,root,rows):
        p=root/"03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-06.csv";p.parent.mkdir(parents=True,exist_ok=True)
        fields=["timestamp_utc","source_window_end_utc","btc_close","btc_high","btc_low","eth_close","eth_high","eth_low","spot_status"]
        with p.open("w",newline="") as fh:
            w=csv.DictWriter(fh,fieldnames=fields);w.writeheader()
            for row in rows:w.writerow(row)

    def test_building_is_watch_only_not_event(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.freeze(root,"BUILDING")
            r=M.build(root,M.parse("2026-10-08T00:00:00Z"))
            self.assertEqual(r["event_count"],0);self.assertFalse(r["warning_is_sell"])

    def test_primary_warning_is_captured_before_maturity(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.freeze(root,"ELEVATED")
            r=M.build(root,M.parse("2026-10-06T18:00:00Z"))
            self.assertEqual(r["event_count"],1);e=r["events"][0]
            self.assertEqual(e["warning_state"],"ELEVATED");self.assertEqual(e["horizons"]["24h"]["maturity_state"],"PENDING")
            self.assertEqual(e["independent_family_weight"],1.0);self.assertFalse(e["authority"]["sell"])
            self.assertFalse(r["economic_action_scoring_ready"])

    def test_numeric_string_reference_price_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.freeze(root,"ELEVATED",btc="85000.0")
            self.assertEqual(M.build(root,M.parse("2026-10-08T00:00:00Z"))["event_count"],0)

    def test_repeated_warning_does_not_inflate_independent_n(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.freeze(root,"ELEVATED")
            p=root/"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/07/CMP-HIGH.json";p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps({"contract":"OFFICIAL_DAILY_COMPASS_v1","compass_id":"CMP-HIGH","issued_at_utc":"2026-10-07T16:14:15Z",
              "market_reference":{"btc_usdt":84000.0,"eth_usdt":2600.0,"observation_open_utc":"2026-10-07T15:00:00Z"},
              "protection_tracker":{"contract":"COMPASS_PROTECTION_TRACKER_v1","data_quality":"OK","pullback_risk_state":"HIGH"}}))
            r=M.build(root,M.parse("2026-10-08T00:00:00Z"))
            self.assertEqual(r["event_count"],2);self.assertEqual(r["provisional_independent_family_count"],1)
            self.assertEqual([x["independent_family_weight"] for x in r["events"]],[1.0,0.0])
            self.assertTrue(all(x["episode_family_status"]=="PROVISIONAL_OPEN_UNTIL_TROUGH_OBSERVED" for x in r["events"]))

    def test_intrabar_extrema_before_warning_must_not_count(self):
        start=M.parse("2026-10-06T16:14:15Z")
        segment=[
            {"close":M.parse("2026-10-06T17:00:00Z"),"btc":100.0,"btc_high":999.0,"btc_low":1.0},
            {"close":M.parse("2026-10-06T18:00:00Z"),"btc":102.0,"btc_high":110.0,"btc_low":95.0}
        ]
        v=M.asset_view(segment,100.0,"BTC",start)
        self.assertEqual(v["state"],"MATURED")
        self.assertEqual(v["excluded_straddling_bar_extrema"],1)
        self.assertAlmostEqual(v["reference_anchor"]["mae_pct"],-5.0)
        self.assertAlmostEqual(v["reference_anchor"]["mfe_pct"],10.0)
        self.assertFalse(v["adverse_barriers"]["-10.0"]["touched"])

    def test_missing_full_post_warning_bar_ohlc_fails_closed(self):
        start=M.parse("2026-10-06T16:14:15Z")
        segment=[
            {"close":M.parse("2026-10-06T17:00:00Z"),"btc":100.0,"btc_high":110.0,"btc_low":90.0},
            {"close":M.parse("2026-10-06T18:00:00Z"),"btc":102.0,"btc_high":None,"btc_low":95.0}
        ]
        v=M.asset_view(segment,100.0,"BTC",start)
        self.assertEqual(v["state"],"UNKNOWN_INCOMPLETE_ASSET_PATH")
        self.assertEqual(v["reason"],"MISSING_FULL_BAR_OHLC")

    def test_spot_fail_rows_cannot_mature_horizon(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.freeze(root,"ELEVATED",issued="2026-10-06T16:00:00Z")
            rows=[]
            for h in range(16,24):
                rows.append({"timestamp_utc":f"2026-10-06T{h:02d}:00:00Z","source_window_end_utc":f"2026-10-06T{h:02d}:59:59Z",
                    "btc_close":85000,"btc_high":85100,"btc_low":84900,"eth_close":2700,"eth_high":2710,"eth_low":2690,"spot_status":"FAIL"})
            self.write_hourly(root,rows)
            r=M.build(root,M.parse("2026-10-07T18:00:00Z"))
            self.assertEqual(r["events"][0]["horizons"]["24h"]["maturity_state"],"UNKNOWN_INCOMPLETE_TAPE")

    def test_family_first_warning_is_earliest_knowledge_time_not_filename(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            self.freeze(root,"HIGH",issued="2026-10-06T09:00:00Z")
            self.freeze(root,"ELEVATED",issued="2026-10-06T17:00:00Z")
            report=M.build(root,M.parse("2026-10-07T00:00:00Z"))
            self.assertEqual(report["event_count"],2)
            events=report["events"]
            self.assertEqual([e["compass_id"] for e in events],["CMP-HIGH","CMP-ELEVATED"])
            self.assertEqual([e["independent_family_weight"] for e in events],[1.0,0.0])
            self.assertEqual(events[0]["episode_family_id"],events[1]["episode_family_id"])
            self.assertTrue(events[0]["episode_family_id"].startswith("M6F-20261006T"))

if __name__=="__main__":unittest.main()
