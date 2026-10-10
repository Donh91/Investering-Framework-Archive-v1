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

if __name__ == "__main__":
    unittest.main()
