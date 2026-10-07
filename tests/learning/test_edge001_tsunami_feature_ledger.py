import json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from scripts.learning.edge001_tsunami_feature_ledger import breadth_context,build

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

    def test_breadth_context_skips_other_valid_json_artifact_shapes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            base=root/"03_DAILY_CAPTURE_LOGS/breadth_rich/2026/10/07"
            base.mkdir(parents=True,exist_ok=True)
            (base/"raw_source_payload.json").write_text(json.dumps([{"symbol":"BTC"}]))
            (base/"other_artifact.json").write_text(json.dumps({"observation":["not","a","mapping"],"retrieved_at_utc":"2026-10-07T07:00:00Z"}))
            valid={
                "observation":{"cutoff_utc":"2026-10-07T07:00:00Z"},
                "retrieved_at_utc":"2026-10-07T07:00:00Z",
                "evidence_semantics":{"canonical_compatible":False,"evidence_role":"PROXY_ONLY","registered_threshold_compatibility":"UNCONFIRMED"},
                "aggregate":{"advancers":26,"decliners":72}
            }
            (base/"valid_owner.json").write_text(json.dumps(valid))
            row=breadth_context(root,datetime(2026,10,7,8,0,tzinfo=timezone.utc))
            self.assertIn(row["status"],{"CONTEXT_ONLY_PIT_UNVERIFIED","CONTEXT_ONLY_PIT_VERIFIED"})
            self.assertEqual(row["path"],"03_DAILY_CAPTURE_LOGS/breadth_rich/2026/10/07/valid_owner.json")
            self.assertEqual(row["aggregate"],{"advancers":26,"decliners":72})

    def test_breadth_context_with_only_non_owner_shapes_is_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            base=root/"03_DAILY_CAPTURE_LOGS/breadth_rich"
            base.mkdir(parents=True,exist_ok=True)
            (base/"raw_source_payload.json").write_text(json.dumps([1,2,3]))
            (base/"wrong_observation.json").write_text(json.dumps({"observation":[],"retrieved_at_utc":"2026-10-07T07:00:00Z"}))
            row=breadth_context(root,datetime(2026,10,7,8,0,tzinfo=timezone.utc))
            self.assertEqual(row["status"],"UNAVAILABLE")
            self.assertFalse(row["scoring_eligible"])

if __name__=="__main__":unittest.main()
