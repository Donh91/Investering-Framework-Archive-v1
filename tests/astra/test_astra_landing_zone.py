import importlib.util
import json
from copy import deepcopy
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/astra/validate_astra_landing_zone.py"
SPEC = importlib.util.spec_from_file_location("astra_lz_validator", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)

EXAMPLE = ROOT / "07_PROMPTS_AND_AGENTS/astra/examples/ASTRA_LANDING_ZONE_VALID_EXAMPLE_v1.json"


class AstraLandingZoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_repository_contracts_exist_and_parse(self):
        self.assertEqual(MOD.validate_repository(ROOT), [])

    def test_valid_blind_example_passes(self):
        self.assertEqual(MOD.validate_run(deepcopy(self.valid)), [])

    def test_duplicate_question_without_adversarial_or_replication_fails(self):
        run = deepcopy(self.valid)
        run["execution_mode"] = "STANDARD"
        run["assignments"][0]["mode"] = "STANDARD"
        run["assignments"][1]["mode"] = "STANDARD"
        run["assignments"][0]["blind_group"] = None
        run["assignments"][1]["blind_group"] = None
        errors = MOD.validate_run(run)
        self.assertTrue(any("duplicate question_hash" in e for e in errors))

    def test_lookahead_evidence_cannot_be_used_for_decision(self):
        run = deepcopy(self.valid)
        run["evidence"][0]["observable_at"] = "2026-09-10T00:00:00Z"
        errors = MOD.validate_run(run)
        self.assertTrue(any("look-ahead" in e for e in errors))

    def test_quarantined_evidence_cannot_be_decision_evidence(self):
        run = deepcopy(self.valid)
        run["evidence"][0]["leakage_status"] = "QUARANTINED_LOOKAHEAD"
        errors = MOD.validate_run(run)
        self.assertTrue(any("not POINT_IN_TIME_VALID" in e for e in errors))

    def test_blind_opposition_requires_commit_before_reveal(self):
        run = deepcopy(self.valid)
        run["assignments"][1]["committed_before_reveal"] = False
        errors = MOD.validate_run(run)
        self.assertTrue(any("committed_before_reveal" in e for e in errors))

    def test_token_budget_preserves_escalation_reserve(self):
        run = deepcopy(self.valid)
        run["assignments"][0]["token_budget"] = 30000
        run["assignments"][1]["token_budget"] = 30000
        errors = MOD.validate_run(run)
        self.assertTrue(any("escalation reserve" in e for e in errors))

    def test_utility_cannot_auto_prune_in_v1(self):
        run = deepcopy(self.valid)
        run["utility_policy"]["auto_pruning_enabled"] = True
        errors = MOD.validate_run(run)
        self.assertTrue(any("auto_pruning_enabled" in e for e in errors))

    def test_market_or_trade_authority_cannot_be_granted(self):
        run = deepcopy(self.valid)
        run["authority"]["trade_action"] = True
        errors = MOD.validate_run(run)
        self.assertTrue(any("authority.trade_action" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
