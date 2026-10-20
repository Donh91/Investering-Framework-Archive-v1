import unittest
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from scripts.framework_intelligence import supervisor_mission_intake_v1 as intake
from scripts.framework_intelligence.supervisor_mission_intake_v1 import classify, receipt, MARKER

class SupervisorMissionIntakeTests(unittest.TestCase):
    def event(self, **changes):
        e={"issue":{"number":1552,"state":"open"},"comment":{"id":123,"author_association":"OWNER","body":MARKER}}
        e.update(changes)
        return e

    def test_owner_explicit_approval_is_triage_only(self):
        r=receipt(self.event(),"Donh91/Investering-Framework-Archive-v1","abc123")
        self.assertEqual(r["state"],"ACTIONABLE_UNCLAIMED")
        self.assertFalse(r["execution_started"])
        self.assertFalse(r["codex_ready"])
        self.assertEqual(r["authority"],"TRIAGE_ONLY")

    def test_real_status_comment_marker_mention_rejected(self):
        body="Supervisor update: the literal marker " + MARKER + " is in this status comment."
        self.assertEqual(classify(self.event(comment={"id":6088518866,"author_association":"OWNER","body":body}))[0],"IGNORED")

    def test_negative_and_quoted_marker_rejected(self):
        for body in ("Do NOT " + MARKER + " yet", "> " + MARKER, "Text" + chr(10) + MARKER):
            self.assertEqual(classify(self.event(comment={"id":124,"author_association":"OWNER","body":body}))[0],"IGNORED")

    def test_crlf_and_trailing_space_first_line_accepted_for_triage_only(self):
        for body in (MARKER+chr(13)+chr(10)+"Please triage.", MARKER+" "+chr(10)+"Please triage."):
            self.assertIn(chr(10), body)
            result=receipt(self.event(comment={"id":125,"author_association":"OWNER","body":body}),"repo","sha")
            self.assertEqual(result["state"],"ACTIONABLE_UNCLAIMED")
            self.assertFalse(result["human_approval_verified"])
            self.assertFalse(result["execution_started"])

    def test_null_body_rejected(self):
        self.assertEqual(classify(self.event(comment={"id":124,"author_association":"OWNER","body":None}))[0],"IGNORED")

    def test_first_line_marker_allows_only_triage(self):
        r=receipt(self.event(comment={"id":124,"author_association":"OWNER","body":MARKER+"\nPlease triage."}),"repo","sha")
        self.assertEqual(r["state"],"ACTIONABLE_UNCLAIMED")
        self.assertFalse(r["human_approval_verified"])
        self.assertFalse(r["execution_started"])

    def test_untrusted_comment_does_not_dispatch(self):
        for assoc in ("NONE","CONTRIBUTOR","MEMBER","COLLABORATOR"):
            self.assertEqual(classify(self.event(comment={"id":123,"author_association":assoc,"body":MARKER}))[0],"IGNORED")

    def test_missing_marker_ignored(self):
        self.assertEqual(classify(self.event(comment={"id":123,"author_association":"OWNER","body":"please do this"}))[0],"IGNORED")

    def test_other_issue_ignored(self):
        self.assertEqual(classify(self.event(issue={"number":1530,"state":"open"}))[0],"IGNORED")

    def test_closed_issue_ignored(self):
        self.assertEqual(classify(self.event(issue={"number":1552,"state":"closed"}))[0],"IGNORED")

    def test_pr_ignored(self):
        self.assertEqual(classify(self.event(issue={"number":1552,"state":"open","pull_request":{}}))[0],"IGNORED")


