"""No-network tests for exact-source Sol MAX patch artifact admission."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent import sol_max_elite_patch_admit as m
from scripts.api_agent import sol_max_elite_transport as t
from tests.api_agent.test_sol_max_elite_transport import sample, HEAD, MISSION

PATH = "scripts/example.py"
PATCH = (
    "diff --git a/scripts/example.py b/scripts/example.py\n"
    "index 1234567..7654321 100644\n"
    "--- a/scripts/example.py\n"
    "+++ b/scripts/example.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def fix():\n"
    "-    return 1\n"
    "+    return 2\n"
)


def fixture(root: Path, status="PATCH", patch=PATCH):
    sample(root)
    source = t.render_source(root, MISSION, HEAD)["packet"]
    request = t.checked_request(source)
    proposal = {"status": status, "unified_diff": patch,
                "rationale": "Synthetic isolated candidate, no merge",
                "tests": ["synthetic test"]}
    response = {
        "id": "resp_synthetic1234", "model": t.MODEL,
        "status": "completed", "output": [
            {"type": "message", "content": [
                {"type": "output_text", "text": json.dumps(proposal)}]}],
        "usage": {"input_tokens": 100, "output_tokens": 300},
    }
    return source, request, response


class ElitePatchAdmissionTests(unittest.TestCase):
    def test_valid_patch_only_creates_advisory_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            source, request, response = fixture(Path(td))
            receipt, proposal = m.admit(source, request, response)
            self.assertEqual(receipt["status"], "UNTRUSTED_PATCH_REQUIRES_REVIEW")
            self.assertEqual(receipt["changed_paths"], [PATH])
            self.assertEqual(receipt["source_head"], HEAD)
            self.assertFalse(receipt["source_written"])
            self.assertFalse(receipt["code_executed"])
            self.assertFalse(receipt["merge_authorized"])
            self.assertEqual(receipt["patch_sha256"], t.digest(PATCH.encode()))
            self.assertEqual(proposal["status"], "PATCH")

    def test_abstention_preserves_no_patch_and_no_execution(self):
        with tempfile.TemporaryDirectory() as td:
            source, request, response = fixture(Path(td), status="ABSTAIN", patch="")
            receipt, _ = m.admit(source, request, response)
            self.assertEqual(receipt["status"], "ABSTAIN")
            self.assertEqual(receipt["changed_paths"], [])
            self.assertIsNone(receipt["patch_sha256"])
            bad = json.loads(response["output"][0]["content"][0]["text"])
            bad["unified_diff"] = PATCH
            response["output"][0]["content"][0]["text"] = json.dumps(bad)
            with self.assertRaisesRegex(ValueError, "ABSTAIN_WITH_PATCH"):
                m.admit(source, request, response)

    def test_bad_source_hash_cannot_supply_false_patch_context(self):
        with tempfile.TemporaryDirectory() as td:
            source, request, response = fixture(Path(td))
            source["source_files"][PATH]["content"] += " malicious"
            with self.assertRaisesRegex(ValueError, "SOURCE_REQUEST_NOT_EXACTLY_BOUND"):
                m.admit(source, request, response)
            request = t.checked_request(source)
            with self.assertRaisesRegex(ValueError, "SOURCE_HASH_MISMATCH"):
                m.admit(source, request, response)

    def test_wrong_model_and_multiple_output_blocks_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            src, req, response = fixture(Path(td))
            response["model"] = "gpt-6-astra"
            with self.assertRaisesRegex(ValueError, "COMPLETION_OR_MODEL"):
                m.admit(src, req, response)
            response["model"] = t.MODEL
            response["output"][0]["content"].append(response["output"][0]["content"][0].copy())
            with self.assertRaisesRegex(ValueError, "STRUCTURED_TEXT_INVALID"):
                m.admit(src, req, response)

    def test_unlisted_file_delete_symlink_rename_and_header_spoofing_fail(self):
        with tempfile.TemporaryDirectory() as td:
            src, req, response = fixture(Path(td))
            poison = [
                PATCH.replace("scripts/example.py", ".github/workflows/bypass.yml"),
                PATCH.replace("scripts/example.py", "../secrets/token"),
                PATCH.replace("+++ b/scripts/example.py", "+++ b/scripts/other.py"),
                PATCH.replace("index 1234567..7654321 100644",
                              "deleted file mode 100644"),
                PATCH.replace("index 1234567..7654321 100644",
                              "rename from scripts/example.py"),
                PATCH + PATCH,
                "diff --git a/scripts/example.py b/scripts/example.py\n"
                "GIT binary patch\n",
                PATCH.replace("@@ -1,2 +1,2 @@", "no-hunk"),
            ]
            for bad in poison:
                with self.subTest(prefix=bad[:35]):
                    with self.assertRaises(ValueError):
                        m.patch_paths(bad, src["source_files"])

    def test_patch_with_private_token_pattern_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            src, _, _ = fixture(Path(td))
            injected = PATCH + "+sk-proj-" + "A" * 25 + "\n"
            with self.assertRaisesRegex(ValueError, "OVERSIZED_BINARY_OR_SECRET"):
                m.patch_paths(injected, src["source_files"])

    def test_complete_cli_artifact_is_readable_but_not_executed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src, req, rsp = fixture(root)
            for name, data in (("source.json", src), ("request.json", req),
                               ("provider_response.json", rsp)):
                (root / name).write_text(json.dumps(data))
            args = [root / "source.json", root / "request.json", root / "provider_response.json"]
            (root / "out").mkdir()
            for name in ("patch_candidate.json", "proposal.json", "candidate.patch"):
                self.assertFalse((root / "out" / name).exists())
            receipt, proposal = m.admit(*(json.loads(x.read_text()) for x in args))
            (root / "out" / "patch_candidate.json").write_bytes(t.canonical(receipt))
            (root / "out" / "proposal.json").write_bytes(t.canonical(proposal))
            (root / "out" / "candidate.patch").write_text(proposal["unified_diff"])
            self.assertEqual((root / "out" / "candidate.patch").read_text(), PATCH)
            self.assertEqual(json.loads((root / "out" / "patch_candidate.json").read_text())
                             ["source_written"], False)


    def test_authenticated_get_receipt_must_match_exact_source_and_response(self):
        with tempfile.TemporaryDirectory() as td:
            source, request, response = fixture(Path(td))
            receipt = {
                "contract": "S1_SOL_ELITE_GET_RECEIPT_v1",
                "origin_run": "41900777596",
                "response_id": response["id"],
                "mission": source["mission_id"],
                "source_head": source["source_head"],
                "context_sha256": t.digest(t.canonical(source)),
                "status": "COMPLETED",
                "http_status": 200,
                "new_paid_post": False,
                "source_applied": False,
                "merge_authorized": False,
            }
            m.verify_get_receipt(source, response, receipt)
            for field, forged in (
                ("response_id", "resp_wrong0000"),
                ("mission", "S1-UNAUTHORIZED-20261104"),
                ("source_head", "b" * 40),
                ("context_sha256", "0" * 64),
                ("status", "PENDING_GET_ONLY"),
                ("http_status", 404),
                ("new_paid_post", True),
                ("source_applied", True),
                ("merge_authorized", True),
                ("origin_run", "invalid-run"),
            ):
                with self.subTest(field=field):
                    tampered = dict(receipt)
                    tampered[field] = forged
                    with self.assertRaisesRegex(ValueError, "GET_RECEIPT_NOT_SOURCE_BOUND"):
                        m.verify_get_receipt(source, response, tampered)
            with self.assertRaises(ValueError):
                m.verify_get_receipt(source, response, {})
            with self.assertRaises(ValueError):
                m.verify_get_receipt(source, response, [])



if __name__ == "__main__":
    unittest.main()
