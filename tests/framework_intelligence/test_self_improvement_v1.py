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


    def test_empty_census_never_reports_clean(self):
        self.health["workflows"] = []
        self._save(self.health_path, self.health)
        result = self.snapshot()
        self.assertEqual(result["operational_verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertIn("EMPTY_WORKFLOW_CENSUS", result["input_issues"])

    def test_unknown_missing_or_invalid_status_fails_closed(self):
        for value in ("UNKNOWN", None, "", "BLUE"):
            with self.subTest(value=value):
                self.output.unlink(missing_ok=True)
                self.health["workflows"][0]["status"] = value
                self._save(self.health_path, self.health)
                result = self.snapshot()
                self.assertEqual(result["operational_verdict"], "INSUFFICIENT_EVIDENCE")
                self.assertTrue(result["input_issues"])

    def test_case_normalization_and_amber_advisory(self):
        for value, verdict in (("red", "NEEDS_DIAGNOSIS"),
                               ("AMBER", "ADVISORY_DEGRADED"),
                               ("YELLOW", "ADVISORY_DEGRADED"),
                               ("green", "NO_RED_HEALTH_INCIDENTS")):
            with self.subTest(value=value):
                self.output.unlink(missing_ok=True)
                self.health["workflows"][0]["status"] = value
                self.health["status"] = "RED" if value.lower() == "red" else "GREEN" if value.lower() == "green" else "AMBER"
                self._save(self.health_path, self.health)
                self.assertEqual(self.snapshot()["operational_verdict"], verdict)

    def test_recurring_red_after_green_keeps_history(self):
        first = self.snapshot()
        self.assertEqual(first["incident_history"][0]["observation_count"], 1)
        self.health["workflows"][0]["status"] = "GREEN"
        self.health["status"] = "GREEN"
        self.health["workflows"][0]["live"]["latest_run"]["id"] = 13
        self._save(self.health_path, self.health)
        middle = self.snapshot()
        self.assertEqual(middle["incident_count"], 0)
        self.assertEqual(middle["incident_history"][0]["observation_count"], 1)
        self.health["workflows"][0]["status"] = "RED"
        self.health["status"] = "RED"
        self.health["workflows"][0]["live"]["latest_run"]["id"] = 14
        self._save(self.health_path, self.health)
        last = self.snapshot()
        self.assertEqual(last["incidents"][0]["observation_count"], 2)
        self.assertEqual(last["incident_history"][0]["first_seen_at_utc"],
                         first["incidents"][0]["first_seen_at_utc"])

    def test_corrupt_prior_is_isolated_without_touching_sources(self):
        self.snapshot()
        self.output.write_text('{"contract":"OTHER"}')
        result = self.snapshot()
        self.assertEqual(result["prior_status"], "INVALID_IGNORED")
        self.assertEqual(result["operational_verdict"], "NEEDS_DIAGNOSIS")
        self.assertFalse(result["authority"]["automatic_code_write"])

    def test_corrupted_history_never_becomes_false_green_and_is_persistent(self):
        self.health["workflows"][0]["status"] = "GREEN"
        self.health["status"] = "GREEN"
        self._save(self.health_path, self.health)
        clean = self.snapshot()
        self.assertEqual(clean["operational_verdict"], "NO_RED_HEALTH_INCIDENTS")
        self.output.write_text('{"contract":"OTHER"}', encoding="utf-8")
        damaged = self.snapshot()
        self.assertEqual(damaged["prior_status"], "INVALID_IGNORED")
        self.assertEqual(damaged["operational_verdict"], "NEEDS_DIAGNOSIS")
        self.assertEqual(damaged["incident_count"], 1)
        self.assertEqual(damaged["incidents"][0]["classification"], "HISTORY_INTEGRITY_LOSS")
        self.assertIn("PRIOR_INCIDENT_HISTORY_INTEGRITY_LOST", damaged["input_issues"])
        self.assertFalse(damaged["incidents"][0]["automatic_code_write_allowed"])
        subsequent = self.snapshot()
        self.assertEqual(subsequent["prior_status"], "VALID")
        self.assertEqual(subsequent["operational_verdict"], "NEEDS_DIAGNOSIS")
        self.assertEqual(subsequent["incidents"][0]["fingerprint"], damaged["incidents"][0]["fingerprint"])
        self.assertEqual(subsequent["incidents"][0]["first_seen_at_utc"], damaged["incidents"][0]["first_seen_at_utc"])
        self.assertEqual(subsequent["incidents"][0]["observation_count"], 1)
        self.assertIn("PRIOR_INCIDENT_HISTORY_INTEGRITY_LOST", subsequent["input_issues"])

    def test_malformed_or_duplicate_prior_history_requires_persistent_integrity_review(self):
        self.health["workflows"][0]["status"] = "GREEN"
        self.health["status"] = "GREEN"
        self._save(self.health_path, self.health)
        for history in ([{"unbound": "no fingerprint"}],
                        [{"fingerprint": "duplicated"}, {"fingerprint": "duplicated"}],
                        "not_a_list"):
            with self.subTest(history=history):
                self.output.unlink(missing_ok=True)
                self.snapshot()
                bad = json.loads(self.output.read_text(encoding="utf-8"))
                bad["incident_history"] = history
                self.output.write_text(json.dumps(bad), encoding="utf-8")
                result = self.snapshot()
                self.assertEqual(result["operational_verdict"], "NEEDS_DIAGNOSIS")
                self.assertEqual(result["incidents"][0]["classification"], "HISTORY_INTEGRITY_LOSS")
                self.assertIn("PRIOR_INCIDENT_HISTORY_INTEGRITY_LOST", result["input_issues"])

    def test_real_shape_six_amber_is_visible(self):
        self.health["workflows"] = [
            {"workflow": f"workflow-{i}.yml", "status": "GREEN" if i < 192 else "AMBER",
             "findings": ["EVIDENCE_PARTIAL"] if i >= 192 else []}
            for i in range(198)
        ]
        self.health["status"] = "AMBER"
        self._save(self.health_path, self.health)
        result = self.snapshot()
        self.assertEqual(result["operational_verdict"], "ADVISORY_DEGRADED")
        self.assertEqual(result["workflow_census_count"], 198)
        self.assertEqual(result["incident_count"], 6)
        self.assertEqual(len(result["incident_history"]), 6)

    def test_absent_run_id_does_not_fake_repeat(self):
        self.health["workflows"][0]["live"]["latest_run"].pop("id")
        self._save(self.health_path, self.health)
        self.snapshot()
        self.assertEqual(self.snapshot()["incidents"][0]["observation_count"], 1)


    # Claude audit 2026-10-17: new adversarial cases, adjusted for merged HEAD.
    def test_top_level_red_without_red_rows_is_insufficient(self):
        self.health["workflows"][0]["status"] = "GREEN"
        self._save(self.health_path, self.health)
        result = self.snapshot()
        self.assertEqual(result["operational_verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertIn("TOP_LEVEL_RED_WITHOUT_RED_ROWS", result["input_issues"])

    def test_green_summary_cannot_override_red_workflow(self):
        self.health["status"] = "GREEN"
        self._save(self.health_path, self.health)
        result = self.snapshot()
        self.assertIn("TOP_LEVEL_GREEN_WITH_RED_ROWS", result["input_issues"])
        self.assertEqual(result["incidents"][0]["observation_count"], 0)

    def test_api_error_and_count_mismatch_stop_false_confidence(self):
        for kind in ("api_error", "red_count"):
            with self.subTest(kind=kind):
                self.output.unlink(missing_ok=True)
                self.health.pop("api_error", None)
                self.health.pop("red_count", None)
                self.health[kind] = "actions_read_denied" if kind == "api_error" else 0
                self._save(self.health_path, self.health)
                result = self.snapshot()
                self.assertEqual(result["operational_verdict"], "INSUFFICIENT_EVIDENCE")
                self.assertFalse(result["source_observation_counted"])
                self.assertEqual(result["incidents"][0]["observation_count"], 0)

    def test_stale_receipt_must_not_create_new_history(self):
        self.health["generated_at_utc"] = "2026-10-01T00:00:00Z"
        self._save(self.health_path, self.health)
        stale = self.snapshot()
        self.assertEqual(stale["operational_verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(stale["incident_history"], [])
        self.assertEqual(stale["incidents"][0]["observation_count"], 0)
        self.health["generated_at_utc"] = "2026-10-16T07:00:00Z"
        self._save(self.health_path, self.health)
        fresh = self.snapshot()
        self.assertEqual(fresh["incidents"][0]["observation_count"], 1)
        self.assertEqual(fresh["incidents"][0]["first_seen_at_utc"], "2026-10-16T07:00:00Z")

    def test_time_regression_does_not_mutate_recurrence(self):
        first = self.snapshot()
        self.health["generated_at_utc"] = "2026-10-16T06:59:00Z"
        self.health["workflows"][0]["live"]["latest_run"]["id"] = 13
        self._save(self.health_path, self.health)
        result = self.snapshot()
        self.assertEqual(first["incidents"][0]["observation_count"], 1)
        self.assertIn("SOURCE_TIME_REGRESSION", result["input_issues"])
        self.assertEqual(result["operational_verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["incidents"][0]["observation_count"], 1)

    def test_run_id_aba_must_not_count_three_observations(self):
        self.snapshot()
        self.health["workflows"][0]["live"]["latest_run"]["id"] = 13
        self._save(self.health_path, self.health)
        self.assertEqual(self.snapshot()["incidents"][0]["observation_count"], 2)
        self.health["workflows"][0]["live"]["latest_run"]["id"] = 12
        self._save(self.health_path, self.health)
        self.assertEqual(self.snapshot()["incidents"][0]["observation_count"], 2)

    def test_no_run_id_fresh_receipt_is_counted_once(self):
        self.health["workflows"][0]["live"]["latest_run"].pop("id")
        self._save(self.health_path, self.health)
        self.snapshot()
        self.health["new_receipt_marker"] = "changed"
        self._save(self.health_path, self.health)
        self.assertEqual(self.snapshot()["incidents"][0]["observation_count"], 2)
        self.assertEqual(self.snapshot()["incidents"][0]["observation_count"], 2)

    def test_invalid_matured_outcome_not_republished_as_object(self):
        self.registry["candidates"][0]["matured_outcome_count"] = {"nested": "object"}
        self._save(self.registry_path, self.registry)
        result = self.snapshot()
        item = next(c for c in result["challengers"] if c["source_state"] == "MATURED_SUPPORTED")
        self.assertIsNone(item["matured_outcome_count"])
        self.assertEqual(item["evidence_direction"], "POSITIVE_UNVERIFIED")
        self.registry["candidate_count"] = True
        self._save(self.registry_path, self.registry)
        with self.assertRaises(ValueError):
            self.snapshot()
        self.registry["candidate_count"] = 3
        self.registry["state_counts"]["MATURED_SUPPORTED"] = True
        self._save(self.registry_path, self.registry)
        with self.assertRaises(ValueError):
            self.snapshot()

    def test_output_escape_or_source_overwrite_is_blocked(self):
        with self.assertRaises(ValueError):
            build_snapshot(self.root, self.root.parent / "outside-self-improvement.json", now=self.now)
        with self.assertRaises(ValueError):
            build_snapshot(self.root, self.health_path, now=self.now)

    def test_live_coverage_collapse_is_reported(self):
        self.snapshot()
        self.health["workflows"].append({"workflow": "not-observed.yml", "status": "GREEN"})
        self._save(self.health_path, self.health)
        result = self.snapshot()
        self.assertIn("SUSPECTED_LIVE_COVERAGE_COLLAPSE", result["input_issues"])
        self.assertFalse(result["source_observation_counted"])


    def test_malformed_present_prior_source_binding_fails_closed_not_crashes(self):
        self.snapshot()
        prior = json.loads(self.output.read_text())
        prior["source_sha256"] = ["invalid"]
        prior["source_generated_at_utc"] = {"automation_health": "bad"}
        self.output.write_text(json.dumps(prior))
        result = self.snapshot()
        self.assertIn("PRIOR_SOURCE_BINDING_UNREADABLE", result["input_issues"])
        self.assertEqual(result["operational_verdict"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(result["source_observation_counted"])


if __name__ == "__main__":
    unittest.main()
