"""No-network, no-credential patch sandbox tests on disposable Git repositories."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent import sol_max_elite_sandbox as s
from scripts.api_agent import sol_max_elite_transport as t

PATH = "scripts/example.py"
ORIG = b"def fix():\n    return 1\n"
PATCH = (
    "diff --git a/scripts/example.py b/scripts/example.py\n"
    "index 1234567..7654321 100644\n"
    "--- a/scripts/example.py\n"
    "+++ b/scripts/example.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def fix():\n"
    "-    return 1\n"
    "+    return 2\n"
).encode()


def local_git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_case(repo: Path):
    local_git(repo, "init", "-q")
    local_git(repo, "config", "user.email", "test@example.invalid")
    local_git(repo, "config", "user.name", "Test")
    file = repo / PATH
    file.parent.mkdir(parents=True)
    file.write_bytes(ORIG)
    local_git(repo, "add", PATH)
    local_git(repo, "commit", "-qm", "fixture")
    head = local_git(repo, "rev-parse", "HEAD")
    source = {
        "contract": "S1_SOL_ELITE_SOURCE_PACKET_v1",
        "repo": t.REPO, "source_head": head,
        "mission_id": "S1-ELITE-EXECUTOR-20261104",
        "source_files": {PATH: {
            "bytes": len(ORIG), "sha256": t.digest(ORIG), "content": ORIG.decode(),
        }},
    }
    candidate = {
        "contract": "S1_SOL_ELITE_PATCH_CANDIDATE_v1",
        "status": "UNTRUSTED_PATCH_REQUIRES_REVIEW",
        "source_head": head,
        "source_sha256": t.digest(t.canonical(source)),
        "patch_sha256": t.digest(PATCH),
        "changed_paths": [PATH],
        "response_id": "resp_sandbox0000",
        "source_written": False, "code_executed": False, "merge_authorized": False,
    }
    receipt = {
        "contract": "S1_SOL_ELITE_GET_RECEIPT_v1",
        "status": "COMPLETED", "http_status": 200,
        "response_id": candidate["response_id"],
        "mission": source["mission_id"],
        "source_head": head,
        "context_sha256": t.digest(t.canonical(source)),
        "new_paid_post": False, "source_applied": False, "merge_authorized": False,
    }
    return source, candidate, receipt


class EliteSandboxTests(unittest.TestCase):
    def test_valid_patch_applies_only_in_disposable_worktree(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            src, cand, receipt = make_case(repo)
            result = s.verify_in_sandbox(repo, src, cand, receipt, PATCH)
            self.assertEqual(result["status"], "PATCH_APPLIES_AND_PYTHON_SYNTAX_VALID")
            self.assertFalse(result["source_pushed"])
            self.assertFalse(result["model_code_executed"])
            self.assertFalse(result["domain_regressions_executed"])
            self.assertEqual(result["changed_paths"], [PATH])
            self.assertEqual((repo / PATH).read_bytes(), ORIG)
            self.assertEqual(local_git(repo, "status", "--porcelain"), "")

    def test_wrong_response_source_and_changed_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            src, cand, receipt = make_case(repo)
            for field, value in [
                ("response_id", "resp_zzzz9999"),
                ("source_sha256", "0" * 64),
                ("changed_paths", ["scripts/unlisted.py"]),
            ]:
                modified = dict(cand)
                modified[field] = value
                with self.subTest(field=field), self.assertRaises(ValueError):
                    s.verify_in_sandbox(repo, src, modified, receipt, PATCH)
            modified_receipt = dict(receipt, status="PENDING_GET_ONLY")
            with self.assertRaises(ValueError):
                s.verify_in_sandbox(repo, src, cand, modified_receipt, PATCH)
            self.assertEqual(local_git(repo, "status", "--porcelain"), "")

    def test_stale_source_and_non_applying_patch_fail_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            src, cand, receipt = make_case(repo)
            (repo / PATH).write_bytes(b"def fix():\n    return 999\n")
            with self.assertRaisesRegex(ValueError, "GIT_VERIFICATION_FAILED"):
                bad = PATCH.replace(b"return 1", b"return 3")
                cand["patch_sha256"] = t.digest(bad)
                s.verify_in_sandbox(repo, src, cand, receipt, bad)
            self.assertEqual((repo / PATH).read_bytes(), b"def fix():\n    return 999\n")

    def test_invalid_python_syntax_in_patch_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            src, cand, receipt = make_case(repo)
            patch = PATCH.replace(b"return 2", b"return )")
            cand["patch_sha256"] = t.digest(patch)
            with self.assertRaisesRegex(ValueError, "SYNTAX_INVALID"):
                s.verify_in_sandbox(repo, src, cand, receipt, patch)
            self.assertEqual((repo / PATH).read_bytes(), ORIG)

if __name__ == "__main__":
    unittest.main()
