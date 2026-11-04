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
            out = mod.call_api(context, Path(t))
            self.assertEqual(out["status"], "ABSTAIN")
            self.assertEqual(len(posted), 1)
            self.assertEqual(posted[0]["model"], "gpt-6.1-sol")
            self.assertEqual(posted[0]["reasoning"]["effort"], "max")
            self.assertIs(posted[0]["store"], False)
            self.assertEqual(posted[0]["text"]["format"]["type"], "json_schema")


if __name__ == "__main__":
    unittest.main()
