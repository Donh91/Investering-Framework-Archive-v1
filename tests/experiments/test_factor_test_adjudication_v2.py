import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "factor_test_adjudication_v2.py"
SOURCE = ROOT / "04_RESEARCH_LAB" / "auto_trading" / "experiments" / "E3_TRIAL_N2_AGGREGATE_RESULT.json"
EXPECTED = ROOT / "04_RESEARCH_LAB" / "auto_trading" / "experiments" / "E3_TRIAL_N3_METHOD_CORRECTION_REPLAY.json"


def load_module():
    spec = importlib.util.spec_from_file_location("factor_test_adjudication_v2", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FactorTestAdjudicationV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()
        cls.source = json.loads(SOURCE.read_text())

    def test_trial_2_original_support_claim_is_not_authorized(self):
        result = self.mod.adjudicate(self.source)
        self.assertEqual(result["source_trial_n"], 2)
        self.assertEqual(result["method_trial_n"], 3)
        self.assertEqual(result["status"], "METHOD_REPLAY_NOT_SUPPORTED")
        self.assertFalse(result["historical_support_claim_authorized"])
        self.assertFalse(result["independent_evidence"])
        self.assertEqual(result["eligible_normalized_transforms"], [])

    def test_all_normalized_transforms_fail_positive_oos_gate(self):
        result = self.mod.adjudicate(self.source)
        for row in result["transform_checks"].values():
            self.assertFalse(row["passed"])
            self.assertFalse(row["rules"]["combined_oos_ic_positive"])
            self.assertFalse(row["rules"]["btc_oos_ic_positive"])
            self.assertFalse(row["rules"]["eth_oos_ic_positive"])

    def test_replay_artifact_is_byte_reproducible(self):
        result = self.mod.adjudicate(self.source)
        self.assertEqual(EXPECTED.read_bytes(), self.mod.canon(result))

    def test_authority_remains_research_only(self):
        result = self.mod.adjudicate(self.source)
        self.assertTrue(result["authority"]["research_only"])
        self.assertFalse(result["authority"]["portfolio_execution"])
        self.assertFalse(result["authority"]["automatic_promotion"])


if __name__ == "__main__":
    unittest.main()
