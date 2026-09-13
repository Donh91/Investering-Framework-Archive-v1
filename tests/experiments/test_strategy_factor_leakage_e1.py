import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "scripts" / "experiments" / "strategy_factor_leakage_e1.py"
ARTIFACT = ROOT / "04_RESEARCH_LAB" / "auto_trading" / "experiments" / "E1_LEAKAGE_VALIDATION_RESULT_v1.json"


def load_module():
    spec = importlib.util.spec_from_file_location("strategy_factor_leakage_e1", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StrategyFactorLeakageE1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_e1_reference_run_passes_all_expected_checks(self):
        report = self.mod.run_e1_validation()
        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["existing_owner"]["kind"], "DATA_QUALITY_TEST")
        self.assertFalse(report["existing_owner"]["parallel_engine_created"])
        self.assertFalse(report["authority"]["portfolio_execution"])
        self.assertTrue(report["gate"]["e3_may_begin_only_if_verdict_pass"])

    def test_causal_features_are_right_truncation_invariant(self):
        rows = self.mod.synthetic_rows()
        self.assertTrue(self.mod.right_truncation_invariance(rows, self.mod.trailing_mean, self.mod.WINDOW)["invariant"])
        self.assertTrue(self.mod.right_truncation_invariance(rows, self.mod.trailing_zscore, self.mod.WINDOW)["invariant"])

    def test_left_truncation_converges_after_warmup(self):
        rows = self.mod.synthetic_rows()
        mean = self.mod.left_truncation_convergence(rows, self.mod.trailing_mean, self.mod.WINDOW, drop_rows=2)
        zscore = self.mod.left_truncation_convergence(rows, self.mod.trailing_zscore, self.mod.WINDOW, drop_rows=2)
        self.assertTrue(mean["converged"])
        self.assertTrue(zscore["converged"])
        self.assertEqual(mean["warmup_rows_required"], self.mod.WINDOW - 1)

    def test_planted_future_leaks_are_detected(self):
        rows = self.mod.synthetic_rows()
        next_value = self.mod.right_truncation_invariance(rows, self.mod.planted_next_value_leak, self.mod.WINDOW)
        centered = self.mod.right_truncation_invariance(rows, self.mod.planted_centered_mean_leak, self.mod.WINDOW)
        self.assertFalse(next_value["invariant"])
        self.assertFalse(centered["invariant"])
        self.assertGreater(len(next_value["mismatch_indices"]), 0)
        self.assertGreater(len(centered["mismatch_indices"]), 0)

    def test_ambiguous_and_duplicate_timestamps_fail_closed(self):
        result = self.mod.timestamp_fail_closed_checks(self.mod.synthetic_rows())
        self.assertTrue(result["fail_closed"])
        self.assertIn("TIMEZONE_REQUIRED", result["rejections"]["naive_timezone"])
        self.assertEqual(result["rejections"]["duplicate_timestamp"], "NON_MONOTONIC_OR_DUPLICATE_TIMESTAMP")

    def test_committed_reference_artifact_is_byte_reproducible(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--verify-artifact", str(ARTIFACT)],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(report["verdict"], "PASS")

    def test_immutable_writer_refuses_overwrite(self):
        report = self.mod.run_e1_validation()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "result.json"
            self.mod.write_immutable(path, report)
            with self.assertRaises(FileExistsError):
                self.mod.write_immutable(path, report)


if __name__ == "__main__":
    unittest.main()
