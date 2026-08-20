"""Evidence-health signals E1/E2 (TASK3 R3-08).

Health must distinguish PLUMBING HEALTH from EVIDENCE HEALTH: a job that exits
zero can still be operationally RED if its evidence output is unusable.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "health" / "build_architecture_health.py"
spec = importlib.util.spec_from_file_location("architecture_health", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

NOW = datetime(2026, 8, 19, 13, 0, 0, tzinfo=timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


class EvidenceHealthTests(unittest.TestCase):
    def build(self, forecasts, outcomes):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        forecast_root = root / "research/framework_memory/forecast_memory"
        outcome_root = root / "research/framework_memory/outcome_memory"
        forecast_root.mkdir(parents=True)
        outcome_root.mkdir(parents=True)
        for index, due in enumerate(forecasts):
            (forecast_root / f"f{index}.json").write_text(json.dumps({
                "contract": "FROZEN_FORECAST_v1", "forecast_id": f"f{index}", "outcome_due_utc": iso(due)}))
        for index, (status, created) in enumerate(outcomes):
            (outcome_root / f"o{index}.json").write_text(json.dumps({
                "contract": "MATURED_OUTCOME_v3", "forecast_id": f"f{index}",
                "status": status, "created_at_utc": iso(created)}))
        return module.evidence_health(root, NOW)

    def test_all_censored_lane_is_detected(self):
        evidence = self.build(
            forecasts=[NOW - timedelta(days=3)] * 5,
            outcomes=[("CENSORED", NOW - timedelta(days=2))] * 5)
        self.assertEqual(evidence["matured_outcome_count"], 0)
        self.assertEqual(evidence["censored_outcome_count"], 5)
        self.assertEqual(evidence["censor_rate"], 1.0)
        self.assertEqual(evidence["forecasts_due_in_window"], 5)

    def test_healthy_lane_reports_low_censor_rate(self):
        evidence = self.build(
            forecasts=[NOW - timedelta(days=3)] * 5,
            outcomes=[("MATURED", NOW - timedelta(days=2))] * 4 + [("CENSORED", NOW - timedelta(days=2))])
        self.assertEqual(evidence["matured_outcome_count"], 4)
        self.assertEqual(evidence["censor_rate"], 0.2)

    def test_outcomes_outside_the_window_are_not_counted(self):
        evidence = self.build(
            forecasts=[NOW - timedelta(days=40)],
            outcomes=[("MATURED", NOW - timedelta(days=40))])
        self.assertEqual(evidence["adjudicated_outcome_count"], 0)
        self.assertEqual(evidence["forecasts_due_in_window"], 0)
        self.assertIsNone(evidence["censor_rate"])

    def test_empty_repository_produces_no_signal(self):
        evidence = self.build(forecasts=[], outcomes=[])
        self.assertEqual(evidence["adjudicated_outcome_count"], 0)
        self.assertIsNone(evidence["censor_rate"])
        self.assertEqual(evidence["forecasts_due_in_window"], 0)


class EvidenceBlockerTests(unittest.TestCase):
    """The blocker vocabulary and severity mapping reuse the existing scheme."""

    def severity_of(self, evidence):
        blockers = []
        severity = 0

        def add(code, level):
            nonlocal severity
            if code not in blockers:
                blockers.append(code)
            severity = max(severity, level)

        if evidence["forecasts_due_in_window"] > 0 and evidence["matured_outcome_count"] == 0:
            add("NO_MATURED_OUTCOMES_14D", 2)
        if evidence["censor_rate"] is not None:
            if evidence["censor_rate"] >= 1.0:
                add("OUTCOME_CENSOR_RATE_HIGH", 2)
            elif evidence["censor_rate"] > module.EVIDENCE_CENSOR_RATE_AMBER:
                add("OUTCOME_CENSOR_RATE_HIGH", 1)
        return blockers, ("RED" if severity >= 2 else "AMBER" if severity == 1 else "GREEN")

    def test_e1_fires_red_on_a_stopped_loop(self):
        blockers, status = self.severity_of(
            {"forecasts_due_in_window": 12, "matured_outcome_count": 0, "censor_rate": 1.0})
        self.assertIn("NO_MATURED_OUTCOMES_14D", blockers)
        self.assertEqual(status, "RED")

    def test_e2_fires_amber_above_the_threshold(self):
        blockers, status = self.severity_of(
            {"forecasts_due_in_window": 12, "matured_outcome_count": 3, "censor_rate": 0.75})
        self.assertEqual(blockers, ["OUTCOME_CENSOR_RATE_HIGH"])
        self.assertEqual(status, "AMBER")

    def test_e2_does_not_fire_below_the_threshold(self):
        blockers, status = self.severity_of(
            {"forecasts_due_in_window": 12, "matured_outcome_count": 9, "censor_rate": 0.25})
        self.assertEqual(blockers, [])
        self.assertEqual(status, "GREEN")

    def test_no_signal_when_nothing_was_due(self):
        blockers, status = self.severity_of(
            {"forecasts_due_in_window": 0, "matured_outcome_count": 0, "censor_rate": None})
        self.assertEqual(blockers, [])
        self.assertEqual(status, "GREEN")

    def test_severity_vocabulary_is_the_existing_one(self):
        self.assertEqual(module.EVIDENCE_WINDOW_DAYS, 14)
        self.assertEqual(module.EVIDENCE_CENSOR_RATE_AMBER, 0.60)
        source = MODULE_PATH.read_text()
        self.assertIn("ARCHITECTURE_HEALTH_DASHBOARD_v2_3", source)
        self.assertIn("'RED' if severity>=2 else 'AMBER' if severity==1 else 'GREEN'", source)


class EvidenceHealthEndToEndTests(unittest.TestCase):
    def test_a_fully_censored_lane_turns_architecture_health_red(self):
        import subprocess
        import sys
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        forecast_root = root / "research/framework_memory/forecast_memory"
        outcome_root = root / "research/framework_memory/outcome_memory"
        forecast_root.mkdir(parents=True)
        outcome_root.mkdir(parents=True)
        for index in range(4):
            (forecast_root / f"f{index}.json").write_text(json.dumps({
                "contract": "FROZEN_FORECAST_v1", "forecast_id": f"f{index}",
                "outcome_due_utc": iso(NOW - timedelta(days=2))}))
            (outcome_root / f"o{index}.json").write_text(json.dumps({
                "contract": "MATURED_OUTCOME_v3", "forecast_id": f"f{index}",
                "status": "CENSORED", "reason": "METRIC_UNAVAILABLE",
                "created_at_utc": iso(NOW - timedelta(days=1))}))
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--repo-root", str(root),
             "--json-output", str(root / "health.json"), "--md-output", str(root / "health.md"),
             "--now-utc", iso(NOW)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        health = json.loads((root / "health.json").read_text())
        self.assertEqual(health["status"], "RED")
        self.assertIn("NO_MATURED_OUTCOMES_14D", health["blockers"])
        self.assertIn("OUTCOME_CENSOR_RATE_HIGH", health["blockers"])
        self.assertEqual(health["evidence_health"]["censor_rate"], 1.0)
        self.assertEqual(health["contract"], "ARCHITECTURE_HEALTH_DASHBOARD_v2_3")


if __name__ == "__main__":
    unittest.main()
