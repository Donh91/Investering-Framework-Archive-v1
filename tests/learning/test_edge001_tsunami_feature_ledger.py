import json,tempfile,unittest
from pathlib import Path
from scripts.learning.edge001_tsunami_feature_ledger import build

class Edge001FeatureLedgerTests(unittest.TestCase):
    def test_empty_repo_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            j=build(Path(d))
            self.assertEqual(j["row_count"],0)
            self.assertFalse(j["outcome_joined"])
            self.assertFalse(j["warning_is_sell"])
            self.assertEqual(j["live_exit_rule"],"NONE")

    def test_building_is_not_primary_event(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); p=root/"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/07";p.mkdir(parents=True)
            f={"contract":"OFFICIAL_DAILY_COMPASS_v1","compass_id":"x","issued_at_utc":"2026-10-07T08:17:00Z","market_reference":{"observation_open_utc":"2026-10-07T07:00:00Z","btc_usdt":1.0,"eth_usdt":1.0},"protection_tracker":{"contract":"COMPASS_PROTECTION_TRACKER_v1","data_quality":"OK","pullback_risk_state":"BUILDING"}}
            (p/"CMP-x.json").write_text(json.dumps(f))
            self.assertEqual(build(root)["row_count"],0)

if __name__=="__main__":unittest.main()
