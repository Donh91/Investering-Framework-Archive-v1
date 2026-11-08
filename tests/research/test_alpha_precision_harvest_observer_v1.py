"""Adversarial safety checks for no-dispatch Alpha Precision original-owner observer."""
import copy
import json
import unittest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/research/alpha_precision_harvest_observer_v1.py"
spec = spec_from_file_location("alpha_precision_harvest_observer_v1", MODULE_PATH)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

MANIFEST = "04_RESEARCH_LAB/external_specialist_dissection/2026-11-07__ALPHA_RESEARCH_PRECISION_PARALLEL_LANES_v1.json"
ROUTES = "04_RESEARCH_LAB/external_specialist_dissection/alpha_precision_20261107/OWNER_ROUTING_V1.json"

class AlphaPrecisionObserverTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load(MANIFEST)
        self.routes = load(ROUTES)
        self.budget = {"github_actions":{"status":"UNKNOWN","usage":None},
                       "billing_hard_stop_verified": False}

    def test_unknown_budget_gates_all_unrun_github_jobs(self):
        r = mod.observe(self.manifest, self.routes, self.budget)
        assert r["github_actions_account_usage"] == "UNKNOWN_OR_UNATTESTED"
        original = {l["id"]: l for l in self.manifest["lanes"]}
        for lane in r["lanes"]:
            assert lane["automatic_dispatch"] is False
            assert lane["science_admitted"] is False
            if original[lane["id"]]["executor_kind"] == "GITHUB_JOB" and original[lane["id"]]["status"] == "PLANNED":
                assert lane["action_gate"] == "GITHUB_ACTIONS_ACCOUNT_USAGE_UNKNOWN_NO_JOB_DISPATCH"

    def test_even_verified_budget_is_not_research_dispatch_authority(self):
        b = {"github_actions":{"status":"VERIFIED","usage":0},"billing_hard_stop_verified": True}
        r = mod.observe(self.manifest, self.routes, b)
        assert r["github_job_dispatch_authorized"] is False
        assert not any(x["automatic_dispatch"] for x in r["lanes"])

    def test_a_claim_of_completed_lane_is_not_scientific_promotion(self):
        m = copy.deepcopy(self.manifest)
        m["lanes"][0]["status"] = "COMPLETE_VERIFIED"
        r = mod.observe(m, self.routes, self.budget)
        assert r["lanes"][0]["science_admitted"] is False
        assert r["lanes"][0]["action_gate"] == "VERIFY_NATIVE_RECEIPT_AND_SCIENCE_INDEPENDENTLY"

    def test_authority_tamper_fails_closed(self):
        r = copy.deepcopy(self.routes)
        r["automatic_execution_authorized"] = True
        with self.assertRaises(ValueError):
            mod.observe(self.manifest, r, self.budget)

    def test_route_mismatch_fails_closed(self):
        r = copy.deepcopy(self.routes)
        r["lanes"][7]["id"] = "L01"
        with self.assertRaises(ValueError):
            mod.observe(self.manifest, r, self.budget)

    def test_deterministic_no_churn_receipt(self):
        a = mod.observe(self.manifest, self.routes, self.budget)
        b = mod.observe(self.manifest, self.routes, self.budget)
        self.assertEqual(a,b)
        self.assertNotIn("run_evidence", json.dumps(a))
        self.assertNotIn("original_alpha_pr", json.dumps(a))

if __name__ == "__main__":
    unittest.main()
