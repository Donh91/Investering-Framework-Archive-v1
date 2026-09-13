import json
import tempfile
import unittest
from pathlib import Path

from scripts.remediation.reconcile_codex_research_completions import reconcile
from scripts.remediation.merge_codex_research_intake import valid_completion
from scripts.remediation.write_codex_research_completion_receipt import (
    build_completion_receipt,
    canonical_hash,
)


class CodexResearchCompletionReconciliationTests(unittest.TestCase):
    repo_name = "example/framework"

    def make_root(self, *, pr_number=42, branch="agent/task-test"):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "research/codex/transitions").mkdir(parents=True, exist_ok=True)
        task = {
            "candidate_id": "codex-research-example",
            "source_type": "RESEARCH_INTAKE",
            "state": "IN_REMEDIATION",
            "signature": "sig-example",
            "candidate_sha256": "candidate-sha",
            "task_contract_sha256": "task-sha",
            "post_fix_gate": "TEST_GATE",
            "transition_receipt_path": "research/codex/transitions/sig-example.json",
        }
        (root / "LATEST_CODEX_EXECUTION_STATE.json").write_text(
            json.dumps({"tasks": [task]}), encoding="utf-8"
        )
        transition = {
            "contract": "CODEX_RESEARCH_TRANSITION_RECEIPT_v1",
            "state": "IN_REMEDIATION",
            "signature": task["signature"],
            "candidate_id": task["candidate_id"],
            "candidate_sha256": task["candidate_sha256"],
            "task_contract_sha256": task["task_contract_sha256"],
            "branch": branch,
            "pr_number": pr_number,
            "recorded_at_utc": "2026-09-08T00:00:00Z",
        }
        transition["receipt_sha256"] = canonical_hash(
            {k: v for k, v in transition.items() if k != "receipt_sha256"}
        )
        (root / task["transition_receipt_path"]).write_text(
            json.dumps(transition), encoding="utf-8"
        )
        return root, task, transition

    def pr(self, *, number=42, branch="agent/task-test", merged=True, merge_sha=None, repo_name=None):
        return {
            "number": number,
            "merged_at": "2026-09-08T01:00:00Z" if merged else None,
            "merge_commit_sha": merge_sha or ("a" * 40),
            "head": {
                "ref": branch,
                "repo": {"full_name": repo_name or self.repo_name},
            },
        }

    def write_verified_completion(self, root, task, *, pr_number=42):
        receipt = build_completion_receipt(
            root, task["candidate_id"], "a" * 40, pr_number,
            ["fixture:final-main-positive-negative-regression-and-post-fix-proof"],
            verified_at_utc="2026-09-08T02:00:00Z",
        )
        path = root / "research/codex/completions" / f"{task['candidate_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(receipt), encoding="utf-8")
        return path

    def test_exact_merged_pr_without_post_fix_proof_remains_pending(self):
        root, task, _ = self.make_root()
        original_state = (root / "LATEST_CODEX_EXECUTION_STATE.json").read_bytes()
        result = reconcile(
            root,
            self.repo_name,
            fetch_one=lambda repo, number: self.pr(number=number),
            fetch_many=lambda repo, branch: [],
        )
        self.assertEqual(result["reconciled"], [])
        self.assertEqual(result["pending"][0]["reason"], "MERGED_POST_FIX_VERIFICATION_REQUIRED")
        self.assertEqual(result["pending"][0]["post_fix_gate"], task["post_fix_gate"])
        self.assertEqual(result["pending"][0]["merge_commit_sha"], "a" * 40)
        self.assertIsNone(valid_completion(root, task))
        self.assertFalse((root / "research/codex/completions").exists())
        self.assertEqual((root / "LATEST_CODEX_EXECUTION_STATE.json").read_bytes(), original_state)

    def test_existing_verified_completion_is_validated_and_preserved_byte_for_byte(self):
        root, task, _ = self.make_root()
        path = self.write_verified_completion(root, task)
        original = path.read_bytes()
        for _ in range(2):
            result = reconcile(root, self.repo_name, fetch_one=lambda repo, number: self.pr())
            self.assertEqual(result["reconciled"][0]["status"], "ALREADY_PRESENT")
            self.assertEqual(result["pending"], [])
            self.assertEqual(path.read_bytes(), original)
            self.assertIsNotNone(valid_completion(root, task))

    def test_open_or_unmerged_pr_is_not_materialized(self):
        root, _, _ = self.make_root()
        result = reconcile(
            root,
            self.repo_name,
            fetch_one=lambda repo, number: self.pr(number=number, merged=False),
            fetch_many=lambda repo, branch: [],
        )
        self.assertEqual(result["pending"][0]["reason"], "BOUND_PR_NOT_VERIFIED_MERGED")
        self.assertFalse((root / "research/codex/completions/codex-research-example.json").exists())

    def test_wrong_branch_or_head_repository_is_rejected(self):
        for pr in (
            self.pr(branch="agent/other"),
            self.pr(repo_name="other/framework"),
        ):
            with self.subTest(pr=pr):
                root, _, _ = self.make_root()
                result = reconcile(
                    root,
                    self.repo_name,
                    fetch_one=lambda repo, number, pr=pr: pr,
                    fetch_many=lambda repo, branch: [],
                )
                self.assertEqual(result["pending"][0]["reason"], "BOUND_PR_NOT_VERIFIED_MERGED")
                self.assertFalse((root / "research/codex/completions/codex-research-example.json").exists())

    def test_transition_without_pr_number_requires_unique_merged_branch_match(self):
        root, _, _ = self.make_root(pr_number=None)
        result = reconcile(
            root,
            self.repo_name,
            fetch_one=lambda repo, number: self.fail("exact fetch should not run"),
            fetch_many=lambda repo, branch: [self.pr(number=77, branch=branch)],
        )
        self.assertEqual(result["pending"][0]["pr_number"], 77)
        self.assertEqual(result["pending"][0]["reason"], "MERGED_POST_FIX_VERIFICATION_REQUIRED")
        self.assertFalse((root / "research/codex/completions").exists())

    def test_ambiguous_merged_branch_matches_fail_closed(self):
        root, _, _ = self.make_root(pr_number=None)
        result = reconcile(
            root,
            self.repo_name,
            fetch_one=lambda repo, number: self.fail("exact fetch should not run"),
            fetch_many=lambda repo, branch: [
                self.pr(number=77, branch=branch),
                self.pr(number=78, branch=branch, merge_sha="b" * 40),
            ],
        )
        self.assertEqual(
            result["pending"][0]["reason"],
            "AMBIGUOUS_MERGED_PR_FOR_TRANSITION_BRANCH",
        )
        self.assertFalse((root / "research/codex/completions/codex-research-example.json").exists())

    def test_api_failure_preserves_in_remediation_without_fabrication(self):
        root, _, _ = self.make_root()

        def unavailable(repo, number):
            raise RuntimeError("GITHUB_API_UNAVAILABLE:test")

        result = reconcile(
            root,
            self.repo_name,
            fetch_one=unavailable,
            fetch_many=lambda repo, branch: [],
        )
        self.assertEqual(result["pending"][0]["reason"], "GITHUB_API_UNAVAILABLE:test")
        self.assertFalse((root / "research/codex/completions/codex-research-example.json").exists())

    def test_invalid_transition_hash_is_hard_failure(self):
        root, task, _ = self.make_root()
        path = root / task["transition_receipt_path"]
        transition = json.loads(path.read_text(encoding="utf-8"))
        transition["receipt_sha256"] = "0" * 64
        path.write_text(json.dumps(transition), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "INVALID_TRANSITION"):
            reconcile(
                root,
                self.repo_name,
                fetch_one=lambda repo, number: self.pr(number=number),
                fetch_many=lambda repo, branch: [],
            )

    def test_existing_completion_cannot_be_silently_rebound(self):
        root, task, _ = self.make_root()
        path = self.write_verified_completion(root, task)
        original = path.read_bytes()
        with self.assertRaisesRegex(RuntimeError, "CONTRADICTS_VERIFIED_MERGE"):
            reconcile(
                root,
                self.repo_name,
                fetch_one=lambda repo, number: self.pr(number=number, merge_sha="c" * 40),
                fetch_many=lambda repo, branch: [],
            )
        self.assertEqual(path.read_bytes(), original)

    def test_self_hashed_receipt_missing_verification_or_with_invalid_binding_is_rejected(self):
        for field, value in (
            ("verification_evidence", []),
            ("candidate_sha256", "wrong-candidate"),
            ("task_contract_sha256", "wrong-task"),
            ("execution_quality", {"contract": "INVALID"}),
            ("status", "UNVERIFIED"),
        ):
            with self.subTest(field=field):
                root, task, _ = self.make_root()
                path = self.write_verified_completion(root, task)
                receipt = json.loads(path.read_text())
                receipt[field] = value
                receipt["receipt_sha256"] = canonical_hash(
                    {k: v for k, v in receipt.items() if k != "receipt_sha256"}
                )
                path.write_text(json.dumps(receipt))
                original = path.read_bytes()
                with self.assertRaisesRegex(RuntimeError, "EXISTING_COMPLETION_INVALID"):
                    reconcile(root, self.repo_name, fetch_one=lambda repo, number: self.pr())
                self.assertEqual(path.read_bytes(), original)

    def test_existing_completion_cannot_satisfy_a_different_post_fix_gate(self):
        root, task, _ = self.make_root()
        path = self.write_verified_completion(root, task)
        receipt = json.loads(path.read_text())
        receipt["post_fix_gate"] = "WEAKER_GATE"
        receipt["receipt_sha256"] = canonical_hash(
            {k: v for k, v in receipt.items() if k != "receipt_sha256"}
        )
        path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(RuntimeError, "CONTRADICTS_VERIFIED_MERGE"):
            reconcile(root, self.repo_name, fetch_one=lambda repo, number: self.pr())


if __name__ == "__main__":
    unittest.main()
