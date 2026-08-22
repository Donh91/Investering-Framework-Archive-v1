import json
import tempfile
import unittest
from pathlib import Path

from scripts.agent_runtime.evaluate_persistent_runtime_readiness import evaluate


class RuntimeReadinessTest(unittest.TestCase):
    def build(self, ready=False):
        root = Path(tempfile.mkdtemp())
        candidate = root / "candidate.json"
        candidate.write_text(json.dumps({
            "contract": "PERSISTENT_AGENT_RUNTIME_CANDIDATE_v1",
            "candidate_id": "ARC-PERSISTENT-AGENT-RUNTIME-001",
            "maximum_automatic_stage": "READY_FOR_ISOLATED_CANARY",
            "required_internal_contracts": ["AGENT_OBJECTIVE_CONTRACT_v1"],
            "internal_need_thresholds": {
                "cross_run_context_loss_or_manual_handover_events": 1,
                "interrupted_long_task_events": 1,
                "message_delivery_or_continuation_failures": 1,
                "scheduled_state_loss_events": 1
            },
            "stability_requirements": {
                "automation_red_count": 0,
                "unresolved_p0_remediation_count": 0,
                "hash_mismatch_count": 0,
                "missing_required_handoff_pointer_count": 0,
                "minimum_successful_observation_runs": 2
            },
            "upstream_requirements": {
                "pinned_version": True,
                "minimum_observation_days": 30,
                "no_breaking_change_during_observation": True,
                "compaction_recovery_regression_tested": True,
                "silent_success_on_failure_prohibited": True,
                "refinement_preview_and_rollback": True,
                "session_persistence_tested": True,
                "external_sandbox_and_kill_switch": True
            }
        }))
        (root / "research/architecture_health").mkdir(parents=True)
        (root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json").write_text('{"status":"GREEN","red_count":0}')
        (root / "research/remediation").mkdir(parents=True)
        (root / "research/remediation/LATEST_REMEDIATION_QUEUE.json").write_text('{"items":[]}')
        (root / "LATEST_HANDOFF.json").write_text('{"pointers":{"capture":{"path":"x"}}}')
        upstream = root / "upstream.json"
        evidence = {
            "successful_observation_runs": 2,
            "observation_days": 30
        }
        for key in (
            "pinned_version", "no_breaking_change_during_observation",
            "compaction_recovery_regression_tested", "silent_success_on_failure_prohibited",
            "refinement_preview_and_rollback", "session_persistence_tested",
            "external_sandbox_and_kill_switch"
        ):
            evidence[key] = ready
        upstream.write_text(json.dumps(evidence))
        if ready:
            (root / "09_SOURCE_QA/incidents").mkdir(parents=True)
            (root / "09_SOURCE_QA/incidents/runtime.md").write_text(
                "CONTEXT_LOSS INTERRUPTED_LONG_TASK MESSAGE_DELIVERY_FAILED SCHEDULED_STATE_LOSS"
            )
            (root / "00_FMOS").mkdir(parents=True)
            (root / "00_FMOS/contracts.md").write_text("AGENT_OBJECTIVE_CONTRACT_v1")
        return root, candidate, upstream

    def test_incomplete_evidence_stays_incubating(self):
        root, candidate, upstream = self.build(False)
        result = evaluate(root, candidate, upstream)
        self.assertEqual(result["recommended_stage"], "INCUBATING")
        self.assertFalse(result["automatic_installation"])
        self.assertFalse(result["automatic_merge"])

    def test_full_fixture_caps_at_isolated_canary(self):
        root, candidate, upstream = self.build(True)
        result = evaluate(root, candidate, upstream)
        self.assertEqual(result["recommended_stage"], "READY_FOR_ISOLATED_CANARY")
        self.assertEqual(result["maximum_automatic_stage"], "READY_FOR_ISOLATED_CANARY")
        self.assertFalse(result["runtime_authority"])


if __name__ == "__main__":
    unittest.main()
