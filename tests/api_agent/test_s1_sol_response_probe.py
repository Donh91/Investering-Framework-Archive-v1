"""GET-only incident-recovery tests. No actual OpenAI/GitHub requests."""
import json
import os
import unittest
from unittest.mock import patch
from scripts.api_agent import s1_sol_response_probe as s

class FakeHTTP:
    status = 200
    def __init__(self, obj): self.obj = obj
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, *args): return json.dumps(self.obj).encode()

class ProbeTests(unittest.TestCase):
    def test_get_only_one_request(self):
        calls = []
        def open_(request, timeout):
            calls.append((request.get_method(), request.full_url))
            return FakeHTTP({"id": s.RESPONSE_ID, "status": "in_progress"})
        code, body = s.fetch_once("test-secret", urlopen=open_)
        self.assertEqual((code, body["status"]), (200, "in_progress"))
        self.assertEqual(calls, [("GET", "https://api.openai.com/v1/responses/" + s.RESPONSE_ID)])

    def test_missing_api_key_blocks_network(self):
        calls = []
        with self.assertRaisesRegex(ValueError, "KEY_MISSING"):
            s.fetch_once("", urlopen=lambda *a: calls.append(True))
        self.assertFalse(calls)

    def test_404_means_unavailable_not_zero_cost(self):
        result, output = s.interpret(404, {})
        self.assertEqual(result["state"], "EXPIRED_OR_NOT_STORED")
        self.assertEqual(result["provider_billing"], "NOT_RECONCILED")
        self.assertFalse(result["paid_post_performed"])
        self.assertIsNone(output)

    def test_pending_stays_recoverable(self):
        result, output = s.interpret(200, {"id": s.RESPONSE_ID, "status": "in_progress"})
        self.assertEqual(result["state"], "PENDING_COLLECT")
        self.assertIsNone(output)

    def test_completed_is_untrusted_and_does_not_apply(self):
        payload = {"id": s.RESPONSE_ID, "status": "completed",
                   "output": [{"type": "message", "content": [{"type": "output_text", "text": "DIFF"}]}],
                   "usage": {"input_tokens": 300, "output_tokens": 400,
                             "output_tokens_details": {"reasoning_tokens": 350}}}
        receipt, output = s.interpret(200, payload)
        self.assertEqual(receipt["state"], "COMPLETED")
        self.assertEqual(receipt["usage"]["reasoning_tokens"], 350)
        self.assertFalse(receipt["automatic_patch_application"])
        self.assertEqual(output, payload)

    def test_incomplete_never_claims_patch(self):
        receipt, output = s.interpret(200, {"id": s.RESPONSE_ID, "status": "incomplete"})
        self.assertEqual(receipt["state"], "INCOMPLETE")
        self.assertIsNone(output)

    def test_id_mismatch(self):
        receipt, output = s.interpret(200, {"id": "resp_other", "status": "completed"})
        self.assertEqual(receipt["state"], "MISMATCHED_RESPONSE_ID")
        self.assertIsNone(output)

    def test_unknown_http(self):
        self.assertEqual(s.interpret(403, {})[0]["state"], "RETRIEVAL_DENIED_OR_UNKNOWN")

    def test_transient_503(self):
        self.assertEqual(s.interpret(503, {})[0]["state"], "TRANSIENT_GET_ERROR")

    def test_no_launch_commit_blocks_native_and_paid_network(self):
        calls = []
        def git_run(cmd, **kw):
            calls.append(cmd)
            return "b"*40 if cmd[1] == "rev-parse" else "ordinary commit"
        with patch.dict(os.environ, {"GH_TOKEN": ""}):
            self.assertFalse(s.authorized("b"*40, s.REPO, git_run=git_run))
        self.assertEqual(len(calls), 2)

    def test_native_new_head_can_retrieve_old_response(self):
        calls = []
        def git_run(cmd, **kw):
            calls.append(cmd)
            if cmd[1] == "rev-parse": return "b"*40
            if cmd[1] == "log": return s.LAUNCH_MESSAGE
            return json.dumps({"state": "open", "draft": False,
                               "head": {"sha": "b"*40, "repo": {"full_name": s.REPO}}})
        with patch.dict(os.environ, {"GH_TOKEN": "gh-test"}):
            self.assertTrue(s.authorized("b"*40, s.REPO, git_run=git_run))
        self.assertNotEqual("b"*40, s.SOURCE_HEAD)
        self.assertEqual(len(calls), 3)

    def test_mismatched_head_denied(self):
        with self.assertRaisesRegex(ValueError, "CHECKOUT_HEAD_DRIFT"):
            s.authorized("b"*40, s.REPO, git_run=lambda *a, **k: "a"*40)

    def test_invalid_repository_denied(self):
        with self.assertRaisesRegex(ValueError, "BAD_REPO_OR_HEAD"):
            s.authorized("b"*40, "someone/foreign")

if __name__ == "__main__":
    unittest.main()
