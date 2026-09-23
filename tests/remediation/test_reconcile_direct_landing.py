from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).parents[2]
OWNER_PATH = REPO / "scripts" / "remediation" / "merge_codex_research_intake.py"
RECONCILE_PATH = REPO / "scripts" / "remediation" / "reconcile_codex_research_merges.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


owner = load_module("merge_codex_research_intake_direct_landing_test", OWNER_PATH)
reconcile = load_module("reconcile_codex_research_merges_direct_landing_test", RECONCILE_PATH)


class DirectLandingReconciliationTests(unittest.TestCase):
    def init_repo(self, root: Path) -> str:
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        (root / "README.md").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "base"], cwd=root, check=True, capture_output=True)
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def candidate(self) -> dict:
        return {
            "contract": "CODEX_RESEARCH_CANDIDATE_v1",
            "candidate_id": "test-direct-landing",
            "status": "SUBMITTED",
            "authority_boundary": "CODE_REMEDIATION_ONLY",
            "requires_framework_owner_authority": False,
            "submitted_at_utc": "2026-09-23T11:40:00Z",
            "requested_priority": "EXPEDITED",
            "objective": "Prove a direct main landing leaves stale Codex state without authorizing resolution.",
            "allowed_change_scope": ["scripts/remediation"],
            "forbidden_changes": sorted(owner.REQUIRED_FORBIDDEN),
            "evidence": ["direct landing fixture"],
            "reproduction": "Bind a direct landing commit already contained in HEAD.",
            "acceptance_tests": {
                "positive": ["main-contained landing becomes post-fix observation"],
                "negative": ["non-main commit is rejected"],
            },
            "post_fix_gate": "RECONCILE_TESTS_PASS_PLUS_FIVE_LISTED_TASKS_LEAVE_STALE_STATES",
        }

    def task(self, root: Path) -> dict:
        candidate = self.candidate()
        path = root / "research/codex/intake/2026/09/test-direct-landing.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return owner.build_research_task(root, path, candidate, owner.canonical_hash(candidate))

    def receipt(self, task: dict, landing_sha: str) -> dict:
        value = {
            "contract": owner.DIRECT_MERGE_CONTRACT,
            "status": owner.DIRECT_MERGE_STATUS,
            "resolution_mode": "DIRECT_MAIN_LANDING",
            "authority": "OBSERVABILITY_ONLY_NO_COMPLETION_AUTHORITY",
            "signature": task["signature"],
            "candidate_id": task["candidate_id"],
            "candidate_sha256": task["candidate_sha256"],
            "task_contract_sha256": task["task_contract_sha256"],
            "branch": "agent/superseded-task-branch",
            "superseded_pr_number": 777,
            "landing_commit_sha": landing_sha,
            "landed_at_utc": "2026-09-23T12:00:00Z",
            "verified_at_utc": "2026-09-23T12:05:00Z",
            "post_fix_gate": task["post_fix_gate"],
            "equivalence_evidence": [
                "superseded PR head and direct landing implement the same bounded allowed scope"
            ],
            "verification_evidence": [
                "direct landing is contained in current HEAD",
                "focused regression evidence is present",
            ],
        }
        value["receipt_sha256"] = owner.canonical_hash(
            {k: v for k, v in value.items() if k != "receipt_sha256"}
        )
        return value

    def write_receipt(self, root: Path, task: dict, receipt: dict) -> Path:
        path = root / "research/codex/direct_merges" / f"{task['candidate_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def seed_queue_outputs(self, root: Path) -> Path:
        output = root / "research/remediation"
        output.mkdir(parents=True, exist_ok=True)
        (output / "LATEST_REMEDIATION_QUEUE.json").write_text(json.dumps({"items": []}) + "\n")
        (output / "LATEST_CODEX_READY_TASKS.json").write_text(json.dumps({"tasks": []}) + "\n")
        (output / "LATEST_NEEDS_MORE_EVIDENCE.json").write_text(json.dumps({"items": []}) + "\n")
        return output

    def test_direct_landing_commit_on_head_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            landing = self.init_repo(root)
            task = self.task(root)
            self.write_receipt(root, task, self.receipt(task, landing))
            accepted = owner.valid_direct_merge_receipt(root, task)
            self.assertIsNotNone(accepted)
            self.assertEqual(accepted["landing_commit_sha"], landing)

    def test_receipt_naming_commit_not_on_main_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.init_repo(root)
            task = self.task(root)
            self.write_receipt(root, task, self.receipt(task, "f" * 40))
            self.assertIsNone(owner.valid_direct_merge_receipt(root, task))

    def test_direct_landing_moves_codex_ready_to_post_fix_never_resolved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            landing = self.init_repo(root)
            task = self.task(root)
            self.write_receipt(root, task, self.receipt(task, landing))
            output = self.seed_queue_outputs(root)

            owner.merge(root, output)

            state = json.loads((root / "LATEST_CODEX_EXECUTION_STATE.json").read_text())
            row = next(x for x in state["tasks"] if x.get("candidate_id") == task["candidate_id"])
            self.assertEqual(row["state"], "POST_FIX_OBSERVATION")
            self.assertEqual(row["route"], "EVIDENCE")
            self.assertEqual(row["resolution_mode"], "DIRECT_MAIN_LANDING")
            self.assertEqual(row["merge_commit_sha"], landing)
            self.assertEqual(row["pr_number"], 777)
            self.assertEqual(row["post_fix_gate_status"], "REQUIRED_NOT_YET_VERIFIED")
            self.assertNotEqual(row["state"], "RESOLVED")

            ready = json.loads((output / "LATEST_CODEX_READY_TASKS.json").read_text())
            self.assertEqual(ready["tasks"], [])

    def test_reconciler_accepts_direct_receipt_without_transition(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            landing = self.init_repo(root)
            task = self.task(root)
            self.write_receipt(root, task, self.receipt(task, landing))
            (root / "LATEST_CODEX_EXECUTION_STATE.json").write_text(
                json.dumps({"tasks": [dict(task, state="CODEX_READY")]}) + "\n",
                encoding="utf-8",
            )

            result = reconcile.reconcile(root, "Donh91/Investering-Framework-Archive-v1")
            self.assertEqual(len(result["reconciled"]), 1)
            row = result["reconciled"][0]
            self.assertEqual(row["status"], "DIRECT_RECEIPT_VERIFIED")
            self.assertEqual(row["resolution_mode"], "DIRECT_MAIN_LANDING")
            self.assertEqual(row["merge_commit_sha"], landing)
            self.assertEqual(row["next_state"], "POST_FIX_OBSERVATION")
            self.assertFalse(result["resolution_authorized"])
            self.assertEqual(result["completion_receipts_created"], 0)


if __name__ == "__main__":
    unittest.main()
