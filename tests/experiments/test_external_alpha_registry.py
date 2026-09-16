import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "external_alpha_registry.py"
REGISTRY = ROOT / "04_RESEARCH_LAB" / "auto_trading" / "external_alpha" / "EXTERNAL_ALPHA_REGISTRY.json"


def load_module():
    spec = importlib.util.spec_from_file_location("external_alpha_registry", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ExternalAlphaRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        cls.registry = json.loads(REGISTRY.read_text())

    def candidate(self, candidate_id):
        return next(c for c in self.registry["candidates"] if c["candidate_id"] == candidate_id)

    def test_seed_registry_is_valid(self):
        self.assertEqual(self.module.validate_registry(self.registry), [])
        self.assertEqual(len(self.registry["candidates"]), 4)
        self.assertEqual(
            [c["candidate_id"] for c in self.registry["candidates"]],
            ["EXT-ALPHA-0001", "EXT-ALPHA-0002", "EXT-ALPHA-0003", "EXT-ALPHA-0004"],
        )

    def test_expected_scores_are_deterministic(self):
        expected = {
            "EXT-ALPHA-0001": (53, "RESEARCH_QUEUE"),
            "EXT-ALPHA-0002": (76, "REVERSE_ENGINEER"),
            "EXT-ALPHA-0003": (61, "RESEARCH_QUEUE"),
            "EXT-ALPHA-0004": (68, "RESEARCH_QUEUE"),
        }
        for candidate_id, (score, decision) in expected.items():
            result = self.module.score_candidate(self.candidate(candidate_id))
            self.assertEqual(result["score"], score)
            self.assertEqual(result["decision"], decision)

    def test_marketing_only_candidate_is_hard_capped(self):
        candidate = copy.deepcopy(self.candidate("EXT-ALPHA-0002"))
        candidate["evidence"]["marketing_only"] = True
        result = self.module.score_candidate(candidate)
        self.assertEqual(result["score"], 24)
        self.assertEqual(result["decision"], "REJECT")
        self.assertIn("MARKETING_ONLY", {cap["reason"] for cap in result["caps"]})

    def test_selective_winner_feed_cannot_enter_research_queue(self):
        candidate = copy.deepcopy(self.candidate("EXT-ALPHA-0002"))
        candidate["evidence"]["loser_coverage"] = "SELECTIVE"
        candidate["evidence"]["selective_winners_only"] = True
        result = self.module.score_candidate(candidate)
        self.assertEqual(result["score"], 29)
        self.assertEqual(result["decision"], "REJECT")

    def test_ambiguous_identity_is_hard_capped(self):
        candidate = copy.deepcopy(self.candidate("EXT-ALPHA-0002"))
        candidate["evidence"]["identity_status"] = "AMBIGUOUS"
        result = self.module.score_candidate(candidate)
        self.assertEqual(result["score"], 29)
        self.assertEqual(result["decision"], "REJECT")

    def test_no_falsifier_blocks_reverse_engineering(self):
        candidate = copy.deepcopy(self.candidate("EXT-ALPHA-0002"))
        candidate["evidence"]["falsifier_defined"] = False
        result = self.module.score_candidate(candidate)
        self.assertLess(result["score"], 50)
        self.assertEqual(result["decision"], "WATCH")

    def test_copyability_cannot_be_verified_before_source_alpha(self):
        candidate = copy.deepcopy(self.candidate("EXT-ALPHA-0001"))
        candidate["rulings"]["copyability"] = "VERIFIED"
        errors = self.module.validate_candidate(candidate)
        self.assertTrue(any("copyability VERIFIED requires source_alpha VERIFIED" in e for e in errors))

    def test_scalability_cannot_be_verified_before_copyability(self):
        candidate = copy.deepcopy(self.candidate("EXT-ALPHA-0001"))
        candidate["rulings"]["source_alpha"] = "VERIFIED"
        candidate["rulings"]["scalability"] = "VERIFIED"
        errors = self.module.validate_candidate(candidate)
        self.assertTrue(any("scalability VERIFIED requires copyability VERIFIED" in e for e in errors))

    def test_transfer_candidate_requires_verified_source_and_copy_alpha(self):
        candidate = copy.deepcopy(self.candidate("EXT-ALPHA-0001"))
        candidate["promotion_state"] = "TRANSFER_CANDIDATE"
        errors = self.module.validate_candidate(candidate)
        self.assertTrue(any("TRANSFER_CANDIDATE requires source_alpha VERIFIED" in e for e in errors))
        self.assertTrue(any("TRANSFER_CANDIDATE requires copyability VERIFIED" in e for e in errors))

    def test_meta_learning_is_locked_for_seed_registry(self):
        gate = self.module.meta_learning_gate(self.registry)
        self.assertEqual(gate["status"], "LOCKED")
        self.assertEqual(gate["counts"]["candidates_at_source_alpha_stage"], 0)
        self.assertEqual(gate["counts"]["settled_source_alpha_rulings"], 0)
        self.assertEqual(gate["counts"]["settled_copyability_rulings"], 0)

    def test_meta_learning_unlocks_only_when_all_thresholds_pass(self):
        registry = copy.deepcopy(self.registry)
        template = copy.deepcopy(self.candidate("EXT-ALPHA-0002"))
        registry["candidates"] = []
        for index in range(5):
            candidate = copy.deepcopy(template)
            candidate["candidate_id"] = f"EXT-ALPHA-{1000 + index:04d}"
            candidate["current_stage"] = "SOURCE_ALPHA"
            candidate["promotion_state"] = "RESEARCH_ONLY"
            if index < 3:
                candidate["rulings"]["source_alpha"] = "VERIFIED"
            else:
                candidate["rulings"]["source_alpha"] = "PENDING"
            if index < 2:
                candidate["rulings"]["copyability"] = "VERIFIED"
            else:
                candidate["rulings"]["copyability"] = "PENDING"
            registry["candidates"].append(candidate)

        gate = self.module.meta_learning_gate(registry)
        self.assertEqual(gate["status"], "UNLOCKED")


if __name__ == "__main__":
    unittest.main()
