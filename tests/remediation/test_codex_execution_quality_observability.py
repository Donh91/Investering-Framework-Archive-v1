import json
import tempfile
import unittest
from pathlib import Path

from scripts.remediation.merge_codex_research_intake import (
    build_research_task,
    canonical_hash as merge_hash,
    merge,
    valid_completion,
)
from scripts.remediation.write_codex_research_completion_receipt import (
    build_completion_receipt,
    canonical_hash as completion_hash,
    normalize_execution_quality,
)


class CodexExecutionQualityObservabilityTests(unittest.TestCase):
    def make_root(self):
        root = Path(tempfile.mkdtemp())
        (root / "research/codex").mkdir(parents=True, exist_ok=True)
        return root

    def task(self, candidate_id="codex-research-quality-test", state="IN_REMEDIATION"):
        return {
            "candidate_id": candidate_id,
            "source_type": "RESEARCH_INTAKE",
            "state": state,
            "signature": "abc123",
            "candidate_sha256": "candidate-sha",
            "task_contract_sha256": "task-sha",
            "post_fix_gate": "TEST_GATE",
        }

    def write_execution_state(self, root, task):
        (root / "LATEST_CODEX_EXECUTION_STATE.json").write_text(
            json.dumps({"tasks": [task]}), encoding="utf-8"
        )

    def test_new_completion_without_telemetry_is_explicitly_unavailable(self):
        root = self.make_root()
        self.write_execution_state(root, self.task())
        receipt = build_completion_receipt(
            root,
            "codex-research-quality-test",
            "merge-sha",
            123,
            ["ci:success"],
            verified_at_utc="2026-08-31T00:00:00Z",
        )
        quality = receipt["execution_quality"]
        self.assertEqual(quality["telemetry_status"], "UNAVAILABLE")
        self.assertEqual(quality["metrics"], {})
        self.assertEqual(quality["failure_attribution"], [])
        expected_hash = completion_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
        self.assertEqual(receipt["receipt_sha256"], expected_hash)

    def test_captured_telemetry_is_dimensioned_and_evidence_backed(self):
        root = self.make_root()
        self.write_execution_state(root, self.task())
        telemetry = root / "telemetry.json"
        telemetry.write_text(json.dumps({
            "contract": "CODEX_EXECUTION_TELEMETRY_v1",
            "telemetry_status": "PARTIAL",
            "evidence": ["run:42", "test:unit"],
            "metrics": {
                "first_model_triggered_test_outcome": "FAIL",
                "tool_calls_before_first_edit": 6,
                "unique_files_read_before_first_edit": 4,
                "edits_after_first_test": 2,
                "test_cycles": 3,
                "rework_cycles": 1,
                "final_test_success": True,
            },
            "failure_attribution": [
                {"dimension": "TEST_FAILURE", "evidence_ref": "run:42#first-test"}
            ],
        }), encoding="utf-8")
        receipt = build_completion_receipt(
            root,
            "codex-research-quality-test",
            "merge-sha",
            123,
            ["ci:success"],
            telemetry_path=telemetry,
            verified_at_utc="2026-08-31T00:00:00Z",
        )
        quality = receipt["execution_quality"]
        self.assertEqual(quality["telemetry_status"], "PARTIAL")
        self.assertEqual(quality["metrics"]["first_model_triggered_test_outcome"], "FAIL")
        self.assertEqual(quality["metrics"]["rework_cycles"], 1)
        self.assertEqual(quality["failure_attribution"][0]["dimension"], "TEST_FAILURE")

    def test_unavailable_telemetry_cannot_hide_observations(self):
        with self.assertRaisesRegex(ValueError, "UNAVAILABLE_WITH_OBSERVATIONS"):
            normalize_execution_quality({
                "contract": "CODEX_EXECUTION_TELEMETRY_v1",
                "telemetry_status": "UNAVAILABLE",
                "evidence": [],
                "metrics": {"total_edits": 2},
                "failure_attribution": [],
            })

    def test_unknown_metrics_and_missing_evidence_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "UNKNOWN_METRIC"):
            normalize_execution_quality({
                "contract": "CODEX_EXECUTION_TELEMETRY_v1",
                "telemetry_status": "PARTIAL",
                "evidence": ["run:1"],
                "metrics": {"magic_quality_score": 99},
                "failure_attribution": [],
            })
        with self.assertRaisesRegex(ValueError, "EVIDENCE_REQUIRED"):
            normalize_execution_quality({
                "contract": "CODEX_EXECUTION_TELEMETRY_v1",
                "telemetry_status": "CAPTURED",
                "evidence": [],
                "metrics": {"total_edits": 1},
                "failure_attribution": [],
            })

    def test_legacy_completion_remains_valid(self):
        root = self.make_root()
        task = self.task()
        path = root / "research/codex/completions"
        path.mkdir(parents=True, exist_ok=True)
        receipt = {
            "contract": "CODEX_RESEARCH_COMPLETION_RECEIPT_v1",
            "status": "VERIFIED",
            "candidate_id": task["candidate_id"],
            "signature": task["signature"],
            "candidate_sha256": task["candidate_sha256"],
            "task_contract_sha256": task["task_contract_sha256"],
            "pr_number": 100,
            "merge_commit_sha": "legacy-merge",
            "verified_at_utc": "2026-08-20T00:00:00Z",
            "verification_evidence": ["legacy:ci-pass"],
            "post_fix_gate": "TEST_GATE",
        }
        receipt["receipt_sha256"] = merge_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
        (path / f"{task['candidate_id']}.json").write_text(json.dumps(receipt), encoding="utf-8")
        self.assertIsNotNone(valid_completion(root, task))

    def make_candidate(self):
        return {
            "contract": "CODEX_RESEARCH_CANDIDATE_v1",
            "candidate_id": "codex-research-quality-integration",
            "submitted_at_utc": "2026-08-31T00:00:00Z",
            "status": "SUBMITTED",
            "origin": {"type": "AUDIT"},
            "title": "Quality integration",
            "objective": "Preserve bounded Codex execution-quality telemetry.",
            "finding_key": "CODEX_EXECUTION_QUALITY_OBSERVABILITY_MISSING",
            "allowed_change_scope": ["scripts/remediation/directly related test scope"],
            "evidence": [{"kind": "REPO_PATH", "ref": "scripts/remediation/example.py"}],
            "reproduction": "Two equal final states currently hide different execution paths.",
            "acceptance_tests": {"positive": ["telemetry survives"], "negative": ["no inference"]},
            "authority_boundary": "CODE_REMEDIATION_ONLY",
            "requires_framework_owner_authority": False,
            "forbidden_changes": [
                "market gates", "model weights", "canonical authority", "portfolio logic", "API budget", "new policy semantics"
            ],
            "requested_priority": "NORMAL",
            "post_fix_gate": "TEST_GATE",
        }

    def prepare_merge_repo(self, *, legacy=False):
        root = self.make_root()
        candidate = self.make_candidate()
        candidate_path = root / "research/codex/intake/2026/08" / f"{candidate['candidate_id']}.json"
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

        output = root / "research/remediation"
        output.mkdir(parents=True, exist_ok=True)
        (output / "LATEST_REMEDIATION_QUEUE.json").write_text(json.dumps({"items": []}), encoding="utf-8")
        (output / "LATEST_CODEX_READY_TASKS.json").write_text(json.dumps({"tasks": []}), encoding="utf-8")
        (output / "LATEST_NEEDS_MORE_EVIDENCE.json").write_text(json.dumps({"items": []}), encoding="utf-8")

        candidate_sha = merge_hash(candidate)
        task = build_research_task(root, candidate_path, candidate, candidate_sha)
        completion_dir = root / "research/codex/completions"
        completion_dir.mkdir(parents=True, exist_ok=True)
        receipt = {
            "contract": "CODEX_RESEARCH_COMPLETION_RECEIPT_v1",
            "status": "VERIFIED",
            "candidate_id": candidate["candidate_id"],
            "signature": task["signature"],
            "candidate_sha256": candidate_sha,
            "task_contract_sha256": task["task_contract_sha256"],
            "pr_number": 321,
            "merge_commit_sha": "integration-merge",
            "verified_at_utc": "2026-08-31T00:10:00Z",
            "verification_evidence": ["ci:green"],
            "post_fix_gate": "TEST_GATE",
        }
        if not legacy:
            receipt["execution_quality"] = {
                "contract": "CODEX_EXECUTION_QUALITY_v1",
                "telemetry_status": "CAPTURED",
                "evidence": ["run:integration"],
                "metrics": {"total_edits": 2, "test_cycles": 1, "final_test_success": True},
                "failure_attribution": [],
            }
        receipt["receipt_sha256"] = merge_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
        (completion_dir / f"{candidate['candidate_id']}.json").write_text(json.dumps(receipt), encoding="utf-8")
        return root, output, task

    def test_merge_propagates_quality_to_state_and_ledger_without_queue_authority(self):
        root, output, task = self.prepare_merge_repo(legacy=False)
        merge(root, output)
        state = json.loads((root / "LATEST_CODEX_EXECUTION_STATE.json").read_text(encoding="utf-8"))
        resolved = next(x for x in state["tasks"] if x["signature"] == task["signature"])
        self.assertEqual(resolved["state"], "RESOLVED")
        self.assertEqual(resolved["execution_quality"]["telemetry_status"], "CAPTURED")
        self.assertEqual(state["queue_authority"], "LATEST_CODEX_READY_TASKS.json")
        ready = json.loads((output / "LATEST_CODEX_READY_TASKS.json").read_text(encoding="utf-8"))
        self.assertFalse(any(x.get("signature") == task["signature"] for x in ready["tasks"]))
        ledger_lines = (root / "research/codex/CODEX_EXECUTION_LEDGER.jsonl").read_text(encoding="utf-8").splitlines()
        event = next(json.loads(line) for line in ledger_lines if json.loads(line).get("signature") == task["signature"])
        self.assertEqual(event["execution_quality"]["metrics"]["total_edits"], 2)

    def test_merge_classifies_legacy_missing_telemetry_without_backfill(self):
        root, output, task = self.prepare_merge_repo(legacy=True)
        merge(root, output)
        state = json.loads((root / "LATEST_CODEX_EXECUTION_STATE.json").read_text(encoding="utf-8"))
        resolved = next(x for x in state["tasks"] if x["signature"] == task["signature"])
        quality = resolved["execution_quality"]
        self.assertEqual(quality["telemetry_status"], "UNAVAILABLE")
        self.assertTrue(quality["legacy_receipt_without_telemetry"])
        self.assertEqual(quality["metrics"], {})
        self.assertEqual(quality["failure_attribution"], [])

    def test_malformed_hashed_quality_block_does_not_resolve(self):
        root, output, task = self.prepare_merge_repo(legacy=False)
        completion = root / "research/codex/completions" / f"{task['candidate_id']}.json"
        receipt = json.loads(completion.read_text(encoding="utf-8"))
        receipt["execution_quality"] = {
            "contract": "CODEX_EXECUTION_QUALITY_v1",
            "telemetry_status": "CAPTURED",
            "evidence": [],
            "metrics": {"total_edits": 2},
            "failure_attribution": [],
        }
        receipt["receipt_sha256"] = merge_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
        completion.write_text(json.dumps(receipt), encoding="utf-8")
        self.assertIsNone(valid_completion(root, task))


if __name__ == "__main__":
    unittest.main()
