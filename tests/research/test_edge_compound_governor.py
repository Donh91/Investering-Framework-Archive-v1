import json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from scripts.research.edge_compound_governor import build

class EdgeCompoundGovernorTests(unittest.TestCase):

    def seed_owner_pair(self,root,horizons=None):
        horizons=horizons or {}
        m6=root/"research/framework_memory/m6_warning_events/LATEST.json";m6.parent.mkdir(parents=True,exist_ok=True)
        f=root/"research/framework_memory/edge001_tsunami_features/LATEST.json";f.parent.mkdir(parents=True,exist_ok=True)
        when="2026-10-07T00:00:00Z"
        event={"compass_id":"CMP-TEST","knowledge_timestamp":when,
            "episode_family_id":"M6F-20261007T000000Z","independent_family_weight":1.0,
            "horizons":horizons}
        m6.write_text(json.dumps({"integrity_revision":"v1.2_POST_KNOWLEDGE_BAR_INTEGRITY",
            "event_count":1,"provisional_independent_family_count":1,"events":[event]}))
        f.write_text(json.dumps({"integrity_revision":"v1.1_PIT_STRICT",
            "rows":[{"compass_id":"CMP-TEST","knowledge_timestamp":when}]}))

    def seed_empty_owners(self,root):
        m6=root/"research/framework_memory/m6_warning_events/LATEST.json";m6.parent.mkdir(parents=True,exist_ok=True)
        f=root/"research/framework_memory/edge001_tsunami_features/LATEST.json";f.parent.mkdir(parents=True,exist_ok=True)
        m6.write_text(json.dumps({"integrity_revision":"v1.2_POST_KNOWLEDGE_BAR_INTEGRITY","event_count":0,"events":[]}))
        f.write_text(json.dumps({"integrity_revision":"v1.1_PIT_STRICT","rows":[]}))


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
            self.seed_empty_owners(root)
            r=build(root,root/"out.json",root/"hist",datetime(2026,10,7,tzinfo=timezone.utc))
            self.assertEqual(r["decision"],"COLLECT")
            self.assertFalse(r["external_routing"]["sol_recommended"])
            self.assertFalse(r["external_routing"]["claude_recommended"])

    def test_new_7d_warning_family_never_implies_adverse_conclusion(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            self.seed_owner_pair(root,{"7d":{"maturity_state":"MATURED"}})
            cal=root/"research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json";cal.parent.mkdir(parents=True)
            cal.write_text(json.dumps({"eligible_series_row_count":0,"warning_series_row_count":0}))
            out=root/"out.json";hist=root/"hist"
            first=build(root,out,hist,datetime(2026,10,7,tzinfo=timezone.utc))
            self.assertEqual(first["deltas"],["INITIAL_GOVERNOR_SNAPSHOT"])
            self.assertEqual(first["decision"],"COLLECT")
            self.assertFalse(first["external_routing"]["sol_recommended"])
            self.assertFalse(first["external_routing"]["claude_recommended"])
            self.assertFalse(first["conclusion_layer"]["review_due"])
            # establish prior state with zero 7d family
            prior=json.loads(out.read_text());prior["semantic_state"]["matured_family_counts"]["7d"]=0
            out.write_text(json.dumps(prior))
            second=build(root,out,hist,datetime(2026,10,8,tzinfo=timezone.utc))
            self.assertEqual(second["decision"],"COLLECT")
            self.assertFalse(second["external_routing"]["sol_recommended"])
            self.assertFalse(second["external_routing"]["claude_recommended"])
            self.assertFalse(second["conclusion_layer"]["automatic_promotion"])
            self.assertFalse(second["conclusion_layer"]["review_due"])
            self.assertEqual(second["semantic_state"]["m6_family_semantics"],
                "PROVISIONAL_WARNING_OBSERVATION_CLUSTERS_NOT_PEAK_TROUGH_ADVERSE_FAMILIES")

    def test_out_of_order_m6_owner_blocks_fresh_governor(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            self.seed_owner_pair(root)
            m6=root/"research/framework_memory/m6_warning_events/LATEST.json"
            j=json.loads(m6.read_text());base=j["events"][0]
            j["events"]=[base,dict(base,compass_id="CMP-OLDER",knowledge_timestamp="2026-10-06T23:00:00Z",
                episode_family_id="M6F-20261007T000000Z",independent_family_weight=0.0)]
            j["event_count"]=2
            m6.write_text(json.dumps(j))
            out=build(root,root/"out.json",root/"history",datetime(2026,10,8,tzinfo=timezone.utc))
            self.assertEqual(out["decision"],"FALSIFY")
            self.assertIn("M6_EVENT_CHRONOLOGY_FAMILY_OR_COHORT_INVALID",out["semantic_state"]["blockers"])
            self.assertFalse(out["external_routing"]["automatic_dispatch"])

    def test_reconcile_stale_bootstrap_does_not_trigger_expensive_review(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            self.seed_owner_pair(root,{"7d":{"maturity_state":"MATURED"},"14d":{"maturity_state":"MATURED"}})
            out=root/"LATEST.json";history=root/"history";now=datetime(2026,10,8,tzinfo=timezone.utc)
            original=build(root,out,history,now)
            legacy=dict(original)
            legacy["decision"]="CONCLUSION_REVIEW"
            legacy["deltas"]=["INITIAL_GOVERNOR_SNAPSHOT"]
            legacy["external_routing"]={"sol_recommended":True,"claude_recommended":True,"automatic_dispatch":False}
            out.write_text(json.dumps(legacy))
            repaired=build(root,out,history,now)
            self.assertEqual(repaired["decision"],"COLLECT")
            self.assertEqual(repaired["deltas"],["LEGACY_BOOTSTRAP_FALSE_ESCALATION_SUPERSEDED_NO_NEW_EVIDENCE"])
            self.assertFalse(repaired["external_routing"]["sol_recommended"])
            self.assertFalse(repaired["external_routing"]["claude_recommended"])
            self.assertFalse(repaired["conclusion_layer"]["review_due"])
            self.assertEqual(repaired["prior_false_bootstrap_supersession"]["previous_decision"],"CONCLUSION_REVIEW")
            self.assertTrue(any(history.rglob("*.json")))
            self.assertFalse(build(root,out,history,now)["material_delta"])

if __name__=="__main__":unittest.main()
