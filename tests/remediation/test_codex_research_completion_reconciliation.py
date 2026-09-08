import json
import tempfile
import unittest
from pathlib import Path

from scripts.remediation.reconcile_codex_research_completions import reconcile
from scripts.remediation.write_codex_research_completion_receipt import canonical_hash


class CodexResearchCompletionReconciliationTests(unittest.TestCase):
    repo_name = "example/framework"

    def make_root(self, *, pr_number=42, branch="agent/task-test"):
        root = Path(tempfile.mkdtemp())
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

    def test_exact_bound_merged_pr_materializes_existing_completion_contract(self):
        root, task, _ = self.make_root()
        result = reconcile(
            root,
            self.repo_name,
            fetch_one=lambda repo, number: self.pr(number=number),
            fetch_many=lambda repo, branch: [],
        )
        self.assertEqual(result["reconciled"][0]["status"], "MATERIALIZED")
        path = root / "research/codex/completions/codex-research-example.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["contract"], "CODEX_RESEARCH_COMPLETION_RECEIPT_v1")
        self.assertEqual(receipt["pr_number"], 42)
        self.assertEqual(receipt["merge_commit_sha"], "a" * 40)
        self.assertEqual(receipt["execution_quality"]["telemetry_status"], "UNAVAILABLE")
        self.assertEqual(
            receipt["receipt_sha256"],
            canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"}),
        )

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
        self.assertEqual(result["reconciled"][0]["pr_number"], 77)

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
        root, _, _ = self.make_root()
        first = reconcile(
            root,
            self.repo_name,
            fetch_one=lambda repo, number: self.pr(number=number),
            fetch_many=lambda repo, branch: [],
        )
        self.assertEqual(first["reconciled"][0]["status"], "MATERIALIZED")
        with self.assertRaisesRegex(RuntimeError, "CONTRADICTS_VERIFIED_MERGE"):
            reconcile(
                root,
                self.repo_name,
                fetch_one=lambda repo, number: self.pr(number=number, merge_sha="c" * 40),
                fetch_many=lambda repo, branch: [],
            )


if __name__ == "__main__":
    unittest.main()
