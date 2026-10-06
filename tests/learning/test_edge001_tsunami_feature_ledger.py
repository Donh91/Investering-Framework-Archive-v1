import json,tempfile,unittest
from pathlib import Path
from scripts.learning.edge001_tsunami_feature_ledger import build

class Edge001FeatureLedgerTests(unittest.TestCase):
    def test_empty_repo_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            j=build(Path(d))
            self.assertEqual(j["row_count"],0)
            self.assertFalse(j["outcome_joined"])
            self.assertFalse(j["scoring_ready"])
            self.assertFalse(j["warning_is_sell"])
            self.assertEqual(j["live_exit_rule"],"NONE")

    def _freeze(self,root,state="ELEVATED",btc=1.0,eth=1.0):
        p=root/"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/07";p.mkdir(parents=True,exist_ok=True)
        f={"contract":"OFFICIAL_DAILY_COMPASS_v1","compass_id":"x","issued_at_utc":"2026-10-07T08:17:00Z",
           "market_reference":{"observation_open_utc":"2026-10-07T07:00:00Z","btc_usdt":btc,"eth_usdt":eth},
           "protection_tracker":{"contract":"COMPASS_PROTECTION_TRACKER_v1","data_quality":"OK","pullback_risk_state":state}}
        (p/"CMP-x.json").write_text(json.dumps(f))

    def test_building_is_not_primary_event(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self._freeze(root,"BUILDING")
            self.assertEqual(build(root)["row_count"],0)

    def test_numeric_strings_do_not_create_cohort_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self._freeze(root,"ELEVATED","1.0",1.0)
            self.assertEqual(build(root)["row_count"],0)

    def test_primary_without_hourly_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self._freeze(root)
            j=build(root)
            self.assertEqual(j["row_count"],1)
            row=j["rows"][0]
            self.assertEqual(row["features"]["state"],"UNKNOWN_NO_LEGAL_HOURLY_ROW")
            self.assertFalse(row["scoring_eligible"])
            self.assertFalse(row["outcome_joined"])

if __name__=="__main__":unittest.main()
