import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).parents[2]
OWNER_PATH = REPO / "scripts" / "remediation" / "merge_codex_research_intake.py"
RECONCILE_PATH = REPO / "scripts" / "remediation" / "reconcile_codex_research_merges.py"
WORKFLOW_PATH = REPO / ".github" / "workflows" / "remediation-maturation.yml"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


owner = load_module("merge_codex_research_intake_test", OWNER_PATH)
reconcile = load_module("reconcile_codex_research_merges_test", RECONCILE_PATH)


class CodexResearchMergeReconciliationTests(unittest.TestCase):
    def candidate(self):
        return {
            "contract": "CODEX_RESEARCH_CANDIDATE_v1",
            "candidate_id": "test-merge-reconciliation",
            "status": "SUBMITTED",
            "authority_boundary": "CODE_REMEDIATION_ONLY",
            "requires_framework_owner_authority": False,
            "requested_priority": "EXPEDITED",
            "submitted_at_utc": "2026-09-13T09:00:00Z",
            "objective": "Prove merged work enters post-fix observation before resolution.",
            "allowed_change_scope": ["scripts/remediation"],
            "forbidden_changes": sorted(owner.REQUIRED_FORBIDDEN),
            "evidence": ["synthetic positive/negative acceptance fixture"],
            "reproduction": "Create a valid transition, then a verified merge receipt without a completion receipt.",
            "acceptance_tests": {
                "positive": ["verified bound merge becomes POST_FIX_OBSERVATION"],
                "negative": ["unmerged or wrong-branch PR cannot create merge receipt"],
            },
            "post_fix_gate": "TWO_CONSECUTIVE_REMEDIATION_MATURATION_RUNS_WITH_NO_MERGED_RESEARCH_TASK_ZOMBIES",
        }

    def write_fixture(self, root: Path):
        candidate = self.candidate()
        candidate_path = root / "research/codex/intake/2026/09/test-merge-reconciliation.json"
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
        candidate_sha = owner.canonical_hash(candidate)
        task = owner.build_research_task(root, candidate_path, candidate, candidate_sha)
        transition = {
            "contract": "CODEX_RESEARCH_TRANSITION_RECEIPT_v1",
            "state": "IN_REMEDIATION",
            "signature": task["signature"],
            "candidate_id": task["candidate_id"],
            "candidate_path": task["candidate_path"],
            "candidate_sha256": task["candidate_sha256"],
            "branch": "agent/test-merge-reconciliation",
            "pr_number": 123,
            "recorded_at_utc": "2026-09-13T09:05:00Z",
            "objective": task["objective"],
            "allowed_change_scope": task["allowed_change_scope"],
            "forbidden_changes": task["forbidden_changes"],
            "post_fix_gate": task["post_fix_gate"],
            "task_contract_sha256": task["task_contract_sha256"],
        }
        transition["receipt_sha256"] = owner.canonical_hash({k: v for k, v in transition.items() if k != "receipt_sha256"})
        transition_path = root / task["transition_receipt_path"]
        transition_path.parent.mkdir(parents=True, exist_ok=True)
        transition_path.write_text(json.dumps(transition, indent=2, sort_keys=True) + "\n")
        return task, transition

    def test_unmerged_or_wrong_branch_pr_never_qualifies(self):
        transition = {"branch": "agent/test", "pr_number": 7}
        unmerged = {
            "number": 7,
            "merged_at": None,
            "merge_commit_sha": None,
            "head": {"ref": "agent/test", "repo": {"full_name": "Donh91/Investering-Framework-Archive-v1"}},
        }
        self.assertIsNone(
            reconcile.verify_merged_pr(
                "Donh91/Investering-Framework-Archive-v1",
                transition,
                fetch_one=lambda _repo, _number: unmerged,
            )
        )
        wrong_branch = dict(unmerged)
        wrong_branch.update({"merged_at": "2026-09-13T09:10:00Z", "merge_commit_sha": "a" * 40})
        wrong_branch["head"] = {"ref": "agent/other", "repo": {"full_name": "Donh91/Investering-Framework-Archive-v1"}}
        self.assertIsNone(
            reconcile.verify_merged_pr(
                "Donh91/Investering-Framework-Archive-v1",
                transition,
                fetch_one=lambda _repo, _number: wrong_branch,
            )
        )

    def test_reconciler_creates_merge_receipt_but_never_completion_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            task, _transition = self.write_fixture(root)
            state = {"contract": "CODEX_EXECUTION_STATE_v1", "tasks": [dict(task, state="IN_REMEDIATION")]}
            (root / "LATEST_CODEX_EXECUTION_STATE.json").write_text(json.dumps(state) + "\n")
            merged = {
                "number": 123,
                "merged_at": "2026-09-13T09:10:00Z",
                "merge_commit_sha": "b" * 40,
                "head": {"ref": "agent/test-merge-reconciliation", "repo": {"full_name": "Donh91/Investering-Framework-Archive-v1"}},
            }
            result = reconcile.reconcile(
                root,
                "Donh91/Investering-Framework-Archive-v1",
                fetch_one=lambda _repo, _number: merged,
                verified_at="2026-09-13T09:11:00Z",
            )
            self.assertEqual(len(result["reconciled"]), 1)
            self.assertEqual(result["completion_receipts_created"], 0)
            self.assertFalse(result["resolution_authorized"])
            self.assertTrue((root / "research/codex/merges/test-merge-reconciliation.json").exists())
            self.assertFalse((root / "research/codex/completions/test-merge-reconciliation.json").exists())

    def test_merge_receipt_moves_owner_to_post_fix_observation_not_resolved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            task, transition = self.write_fixture(root)
            pr = {
                "number": 123,
                "merged_at": "2026-09-13T09:10:00Z",
                "merge_commit_sha": "c" * 40,
            }
            merge_receipt = reconcile.build_merge_receipt(task, transition, pr, verified_at="2026-09-13T09:11:00Z")
            merge_path = root / "research/codex/merges/test-merge-reconciliation.json"
            merge_path.parent.mkdir(parents=True, exist_ok=True)
            merge_path.write_text(json.dumps(merge_receipt, indent=2, sort_keys=True) + "\n")

            output = root / "research/remediation"
            output.mkdir(parents=True, exist_ok=True)
            (output / "LATEST_REMEDIATION_QUEUE.json").write_text(json.dumps({"items": []}) + "\n")
            (output / "LATEST_CODEX_READY_TASKS.json").write_text(json.dumps({"tasks": []}) + "\n")
            (output / "LATEST_NEEDS_MORE_EVIDENCE.json").write_text(json.dumps({"items": []}) + "\n")

            owner.merge(root, output)
            state = json.loads((root / "LATEST_CODEX_EXECUTION_STATE.json").read_text())
            selected = [row for row in state["tasks"] if row.get("candidate_id") == "test-merge-reconciliation"]
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]["state"], "POST_FIX_OBSERVATION")
            self.assertEqual(selected[0]["route"], "EVIDENCE")
            self.assertEqual(selected[0]["post_fix_gate_status"], "REQUIRED_NOT_YET_VERIFIED")
            self.assertNotEqual(selected[0]["state"], "RESOLVED")

    def test_poison_item_does_not_starve_healthy_item(self):
        from unittest.mock import patch

        for failure in ("invalid_pr", "malformed_transition", "conflicting_receipt", "api_error"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                bad_candidate = dict(self.candidate(), candidate_id="bad-item")
                with patch.object(self, "candidate", return_value=bad_candidate):
                    bad_task, bad_transition = self.write_fixture(root)
                good_task, _ = self.write_fixture(root)
                bad_path = root / bad_task["transition_receipt_path"]
                if failure == "invalid_pr":
                    bad_transition["pr_number"] = True
                    bad_transition["receipt_sha256"] = owner.canonical_hash({
                        k: v for k, v in bad_transition.items() if k != "receipt_sha256"
                    })
                    bad_path.write_text(json.dumps(bad_transition))
                elif failure == "malformed_transition":
                    bad_path.write_text('["not a receipt"]')
                else:
                    bad_transition["pr_number"] = 124
                    bad_transition["receipt_sha256"] = owner.canonical_hash({
                        k: v for k, v in bad_transition.items() if k != "receipt_sha256"
                    })
                    bad_path.write_text(json.dumps(bad_transition))
                frozen_path = root / "research/codex/merges/bad-item.json"
                if failure == "conflicting_receipt":
                    frozen_path.parent.mkdir(parents=True, exist_ok=True)
                    frozen_path.write_text('{"immutable": "do not replace"}\n')
                before = frozen_path.read_bytes() if frozen_path.exists() else None
                (root / "LATEST_CODEX_EXECUTION_STATE.json").write_text(json.dumps({
                    "tasks": [dict(bad_task, state="IN_REMEDIATION"),
                              dict(good_task, state="IN_REMEDIATION")]
                }))

                def fetch(_repo, number):
                    if failure == "api_error" and number == 124:
                        raise RuntimeError("GITHUB_API_UNAVAILABLE:PRIVATE_RESPONSE_CANARY")
                    return {"number": number, "merged_at": "2026-09-13T09:10:00Z",
                            "merge_commit_sha": "b" * 40,
                            "head": {"ref": "agent/test-merge-reconciliation",
                                     "repo": {"full_name": "Donh91/Investering-Framework-Archive-v1"}}}

                result = reconcile.reconcile(root, "Donh91/Investering-Framework-Archive-v1",
                                             fetch_one=fetch, verified_at="2026-09-13T09:11:00Z")
                self.assertEqual([r["candidate_id"] for r in result["reconciled"]],
                                 [good_task["candidate_id"]])
                self.assertEqual(len(result["pending"]), 1)
                self.assertEqual(result["pending"][0]["candidate_id"], "bad-item")
                self.assertNotIn("PRIVATE_RESPONSE_CANARY", json.dumps(result))
                self.assertEqual(result["completion_receipts_created"], 0)
                self.assertFalse(result["resolution_authorized"])
                if before is not None:
                    self.assertEqual(frozen_path.read_bytes(), before)
                else:
                    self.assertFalse(frozen_path.exists())
                good_path = root / "research/codex/merges/test-merge-reconciliation.json"
                good_bytes = good_path.read_bytes()
                replay = reconcile.reconcile(root, "Donh91/Investering-Framework-Archive-v1",
                                             fetch_one=fetch, verified_at="2026-09-13T10:11:00Z")
                self.assertEqual(replay["reconciled"][0]["status"], "ALREADY_PRESENT")
                self.assertEqual(good_path.read_bytes(), good_bytes)

    def test_workflow_reconciles_between_two_owner_materializations(self):
        text = WORKFLOW_PATH.read_text()
        first = text.find("python scripts/remediation/merge_codex_research_intake.py")
        reconcile_pos = text.find("python scripts/remediation/reconcile_codex_research_merges.py")
        second = text.find("python scripts/remediation/merge_codex_research_intake.py", first + 1)
        self.assertGreaterEqual(first, 0)
        self.assertGreater(reconcile_pos, first)
        self.assertGreater(second, reconcile_pos)
        self.assertIn("research/codex/merges", text)


if __name__ == "__main__":
    unittest.main()
