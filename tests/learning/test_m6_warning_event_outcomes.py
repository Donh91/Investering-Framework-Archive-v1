from __future__ import annotations
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("m6",ROOT/"scripts/learning/m6_warning_event_outcomes.py")
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

class M6WarningEventTests(unittest.TestCase):
    def freeze(self,root,state):
        p=root/"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/06"/f"CMP-{state}.json";p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({"contract":"OFFICIAL_DAILY_COMPASS_v1","compass_id":f"CMP-{state}","issued_at_utc":"2026-10-06T16:14:15Z",
          "market_reference":{"btc_usdt":85000.0,"eth_usdt":2700.0,"observation_open_utc":"2026-10-06T15:00:00Z"},
          "protection_tracker":{"contract":"COMPASS_PROTECTION_TRACKER_v1","data_quality":"OK","pullback_risk_state":state}}))
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
    def test_repeated_warning_does_not_inflate_independent_n(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);self.freeze(root,"ELEVATED")
            p=root/"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/07/CMP-HIGH.json";p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps({"contract":"OFFICIAL_DAILY_COMPASS_v1","compass_id":"CMP-HIGH","issued_at_utc":"2026-10-07T16:14:15Z",
              "market_reference":{"btc_usdt":84000.0,"eth_usdt":2600.0,"observation_open_utc":"2026-10-07T15:00:00Z"},
              "protection_tracker":{"contract":"COMPASS_PROTECTION_TRACKER_v1","data_quality":"OK","pullback_risk_state":"HIGH"}}))
            r=M.build(root,M.parse("2026-10-08T00:00:00Z"))
            self.assertEqual(r["event_count"],2);self.assertEqual(r["independent_family_count"],1)
            self.assertEqual([x["independent_family_weight"] for x in r["events"]],[1.0,0.0])
if __name__=="__main__":unittest.main()
