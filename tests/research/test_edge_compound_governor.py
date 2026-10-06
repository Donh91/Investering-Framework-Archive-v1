import json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from scripts.research.edge_compound_governor import build

class EdgeCompoundGovernorTests(unittest.TestCase):
    def test_empty_repo_fails_closed_without_external_dispatch(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);out=root/"out.json";hist=root/"hist"
            r=build(root,out,hist,datetime(2026,10,7,tzinfo=timezone.utc))
            self.assertTrue(r["material_delta"])
            self.assertFalse(r["external_routing"]["automatic_dispatch"])
            self.assertFalse(r["authority"]["portfolio_action"])
            self.assertEqual(r["rules"]["live_exit_rule"],"NONE")

    def test_building_collects_without_external_review(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            ptr=root/"04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json";ptr.parent.mkdir(parents=True)
            freeze=root/"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/07/CMP-x.json";freeze.parent.mkdir(parents=True)
            freeze.write_text(json.dumps({"protection_tracker":{"pullback_risk_state":"BUILDING","distribution_risk":"NONE"}}))
            ptr.write_text(json.dumps({"compass_path":freeze.relative_to(root).as_posix()}))
            r=build(root,root/"out.json",root/"hist",datetime(2026,10,7,tzinfo=timezone.utc))
            self.assertEqual(r["decision"],"COLLECT")
            self.assertFalse(r["external_routing"]["sol_recommended"])
            self.assertFalse(r["external_routing"]["claude_recommended"])

    def test_strict_collectors_with_new_7d_family_recommend_sol_only(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            m6=root/"research/framework_memory/m6_warning_events/LATEST.json";m6.parent.mkdir(parents=True)
            feat=root/"research/framework_memory/edge001_tsunami_features/LATEST.json";feat.parent.mkdir(parents=True)
            cal=root/"research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json";cal.parent.mkdir(parents=True)
            m6.write_text(json.dumps({"integrity_revision":"v1.1_STRICT_TAPE_AND_ANCHOR","event_count":1,"provisional_independent_family_count":1,
                "events":[{"episode_family_id":"F1","horizons":{"7d":{"maturity_state":"MATURED"}}}]}))
            feat.write_text(json.dumps({"integrity_revision":"v1.1_PIT_STRICT","rows":[]}))
            cal.write_text(json.dumps({"eligible_series_row_count":0,"warning_series_row_count":0}))
            out=root/"out.json";hist=root/"hist"
            first=build(root,out,hist,datetime(2026,10,7,tzinfo=timezone.utc))
            # establish prior state with zero 7d family
            prior=json.loads(out.read_text());prior["semantic_state"]["matured_family_counts"]["7d"]=0
            out.write_text(json.dumps(prior))
            second=build(root,out,hist,datetime(2026,10,8,tzinfo=timezone.utc))
            self.assertEqual(second["decision"],"CONCLUSION_REVIEW")
            self.assertTrue(second["external_routing"]["sol_recommended"])
            self.assertFalse(second["external_routing"]["claude_recommended"])
            self.assertFalse(second["conclusion_layer"]["automatic_promotion"])

if __name__=="__main__":unittest.main()
