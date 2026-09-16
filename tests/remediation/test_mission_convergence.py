import json
import tempfile
import unittest
from pathlib import Path

from scripts.remediation import merge_codex_research_intake as base
from scripts.remediation import merge_codex_research_intake_converged as gated
from scripts.remediation import mission_convergence as convergence


class MissionConvergenceTests(unittest.TestCase):
    def make_root(self):
        root = Path(tempfile.mkdtemp())
        (root / "research/codex").mkdir(parents=True, exist_ok=True)
        return root

    def candidate(self, candidate_id="mission-convergence-test"):
        return {
            "contract": "CODEX_RESEARCH_CANDIDATE_v1",
            "candidate_id": candidate_id,
            "status": "SUBMITTED",
            "authority_boundary": "CODE_REMEDIATION_ONLY",
            "requires_framework_owner_authority": False,
            "requested_priority": "EXPEDITED",
            "submitted_at_utc": "2026-09-13T15:31:00Z",
            "objective": "Prove closure requires full mission coverage rather than a green PR alone.",
            "allowed_change_scope": ["scripts/remediation", "tests/remediation"],
            "forbidden_changes": sorted(base.REQUIRED_FORBIDDEN),
            "evidence": ["Spec Kit converge pattern"],
            "reproduction": "Create a verified completion without a convergence receipt.",
            "acceptance_tests": {
                "positive": [
                    "complete requirement coverage with evidence is admitted",
                    "legacy completion before activation remains valid",
                ],
                "negative": [
                    "missing coverage cannot converge",
                    "actionable gaps cannot converge",
                ],
            },
            "post_fix_gate": "ONE_VERIFIED_POST_FIX_RUN",
        }

    def prepare_task(self, root, candidate=None, state="POST_FIX_OBSERVATION"):
        candidate = candidate or self.candidate()
        path = root / "research/codex/intake/2026/09" / f"{candidate['candidate_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        task = base.build_research_task(root, path, candidate, base.canonical_hash(candidate))
        task["state"] = state
        (root / "LATEST_CODEX_EXECUTION_STATE.json").write_text(
            json.dumps({"contract": "CODEX_EXECUTION_STATE_v1", "tasks": [task]}, indent=2) + "\n",
            encoding="utf-8",
        )
        return candidate, task

    def assessment_for(self, task, candidate, *, gaps=None, blocked_ref=None):
        inventory = convergence.requirement_inventory(task, candidate)
        coverage = []
        for item in inventory:
            coverage.append({
                "source_ref": item["source_ref"],
                "status": "BLOCKED" if item["source_ref"] == blocked_ref else "SATISFIED",
                "evidence": [f"evidence:{item['source_ref']}"],
            })
        return {
            "contract": convergence.ASSESSMENT_CONTRACT,
            "candidate_id": candidate["candidate_id"],
            "coverage": coverage,
            "gaps": gaps or [],
        }

    def write_completion(self, root, task, *, verified_at="2026-09-13T16:10:00Z"):
        receipt = {
            "contract": "CODEX_RESEARCH_COMPLETION_RECEIPT_v1",
            "status": "VERIFIED",
            "candidate_id": task["candidate_id"],
            "signature": task["signature"],
            "candidate_sha256": task["candidate_sha256"],
            "task_contract_sha256": task["task_contract_sha256"],
            "pr_number": 404,
            "merge_commit_sha": "d" * 40,
            "verified_at_utc": verified_at,
            "verification_evidence": ["ci:green", "post-fix:pass"],
            "post_fix_gate": task["post_fix_gate"],
        }
        receipt["receipt_sha256"] = base.canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
        path = root / "research/codex/completions" / f"{task['candidate_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return receipt

    def test_complete_coverage_builds_converged_hash_bound_receipt(self):
        root = self.make_root()
        candidate, task = self.prepare_task(root)
        assessment = self.assessment_for(task, candidate)
        assessment_path = root / "assessment.json"
        assessment_path.write_text(json.dumps(assessment), encoding="utf-8")
        receipt = convergence.build_receipt(
            root,
            candidate["candidate_id"],
            "d" * 40,
            404,
            assessment_path,
            assessed_at_utc="2026-09-13T16:09:00Z",
        )
        self.assertEqual(receipt["status"], convergence.STATUS_CONVERGED)
        self.assertEqual(receipt["gaps"], [])
        self.assertTrue(all(x["status"] == "SATISFIED" for x in receipt["coverage"]))
        self.assertEqual(
            receipt["receipt_sha256"],
            convergence.canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"}),
        )

    def test_missing_requirement_coverage_is_rejected(self):
        root = self.make_root()
        candidate, task = self.prepare_task(root)
        assessment = self.assessment_for(task, candidate)
        assessment["coverage"].pop()
        inventory = convergence.requirement_inventory(task, candidate)
        with self.assertRaisesRegex(ValueError, "COVERAGE_INCOMPLETE"):
            convergence.normalize_assessment(assessment, inventory)

    def test_blocked_requirement_or_actionable_gap_is_not_converged(self):
        root = self.make_root()
        candidate, task = self.prepare_task(root)
        assessment = self.assessment_for(task, candidate, blocked_ref="objective")
        coverage, gaps, status = convergence.normalize_assessment(
            assessment, convergence.requirement_inventory(task, candidate)
        )
        self.assertEqual(status, convergence.STATUS_NOT_CONVERGED)
        self.assertTrue(any(x["status"] == "BLOCKED" for x in coverage))
        self.assertEqual(gaps, [])

        assessment = self.assessment_for(
            task,
            candidate,
            gaps=[{"gap_type": "unrequested", "source_ref": "", "evidence": ["diff:unexpected-file"]}],
        )
        _coverage, gaps, status = convergence.normalize_assessment(
            assessment, convergence.requirement_inventory(task, candidate)
        )
        self.assertEqual(status, convergence.STATUS_NOT_CONVERGED)
        self.assertEqual(gaps[0]["gap_type"], "unrequested")

    def test_post_activation_completion_cannot_resolve_without_convergence(self):
        root = self.make_root()
        _candidate, task = self.prepare_task(root)
        completion = self.write_completion(root, task)
        self.assertIsNotNone(base.valid_completion(root, task))
        self.assertTrue(convergence.completion_requires_convergence(completion))
        self.assertIsNone(gated.valid_completion(root, task))

    def test_matching_convergence_admits_completion_and_mutation_fails_closed(self):
        root = self.make_root()
        candidate, task = self.prepare_task(root)
        completion = self.write_completion(root, task)
        assessment_path = root / "assessment.json"
        assessment_path.write_text(json.dumps(self.assessment_for(task, candidate)), encoding="utf-8")
        receipt = convergence.build_receipt(
            root,
            candidate["candidate_id"],
            completion["merge_commit_sha"],
            completion["pr_number"],
            assessment_path,
        )
        convergence_path = root / "research/codex/convergence" / f"{candidate['candidate_id']}.json"
        convergence_path.parent.mkdir(parents=True, exist_ok=True)
        convergence_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.assertIsNotNone(gated.valid_completion(root, task))

        mutated = dict(receipt)
        mutated["merge_commit_sha"] = "e" * 40
        mutated["receipt_sha256"] = convergence.canonical_hash(
            {k: v for k, v in mutated.items() if k != "receipt_sha256"}
        )
        convergence_path.write_text(json.dumps(mutated), encoding="utf-8")
        self.assertIsNone(gated.valid_completion(root, task))

    def test_candidate_mutation_after_task_binding_fails_closed(self):
        root = self.make_root()
        candidate, task = self.prepare_task(root)
        candidate["objective"] = "mutated objective after task binding"
        candidate_path = root / task["candidate_path"]
        candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assessment_path = root / "assessment.json"
        assessment_path.write_text(json.dumps(self.assessment_for(task, candidate)), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "CANDIDATE_HASH_MISMATCH"):
            convergence.build_receipt(root, task["candidate_id"], "d" * 40, 404, assessment_path)

    def test_convergence_cannot_be_built_before_post_fix_observation(self):
        root = self.make_root()
        candidate, task = self.prepare_task(root, state="IN_REMEDIATION")
        assessment_path = root / "assessment.json"
        assessment_path.write_text(json.dumps(self.assessment_for(task, candidate)), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "TASK_NOT_IN_POST_FIX_OBSERVATION"):
            convergence.build_receipt(root, candidate["candidate_id"], "d" * 40, 404, assessment_path)

    def test_missing_verification_timestamp_requires_convergence(self):
        completion = {"contract": "CODEX_RESEARCH_COMPLETION_RECEIPT_v1"}
        self.assertTrue(convergence.completion_requires_convergence(completion))

    def test_legacy_completion_before_activation_is_grandfathered(self):
        root = self.make_root()
        _candidate, task = self.prepare_task(root)
        completion = self.write_completion(root, task, verified_at="2026-09-13T15:59:59Z")
        self.assertFalse(convergence.completion_requires_convergence(completion))
        self.assertIsNotNone(gated.valid_completion(root, task))

    def test_workflow_uses_convergence_aware_owner(self):
        workflow = (Path(__file__).parents[2] / ".github/workflows/remediation-maturation.yml").read_text(encoding="utf-8")
        self.assertEqual(workflow.count("merge_codex_research_intake_converged.py"), 2)
        self.assertNotIn("python scripts/remediation/merge_codex_research_intake.py", workflow)


if __name__ == "__main__":
    unittest.main()
