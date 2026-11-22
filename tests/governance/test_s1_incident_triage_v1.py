"""Adversarial, offline proof for S1 incident classification advisory."""
import unittest
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.health.automation_health_resolution import record_status, resolve_recovered
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


class NativeHealthConsumerTests(unittest.TestCase):
    def write_health(self, root, when):
        path = root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "generated_at_utc": when, "status": "GREEN",
            "red_count": 0, "amber_count": 0, "workflow_count": 6,
            "scheduled_workflow_count": 2, "api_error": None, "warnings": [],
            "orphaned_registered_workflows": [], "workflows": [],
        }) + "\n")

    def test_native_record_resolve_rejects_green_before_incident(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            incident = root / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-20-attempt-1.md"
            incident.parent.mkdir(parents=True)
            incident.write_text("# later RED incident\n")
            for run_id, when in ((10, "2026-11-21T05:30:00Z"),
                                 (11, "2026-11-21T17:30:00Z"),
                                 (21, "2026-11-22T05:30:00Z")):
                self.write_health(root, when)
                record_status(root, run_id, 1, "a" * 40, "schedule")
                self.assertEqual(resolve_recovered(root, run_id), [])
            self.write_health(root, "2026-11-22T17:30:00Z")
            record_status(root, 22, 1, "a" * 40, "schedule")
            created = resolve_recovered(root, 22)
            self.assertEqual(len(created), 1)
            self.assertEqual(json.loads((root / created[0]).read_text())["fleet_green_run_ids"], [21, 22])
            self.assertTrue(incident.exists())

    def test_native_record_resolve_refuses_manual_and_amber(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            incident = root / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
            incident.parent.mkdir(parents=True)
            incident.write_text("# original RED incident\n")
            self.write_health(root, "2026-11-21T05:30:00Z")
            record_status(root, 10, 1, "a" * 40, "workflow_dispatch")
            self.write_health(root, "2026-11-21T17:30:00Z")
            record_status(root, 11, 1, "a" * 40, "schedule")
            self.assertEqual(resolve_recovered(root, 11), [])
            health = root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
            data = json.loads(health.read_text())
            data.update(generated_at_utc="2026-11-22T05:30:00Z",
                        status="AMBER", amber_count=1, warnings=["API_DEGRADED"])
            health.write_text(json.dumps(data))
            record_status(root, 12, 1, "a" * 40, "schedule")
            self.assertEqual(resolve_recovered(root, 12), [])
            self.assertTrue(incident.exists())


class HealthOriginProducerConsumerTests(unittest.TestCase):
    @staticmethod
    def _script():
        root = Path(__file__).resolve().parents[2]
        workflow = (root / ".github/workflows/automation-production-health.yml").read_text()
        section = workflow.split(
            "      - name: Open one source-bound incident issue for RED health", 1
        )[1].split("      - name: Record observed fleet status", 1)[0]
        lines = section.splitlines()
        start = lines.index("        run: |") + 1
        return "\n".join(line[10:] if line.startswith("          ") else line
                         for line in lines[start:]) + "\n"

    def test_real_health_issue_step_binds_native_source_and_rejects_drift(self):
        # Executes the ACTUAL GitHub YAML shell step offline against local git
        # and a fake gh, not an invented equivalent implementation.
        script = self._script()
        rubric = (Path(__file__).resolve().parents[2]
                  / "00_FMOS/S1/STEWARD_STATES.md").read_text()
        for token in ("FRESH AUTOMATION HEALTH INCIDENT",
                      "AUTOMATION_HEALTH_RED_ORIGIN_v1",
                      "source_main", "source_blob", "source_generated_at_utc",
                      "run_event", "SOURCE_UNVERIFIED", "EVIDENCE_BINDINGS B5"):
            self.assertIn(token, rubric)
        with TemporaryDirectory() as folder:
            root = Path(folder)
            remote, working = root / "origin.git", root / "working"
            subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
            working.mkdir()
            def git(*args):
                return subprocess.run(["git", *args], cwd=working, check=True,
                                      capture_output=True, text=True).stdout.strip()
            git("init", "-q")
            git("config", "user.name", "test")
            git("config", "user.email", "test@example.invalid")
            source = working / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
            source.parent.mkdir(parents=True)
            source.write_text(json.dumps({
                "repository": "Donh91/Investering-Framework-Archive-v1",
                "generated_at_utc": "2026-11-22T20:00:00Z",
                "red_count": 1, "status": "RED",
            }) + "\n")
            source.with_suffix(".md").write_text("# Automation Production Health\nStatus: RED\n")
            git("add", ".")
            git("commit", "-qm", "source")
            git("branch", "-M", "main")
            git("remote", "add", "origin", str(remote))
            git("push", "-u", "origin", "main")
            mock = root / "bin"
            mock.mkdir()
            gh = mock / "gh"
            gh.write_text(
                "#!/usr/bin/env python3\n"
                "import os, sys, shutil\n"
                "args=sys.argv[1:]\n"
                "if args[:2] == ['issue', 'list']:\n"
                " print(os.environ.get('MOCK_EXISTING', ''), end=''); sys.exit(0)\n"
                "if args[:2] in (['issue','create'], ['issue','comment']):\n"
                " shutil.copyfile(args[-1], os.environ['CAPTURE_FILE']); sys.exit(0)\n"
                "sys.exit(91)\n"
            )
            gh.chmod(0o755)
            capture = root / "captured.txt"
            env = {**os.environ, "PATH": str(mock) + os.pathsep + os.environ["PATH"],
                   "RUNNER_TEMP": str(root), "GITHUB_REPOSITORY": "Donh91/Investering-Framework-Archive-v1",
                   "GITHUB_RUN_ID": "12345", "GITHUB_EVENT_NAME": "schedule",
                   "CAPTURE_FILE": str(capture)}
            for existing in ("", "777"):
                env["MOCK_EXISTING"] = existing
                run = subprocess.run(["bash", "-e", "-c", script], cwd=working,
                                     env=env, capture_output=True, text=True, timeout=30)
                self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
                receipt = capture.read_text()
                self.assertIn("AUTOMATION_HEALTH_RED_ORIGIN_v1", receipt)
                self.assertIn("run_id: 12345", receipt)
                self.assertIn("run_event: schedule", receipt)
                self.assertIn("status: RED", receipt)
                self.assertIn("source_main: " + git("rev-parse", "origin/main"), receipt)
                self.assertIn("source_blob: " + git("hash-object", str(source)), receipt)
                self.assertIn("source_generated_at_utc: 2026-11-22T20:00:00Z", receipt)
            prior = capture.read_text()
            source.write_text(source.read_text().replace('"red_count": 1', '"red_count": 2'))
            failure = subprocess.run(["bash", "-e", "-c", script], cwd=working,
                                     env=env, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(failure.returncode, 0)
            self.assertEqual(capture.read_text(), prior)


if __name__ == "__main__":
    unittest.main()
