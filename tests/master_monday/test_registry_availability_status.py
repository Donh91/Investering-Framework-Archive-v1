from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


context_builder = load_module("weekly_context_registry_status", PROJECT / "scripts/api_agent/build_weekly_calibration_context.py")
publisher_path = PROJECT / "scripts/master_monday/publish_master_monday_outputs.py"


class RegistryAvailabilityStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime(2026, 8, 3, tzinfo=timezone.utc)
        self.end = datetime(2026, 8, 10, tzinfo=timezone.utc)

    def learning(self, root: Path, registry_value=...):
        registry = root / "registry.json"
        outcomes = root / "outcomes"
        outcomes.mkdir(exist_ok=True)
        if registry_value is not ...:
            registry.write_text(registry_value if isinstance(registry_value, str) else json.dumps(registry_value))
        return context_builder.load_experiment_learning(registry, outcomes, self.start, self.end)

    def publish(self, root: Path, learning: dict, api_scorecard: dict | None = None) -> tuple[dict, dict, str]:
        freeze = root / "freeze.json"
        preflight = root / "preflight.json"
        context = root / "context.json"
        output = root / "published"
        freeze.write_text(json.dumps({"iso_year": 2026, "iso_week": 35, "freeze_sha256": "freeze"}))
        preflight.write_text(json.dumps({"package_sha256": "preflight", "packet": {"status": "FULL_MASTER_MONDAY_INPUT"}}))
        context.write_text(json.dumps({"context_hash": "context", "experiment_learning": learning}))
        command = [
            sys.executable,
            str(publisher_path),
            "--freeze", str(freeze),
            "--preflight", str(preflight),
            "--context", str(context),
            "--api-status", "success",
            "--output-dir", str(output),
        ]
        if api_scorecard is not None:
            api_output = root / "api-output.json"
            api_output.write_text(json.dumps({"scorecard": api_scorecard}))
            command.extend(["--api-output", str(api_output)])
        subprocess.run(command, cwd=PROJECT, check=True)
        scorecard = json.loads((output / "MASTER_MONDAY_CALIBRATION_SCORECARD.json").read_text())
        pointer = json.loads((output / "MASTER_MONDAY_DELIVERY_POINTER.json").read_text())
        report = (output / "MASTER_MONDAY_REPORT.md").read_text()
        return scorecard, pointer, report

    def test_valid_empty_registry_remains_pending(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            learning = self.learning(root, {
                "contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1",
                "generated_at_utc": "2026-08-06T03:00:00Z",
                "candidate_count": 0,
                "state_counts": {},
                "candidates": [],
            })
            self.assertEqual(learning["status"], "AVAILABLE")
            self.assertEqual(learning["new_matured_outcomes"], [])
            scorecard, pointer, report = self.publish(root, learning)
            self.assertEqual(scorecard["status"], "PENDING_MATURED_OUTCOMES")
            self.assertEqual(pointer["experiment_learning_status"], "AVAILABLE")
            self.assertEqual(pointer["scorecard_status"], "PENDING_MATURED_OUTCOMES")
            self.assertIn("Experiment registry evidence: **AVAILABLE**", report)

    def test_missing_registry_is_unavailable_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            learning = self.learning(root)
            self.assertEqual(learning["status"], "UNAVAILABLE_REGISTRY_MISSING")
            self.assertIsNone(learning["new_matured_outcomes"])
            scorecard, pointer, report = self.publish(root, learning)
            self.assertEqual(scorecard["status"], "UNAVAILABLE_EXPERIMENT_REGISTRY")
            self.assertIsNone(scorecard["matured_outcome_count"])
            self.assertEqual(pointer["experiment_learning_status"], "UNAVAILABLE_REGISTRY_MISSING")
            self.assertEqual(pointer["scorecard_status"], "UNAVAILABLE_EXPERIMENT_REGISTRY")
            self.assertIn("Experiment registry evidence: **UNAVAILABLE_REGISTRY_MISSING**", report)

            api_pending = {
                "status": "PENDING_MATURED_OUTCOMES",
                "matured_outcome_count": 0,
            }
            scorecard, _, _ = self.publish(root, learning, api_pending)
            self.assertEqual(scorecard["status"], "UNAVAILABLE_EXPERIMENT_REGISTRY")
            self.assertIsNone(scorecard["matured_outcome_count"])

    def test_unreadable_and_contract_invalid_registries_are_not_empty_sets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unreadable = self.learning(root, "not-json")
            self.assertEqual(unreadable["status"], "UNAVAILABLE_REGISTRY_UNREADABLE")
            self.assertIsNone(unreadable["new_matured_outcomes"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = self.learning(root, {"contract": "WRONG", "candidates": []})
            self.assertEqual(invalid["status"], "UNAVAILABLE_REGISTRY_CONTRACT_INVALID")
            self.assertIsNone(invalid["new_matured_outcomes"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            invalid = self.learning(root, [])
            self.assertEqual(invalid["status"], "UNAVAILABLE_REGISTRY_CONTRACT_INVALID")
            self.assertIsNone(invalid["new_matured_outcomes"])


if __name__ == "__main__":
    unittest.main()
