"""Adversarial contracts for the HRE design, source-clock and authority limits."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/validate_historical_reality_program_v1.py"
spec = importlib.util.spec_from_file_location("hre_validator", SCRIPT)
hre = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hre)


class HistoricalRealityDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q = json.loads((ROOT / "research/historical_reality_engine/RESEARCH_QUEUE_v1.json").read_text())
        cls.a = json.loads((ROOT / "research/historical_reality_engine/EPISODE_ATLAS_v1.json").read_text())

    def copies(self):
        return copy.deepcopy(self.q), copy.deepcopy(self.a)

    def test_design_passes_without_claiming_execution(self):
        q, a = self.copies()
        self.assertEqual(hre.inspect(q, a), [])
        self.assertTrue(q["activation"])
        self.assertTrue(q["owner_approval_receipt"].startswith("https://github.com/Donh91/"))
        self.assertTrue(all(t["completion_receipt"] is None for t in q["tasks"]))

    def test_rejects_unauthorized_paid_dispatch(self):
        q, a = self.copies()
        q["automatic_paid_sol"] = True
        self.assertIn("forbidden_authority:automatic_paid_sol", hre.inspect(q, a))

    def test_rejects_unauthorized_activation(self):
        q, a = self.copies()
        q.pop("owner_approval_receipt")
        self.assertIn("activation_without_authenticated_owner_receipt", hre.inspect(q, a))

    def test_rejects_duplicate_task(self):
        q, a = self.copies()
        q["tasks"].append(copy.deepcopy(q["tasks"][0]))
        self.assertIn("duplicate_task_id", hre.inspect(q, a))

    def test_rejects_dependency_cycle(self):
        q, a = self.copies()
        q["tasks"][0]["depends_on"] = ["HR-002"]
        self.assertIn("cyclic_dependencies", hre.inspect(q, a))

    def test_rejects_unowned_task(self):
        q, a = self.copies()
        q["tasks"][0]["original_owner_issue"] = ""
        self.assertTrue(any("no_original_owner" in err for err in hre.inspect(q, a)))

    def test_rejects_unverified_completion(self):
        q, a = self.copies()
        q["tasks"][0]["stage"] = "MERGED_MAIN_VERIFIED"
        self.assertTrue(any("completion_without_native_evidence" in err for err in hre.inspect(q, a)))

    def test_rejects_fabricated_forecast_accuracy(self):
        q, a = self.copies()
        a["episodes"][0]["forecast_accuracy"] = 0.98
        self.assertTrue(any("fabricated_unscored_outcome" in err for err in hre.inspect(q, a)))

    def test_rejects_historical_original_fabrication(self):
        q, a = self.copies()
        a["episodes"][0]["retrospective_original_policy"] = "ORIGINAL_ISSUED_2020"
        self.assertTrue(any("fabricated_original_era" in err for err in hre.inspect(q, a)))

    def test_rejects_future_vintage_in_wrong_window(self):
        q, a = self.copies()
        a["episodes"][0]["candidate_anchor_utc"] = "2026-11-07T00:00:00Z"
        self.assertTrue(any("outside_episode_window" in err for err in hre.inspect(q, a)))

    def test_rejects_source_pit_without_real_receipt(self):
        q, a = self.copies()
        a["episodes"][0]["feature_coverage"] = "ADMITTED"
        self.assertTrue(any("fake_source_admission" in err for err in hre.inspect(q, a)))

    def test_rejects_claimed_cross_family_skill_automation(self):
        q, a = self.copies()
        q["automatic_research_model_promotion"] = True
        self.assertTrue(any("automatic_research_model_promotion" in err for err in hre.inspect(q, a)))


if __name__ == "__main__":
    unittest.main()
