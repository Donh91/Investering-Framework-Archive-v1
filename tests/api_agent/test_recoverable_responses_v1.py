"""No-network adversarial tests for one-POST / durable GET-only Sol MAX delivery."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent import recoverable_responses_v1 as t


def payload():
    return {"model": "gpt-6.1-sol", "reasoning": {"effort": "max"},
            "background": True, "store": True,
            "input": [{"role": "user", "content": "PUBLIC TEST DATA"}]}


class HttpResult:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.data).encode()


class RecoveryTests(unittest.TestCase):
    def test_one_post_handle_persisted_and_get_only(self):
        with tempfile.TemporaryDirectory() as td:
            calls = []
            def post(req, timeout):
                calls.append(req.get_method())
                self.assertTrue(json.loads(req.data)["background"])
                return HttpResult({"id": "resp_abc1234", "status": "in_progress"})
            def get(req, timeout):
                calls.append(req.get_method())
                self.assertTrue(req.full_url.endswith("/resp_abc1234"))
                return HttpResult({"id": "resp_abc1234", "status": "completed",
                                   "output_text": "ok"})
            root = Path(td) / "attempt"
            result = t.submit_or_resume(payload(), "fake", root, post=post, get=get)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(calls, ["POST", "GET"])
            self.assertEqual(json.loads((root / "response_handle.json").read_text())["state"],
                             "GET_ONLY")
            self.assertEqual(json.loads((root / "attempt.json").read_text())["max_paid_posts"], 1)
            same = t.submit_or_resume(payload(), "fake", root, resume=True,
                                      post=lambda *_: self.fail("POST on recovery"), get=get)
            self.assertEqual(same["status"], "completed")
            self.assertEqual(calls, ["POST", "GET", "GET"])
            with self.assertRaisesRegex(ValueError, "ATTEMPT_EXISTS_NO_REPOST"):
                t.start(payload(), "fake", root, post=lambda *_: self.fail("duplicate POST"))

    def test_remote_disconnect_preserves_unknown_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "attempt"
            calls = []
            def lost(*_args, **_kwargs):
                calls.append("POST")
                raise ConnectionResetError("connection lost after possible billing")
            with self.assertRaises(ConnectionResetError):
                t.start(payload(), "fake", root, post=lost)
            self.assertEqual(json.loads((root / "attempt.json").read_text())["state"],
                             "POST_OUTCOME_UNKNOWN")
            self.assertFalse((root / "response_handle.json").exists())
            with self.assertRaisesRegex(ValueError, "NO_HANDLE_NO_REPOST"):
                t.submit_or_resume(payload(), "fake", root, resume=True,
                                   post=lambda *_: self.fail("unwanted POST"))
            with self.assertRaisesRegex(ValueError, "ATTEMPT_EXISTS_NO_REPOST"):
                t.start(payload(), "fake", root, post=lost)
            self.assertEqual(calls, ["POST"])

    def test_pending_is_resumeable_without_repost(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "attempt"
            calls = []
            def post(req, timeout):
                calls.append("POST")
                return HttpResult({"id": "resp_pending1234", "status": "queued"})
            def pending(req, timeout):
                calls.append("GET")
                return HttpResult({"id": "resp_pending1234", "status": "in_progress"})
            with self.assertRaises(t.PendingResponse):
                t.submit_or_resume(payload(), "fake", root, max_polls=1, post=post, get=pending)
            def done(req, timeout):
                calls.append("GET")
                return HttpResult({"id": "resp_pending1234", "status": "completed"})
            output = t.submit_or_resume(payload(), "fake", root, resume=True,
                                        post=lambda *_: self.fail("duplicate"), get=done)
            self.assertEqual(output["status"], "completed")
            self.assertEqual(calls, ["POST", "GET", "GET"])

    def test_hash_or_id_tampering_blocks_get(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "attempt"
            t.start(payload(), "fake", root,
                    post=lambda *_args, **_kwargs: HttpResult({"id": "resp_abc1234"}))
            forged = copy.deepcopy(payload())
            forged["input"][0]["content"] = "CHANGED"
            with self.assertRaisesRegex(ValueError, "SOURCE_OR_CLAIM_MISMATCH"):
                t.collect(forged, "fake", root, get=lambda *_: self.fail("GET untrusted"))
            handle_path = root / "response_handle.json"
            handle = json.loads(handle_path.read_text())
            handle["response_id"] = "../escape"
            handle_path.write_text(json.dumps(handle))
            with self.assertRaisesRegex(ValueError, "RESPONSE_ID_OR_KEY_INVALID"):
                t.collect(payload(), "fake", root, get=lambda *_: self.fail("bad ID"))
            handle["response_id"] = "resp_abc1234"
            handle_path.write_text(json.dumps(handle))
            with self.assertRaisesRegex(ValueError, "PROVIDER_RESPONSE_ID_MISMATCH"):
                t.collect(payload(), "fake", root,
                          get=lambda *_args, **_kwargs: HttpResult({
                              "id": "resp_other1234", "status": "completed"}))

    def test_no_unsafe_model_or_unstored_background(self):
        with tempfile.TemporaryDirectory() as td:
            for changed in ({"model": "gpt-6-astra"},
                            {"reasoning": {"effort": "high"}},
                            {"store": False}, {"background": False}):
                item = {**payload(), **changed}
                with self.assertRaisesRegex(ValueError, "PAYLOAD_NOT_ADMITTED"):
                    t.start(item, "fake", Path(td) / "out",
                            post=lambda *_: self.fail("unsafe POST"))
            self.assertFalse((Path(td) / "out" / "attempt.json").exists())

    def test_failed_or_unknown_provider_status_is_not_success(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "attempt"
            t.start(payload(), "fake", root,
                    post=lambda *_args, **_kwargs: HttpResult({"id": "resp_abc1234"}))
            for status in ("failed", "cancelled", "incomplete"):
                with self.assertRaisesRegex(ValueError, "BACKGROUND_TERMINAL_"):
                    t.collect(payload(), "fake", root,
                              get=lambda *_args, **_kwargs: HttpResult({
                                  "id": "resp_abc1234", "status": status}))
            with self.assertRaisesRegex(ValueError, "UNRECOGNIZED_PROVIDER_STATUS"):
                t.collect(payload(), "fake", root,
                          get=lambda *_args, **_kwargs: HttpResult({
                              "id": "resp_abc1234", "status": "weird"}))


if __name__ == "__main__":
    unittest.main()
