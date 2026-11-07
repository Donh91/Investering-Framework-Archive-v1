"""Proposal-only Kompas scientific 10-lane program, adversarial authority tests.

No network, paid API, GH job dispatch, model promotion, trading or S1 action.
"""
import copy
import json
import unittest
from pathlib import Path

from scripts.research import validate_kompas_scientific_edge_program_v2_1 as v

REPO=Path(__file__).resolve().parents[2]

class KompasScientificProgramContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program=json.loads((REPO/v.MISSION).read_text())
        cls.receipt=json.loads((REPO/v.RECEIPT).read_text())

    def test_static_program_validates_and_real_paths_exist(self):
        self.assertEqual(v.validate_manifest(self.program),[])
        self.assertEqual(v.validate_receipt(self.receipt),[])
        self.assertEqual(v.validate_bundle(REPO),[])

    def test_ten_distinct_falsifiable_questions_and_genuine_owners(self):
        lanes=self.program["lanes"]
        self.assertEqual([x["lane_id"] for x in lanes],[f"L{i:02d}" for i in range(1,11)])
        self.assertEqual(len({x["hypothesis"] for x in lanes}),10)
        self.assertEqual(len({x["falsifier"] for x in lanes}),10)
        self.assertTrue(all(x["original_owner_issue"] in {1596,1156,1827,1516,1553,1530,1593} for x in lanes))
        self.assertTrue(all(x["first_source_anchor_blob_sha"] for x in lanes))
        self.assertTrue(all(x["reactivation_trigger"] for x in lanes))
        self.assertEqual(self.program["max_simultaneous_compute_jobs"],3)

    def test_no_duplicate_control_plane_or_implicit_paid_permission(self):
        self.assertTrue(self.program["no_new_supervisor"])
        self.assertTrue(self.program["no_new_workflow"])
        self.assertTrue(self.program["no_new_schedule"])
        self.assertTrue(self.program["no_new_github_identity"])
        self.assertFalse(self.program["approval_is_api_payment_release"])
        self.assertFalse(self.program["approval_is_release_permission"])
        self.assertEqual(self.program["max_automatic_paid_usd"],0)
        self.assertFalse(self.program["restricted_round3_outcome_scoring_allowed"])
        self.assertFalse(self.program["restricted_round3_hypothesis_testing_allowed"])

    def test_authority_bypass_and_paid_api_tamper_are_rejected(self):
        j=copy.deepcopy(self.program)
        j["no_new_supervisor"]=False
        j["approved_paid_spend_in_this_proposal_usd"]=8
        j["restricted_round3_outcome_scoring_allowed"]=True
        errors=v.validate_manifest(j)
        self.assertIn("authority_broadened:no_new_supervisor",errors)
        self.assertIn("paid_release_without_native_gate",errors)
        self.assertIn("permission_bypass:restricted_round3_outcome_scoring_allowed",errors)

    def test_approval_receipt_is_exact_and_does_not_grant_api_release(self):
        j=copy.deepcopy(self.program)
        self.assertEqual(j["proposal_state"], "OWNER_APPROVED_PLAN_RELEASE_GATED")
        self.assertIn("issuecomment-6711560934", j["owner_approval_receipt"])
        j["owner_approval_receipt"]="https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596#issuecomment-FAKE"
        j["approval_is_api_payment_release"]=True
        e=v.validate_manifest(j)
        self.assertIn("missing_authenticated_owner_approval_record",e)
        self.assertIn("permission_bypass:approval_is_api_payment_release",e)

    def test_w46_priority_and_monday_s1_freeze_cannot_be_removed(self):
        j=copy.deepcopy(self.program)
        j["next_w46_local_date"]="2026-11-16"
        j["w46_priority"]=False
        j["monday_readonly_copenhagen"]="09:00-09:30"
        j["wave_sequence"][0]["lanes"].remove("L06")
        e=v.validate_manifest(j)
        self.assertIn("first_w46_priority_changed",e)
        self.assertIn("s1_monday_gate_changed",e)
        self.assertIn("waveA_w46_protection",e)

    def test_original_source_first_known_cannot_be_fabricated(self):
        j=copy.deepcopy(self.program)
        lane=j["lanes"][1]
        lane["source_first_known_at_utc"]="2026-10-12T00:00:00Z"
        lane["source_pit_admission"]="FULLY_ADMITTED"
        lane["release_claim_allowed"]=True
        e=v.validate_manifest(j)
        self.assertIn("L02:fabricated_evidence:source_first_known_at_utc",e)
        self.assertIn("L02:scientific_or_release_bypass",e)

    def test_no_ten_fake_ai_agents_from_ten_research_rows(self):
        j=copy.deepcopy(self.program)
        j["lanes"][9]["actual_ai_agent_execution_id"]="GROK_UNVERIFIED"
        j["lanes"][9]["status"]="COMPLETE_VERIFIED"
        j["lanes"][9]["result_claim"]="FULLY_VALIDATED"
        e=v.validate_manifest(j)
        self.assertIn("L10:fabricated_evidence:actual_ai_agent_execution_id",e)
        self.assertIn("L10:fake_execution_status",e)
        self.assertIn("L10:preclaimed_result",e)

    def test_graph_cycles_unknown_source_and_duplicate_lane_fail(self):
        j=copy.deepcopy(self.program)
        j["lanes"][0]["depends_on"]=["L10"]
        e=v.validate_manifest(j)
        self.assertTrue(any(x.startswith("dependency_cycle:") for x in e))
        j=copy.deepcopy(self.program)
        j["lanes"][0]["depends_on"]=["L99"]
        self.assertTrue(any(x.startswith("unknown_dependency:") for x in v.validate_manifest(j)))
        j=copy.deepcopy(self.program)
        j["lanes"][0]["lane_id"]="L02"
        self.assertIn("lane_roster_or_duplicate",v.validate_manifest(j))

    def test_no_secret_or_traversal_source_in_public_manifest(self):
        j=copy.deepcopy(self.program)
        j["lanes"][0]["first_source_anchor_path"]="../../Donh91/secrets/raw"
        self.assertIn("L01:unsafe_source_path",v.validate_manifest(j))

    def test_template_does_not_claim_workflow_or_s1_success(self):
        j=copy.deepcopy(self.receipt)
        j["execution"]["native_workflow_run_id"]=123
        j["execution"]["naturally_scheduled_s1_own_merge"]=True
        j["execution"]["actual_approval_receipt_url"]="https://example.com/fake"
        j["change"]["merge_sha"]="0"*40
        j["closure"]["predictive_edge_proven"]=True
        e=v.validate_receipt(j)
        self.assertIn("template_execution_fabricated:native_workflow_run_id",e)
        self.assertIn("template_execution_fabricated:actual_approval_receipt_url",e)
        self.assertIn("template_claims_authority:naturally_scheduled_s1_own_merge",e)
        self.assertIn("template_fake_merge",e)
        self.assertIn("template_unproven_result:predictive_edge_proven",e)

    def test_time_machine_scope_and_optimistic_outcomes_rejected(self):
        j=copy.deepcopy(self.program)
        j["historical_reality_engine"]="NEW_TIME_MACHINE"
        j["lanes"][0]["finding_disposition"]="PRODUCTION_READY"
        j["lanes"][0]["actual_native_run_id"]=987
        e=v.validate_manifest(j)
        self.assertIn("time_machine_scope_collision",e)
        self.assertIn("L01:predeclared_finding",e)
        self.assertIn("L01:fabricated_evidence:actual_native_run_id",e)

if __name__=="__main__":
    unittest.main()
