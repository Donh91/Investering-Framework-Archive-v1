"""Adversarial, offline proof for S1 incident classification advisory."""
import unittest
import json
import os
import hashlib
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.health.automation_health_resolution import record_status, resolve_recovered, canonical_hash
from scripts.governance.s1_incident_triage_v1 import (
    IncidentEvidenceError, incident_triage, verify_health_red_origin, _git_blob_sha,
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
    """Real workflow shell -> committed Git history -> bot comment -> S1 admission."""

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

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.working, check=True,
                              capture_output=True, text=True).stdout.strip()

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.working = self.root / "working"
        remote = self.root / "origin.git"
        subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
        self.working.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "test")
        self.git("config", "user.email", "test@example.invalid")
        self.source = self.working / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
        self.source.parent.mkdir(parents=True)
        self.source.write_text(json.dumps({
            "repository": "Donh91/Investering-Framework-Archive-v1",
            "generated_at_utc": "2026-11-22T20:00:00Z",
            "red_count": 1, "status": "RED",
            "workflows": [], "workflow_count": 1, "scheduled_workflow_count": 1,
            "amber_count": 0, "api_error": None, "warnings": [],
        }, sort_keys=True) + "\n")
        self.source.with_suffix(".md").write_text("# Automation Production Health\nStatus: RED\n")
        mod = self.working / "scripts/health/automation_health_resolution.py"
        mod.parent.mkdir(parents=True)
        shutil.copyfile(Path(__file__).resolve().parents[2] /
                        "scripts/health/automation_health_resolution.py", mod)
        self.history_path = self.working / "research/architecture_health/history/12345-attempt-1.json"
        record_status(self.working, 12345, 1, "a" * 40, "schedule")
        self.git("add", ".")
        self.git("commit", "-qm", "source")
        self.git("branch", "-M", "main")
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-u", "origin", "main")
        mock = self.root / "bin"
        mock.mkdir()
        gh = mock / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import os, sys, shutil\n"
            "args=sys.argv[1:]\n"
            "if args[:2] == ['issue', 'list']:\n"
            " print(os.environ.get('MOCK_EXISTING', ''), end=''); sys.exit(0)\n"
            "if args[:2] == ['issue', 'create']:\n"
            " shutil.copyfile(args[-1],os.environ['CAPTURE_ISSUE'])\n"
            " print('https://github.com/Donh91/Investering-Framework-Archive-v1/issues/9001')\n"
            " sys.exit(0)\n"
            "if args[:2] == ['issue', 'comment']:\n"
            " shutil.copyfile(args[-1],os.environ['CAPTURE_FILE']); sys.exit(0)\n"
            "sys.exit(91)\n"
        )
        gh.chmod(0o755)
        self.issue_capture = self.root / "issue.txt"
        self.capture = self.root / "comment.txt"
        self.env = {**os.environ,
                    "PATH": str(mock) + os.pathsep + os.environ["PATH"],
                    "RUNNER_TEMP": str(self.root),
                    "GITHUB_REPOSITORY": "Donh91/Investering-Framework-Archive-v1",
                    "GITHUB_RUN_ID": "12345", "GITHUB_RUN_ATTEMPT": "1",
                    "GITHUB_EVENT_NAME": "schedule",
                    "MOCK_EXISTING": "", "CAPTURE_ISSUE": str(self.issue_capture),
                    "CAPTURE_FILE": str(self.capture)}

    def run_producer(self, *, event="schedule", attempt=1, existing=""):
        return subprocess.run(["bash", "-e", "-c", self._script()], cwd=self.working,
                              env={**self.env, "GITHUB_EVENT_NAME": event,
                                   "GITHUB_RUN_ATTEMPT": str(attempt),
                                   "MOCK_EXISTING": existing},
                              capture_output=True, text=True, timeout=30)

    @staticmethod
    def native_run(*, event="schedule", attempt=1, run_id=12345):
        return {
            "id": run_id, "run_attempt": attempt, "event": event,
            "name": "Automation Production Health",
            "path": ".github/workflows/automation-production-health.yml",
            "head_branch": "main", "status": "completed",
            "conclusion": "success",
            "repository": {"full_name": "Donh91/" + REPO},
        }

    def admission(self, *, body=None, actor="github-actions[bot]",
                  created="2026-11-22T20:05:00Z", edited=None,
                  native=None, attempt=1, source_bytes=None, history_bytes=None,
                  current_source_blob=None):
        body = self.capture.read_text() if body is None else body
        history_path = (self.working / "research/architecture_health/history" /
                        f"12345-attempt-{attempt}.json")
        return verify_health_red_origin(
            body, author_login=actor, created_at=created,
            updated_at=created if edited is None else edited,
            native_run=native or self.native_run(attempt=attempt),
            source_bytes=self.source.read_bytes() if source_bytes is None else source_bytes,
            history_bytes=history_path.read_bytes() if history_bytes is None else history_bytes,
            current_main_source_blob=(self.git("hash-object", str(self.source))
                                      if current_source_blob is None else current_source_blob),
            source_main=self.git("rev-parse", "origin/main"),
        )

    def test_real_producer_body_matches_rubric_token_and_bot_comment(self):
        rubric = (Path(__file__).resolve().parents[2] /
                  "00_FMOS/S1/STEWARD_STATES.md").read_text()
        for term in ("run_event: schedule", "github-actions[bot]",
                     "INCIDENT_ORIGIN_UNVERIFIED", "run_attempt: <positive integer>"):
            self.assertIn(term, rubric)
        for existing in ("", "777"):
            run = self.run_producer(existing=existing)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            body = self.capture.read_text()
            for text in (
                "run_event: schedule", "run_attempt: 1",
                "history_path: research/architecture_health/history/12345-attempt-1.json",
                "history_blob: " + self.git("hash-object", str(self.history_path)),
                "source_blob: " + self.git("hash-object", str(self.source)),
                "source_main: " + self.git("rev-parse", "origin/main"),
                "source_generated_at_utc: 2026-11-22T20:00:00Z",
            ):
                self.assertIn(text, body)
            verified = self.admission()
            self.assertEqual((verified["run_id"], verified["run_attempt"]), (12345, 1))
            self.assertFalse(verified["merge_authorized"])
            self.assertFalse(verified["incident_closed"])
        self.assertNotIn("AUTOMATION_HEALTH_RED_ORIGIN_v1", self.issue_capture.read_text())

    def test_run_attempt_dedup_and_no_forged_rerun(self):
        self.assertEqual(self.run_producer().returncode, 0)
        key = self.admission()["incident_evidence_key"]
        self.assertEqual(self.run_producer(existing="777").returncode, 0)
        self.assertEqual(self.admission()["incident_evidence_key"], key)
        self.assertNotEqual(self.run_producer(existing="777", attempt=2).returncode, 0)
        record_status(self.working, 12345, 2, "a" * 40, "schedule")
        self.git("add", ".")
        self.git("commit", "-qm", "second attempt")
        self.git("push", "origin", "main")
        self.assertEqual(self.run_producer(existing="777", attempt=2).returncode, 0)
        self.assertNotEqual(self.admission(attempt=2)["incident_evidence_key"], key)

    def test_event_author_and_hardcoded_schedule_mutants_rejected(self):
        self.assertEqual(self.run_producer().returncode, 0)
        body = self.capture.read_text()
        for fake in ("run_event=schedule", "run_event: workflow_dispatch"):
            with self.subTest(fake=fake), self.assertRaises(IncidentEvidenceError):
                self.admission(body=body.replace("run_event: schedule", fake))
        for actor in ("Donh91", "github-actions-bot", ""):
            with self.subTest(actor=actor), self.assertRaisesRegex(
                IncidentEvidenceError, "NOT_UNEDITED_ACTIONS_BOT_COMMENT"
            ):
                self.admission(actor=actor)
        with self.assertRaisesRegex(IncidentEvidenceError, "NOT_UNEDITED_ACTIONS_BOT_COMMENT"):
            self.admission(edited="2026-11-22T20:06:00Z")
        with self.assertRaisesRegex(IncidentEvidenceError, "NATIVE_RUN_IDENTITY_MISMATCH"):
            self.admission(native=self.native_run(event="workflow_dispatch"))
        with self.assertRaisesRegex(IncidentEvidenceError, "NATIVE_RUN_IDENTITY_MISMATCH"):
            self.admission(native=self.native_run(run_id=10000))
        before = self.capture.read_text()
        self.assertNotEqual(self.run_producer(event="workflow_dispatch", existing="777").returncode, 0)
        self.assertEqual(self.capture.read_text(), before)

    def test_red_count_mutant_rejected_despite_rehashed_valid_history(self):
        self.assertEqual(self.run_producer().returncode, 0)
        body = self.capture.read_text()
        source_json = json.loads(self.source.read_text())
        source_json["red_count"] = 0
        changed = (json.dumps(source_json, sort_keys=True) + "\n").encode()
        hist = json.loads(self.history_path.read_text())
        hist.update(red_count=0, source_sha256=hashlib.sha256(changed).hexdigest())
        hist["receipt_sha256"] = canonical_hash({
            k:v for k,v in hist.items() if k != "receipt_sha256"
        })
        hist_bytes = (json.dumps(hist, indent=2, sort_keys=True) + "\n").encode()
        body = body.replace(self.git("hash-object", str(self.source)), _git_blob_sha(changed))
        body = body.replace(self.git("hash-object", str(self.history_path)), _git_blob_sha(hist_bytes))
        with self.assertRaisesRegex(IncidentEvidenceError, "REPORT_RED_OR_TIMESTAMP_INVALID"):
            self.admission(body=body, source_bytes=changed, history_bytes=hist_bytes,
                           current_source_blob=_git_blob_sha(changed))

    def test_origin_blob_attempt_and_history_substitution_fails_closed(self):
        self.assertEqual(self.run_producer().returncode, 0)
        body = self.capture.read_text()
        for before, after in (
            ("run_id: 12345", "run_id: 55555"),
            ("run_attempt: 1", "run_attempt: 2"),
            ("source_main: " + self.git("rev-parse", "origin/main"), "source_main: " + "f" * 40),
            ("history_blob: " + self.git("hash-object", str(self.history_path)), "history_blob: " + "e" * 40),
            ("status: RED", "status: GREEN"),
        ):
            with self.subTest(before=before), self.assertRaises(IncidentEvidenceError):
                self.admission(body=body.replace(before, after))
        history = json.loads(self.history_path.read_text())
        history["run_event"] = "workflow_dispatch"
        history["receipt_sha256"] = canonical_hash({
            k:v for k,v in history.items() if k != "receipt_sha256"
        })
        new_history = (json.dumps(history, indent=2, sort_keys=True) + "\n").encode()
        changed_body = body.replace(self.git("hash-object", str(self.history_path)), _git_blob_sha(new_history))
        with self.assertRaisesRegex(IncidentEvidenceError, "HISTORY_NOT_BOUND_TO_NATIVE_RUN"):
            self.admission(body=changed_body, history_bytes=new_history)


if __name__ == "__main__":
    unittest.main()
