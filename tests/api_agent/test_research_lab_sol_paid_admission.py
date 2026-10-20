"""No API/network dependency: tests fail-closed Research Lab Sol paid-admission guard."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent.research_lab_sol_dispatch import paid_attempt_admission, QUEUE_PATH

MISSION = "TASK2-R1-CFGI-PIT-FALSIFICATION-002"


class SolPaidAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.queue = {
            "status": "ACTIVE",
            "trigger_issue": 1476,
            "model": "gpt-6.1-sol",
            "task_name": "RESEARCH_LAB_SOL_ANALYSIS",
            "authority": {"automatic_code_write": False, "automatic_merge": False},
            "active_mission": MISSION,
            "missions": [{"mission_id": MISSION, "state": "ACTIVE_RELEASED"}],
        }
        self.persist()

    def persist(self):
        path = self.root / QUEUE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.queue))

    def check(self):
        return paid_attempt_admission(self.root, MISSION, 1476)

    def test_fresh_exact_owner_release_can_run(self):
        self.assertEqual(self.check(), (True, "NEW_OWNER_RELEASE"))

    def test_same_mission_new_comment_after_paid_receipt_is_noop(self):
        path = (self.root / "research/api_agent/outputs/research_lab_sol" / MISSION
                / "issue-1476/comment-123/receipt.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"status": "PASS", "model": "gpt-6.1-sol"}))
        self.assertEqual(self.check(), (False, "PRIOR_MISSION_ATTEMPT_OR_LIABILITY_EXISTS"))

    def test_ambiguous_started_attempt_without_receipt_blocks_post(self):
        path = (self.root / "research/api_agent/outputs/research_lab_sol" / MISSION
                / "issue-1476/comment-123/context_manifest.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
        self.assertFalse(self.check()[0])

    def test_owner_held_mission_never_repeats(self):
        self.queue["active_mission"] = None
        self.queue["missions"][0]["state"] = "OWNER_HELD_AFTER_LAST_VERIFIED_API_RESULT"
        self.persist()
        self.assertEqual(self.check(), (False, "MISSION_NOT_CURRENTLY_RELEASED"))

    def test_no_second_active_mission_or_mismatched_owner(self):
        self.queue["missions"].append({"mission_id": "OTHER", "state": "ACTIVE_RELEASED"})
        self.persist()
        self.assertFalse(self.check()[0])
        self.queue["missions"] = self.queue["missions"][:1]
        self.queue["active_mission"] = "OTHER"
        self.persist()
        self.assertFalse(self.check()[0])

    def test_wrong_issue_or_authority_is_not_new_permission(self):
        self.assertFalse(paid_attempt_admission(self.root, MISSION, 1156)[0])
        self.queue["authority"]["automatic_merge"] = True
        self.persist()
        self.assertFalse(self.check()[0])

    def test_explicit_no_new_paid_attempts_flag(self):
        self.queue["missions"][0]["new_paid_attempts_authorized"] = False
        self.persist()
        self.assertEqual(self.check(), (False, "PAID_MISSION_HOLD"))


if __name__ == "__main__":
    unittest.main()
