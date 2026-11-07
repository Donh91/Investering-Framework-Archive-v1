"""Deterministic negative and positive fixtures for Research Parallel Lanes v1.
Do not mistake these tests for real GitHub/AI execution or A/B efficacy.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/"scripts"/"research"/"validate_parallel_research_manifest_v1.py"
EXAMPLE=ROOT/".agents"/"skills"/"research-parallel-lanes"/"references"/"EXAMPLE_MISSION.json"
spec=importlib.util.spec_from_file_location("research_parallel_manifest_validator",SCRIPT)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ResearchParallelLanesManifestContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example=json.loads(EXAMPLE.read_text(encoding="utf8"))
    def sample(self):
        return copy.deepcopy(self.example)
    def test_plan_only_3_independent_lanes_valid(self):
        d=self.sample()
        self.assertEqual(mod.validate(d),[])
        self.assertEqual(d["no_new_scheduler"],True)
    def test_refuse_new_scheduler_and_trading_authority(self):
        d=self.sample()
        d["no_new_scheduler"]=False
        d["no_trading_authority"]=False
        errors=mod.validate(d)
        self.assertTrue(any("no_new_scheduler" in x for x in errors))
        self.assertTrue(any("no_trading_authority" in x for x in errors))
    def test_refuse_fabricated_agent_success(self):
        d=self.sample()
        d["lanes"][0]["executor_kind"]="EXISTING_AI_AGENT"
        d["lanes"][0]["status"]="COMPLETE_VERIFIED"
        errors=mod.validate(d)
        self.assertTrue(any("native execution" in x for x in errors))
    def test_refuse_green_job_without_native_receipts(self):
        d=self.sample()
        d["lanes"][1]["status"]="COMPLETE_VERIFIED"
        self.assertTrue(any("job requires positive" in x for x in mod.validate(d)))
        self.assertTrue(any("artifact_sha256" in x for x in mod.validate(d)))
    def test_accept_complete_job_receipt_schema_but_not_claim_authenticity(self):
        d=self.sample()
        d["lanes"][0]["status"]="COMPLETE_VERIFIED"
        d["lanes"][0]["run_evidence"]={
            "workflow_run_id":12,"job_id":34,"artifact_id":56,
            "exact_head_sha":"a"*40,"artifact_sha256":"b"*64,"conclusion":"success"}
        self.assertEqual(mod.validate(d),[])
    def test_source_and_budget_must_be_bound(self):
        d=self.sample()
        d["source_snapshot_sha"]="main"
        d["lanes"][0]["budget_usd"]=2
        x=mod.validate(d)
        self.assertTrue(any("source_snapshot_sha" in e for e in x))
        self.assertTrue(any("budget" in e for e in x))
    def test_duplicate_writer_path_is_rejected(self):
        d=self.sample()
        d["lanes"][2]["output_path"]=d["lanes"][0]["output_path"]
        self.assertTrue(any("parallel write conflict" in e for e in mod.validate(d)))
    def test_bad_dependency_unknown_and_cycle(self):
        d=self.sample()
        d["lanes"][0]["depends_on"]=["L02"]
        d["lanes"][1]["depends_on"]=["L01"]
        x=mod.validate(d)
        self.assertTrue(any("dependency cycle" in e for e in x))
        d=self.sample()
        d["lanes"][2]["depends_on"]=["L99"]
        self.assertTrue(any("unknown/self" in e for e in mod.validate(d)))
    def test_reject_false_complete_when_prerequisite_unverified(self):
        d=self.sample()
        d["lanes"][0]["status"]="COMPLETE_VERIFIED"
        d["lanes"][0]["depends_on"]=["L03"]
        d["lanes"][0]["run_evidence"]={
            "workflow_run_id":12,"job_id":34,"artifact_id":56,
            "exact_head_sha":"a"*40,"artifact_sha256":"b"*64,"conclusion":"success"}
        self.assertTrue(any("dependency" in e and "not verified" in e for e in mod.validate(d)))
    def test_reject_restricted_public_output_and_one_lane(self):
        d=self.sample()
        d["lanes"][0]["output_path"]="Donh91/secrets/private_payload.json"
        self.assertTrue(any("nonrestricted" in e for e in mod.validate(d)))
        d=self.sample()
        d["lanes"]=d["lanes"][:1]
        self.assertTrue(any("2..10" in e for e in mod.validate(d)))
    def test_reject_success_on_planned_and_bare_failed(self):
        d=self.sample()
        d["lanes"][0]["run_evidence"]={"conclusion":"success"}
        self.assertTrue(any("planning-only" in e for e in mod.validate(d)))
        d=self.sample()
        d["lanes"][0]["status"]="FAILED_EVIDENCED"
        self.assertTrue(any("failure receipt" in e for e in mod.validate(d)))

if __name__=="__main__":unittest.main()
