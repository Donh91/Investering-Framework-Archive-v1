from __future__ import annotations

import unittest

from backtest_engine.prospective import classify_receipt, finalize_receipt, summarize_accumulation, validate_receipt
from backtest_engine.shadow_scoreboard import score_shadow_period, validate_shadow_run
from backtest_engine.source_resilience import make_dual_source_row, summarize_live_dual_source

FAMILIES = ["REBUY_LOCK", "NEW_ENTRY_PERMISSION", "TRIM_NO_TRIM", "ROTATION_PERMISSION"]


def valid_receipt(**overrides):
    row = {
        "schema_version": "PROSPECTIVE_DECISION_RECEIPT_v1",
        "receipt_kind": "NO_ACTION",
        "event_id": "EV-1",
        "policy_family": "REBUY_LOCK",
        "rule_version": "V1",
        "knowledge_at_utc": "2026-07-28T17:00:00Z",
        "decision_at_utc": "2026-07-28T17:01:00Z",
        "execution_at_utc": "2026-07-28T17:01:00Z",
        "label_end_utc": "2026-08-04T17:01:00Z",
        "captured_at_utc": "2026-07-28T17:02:00Z",
        "state_before": "LOCKED",
        "state_after": "LOCKED",
        "action_permission": "NONE",
        "no_action_reason": "gate unmet",
        "source_artifact_ids": ["artifact-1"],
        "source_hashes": ["a" * 64],
        "transaction_cost_contract": "ZERO_NO_TRADE",
        "overlap_cluster_key": "REBUY-2026-W31",
        "owner_registry_version": "SELECTED_OWNER_REGISTRY_v1",
        "source_authority_status": "OWNER",
        "rule_frozen_before_outcome": True,
        "holdout_touched": False,
    }
    row.update(overrides)
    return finalize_receipt(row)


class ProspectiveReceiptTests(unittest.TestCase):
    def test_valid_receipt_is_a_class(self):
        row = valid_receipt()
        self.assertEqual(validate_receipt(row, policy_families=FAMILIES), [])
        self.assertEqual(classify_receipt(row, policy_families=FAMILIES), "A_FULLY_REPLAYABLE")

    def test_capture_delay_blocks_a_class(self):
        row = valid_receipt(captured_at_utc="2026-07-28T18:00:00Z")
        self.assertTrue(validate_receipt(row, policy_families=FAMILIES))

    def test_bad_hash_blocks_a_class(self):
        row = valid_receipt(source_hashes=["not-a-hash"])
        self.assertTrue(validate_receipt(row, policy_families=FAMILIES))

    def test_accumulation_requires_five_clusters(self):
        rows = []
        for i in range(5):
            rows.append(valid_receipt(event_id=f"EV-{i}", overlap_cluster_key=f"C-{i}"))
        summary = summarize_accumulation(rows, policy_families=FAMILIES)
        self.assertTrue(summary["per_policy_family"]["REBUY_LOCK"]["economic_ranking_ready"])


class SourceResilienceTests(unittest.TestCase):
    def test_challenger_confirmation_before_30_sessions(self):
        rows = [
            make_dual_source_row(
                session_date=f"2026-07-{day:02d}",
                owner_close=0.029 + day / 1_000_000,
                challenger_close=(0.029 + day / 1_000_000) * 1.0001,
                owner_settled=True,
                challenger_settled=True,
            )
            for day in range(1, 11)
        ]
        contract = {
            "minimum_live_overlap_sessions": 30,
            "thresholds": [0.0275, 0.03],
            "median_abs_close_dev_bps_max": 5,
            "p95_abs_close_dev_bps_max": 20,
            "max_abs_close_dev_bps_max": 75,
            "gate_agreement_rate_min": 0.99,
        }
        summary = summarize_live_dual_source(rows, contract)
        self.assertFalse(summary["owner_substitution_eligible"])
        self.assertEqual(summary["authority"], "CHALLENGER_CONFIRMATION_ONLY")

    def test_dual_source_eligible_after_30_clean_sessions(self):
        rows = [
            make_dual_source_row(
                session_date=f"S-{day}",
                owner_close=0.0295,
                challenger_close=0.0295005,
                owner_settled=True,
                challenger_settled=True,
            )
            for day in range(30)
        ]
        contract = {
            "minimum_live_overlap_sessions": 30,
            "thresholds": [0.0275, 0.03],
            "median_abs_close_dev_bps_max": 5,
            "p95_abs_close_dev_bps_max": 20,
            "max_abs_close_dev_bps_max": 75,
            "gate_agreement_rate_min": 0.99,
        }
        self.assertTrue(summarize_live_dual_source(rows, contract)["owner_substitution_eligible"])


class ShadowScoreboardTests(unittest.TestCase):
    def _run(self, run_id="R1"):
        common = {
            "run_id": run_id,
            "snapshot_utc": "2026-07-28T17:00:00Z",
            "available_sensors": 10,
            "available_clusters": 6,
            "source_failures": [],
            "state_output": "NO_ROTATION",
            "transition_output": "NONE",
            "veto_output": "REBUY_LOCKED",
            "runtime_seconds": 10,
            "explanation_tokens": 100,
            "warnings_emitted": ["BREADTH_WEAK"],
        }
        full = {**common, "profile_id": "FULL_STACK", "payload_bytes": 1000}
        reduced = {**common, "profile_id": "REDUCED_EXECUTION_STACK", "payload_bytes": 700, "runtime_seconds": 7, "explanation_tokens": 70}
        minimal = {**common, "profile_id": "MINIMAL_CORE_STACK", "payload_bytes": 500, "runtime_seconds": 5, "explanation_tokens": 50}
        return [full, reduced, minimal]

    def test_valid_shadow_run(self):
        self.assertEqual(validate_shadow_run(self._run()), [])

    def test_score_shadow_period(self):
        result = score_shadow_period([self._run("R1"), self._run("R2")])
        reduced = result["profiles"]["REDUCED_EXECUTION_STACK"]
        self.assertEqual(reduced["state_agreement_rate"], 1.0)
        self.assertAlmostEqual(reduced["mean_payload_reduction_pct"], 30.0)


if __name__ == "__main__":
    unittest.main()
