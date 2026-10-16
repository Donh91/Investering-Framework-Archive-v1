import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.framework_intelligence.self_improvement_v1 import build_snapshot


class SelfImprovementV1Test(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = datetime(2026, 10, 16, 8, 0, tzinfo=timezone.utc)
        self.health_path = self.root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
        self.registry_path = self.root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"
        self.output = self.root / "research/framework_learning/LATEST_SELF_IMPROVEMENT_V1.json"
        self.health = {
            "contract": "AUTOMATION_PRODUCTION_HEALTH_v2_1",
            "generated_at_utc": "2026-10-16T07:00:00Z",
            "status": "RED",
            "workflows": [{
                "workflow": "framework-learning-operations.yml",
                "status": "RED",
                "findings": ["LATEST_RUN_FAILED"],
                "live": {"failure_streak": 1,
                         "latest_run": {"id": 12, "head_sha": "a" * 40, "conclusion": "failure"}}
            }]
        }
        self.registry = {
            "contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1",
            "generated_at_utc": "2026-10-16T07:05:00Z",
            "candidates": [
                {"candidate_id": "E-supported", "state": "MATURED_SUPPORTED", "matured_outcome_count": 4},
                {"candidate_id": "E-rejected", "state": "MATURED_NOT_SUPPORTED", "matured_outcome_count": 6},
                {"candidate_id": "E-incubating", "state": "INCUBATING", "matured_outcome_count": 0},
            ],
            "candidate_count": 3,
            "state_counts": {"MATURED_SUPPORTED": 1, "MATURED_NOT_SUPPORTED": 1, "INCUBATING": 1},
        }
        self._save(self.health_path, self.health)
        self._save(self.registry_path, self.registry)

    @staticmethod
    def _save(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data) + "\n")

    def snapshot(self):
        return build_snapshot(self.root, self.output, now=self.now)

    def test_supported_experiment_never_becomes_documented_improvement(self):
        result = self.snapshot()
        self.assertEqual(result["scoreboard"]["DOCUMENTED_IMPROVEMENT"], 0)
        self.assertEqual(result["scoreboard"]["UNPROVEN"], 2)
        self.assertEqual(result["scoreboard"]["INSUFFICIENT_EVIDENCE"], 1)
        self.assertEqual(result["challengers"][0]["verdict"], "UNPROVEN")
        self.assertFalse(result["authority"]["automatic_promotion"])
        self.assertFalse(result["authority"]["automatic_merge"])

    def test_repeated_same_run_does_not_fake_multiple_incidents(self):
        first = self.snapshot()
        second = self.snapshot()
        self.assertEqual(first["incidents"][0]["fingerprint"], second["incidents"][0]["fingerprint"])
        self.assertEqual(second["incidents"][0]["observation_count"], 1)
        self.health["workflows"][0]["live"]["latest_run"]["id"] = 13
        self._save(self.health_path, self.health)
        third = self.snapshot()
        self.assertEqual(third["incidents"][0]["observation_count"], 2)

    def test_unknown_failure_never_triggers_blind_retry_or_code_write(self):
        incident = self.snapshot()["incidents"][0]
        self.assertEqual(incident["classification"], "UNKNOWN")
        self.assertFalse(incident["automatic_retry_allowed"])
        self.assertEqual(incident["route"], "EXISTING_REMEDIATION_OWNER")
        self.assertFalse(incident["automatic_code_write_allowed"])

    def test_contract_mismatch_fails_closed_without_output(self):
        self.health["contract"] = "UNTRUSTED"
        self._save(self.health_path, self.health)
        with self.assertRaises(ValueError):
            self.snapshot()
        self.assertFalse(self.output.exists())

    def test_stale_health_cannot_be_reported_current(self):
        self.health["generated_at_utc"] = "2026-10-10T00:00:00Z"
        self._save(self.health_path, self.health)
        result = self.snapshot()
        self.assertEqual(result["input_health"], "STALE")
        self.assertEqual(result["operational_verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(result["incidents"][0]["automatic_retry_allowed"])

    def test_duplicate_candidate_ids_are_rejected(self):
        self.registry["candidates"].append(dict(self.registry["candidates"][0]))
        self.registry["candidate_count"] = 4
        self.registry["state_counts"]["MATURED_SUPPORTED"] = 2
        self._save(self.registry_path, self.registry)
        with self.assertRaises(ValueError):
            self.snapshot()
        self.assertFalse(self.output.exists())

    def test_source_files_remain_byte_identical(self):
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (self.health_path, self.registry_path)]
        result = self.snapshot()
        after = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (self.health_path, self.registry_path)]
        self.assertEqual(before, after)
        self.assertEqual(result["source_sha256"]["automation_health"], before[0])

    def test_negative_outcome_is_preserved_as_negative_not_success(self):
        result = self.snapshot()
        candidate = next(x for x in result["challengers"] if x["candidate_id"] == "E-rejected")
        self.assertEqual(candidate["verdict"], "UNPROVEN")
        self.assertEqual(candidate["source_state"], "MATURED_NOT_SUPPORTED")
        self.assertEqual(result["scoreboard"]["FALSIFIED"], 0)

    def test_malformed_or_missing_source_fails_closed(self):
        self.registry_path.unlink()
        with self.assertRaises((FileNotFoundError, ValueError)):
            self.snapshot()
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
