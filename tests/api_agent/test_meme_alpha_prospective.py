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
from scripts.api_agent.meme_alpha_pump_g2 import (
    PUMP_PUBLIC_DOCS_IDL_COMMIT,
    aggregate_pump_g2_window,
    normalize_pump_complete_event,
    normalize_pump_create_event,
    normalize_pump_trade_event,
    pump_g2_shadow_features,
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


def pump_create_raw(*, timestamp: int = 1000, quote_mint: str = "So11111111111111111111111111111111111111112") -> dict:
    return {
        "name": "TEST",
        "symbol": "TEST",
        "uri": "https://example.invalid/test.json",
        "mint": "MintPump1111111111111111111111111111111111111",
        "bondingCurve": "Curve11111111111111111111111111111111111111",
        "user": "CreatorUser111111111111111111111111111111111",
        "creator": "Creator11111111111111111111111111111111111",
        "timestamp": timestamp,
        "virtualTokenReserves": 1_073_000_000_000_000,
        "virtualSolReserves": 30_000_000_000,
        "realTokenReserves": 793_100_000_000_000,
        "tokenTotalSupply": 1_000_000_000_000_000,
        "tokenProgram": "TokenProgram11111111111111111111111111111111",
        "isMayhemMode": False,
        "isCashbackEnabled": False,
        "quoteMint": quote_mint,
    }


def pump_trade_raw(
    *,
    timestamp: int,
    user: str,
    quote_amount: int,
    token_amount: int,
    is_buy: bool,
    real_quote_reserves: int,
    quote_mint: str = "So11111111111111111111111111111111111111112",
) -> dict:
    return {
        "mint": "MintPump1111111111111111111111111111111111111",
        "solAmount": quote_amount,
        "tokenAmount": token_amount,
        "isBuy": is_buy,
        "user": user,
        "timestamp": timestamp,
        "virtualSolReserves": 30_000_000_000 + real_quote_reserves,
        "virtualTokenReserves": 1_000_000_000_000_000 - token_amount,
        "realSolReserves": real_quote_reserves,
        "realTokenReserves": 700_000_000_000_000,
        "feeRecipient": "Fee111111111111111111111111111111111111111",
        "feeBasisPoints": 125,
        "fee": max(1, quote_amount // 100),
        "creator": "Creator11111111111111111111111111111111111",
        "creatorFeeBasisPoints": 30,
        "creatorFee": max(1, quote_amount // 400),
        "trackVolume": True,
        "totalUnclaimedTokens": 0,
        "totalClaimedTokens": 0,
        "currentSolVolume": quote_amount,
        "lastUpdateTimestamp": timestamp,
        "ixName": "buy" if is_buy else "sell",
        "mayhemMode": False,
        "cashbackFeeBasisPoints": 0,
        "cashback": 0,
        "buybackFeeBasisPoints": 0,
        "buybackFee": 0,
        "shareholders": [],
        "quoteMint": quote_mint,
        "quoteAmount": quote_amount,
        "virtualQuoteReserves": 30_000_000_000 + real_quote_reserves,
        "realQuoteReserves": real_quote_reserves,
        "holderRewardsBps": 0,
        "holderRewards": 0,
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

    def test_pump_official_trade_events_aggregate_g2_without_entity_overclaim(self) -> None:
        create = normalize_pump_create_event(
            pump_create_raw(),
            signature="create-sig",
            slot=1,
            event_index=0,
            observed_at_utc="2026-09-15T12:00:00Z",
        )
        raws = [
            pump_trade_raw(timestamp=1010, user="A", quote_amount=100, token_amount=10, is_buy=True, real_quote_reserves=100),
            pump_trade_raw(timestamp=1020, user="B", quote_amount=200, token_amount=10, is_buy=True, real_quote_reserves=300),
            pump_trade_raw(timestamp=1030, user="A", quote_amount=150, token_amount=10, is_buy=True, real_quote_reserves=450),
            pump_trade_raw(timestamp=1040, user="B", quote_amount=50, token_amount=5, is_buy=False, real_quote_reserves=400),
        ]
        trades = [
            normalize_pump_trade_event(
                raw,
                signature=f"trade-{idx}",
                slot=10 + idx,
                event_index=0,
                observed_at_utc="2026-09-15T12:00:30Z",
            )
            for idx, raw in enumerate(raws)
        ]
        summary = aggregate_pump_g2_window(create, trades + [trades[1]], cutoff_seconds=60)
        self.assertEqual(summary["trade_count"], 4)
        self.assertEqual(summary["address_level_unique_buyers"], 2)
        self.assertEqual(summary["entity_adjusted_unique_buyers"], "UNKNOWN")
        self.assertEqual(summary["gross_buy_quote_raw"], 450)
        self.assertEqual(summary["gross_sell_quote_raw"], 50)
        self.assertEqual(summary["net_trade_quote_flow_raw"], 400)
        self.assertEqual(summary["first_sell_latency_seconds"], 40)
        self.assertEqual(summary["repeat_buyer_fraction"], 0.5)
        self.assertEqual(summary["idl_commit"], PUMP_PUBLIC_DOCS_IDL_COMMIT)
        self.assertFalse(summary["authority"]["automatic_trading"])

    def test_pump_adapter_preserves_custom_quote_mint_and_raw_units(self) -> None:
        usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        create = normalize_pump_create_event(
            pump_create_raw(quote_mint=usdc),
            signature="create-usdc",
            slot=2,
            event_index=0,
            observed_at_utc="2026-09-15T12:00:00Z",
        )
        trade = normalize_pump_trade_event(
            pump_trade_raw(timestamp=1010, user="A", quote_amount=1_500_000, token_amount=1000, is_buy=True, real_quote_reserves=1_500_000, quote_mint=usdc),
            signature="trade-usdc",
            slot=3,
            event_index=0,
            observed_at_utc="2026-09-15T12:00:10Z",
        )
        summary = aggregate_pump_g2_window(create, [trade], cutoff_seconds=60)
        self.assertEqual(summary["quote_mint"], usdc)
        self.assertEqual(summary["gross_buy_quote_raw"], 1_500_000)
        self.assertIn("raw quote-asset units", summary["semantic_warnings"][0])

    def test_pump_quote_mismatch_is_hard_error(self) -> None:
        create = normalize_pump_create_event(
            pump_create_raw(),
            signature="create-sig-2",
            slot=4,
            event_index=0,
            observed_at_utc="2026-09-15T12:00:00Z",
        )
        trade = normalize_pump_trade_event(
            pump_trade_raw(timestamp=1010, user="A", quote_amount=100, token_amount=10, is_buy=True, real_quote_reserves=100, quote_mint="DifferentQuoteMint"),
            signature="trade-bad-quote",
            slot=5,
            event_index=0,
            observed_at_utc="2026-09-15T12:00:10Z",
        )
        with self.assertRaisesRegex(ValueError, "PUMP_G2_QUOTE_MINT_MISMATCH"):
            aggregate_pump_g2_window(create, [trade], cutoff_seconds=60)

    def test_degraded_capture_is_not_training_eligible(self) -> None:
        create = normalize_pump_create_event(
            pump_create_raw(),
            signature="create-degraded",
            slot=6,
            event_index=0,
            observed_at_utc="2026-09-15T12:00:00Z",
        )
        summary = aggregate_pump_g2_window(create, [], cutoff_seconds=300, capture_state="DEGRADED")
        self.assertFalse(summary["eligible_for_training"])
        self.assertEqual(summary["trade_count"], 0)
        self.assertEqual(summary["entity_adjusted_unique_buyers"], "UNKNOWN")

    def test_pump_g2_features_bind_into_point_in_time_shadow_packet(self) -> None:
        create = normalize_pump_create_event(
            pump_create_raw(),
            signature="create-bind",
            slot=7,
            event_index=0,
            observed_at_utc="2026-09-15T12:00:00Z",
        )
        trade = normalize_pump_trade_event(
            pump_trade_raw(timestamp=1010, user="A", quote_amount=100, token_amount=10, is_buy=True, real_quote_reserves=100),
            signature="trade-bind",
            slot=8,
            event_index=0,
            observed_at_utc="2026-09-15T12:00:10Z",
        )
        summary = aggregate_pump_g2_window(create, [trade], cutoff_seconds=300)
        packet = freeze_shadow_observation(
            identity={"chain": "solana", "token_id": summary["mint"], "token_origin_utc": summary["token_origin_utc"]},
            cutoff_minutes=5,
            cutoff_utc=summary["cutoff_utc"],
            features=pump_g2_shadow_features(summary),
        )
        self.assertEqual(packet["identity"]["token_id"], summary["mint"])
        self.assertTrue(all(feature["mutability_class"] == "DERIVED_FROM_PINNED_EVENTS" for feature in packet["features"]))

    def test_pump_completion_is_lifecycle_only_not_profitability(self) -> None:
        complete = normalize_pump_complete_event(
            {
                "user": "User",
                "mint": "MintPump1111111111111111111111111111111111111",
                "bondingCurve": "Curve11111111111111111111111111111111111111",
                "timestamp": 1500,
                "quoteMint": "So11111111111111111111111111111111111111112",
            },
            signature="complete-sig",
            slot=9,
            event_index=0,
            observed_at_utc="2026-09-15T12:10:00Z",
        )
        self.assertEqual(complete["lifecycle_event"], "BONDING_CURVE_COMPLETE")
        self.assertEqual(complete["profitability_claim"], "NONE")


if __name__ == "__main__":
    unittest.main()
