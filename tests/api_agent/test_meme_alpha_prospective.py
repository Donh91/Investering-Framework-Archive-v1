from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.api_agent.meme_alpha_prospective import (
    kill_or_redraft,
    method_review_eligibility,
    queue_slo_status,
    root_trial_id,
    validate_trial_record,
)

POLICY = json.loads(Path("research/api_agent/meme_alpha/MEME_ALPHA_PROSPECTIVE_HARDENING_v1.json").read_text())


def lineage() -> dict:
    return {
        "method_version": "1.1-scientific-hardening",
        "method_sha256": "a" * 64,
        "runtime_contract": "MEME_ALPHA_RUNTIME_v1_2_SOURCE_AUTH",
        "runtime_input_sha256": "b" * 64,
        "runtime_output_sha256": "c" * 64,
        "policy_sha256": "d" * 64,
        "prompt_sha256": "e" * 64,
        "model_id": "gpt-5.6-luna",
        "model_snapshot_or_version": "2026-09-14",
        "query_manifest_sha256": "f" * 64,
        "retrieval_manifest_sha256": "1" * 64,
    }


class MemeAlphaProspectiveTests(unittest.TestCase):
    def test_hierarchical_ids_collapse_to_ecosystem_denominator(self) -> None:
        root = "EE-002-EXAMPLE-20260914"
        self.assertEqual(root_trial_id(root), root)
        self.assertEqual(root_trial_id(root + "::A-001"), root)
        self.assertEqual(root_trial_id(root + "::A-001::T-001"), root)

    def test_discovery_complete_is_not_matured(self) -> None:
        record = {"trial_id": "EE-002-EXAMPLE-20260914", "trial_state": "DISCOVERY_COMPLETE", **lineage()}
        self.assertEqual(validate_trial_record(record, POLICY), [])
        review = method_review_eligibility([record], POLICY)
        self.assertEqual(review["matured_unique_ecosystem_trials"], 0)
        self.assertFalse(review["eligible_for_method_review"])

    def test_positive_matured_trial_requires_executable_outcome_and_missed_winner_audit(self) -> None:
        record = {
            "trial_id": "EE-002-EXAMPLE-20260914",
            "trial_state": "OUTCOME_MATURED",
            "outcome_class": "PROSPECTIVE_SIGNAL_SURVIVED",
            "falsifier_result": "SURVIVED",
            **lineage(),
        }
        errors = validate_trial_record(record, POLICY)
        self.assertIn("MATURED_REQUIRES_MISSED_WINNER_AUDIT", errors)
        self.assertTrue(any(item.startswith("POSITIVE_OUTCOME_REQUIRES_") for item in errors))

    def test_trial_001_is_grandfathered_for_lineage_only(self) -> None:
        record = {
            "trial_id": "EE-001-ARC-20260914",
            "trial_state": "DISCOVERY_COMPLETE",
            "falsifier_result": "NOT_YET_MATURED",
        }
        self.assertEqual(validate_trial_record(record, POLICY), [])

    def test_twenty_unique_matured_roots_are_required(self) -> None:
        records = []
        for idx in range(2, 22):
            record = {
                "trial_id": f"EE-{idx:03d}-ECO{idx}-20260914",
                "trial_state": "OUTCOME_MATURED",
                "outcome_class": "NO_LIVE_TOKEN_MATCH",
                "falsifier_result": "FAILED_OR_NULL",
                "missed_winner_audit": {"status": "COMPLETE", "missed": False},
                **lineage(),
            }
            records.append(record)
        review = method_review_eligibility(records, POLICY)
        self.assertEqual(review["matured_unique_ecosystem_trials"], 20)
        self.assertTrue(review["eligible_for_method_review"])

    def test_p0_latency_breach_is_explicit(self) -> None:
        result = queue_slo_status("P0", "2026-09-14T10:00:00Z", "2026-09-14T11:01:00Z", POLICY)
        self.assertEqual(result["status"], "BREACH")

    def test_kill_criteria_fire_after_20_matured_trials(self) -> None:
        result = kill_or_redraft({
            "matured_unique_ecosystem_trials": 20,
            "sellable_signal_survived_count": 0,
            "actionable_precision": 0.10,
            "matched_control_precision": 0.12,
            "cohort_selection_integrity": True,
            "non_grandfathered_lineage_failures": 0,
            "missed_winner_recall_unacceptably_low": False,
        }, POLICY)
        self.assertEqual(result["decision"], "KILL_OR_REDRAFT")
        self.assertIn("ZERO_SELLABLE_PROSPECTIVE_SIGNAL_SURVIVED", result["reasons"])
        self.assertIn("ACTIONABLE_PRECISION_NOT_ABOVE_MATCHED_CONTROL", result["reasons"])


if __name__ == "__main__":
    unittest.main()
