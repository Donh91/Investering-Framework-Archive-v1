import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "factor_test_admission.py"
E1 = ROOT / "04_RESEARCH_LAB" / "auto_trading" / "experiments" / "E1_LEAKAGE_VALIDATION_RESULT_v1.json"
CANDIDATE = ROOT / "research" / "experiment_lifecycle" / "candidates" / "2026" / "09" / "EC-2ea2db92815b9e670a8e.json"
ADMISSION = ROOT / "research" / "experiment_lifecycle" / "admission" / "2026" / "09" / "EC-2ea2db92815b9e670a8e.json"


def load_module():
    spec = importlib.util.spec_from_file_location("factor_test_admission", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FactorTestCommittedRegistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_committed_factor_candidate_and_admission_are_builder_reproducible(self):
        candidate = json.loads(CANDIDATE.read_text())
        admission = json.loads(ADMISSION.read_text())
        e1 = json.loads(E1.read_text())
        rebuilt_candidate, rebuilt_admission = self.mod.build_records(candidate["spec"], e1, candidate["created_at_utc"])
        self.assertEqual(candidate, rebuilt_candidate)
        self.assertEqual(admission, rebuilt_admission)
        self.assertEqual(candidate["spec"]["kind"], "FACTOR_TEST")
        self.assertEqual(admission["status"], "QUALIFIED_FOR_FORWARD_TEST")
        self.assertEqual(candidate["spec"]["factor_design"]["proposal_trial_n"], 4)
        self.assertFalse(admission["authority"]["portfolio_execution"])


if __name__ == "__main__":
    unittest.main()
