"""Adversarial, offline proof for S1 incident classification advisory."""
import unittest
from scripts.governance.s1_incident_triage_v1 import (
    IncidentEvidenceError, incident_triage,
)
from scripts.health.automation_health_resolution import qualified_natural_fleet_recovery

REPO = "Investering-Framework-Archive-v1"
NOW = "2026-11-22T20:45:00Z"
SHA = "a" * 40


def case(n, *, result="FAILURE", klass="TRANSPORT", event="schedule",
         receipt=False, key="alpha.source.rpc", minute=None, repo=REPO):
    return {
        "incident_key": key,
        "native_run_url": f"https://github.com/Donh91/{repo}/actions/runs/{n}",
        "run_id": n,
        "event": event,
        "result": result,
        "failure_class": klass if result == "FAILURE" else None,
        "source_sha": SHA,
        "consumer_receipt_verified": receipt,
        "observed_at_utc": f"2026-11-22T20:{(minute if minute is not None else n):02d}:00Z",
    }


class IncidentTriageTests(unittest.TestCase):
    def classify(self, series):
        return incident_triage(series, as_of_utc=NOW)

    def test_first_transport_failure_observed_not_repaired(self):
        result = self.classify([case(1)])
        self.assertEqual(result["decision"], "OBSERVE_TRANSIENT")
        self.assertEqual(result["next_action"], "WAIT_FOR_NEXT_NATURAL_RUN")

    def test_two_distinct_transport_failures_require_repair(self):
        result = self.classify([case(1), case(2)])
        self.assertEqual(result["decision"], "REPAIR_CANDIDATE")
        self.assertEqual(result["consecutive_failure_count"], 2)

    def test_duplicate_native_run_never_inflates_failure_count(self):
        one = case(1)
        result = self.classify([one, dict(one), dict(one)])
        self.assertEqual(result["decision"], "OBSERVE_TRANSIENT")
        self.assertEqual(result["unique_runs"], 1)
        self.assertEqual(result["failure_count"], 1)

    def test_conflicting_duplicate_run_fails_closed(self):
        with self.assertRaisesRegex(IncidentEvidenceError, "CONFLICTING_RUN_RECEIPTS"):
            self.classify([case(1), case(1, klass="SEMANTIC")])

    def test_semantic_failure_immediately_requires_repair(self):
        self.assertEqual(self.classify([case(1, klass="SEMANTIC")])["decision"],
                         "REPAIR_CANDIDATE")

    def test_integrity_failure_not_dismissed_by_later_green(self):
        result = self.classify([
            case(1, klass="FALSE_PASS"),
            case(2, result="SUCCESS", receipt=True),
        ])
        self.assertEqual(result["decision"], "INTEGRITY_HOLD")
        self.assertFalse(result["incident_closed"])

    def test_manual_green_does_not_prove_recovery(self):
        result = self.classify([case(1), case(2, result="SUCCESS",
                                        event="workflow_dispatch", receipt=True)])
        self.assertEqual(result["decision"], "RECOVERY_UNVERIFIED")
        self.assertFalse(result["recovery_verified"])

    def test_natural_green_without_consumer_receipt_not_closure(self):
        self.assertEqual(
            self.classify([case(1), case(2, result="SUCCESS")])["decision"],
            "RECOVERY_UNVERIFIED")

    def test_natural_consumer_success_only_recovery_candidate(self):
        result = self.classify([case(1), case(2, result="SUCCESS", receipt=True)])
        self.assertEqual(result["decision"], "RECOVERY_CANDIDATE")
        for field in ("recovery_verified", "incident_closed", "merge_authorized",
                      "dispatch_authorized", "all_inputs_externally_authenticated"):
            self.assertFalse(result[field])

    def test_recurrence_after_green_resets_transient_streak(self):
        result = self.classify([
            case(1), case(2, result="SUCCESS"), case(3)])
        self.assertEqual(result["decision"], "OBSERVE_TRANSIENT")
        self.assertEqual(result["consecutive_failure_count"], 1)

    def test_cross_repo_and_cross_incident_mixing_rejected(self):
        for other in (case(2, repo="Meme-Alpha-Lab"),
                      case(2, key="another.incident")):
            with self.assertRaises(IncidentEvidenceError):
                self.classify([case(1), other])

    def test_forged_evidence_url_rejected(self):
        for replacement in ("https://github.com.evil/Donh91/" + REPO + "/actions/runs/1",
                            "https://github.com/Other/" + REPO + "/actions/runs/1",
                            "https://github.com/Donh91/" + REPO + "/actions/runs/abc",
                            "https://github.com/Donh91/" + REPO + "/actions/runs/1?trust=1"):
            row = case(1)
            row["native_run_url"] = replacement
            with self.assertRaises(IncidentEvidenceError):
                self.classify([row])

    def test_future_unknown_undocumented_receipt_rejected(self):
        for mutation in (
            {"observed_at_utc": "2026-11-22T21:00:00Z"},
            {"source_sha": "a" * 8},
            {"consumer_receipt_verified": "yes"},
            {"run_id": 2},
            {"result": "PASS"},
            {"event": "fake"},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaises(IncidentEvidenceError):
                    self.classify([{**case(1), **mutation}])

    def test_failure_never_has_recovery_receipt(self):
        with self.assertRaisesRegex(IncidentEvidenceError,
                                    "FAILED_RUN_CANNOT_HAVE_RECOVERY_RECEIPT"):
            self.classify([case(1, receipt=True)])

    def test_threshold_validation_and_bounded_history(self):
        for value in (1, 5, True):
            with self.assertRaises(IncidentEvidenceError):
                incident_triage([case(1)], as_of_utc=NOW, threshold=value)
        with self.assertRaises(IncidentEvidenceError):
            self.classify([case(i + 1, minute=i % 45) for i in range(101)])


class FleetHealthRecoveryTests(unittest.TestCase):
    def good(self):
        return {
            "run_event": "schedule", "status": "GREEN",
            "red_count": 0, "amber_count": 0, "workflow_count": 178,
            "scheduled_workflow_count": 41, "api_error": None,
            "warnings": [], "findings": [], "orphaned_registered_workflows": [],
            "source_sha256": "f" * 64, "head_sha": "a" * 40,
        }

    def test_only_complete_natural_fleet_health_qualifies(self):
        self.assertTrue(qualified_natural_fleet_recovery(self.good()))

    def test_manual_and_amber_success_are_not_recovery(self):
        for extra in ({"run_event": "workflow_dispatch"},
                      {"status": "AMBER"}, {"amber_count": 1},
                      {"red_count": 1}, {"api_error": "UPSTREAM_UNAVAILABLE"}):
            with self.subTest(extra=extra):
                self.assertFalse(qualified_natural_fleet_recovery({**self.good(), **extra}))

    def test_partial_or_unknown_source_fails_closed(self):
        for extra in ({"warnings": ["RATE_LIMIT"]},
                      {"findings": ["SOURCE_MISSING"]},
                      {"orphaned_registered_workflows": ["missing"]},
                      {"source_sha256": None}, {"head_sha": ""},
                      {"workflow_count": 0}, {"scheduled_workflow_count": 0}):
            with self.subTest(extra=extra):
                self.assertFalse(qualified_natural_fleet_recovery({**self.good(), **extra}))


if __name__ == "__main__":
    unittest.main()
