import unittest
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

if __name__ == "__main__":
    unittest.main()
