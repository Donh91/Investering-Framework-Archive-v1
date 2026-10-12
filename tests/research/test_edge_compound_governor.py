import json,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from scripts.research.edge_compound_governor import build

class EdgeCompoundGovernorTests(unittest.TestCase):

    def seed_owner_pair(self,root,horizons=None):
        horizons=horizons or {}
        m6=root/"research/framework_memory/m6_warning_events/LATEST.json";m6.parent.mkdir(parents=True,exist_ok=True)
        f=root/"research/framework_memory/edge001_tsunami_features/LATEST.json";f.parent.mkdir(parents=True,exist_ok=True)
        when="2026-10-07T00:00:00Z"
        # A synthetic MATURED outcome must include the frozen complete path
        # contract. A bare maturity string is deliberately insufficient.
        start=datetime.fromisoformat(when.replace("Z","+00:00"))
        expanded={}
        for name,row in horizons.items():
            h=dict(row)
            if h.get("maturity_state")=="MATURED":
                hours={"24h":24,"72h":72,"7d":168,"14d":336,"30d":720}[name]
                target=(start+timedelta(hours=hours)).isoformat().replace("+00:00","Z")
                first=(start+timedelta(hours=1)).isoformat().replace("+00:00","Z")
                outcome={"state":"MATURED",
                    "reference_anchor":{"price":100.0,"mae_pct":-1.0,"mfe_pct":2.0,"terminal_return_pct":0.0},
                    "post_knowledge_close_anchor":{"timestamp":first,"price":100.0,
                        "mae_pct":-1.0,"mfe_pct":2.0,"terminal_return_pct":0.0},
                    "terminal":{"timestamp":target,"close":100.0},
                    "adverse_barriers":{"-10.0":{"touched":False}}}
                h.update({"target_at_utc":target,
                    "coverage":{"reason":"COMPLETE_HOURLY_CLOSE_GRID",
                        "row_count":hours,"max_gap_hours":1.0},
                    "BTC":outcome,"ETH":json.loads(json.dumps(outcome))})
            expanded[name]=h
        horizons=expanded
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

    def test_complete_matured_outcome_evidence_is_structurally_valid(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            self.seed_owner_pair(root,{"24h":{"maturity_state":"MATURED"},
                                       "72h":{"maturity_state":"PENDING"}})
            result=build(root,root/"out.json",root/"history",datetime(2026,10,8,tzinfo=timezone.utc))
            integrity=result["semantic_state"]["m6_matured_payload_integrity"]
            self.assertEqual(integrity["status"],"PASS")
            self.assertEqual(integrity["checked"],1)
            self.assertEqual(integrity["invalid"],0)
            self.assertNotIn("M6_MATURED_OUTCOME_PAYLOAD_INVALID",result["semantic_state"]["blockers"])
            self.assertEqual(result["decision"],"COLLECT")
            self.assertFalse(result["external_routing"]["automatic_dispatch"])

    def test_malformed_matured_asset_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            self.seed_owner_pair(root,{"7d":{"maturity_state":"MATURED"}})
            path=root/"research/framework_memory/m6_warning_events/LATEST.json"
            owner=json.loads(path.read_text())
            del owner["events"][0]["horizons"]["7d"]["ETH"]["post_knowledge_close_anchor"]
            path.write_text(json.dumps(owner))
            result=build(root,root/"out.json",root/"history",datetime(2026,10,15,tzinfo=timezone.utc))
            self.assertEqual(result["decision"],"FALSIFY")
            self.assertEqual(result["semantic_state"]["m6_matured_payload_integrity"]["status"],"BLOCKED")
            self.assertIn("M6_MATURED_OUTCOME_PAYLOAD_INVALID",result["semantic_state"]["blockers"])
            self.assertFalse(result["external_routing"]["automatic_dispatch"])

    def test_false_full_grid_is_not_matured_payload_pass(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            self.seed_owner_pair(root,{"24h":{"maturity_state":"MATURED"}})
            path=root/"research/framework_memory/m6_warning_events/LATEST.json"
            owner=json.loads(path.read_text())
            owner["events"][0]["horizons"]["24h"]["coverage"]["row_count"]=5
            path.write_text(json.dumps(owner))
            result=build(root,root/"out.json",root/"history",datetime(2026,10,8,tzinfo=timezone.utc))
            self.assertEqual(result["decision"],"FALSIFY")
            self.assertEqual(result["semantic_state"]["m6_matured_payload_integrity"]["checked"],1)
            self.assertEqual(result["semantic_state"]["m6_matured_payload_integrity"]["invalid"],1)

    def test_no_matured_horizons_are_not_evidence_of_edge(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            self.seed_owner_pair(root,{"30d":{"maturity_state":"PENDING"}})
            result=build(root,root/"out.json",root/"history",datetime(2026,10,8,tzinfo=timezone.utc))
            integrity=result["semantic_state"]["m6_matured_payload_integrity"]
            self.assertEqual(integrity["status"],"PASS_NO_MATURED_YET")
            self.assertEqual(integrity["checked"],0)
            self.assertEqual(result["semantic_state"]["information_edge_claim"],"NOT_ESTABLISHED")
            self.assertEqual(result["semantic_state"]["economic_action_edge_claim"],"NOT_ESTABLISHED")

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
            legacy["semantic_fingerprint"]="STALE_PRE_FIX_FINGERPRINT"
            legacy["deltas"]=["INITIAL_GOVERNOR_SNAPSHOT"]
            legacy["external_routing"]={"sol_recommended":True,"claude_recommended":True,"automatic_dispatch":False}
            out.write_text(json.dumps(legacy))
            repaired=build(root,out,history,now)
            self.assertEqual(repaired["decision"],"NOOP")
            self.assertEqual(repaired["deltas"],["LEGACY_BOOTSTRAP_FALSE_ESCALATION_SUPERSEDED"])
            self.assertFalse(repaired["external_routing"]["sol_recommended"])
            self.assertFalse(repaired["external_routing"]["claude_recommended"])
            self.assertFalse(repaired["conclusion_layer"]["review_due"])
            self.assertEqual(repaired["prior_false_bootstrap_supersession"]["previous_decision"],"CONCLUSION_REVIEW")
            entries=sorted(history.rglob("*.json"))
            self.assertEqual(len(entries),2)
            self.assertEqual(sorted(json.loads(p.read_text())["decision"] for p in entries),["COLLECT","NOOP"])
            self.assertTrue(any(p.stem.endswith("-bootstrap-supersession") for p in entries))
            self.assertFalse(build(root,out,history,now)["material_delta"])
            self.assertEqual(len(list(history.rglob("*.json"))),2)

if __name__=="__main__":unittest.main()
