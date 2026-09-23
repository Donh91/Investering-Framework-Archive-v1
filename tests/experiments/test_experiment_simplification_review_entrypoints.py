"""Entry-point regressions for the read-only experiment simplification review."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/experiments/experiment_simplification_review.py"


def run(args, cwd):
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True)


class EntryPointTests(unittest.TestCase):
    def test_isolated_test_module_collects_and_passes(self):
        result = run(["-m", "unittest", "tests.experiments.test_experiment_simplification_review"], ROOT)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])

    def test_direct_script_execution_from_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run([str(SCRIPT), "--help"], tmp)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])

    def test_module_execution(self):
        result = run(["-m", "scripts.experiments.experiment_simplification_review", "--help"], ROOT)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])

    def test_cli_review_on_current_registry_is_read_only(self):
        registry = ROOT / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"
        before = registry.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "review.json"
            result = run([str(SCRIPT), "--output", str(out)], ROOT)
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")
            self.assertTrue(out.exists())
        self.assertEqual(registry.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
