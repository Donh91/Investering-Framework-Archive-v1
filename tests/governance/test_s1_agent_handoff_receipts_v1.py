"""Non-network unit tests for S1 message correlation."""
import unittest
from scripts.governance.s1_agent_handoff_receipts_v1 import (
    ReceiptError, handoff_followup, validate_chain,
)

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

    def test_owner_path_traversal_rejected(self):
        for bad in ("https://github.com/Donh91/../evil/issues/5",
                    "https://github.com/Donh91/%2e%2e/evil/issues/5",
                    "https://github.com/Donh91/%2E%2E/evil/issues/5"):
            data = chain()
            for row in data:
                row["original_url"] = bad
            self.reject(data)


    def followup(self, data, at, attempts=1, **context):
        result = handoff_followup(data, at, 2, attempts, **context)
        for key in ("automatically_dispatched", "delivery_authenticated",
                    "actual_job_execution_proven", "release_authorized"):
            self.assertIs(result[key], False)
        self.assertEqual(result["structural_state"], data[-1]["state"])
        self.assertEqual(result["reason"], validate_chain(data)["reason"])
        return result["next_action"]

    def test_missing_ack_deadline_and_retry_bound(self):
        for at, attempts, action in (
            ("2026-11-02T10:01:59.999999Z", 1, "AWAIT_NATIVE_ACK"),
            ("2026-11-02T10:02:00Z", 1, "RETRY_ONLY_IF_NATIVE_INTAKE_AUTHORIZED"),
            ("2026-11-02T10:02:00Z", 2, "DEAD_LETTER_ESCALATE_WITH_ORIGINAL_OWNER"),
        ):
            with self.subTest(at=at, attempts=attempts):
                self.assertEqual(self.followup(chain()[:1], at, attempts), action)

    def test_ack_and_accepted_result_deadlines(self):
        for size in (2, 3):
            for at, action in (
                ("2026-11-02T10:02:59.999999Z", "AWAIT_EXISTING_RECEIVER"),
                ("2026-11-02T10:03:00Z", "RECEIVER_RESULT_OVERDUE_NO_DUPLICATE_REQUEST"),
                ("2026-11-02T10:07:00Z", "RECEIVER_STALLED_ESCALATE_ORIGINAL_OWNER"),
            ):
                with self.subTest(size=size, at=at):
                    self.assertEqual(self.followup(chain()[:size], at), action)
        data = chain()[:3]
        data[2]["at_utc"] = "2026-11-02T10:06:59Z"
        self.assertEqual(self.followup(data, "2026-11-02T10:07:00Z"),
                         "RECEIVER_STALLED_ESCALATE_ORIGINAL_OWNER")

    def test_expired_ack_cannot_renew_liveness(self):
        for ack_at in ("2026-11-02T10:02:00Z", "2026-11-02T10:05:00Z"):
            data = chain()[:3]
            data[1]["at_utc"] = ack_at
            data[2]["at_utc"] = "2026-11-02T10:06:00Z"
            for size in (2, 3):
                with self.subTest(ack_at=ack_at, size=size):
                    self.assertEqual(
                        self.followup(data[:size], data[size - 1]["at_utc"]),
                        "ACK_EXPIRED_ESCALATE_ORIGINAL_OWNER")

    def test_delivered_and_terminal_never_retry(self):
        for size, action in ((4, "VERIFY_NATIVE_RESULT_NOW"),
                             (5, "TERMINAL_NO_DISPATCH")):
            with self.subTest(size=size):
                self.assertEqual(
                    self.followup(chain()[:size], "2026-11-02T11:00:00Z"), action)
        for state, actor in (("REJECTED", "Bridge"), ("TIMED_OUT", "S1")):
            data = chain()[:2]
            data[1].update(state=state, actor=actor)
            self.assertEqual(self.followup(data, "2026-11-02T11:00:00Z"),
                             "TERMINAL_NO_DISPATCH")

    def test_current_context_rejects_stale_head_and_request_replay(self):
        binding = validate_chain(chain())["request_binding_sha256"]
        context = dict(expected_source_head=BASE["source_head"],
                       expected_request_binding_sha256=binding)
        self.assertEqual(
            self.followup(chain()[:1], "2026-11-02T10:00:00Z", **context),
            "AWAIT_NATIVE_ACK")
        for key, value in (("source_head", "b"*40),
                           ("request_id", "req-20261102-002"),
                           ("source_fingerprint", "other12345678")):
            data = chain()[:3]
            for row in data:
                row[key] = value
            with self.subTest(key=key):
                with self.assertRaises(ReceiptError):
                    self.followup(data, "2026-11-02T10:02:00Z", **context)

    def test_cross_request_and_terminal_replay(self):
        data = chain()
        data[1]["request_id"] = "req-20261102-002"
        self.reject(data)
        data = chain()
        data.append({**data[-1], "at_utc": "2026-11-02T10:05:00Z"})
        self.reject(data)

    def test_followup_rejects_future_receipts_and_invalid_retry_policy(self):
        with self.assertRaises(ReceiptError):
            handoff_followup(chain()[:3], "2026-11-02T10:01:59Z", 2, 1)
        for policy in ((0, 1, 2), (10081, 1, 2), (True, 1, 2),
                       (2, 0, 2), (2, 3, 2), (2, True, 2),
                       (2, 1, 0), (2, 1, 4), (2, 1, True)):
            with self.subTest(policy=policy):
                with self.assertRaises(ReceiptError):
                    handoff_followup(chain()[:1], "2026-11-02T10:00:00Z", *policy)


if __name__ == "__main__":
    unittest.main()
