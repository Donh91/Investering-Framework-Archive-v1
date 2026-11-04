"""No-network tests for owner-triggered Sol MAX PR patch candidate."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "s1_sol_max_patch_execution", "scripts/api_agent/s1_sol_max_patch_execution.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
HEAD = "a" * 40
REPO = "Donh91/Investering-Framework-Archive-v1"


def proposal_dir(root, status, diff):
    root.mkdir(parents=True, exist_ok=True)
    (root / "proposal.json").write_text(json.dumps({
        "status": status, "unified_diff": diff, "rationale": "test", "tests": []}))
    (root / "api_meta.json").write_text(json.dumps({
        "model": mod.MODEL, "reasoning_effort": mod.EFFORT}))


class SolMaxPatchTests(unittest.TestCase):
    def test_model_max_and_no_auto_write_authority(self):
        self.assertEqual((mod.MODEL, mod.EFFORT), ("gpt-6.1-sol", "max"))
        self.assertLessEqual(mod.MAX_PATCH_BYTES, 16000)
        self.assertEqual(mod.MAX_OUTPUT_TOKENS, 64000)
        # 64k output tokens cannot exceed the existing USD 0.75 reservation
        # under the bounded source context and current Sol token pricing.
        self.assertLess((mod.MAX_OUTPUT_TOKENS * 10.0 + 40000 * 2.0) / 1e6, mod.RESERVE_USD)
        self.assertEqual(mod.ALLOWED, {
            "scripts/governance/s1_agent_handoff_receipts_v1.py",
            "tests/governance/test_s1_agent_handoff_receipts_v1.py",
        })

    def test_non_owner_launch_commit_is_noop(self):
        with patch.object(mod, "subprocess_check", side_effect=[HEAD, "ordinary review commit"]):
            self.assertEqual(mod.guard(HEAD, REPO)["reason"], "NO_EXACT_OWNER_LAUNCH_COMMIT")
        with self.assertRaises(ValueError):
            mod.guard(HEAD, "someone/untrusted")

    def test_real_owner_launch_is_bound_to_native_pr_head(self):
        native = {"state": "open", "draft": False,
                  "head": {"sha": HEAD, "repo": {"full_name": REPO}}}
        with patch.dict(os.environ, {"GH_TOKEN": "test-token"}), \
             patch.object(mod, "subprocess_check",
                          side_effect=[HEAD, mod.COMMIT_MESSAGE, json.dumps(native)]):
            self.assertTrue(mod.guard(HEAD, REPO)["run"])
        native["head"]["sha"] = "b" * 40
        with patch.dict(os.environ, {"GH_TOKEN": "test-token"}), \
             patch.object(mod, "subprocess_check",
                          side_effect=[HEAD, mod.COMMIT_MESSAGE, json.dumps(native)]):
            with self.assertRaisesRegex(ValueError, "HEAD"):
                mod.guard(HEAD, REPO)

    def test_context_has_exact_allowed_files_without_secrets(self):
        with tempfile.TemporaryDirectory() as t, \
             patch.object(mod, "subprocess_check", return_value=HEAD):
            receipt = mod.build_context(HEAD, Path(t))
            data = (Path(t) / "context.json").read_bytes()
            context = json.loads(data)
            self.assertEqual(receipt["context_sha256"], mod.sha(data))
            self.assertEqual(set(context["files"]), mod.ALLOWED)
            self.assertNotIn("OPENAI_API_KEY", data.decode())
            self.assertNotIn("github_pat_", data.decode())

    def test_abstention_cannot_attach_a_patch(self):
        with tempfile.TemporaryDirectory() as t:
            folder = Path(t)
            proposal_dir(folder, "ABSTAIN", "")
            with patch.object(mod, "subprocess_check", return_value=HEAD):
                self.assertEqual(mod.validate_patch(folder, HEAD)["status"], "ABSTAIN")
            proposal_dir(folder, "ABSTAIN", "diff --git a/foo b/foo\n")
            with patch.object(mod, "subprocess_check", return_value=HEAD):
                with self.assertRaisesRegex(ValueError, "ABSTENTION"):
                    mod.validate_patch(folder, HEAD)

    def test_adversarial_file_scope_escapes_rejected_before_git_apply(self):
        samples = [
            "diff --git a/.github/workflows/evil.yml b/.github/workflows/evil.yml\n",
            "diff --git a/scripts/governance/../secrets.py b/scripts/governance/../secrets.py\n",
            "diff --git a/scripts/governance/s1_agent_handoff_receipts_v1.py b/AGENTS.md\n",
            "diff --git a/scripts/governance/s1_agent_handoff_receipts_v1.py b/scripts/governance/s1_agent_handoff_receipts_v1.py\nnew file mode 100755\n",
        ]
        with tempfile.TemporaryDirectory() as t:
            folder = Path(t)
            for sample in samples:
                proposal_dir(folder, "PATCH", sample)
                with patch.object(mod, "subprocess_check", return_value=HEAD), \
                     patch.object(mod.subprocess, "check_call") as apply:
                    with self.assertRaises(ValueError):
                        mod.validate_patch(folder, HEAD)
                    apply.assert_not_called()

    def test_native_reservation_caps_entire_patch_mission_at_three_owner_bound_attempts(self):
        prev = ("S1_SOL_MAX_PATCH_RESERVATION_V1 HEAD=" + "b"*40 +
                " PR=1877 MODEL=gpt-6.1-sol EFFORT=max MAX_USD=0.75")
        prev2 = ("S1_SOL_MAX_PATCH_RESERVATION_V1 HEAD=" + "c"*40 +
                 " PR=1877 MODEL=gpt-6.1-sol EFFORT=max MAX_USD=0.75")
        current = ("S1_SOL_MAX_PATCH_RESERVATION_V1 HEAD=" + HEAD +
                   " PR=1877 MODEL=gpt-6.1-sol EFFORT=max MAX_USD=0.75")
        def row(body, ident):
            return {"user": {"login": "github-actions[bot]"},
                    "body": body, "id": ident}
        with patch.dict(os.environ, {"GH_TOKEN": "test-token"}), \
             patch.object(mod, "guard", return_value={"run": True}), \
             patch.object(mod, "subprocess_check", side_effect=[
                json.dumps([[row(prev, 1), row(prev2, 2)]]), "posted",
                json.dumps([[row(prev, 1), row(prev2, 2), row(current, 3)]])
             ]) as commands:
            out = mod.claim(HEAD, REPO)
            self.assertEqual(out["claim_id"], 3)
            self.assertEqual(commands.call_count, 3)
        with patch.dict(os.environ, {"GH_TOKEN": "test-token"}), \
             patch.object(mod, "guard", return_value={"run": True}), \
             patch.object(mod, "subprocess_check", return_value=json.dumps([
                 [row(prev, 1), row(prev2, 2), row(
                     "S1_SOL_MAX_PATCH_RESERVATION_V1 HEAD=" + "d"*40 +
                     " PR=1877 MODEL=gpt-6.1-sol EFFORT=max MAX_USD=0.75", 3)]
             ])) as commands:
            with self.assertRaisesRegex(ValueError, "THREE_ATTEMPT_HARD_STOP"):
                mod.claim(HEAD, REPO)
            self.assertEqual(commands.call_count, 1)

    def test_unreserved_api_request_is_rejected_before_any_network(self):
        with tempfile.TemporaryDirectory() as t, \
             patch.dict(os.environ, {"OPENAI_API_KEY": "test-token"}), \
             patch.object(mod.urllib.request, "urlopen") as outbound:
            context = Path(t) / "context.json"
            context.write_text('{}')
            with self.assertRaisesRegex(ValueError, "RESERVATION_MISSING"):
                mod.call_api(context, Path(t))
            outbound.assert_not_called()

    def test_sol_max_background_queue_polls_existing_id_without_second_paid_post(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return json.dumps(self.payload).encode()

        messages = [
            {"id": "resp_queued123", "status": "queued"},
            {
                "id": "resp_queued123", "status": "completed",
                "model": mod.MODEL,
                "usage": {"input_tokens": 35, "output_tokens": 80},
                "output": [{"type": "message", "content": [
                    {"type": "output_text", "text": json.dumps({
                        "status": "ABSTAIN", "unified_diff": "",
                        "rationale": "no safe patch", "tests": []})}]}],
            },
        ]
        sent = []
        def fake_open(req, timeout):
            sent.append((req.get_method(), req.full_url, req.data))
            return FakeResponse(messages[len(sent) - 1])
        with tempfile.TemporaryDirectory() as t, \
             patch.dict(os.environ, {"OPENAI_API_KEY": "test-token"}), \
             patch.object(mod.urllib.request, "urlopen", side_effect=fake_open), \
             patch.object(mod.time, "sleep", return_value=None):
            root = Path(t)
            (root / "context.json").write_text("{}")
            (root / "reservation.json").write_text(json.dumps({
                "status": "RESERVED", "claim_id": 8,
                "model": mod.MODEL, "effort": mod.EFFORT, "source_head": HEAD}))
            result = mod.call_api(root / "context.json", root)
            self.assertEqual(result["status"], "ABSTAIN")
            self.assertEqual([x[0] for x in sent], ["POST", "GET"])
            self.assertIn("resp_queued123", sent[1][1])
            self.assertTrue(json.loads(sent[0][2])["background"])
            self.assertIs(json.loads(sent[0][2])["store"], False)
            handle = json.loads((root / "response_handle.json").read_text())
            self.assertEqual(handle["response_id"], "resp_queued123")
            self.assertEqual(handle["state"], "completed")

    def test_background_wrong_response_id_fails_without_another_paid_post(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return json.dumps(self.payload).encode()
        ids = [
            {"id": "resp_first123", "status": "in_progress"},
            {"id": "resp_different123", "status": "completed"},
        ]
        sent = []
        def fake_open(req, timeout):
            sent.append(req.get_method())
            return FakeResponse(ids[len(sent) - 1])
        with tempfile.TemporaryDirectory() as t, \
             patch.dict(os.environ, {"OPENAI_API_KEY": "test-token"}), \
             patch.object(mod.urllib.request, "urlopen", side_effect=fake_open), \
             patch.object(mod.time, "sleep", return_value=None):
            root = Path(t)
            (root / "context.json").write_text("{}")
            (root / "reservation.json").write_text(json.dumps({
                "status": "RESERVED", "claim_id": 8,
                "model": mod.MODEL, "effort": mod.EFFORT}))
            with self.assertRaisesRegex(ValueError, "BACKGROUND_RESPONSE_ID_CHANGED"):
                mod.call_api(root / "context.json", root)
            self.assertEqual(sent, ["POST", "GET"])

    def test_incomplete_reasoning_exhaustion_is_recorded_without_paid_retry(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return json.dumps({
                    "id": "resp_incomplete123", "model": mod.MODEL,
                    "status": "incomplete",
                    "incomplete_details": {"reason": "max_output_tokens"},
                    "usage": {"input_tokens": 3508, "output_tokens": 16000,
                              "output_tokens_details": {"reasoning_tokens": 16000}},
                    "output": []
                }).encode()
        sent = []
        def fake_open(req, timeout):
            sent.append(req.get_method())
            return FakeResponse()
        with tempfile.TemporaryDirectory() as t, \
             patch.dict(os.environ, {"OPENAI_API_KEY": "test-token"}), \
             patch.object(mod.urllib.request, "urlopen", side_effect=fake_open):
            root = Path(t)
            (root / "context.json").write_text("{}")
            (root / "reservation.json").write_text(json.dumps({
                "status": "RESERVED", "claim_id": 42,
                "model": mod.MODEL, "effort": mod.EFFORT}))
            with self.assertRaisesRegex(ValueError, "API_INCOMPLETE_OUTPUT_TOKENS_EXHAUSTED_NO_PATCH"):
                mod.call_api(root / "context.json", root)
            self.assertEqual(sent, ["POST"])
            meta = json.loads((root / "api_meta.json").read_text())
            self.assertEqual(meta["incomplete_details"]["reason"], "max_output_tokens")
            self.assertEqual(meta["estimated_cost_usd"], 0.167016)
            self.assertFalse((root / "proposal.json").exists())

    def test_paid_call_is_one_request_with_max_store_false_and_schema(self):
        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                data = {"id": "resp_test", "model": mod.MODEL, "status": "completed",
                        "usage": {"input_tokens": 100, "output_tokens": 200},
                        "output": [{"type": "message", "content": [
                            {"type": "output_text", "text": json.dumps({
                                "status": "ABSTAIN", "unified_diff": "",
                                "rationale": "bounded/no safe patch", "tests": []})}]}]}
                return json.dumps(data).encode()
        posted = []
        def fake_open(req, timeout):
            obj = json.loads(req.data)
            posted.append(obj)
            return FakeResponse()
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ, {"OPENAI_API_KEY": "test-token"}), \
             patch.object(mod.urllib.request, "urlopen", side_effect=fake_open):
            context = Path(t) / "context.json"
            context.write_text('{"contract":"fake"}')
            (Path(t) / "reservation.json").write_text(json.dumps({
                "status": "RESERVED", "claim_id": 42,
                "model": mod.MODEL, "effort": mod.EFFORT}))
            out = mod.call_api(context, Path(t))
            self.assertEqual(out["status"], "ABSTAIN")
            self.assertEqual(len(posted), 1)
            self.assertEqual(posted[0]["model"], "gpt-6.1-sol")
            self.assertEqual(posted[0]["reasoning"]["effort"], "max")
            self.assertIs(posted[0]["store"], False)
            self.assertIs(posted[0]["background"], True)
            self.assertEqual(posted[0]["text"]["format"]["type"], "json_schema")


if __name__ == "__main__":
    unittest.main()