class SupervisorCodeProvenanceTests(unittest.TestCase):
    def event(self):
        return {"issue": {"number": 1552, "state": "open"},
                "comment": {"id": 123, "author_association": "OWNER", "body": MARKER}}

    def test_event_and_executed_revision_remain_distinct(self):
        r = receipt(self.event(), "fixture/repo", "a" * 40, "b" * 40)
        self.assertEqual(r["workflow_event_sha"], "a" * 40)
        self.assertEqual(r["executed_code_sha"], "b" * 40)
        self.assertEqual(r["code_binding_status"], "BOUND_TO_EXECUTED_CHECKOUT")
        self.assertFalse(r["human_approval_verified"])
        self.assertFalse(r["execution_started"])
        self.assertFalse(r["codex_ready"])

    def test_legacy_call_does_not_claim_a_code_binding(self):
        r = receipt(self.event(), "fixture/repo", "a" * 40)
        self.assertIsNone(r["executed_code_sha"])
        self.assertEqual(r["code_binding_status"], "UNKNOWN")

    def test_invalid_executed_revision_rejected(self):
        for code_sha in ("main", "abc123", "z" * 40):
            with self.assertRaisesRegex(ValueError, "EXECUTED_CODE_COMMIT_INVALID"):
                receipt(self.event(), "fixture/repo", "a" * 40, code_sha)

    def copy_script(self, root):
        script = root / "scripts/framework_intelligence/supervisor_mission_intake_v1.py"
        script.parent.mkdir(parents=True)
        shutil.copyfile(intake.__file__, script)
        return script

    def test_cli_records_actual_checkout_after_event_revision(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script = self.copy_script(root)
            def git(*args):
                return subprocess.check_output(["git", "-c", "user.name=Audit fixture",
                    "-c", "user.email=audit-fixture@example.invalid", *args], cwd=root, text=True).strip()
            git("init", "-q")
            git("add", "scripts")
            git("commit", "-q", "-m", "Event revision")
            event_sha = git("rev-parse", "HEAD")
            (root / "later.txt").write_text("Later checkout revision\n")
            git("add", "later.txt")
            git("commit", "-q", "-m", "Later checkout")
            code_sha = git("rev-parse", "HEAD")
            event = root / "event.json"
            event.write_text(json.dumps(self.event()))
            output = root / "receipt.json"
            subprocess.run([sys.executable, str(script), "--event", str(event),
                "--repo", "fixture/repo", "--head-sha", event_sha,
                "--output", str(output)], check=True, capture_output=True, text=True)
            r = json.loads(output.read_text())
            self.assertNotEqual(event_sha, code_sha)
            self.assertEqual(r["workflow_event_sha"], event_sha)
            self.assertEqual(r["executed_code_sha"], code_sha)
            self.assertEqual(r["state"], "ACTIONABLE_UNCLAIMED")
            self.assertFalse(r["execution_started"])

    def test_cli_dirty_tracked_code_fails_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script = self.copy_script(root)
            git = ["git", "-c", "user.name=Audit fixture",
                   "-c", "user.email=audit-fixture@example.invalid"]
            subprocess.run(git + ["init", "-q"], cwd=root, check=True, capture_output=True)
            subprocess.run(git + ["add", "scripts"], cwd=root, check=True, capture_output=True)
            subprocess.run(git + ["commit", "-q", "-m", "Clean source"], cwd=root, check=True, capture_output=True)
            script.write_text(script.read_text() + "\n# Dirty tracked source fixture\n")
            event = root / "event.json"
            event.write_text(json.dumps(self.event()))
            output = root / "receipt.json"
            result = subprocess.run([sys.executable, str(script), "--event", str(event),
                "--repo", "fixture/repo", "--head-sha", "a" * 40,
                "--output", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("EXECUTED_CODE_CHECKOUT_DIRTY", result.stderr)
            self.assertFalse(output.exists())

    def test_cli_without_git_checkout_fails_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script = self.copy_script(root)
            event = root / "event.json"
            event.write_text(json.dumps(self.event()))
            output = root / "receipt.json"
            result = subprocess.run([sys.executable, str(script), "--event", str(event),
                "--repo", "fixture/repo", "--head-sha", "a" * 40,
                "--output", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("EXECUTED_CODE_COMMIT_UNAVAILABLE", result.stderr)
            self.assertFalse(output.exists())

if __name__ == "__main__":
    unittest.main()
