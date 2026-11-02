"""Non-network unit tests for S1 message correlation."""
import unittest
from scripts.governance.s1_agent_handoff_receipts_v1 import validate_chain, ReceiptError

URL = "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156"
BASE = dict(request_id="req-20261102-001", source_head="a"*40,
            source_fingerprint="source12345678", sender="S1",
            recipient="Bridge", original_url=URL, native_event_url=URL)


def chain():
    result = []
    for i, (state, actor) in enumerate((
        ("REQUESTED", "S1"), ("ACKNOWLEDGED", "Bridge"),
        ("ACCEPTED", "Bridge"), ("RESULT_DELIVERED", "Bridge"),
        ("S1_VERIFIED", "S1"))):
        row = {**BASE, "state": state, "actor": actor,
               "at_utc": "2026-11-02T10:0%d:00Z" % i}
        if state == "RESULT_DELIVERED":
            row["result_url"] = URL
        if state == "S1_VERIFIED":
            row["verification"] = "PASS"
            row["verification_url"] = URL
        result.append(row)
    return result


class HandoffTests(unittest.TestCase):
    def reject(self, data):
        with self.assertRaises(ReceiptError):
            validate_chain(data)

    def test_complete_is_only_structural(self):
        result = validate_chain(chain())
        self.assertEqual(result["structural_state"], "S1_VERIFIED")
        self.assertFalse(result["authenticated_delivery"])
        self.assertFalse(result["actual_job_execution_proven"])
        self.assertFalse(result["release_authorized"])

    def test_no_ack(self):
        data = chain()
        self.reject(data[:1] + data[2:])

    def test_changed_head(self):
        data = chain()
        data[1]["source_head"] = "b"*40
        self.reject(data)

    def test_wrong_actor(self):
        data = chain()
        data[1]["actor"] = "NotBridge"
        self.reject(data)

    def test_missing_result_link(self):
        data = chain()
        del data[3]["result_url"]
        self.reject(data)

    def test_duplicate_time(self):
        data = chain()
        data[2]["at_utc"] = data[1]["at_utc"]
        self.reject(data)

    def test_failed_verification(self):
        data = chain()
        del data[4]["verification_url"]
        self.reject(data)

    def test_no_terminal_replay(self):
        data = chain()
        self.reject(data + [data[-1]])

    def test_invalid_utc_date(self):
        data = chain()
        data[1]["at_utc"] = "2026-02-30T10:01:00Z"
        self.reject(data)


if __name__ == "__main__":
    unittest.main()
