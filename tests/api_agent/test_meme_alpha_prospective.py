from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.api_agent.meme_alpha_prospective import (
    binary_prevalence_canary,
    freeze_shadow_observation,
    kill_or_redraft,
    method_review_eligibility,
    queue_slo_status,
    root_trial_id,
    validate_shadow_feature,
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


def shadow_feature(
    name: str,
    value: object,
    *,
    effective_at: str = "2026-09-15T12:04:00Z",
    observed_at: str = "2026-09-15T12:04:30Z",
    mutability: str = "SNAPSHOT_PINNED",
) -> dict:
    return {
        "feature_name": name,
        "feature_value_at_cutoff": value,
        "feature_effective_at_utc": effective_at,
        "source_observed_at_utc": observed_at,
        "source_or_schema_version": "fixture-v1",
        "source_record_or_event_identity": f"fixture:{name}",
        "mutability_class": mutability,
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

    def test_shadow_packet_is_order_stable_and_hash_stable(self) -> None:
        identity = {
            "chain": "solana",
            "token_id": "Mint111111111111111111111111111111111111111",
            "token_origin_utc": "2026-09-15T12:00:00Z",
        }
        a = shadow_feature("unique_independent_buyers_cumulative", 12)
        b = shadow_feature("net_real_capital_inflow", 4.2)
        first = freeze_shadow_observation(
            identity=identity,
            cutoff_minutes=5,
            cutoff_utc="2026-09-15T12:05:00Z",
            features=[b, a],
            wallet_roles=["SELF_INITIATED_TRADE", "UNKNOWN"],
        )
        second = freeze_shadow_observation(
            identity=identity,
            cutoff_minutes=5,
            cutoff_utc="2026-09-15T12:05:00Z",
            features=[a, b],
            wallet_roles=["UNKNOWN", "SELF_INITIATED_TRADE"],
        )
        self.assertEqual(first["observation_sha256"], second["observation_sha256"])
        self.assertEqual([item["feature_name"] for item in first["features"]], sorted([a["feature_name"], b["feature_name"]]))
        self.assertFalse(first["authority"]["automatic_trading"])

    def test_mutable_live_feature_is_rejected(self) -> None:
        feature = shadow_feature("creator_label", "BOT_FARM", mutability="MUTABLE_LIVE_FIELD")
        errors = validate_shadow_feature(feature, "2026-09-15T12:05:00Z")
        self.assertIn("MUTABLE_LIVE_FIELD_NOT_HISTORICAL_EVIDENCE", errors)

    def test_future_effective_wallet_quality_cannot_backfill(self) -> None:
        feature = shadow_feature(
            "wallet_as_of_hit_rate_shrunk",
            0.72,
            effective_at="2026-09-15T12:10:00Z",
            observed_at="2026-09-15T12:10:00Z",
            mutability="DERIVED_FROM_PINNED_EVENTS",
        )
        errors = validate_shadow_feature(feature, "2026-09-15T12:05:00Z")
        self.assertIn("FEATURE_EFFECTIVE_AFTER_CUTOFF", errors)

    def test_late_snapshot_cannot_masquerade_as_cutoff_state(self) -> None:
        feature = shadow_feature(
            "holder_count",
            99,
            effective_at="2026-09-15T12:04:00Z",
            observed_at="2026-09-15T12:06:00Z",
            mutability="SNAPSHOT_PINNED",
        )
        errors = validate_shadow_feature(feature, "2026-09-15T12:05:00Z")
        self.assertIn("SNAPSHOT_OBSERVED_AFTER_CUTOFF", errors)

    def test_immutable_event_may_be_reconstructed_later_when_event_time_is_pre_cutoff(self) -> None:
        feature = shadow_feature(
            "first_sell_latency_seconds",
            88,
            effective_at="2026-09-15T12:01:28Z",
            observed_at="2026-09-15T14:00:00Z",
            mutability="IMMUTABLE_EVENT",
        )
        self.assertEqual(validate_shadow_feature(feature, "2026-09-15T12:05:00Z"), [])

    def test_unknown_feature_is_preserved_without_becoming_negative(self) -> None:
        feature = shadow_feature(
            "creator_or_funder_linked_share",
            "UNKNOWN",
            mutability="UNKNOWN",
        )
        packet = freeze_shadow_observation(
            identity={
                "chain": "solana",
                "token_id": "Mint222222222222222222222222222222222222222",
                "token_origin_utc": "2026-09-15T12:00:00Z",
            },
            cutoff_minutes=5,
            cutoff_utc="2026-09-15T12:05:00Z",
            features=[feature],
        )
        self.assertEqual(packet["features"][0]["feature_value_at_cutoff"], "UNKNOWN")

    def test_stale_collector_is_degraded_data_not_market_silence(self) -> None:
        packet = freeze_shadow_observation(
            identity={
                "chain": "solana",
                "token_id": "Mint333333333333333333333333333333333333333",
                "token_origin_utc": "2026-09-15T12:00:00Z",
            },
            cutoff_minutes=5,
            cutoff_utc="2026-09-15T12:05:00Z",
            features=[shadow_feature("buyer_velocity", 3.0)],
            collector_status="STALE",
        )
        self.assertEqual(packet["data_state"], "DEGRADED_DATA")
        self.assertNotIn("NO_ALPHA", packet.values())

    def test_prevalence_canary_flags_large_retro_shadow_shift_without_market_interpretation(self) -> None:
        retrospective = [True] * 15 + [False] * 85
        shadow = [True] * 48 + [False] * 52
        result = binary_prevalence_canary(retrospective, shadow, max_allowed_abs_delta=0.10)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertAlmostEqual(result["positive_rate_delta"], 0.33, places=6)
        self.assertFalse(result["market_interpretation_allowed"])


if __name__ == "__main__":
    unittest.main()
