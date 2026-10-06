from __future__ import annotations

import unittest

from scripts.api_agent.meme_alpha_clean_g3 import (
    compute_asof_wallet_quality,
    compute_asof_wallet_quality_for_graph,
)
from scripts.api_agent.meme_alpha_pons_early_buyer import (
    build_pons_early_buyer_graph,
    build_pons_wallet_precursor_packet,
)


def case() -> dict:
    return {
        "contract": "MAL_PONS_CURVE_CAPTURE_CASE_V1",
        "case_id": "PCC-TEST",
        "chain": "robinhood-chain",
        "chain_id": 4663,
        "token_address": "0x" + "11" * 20,
        "curve_address": "0x" + "22" * 20,
        "launch_block": 100,
        "launch_block_timestamp_utc": "2026-10-06T20:00:00Z",
        "frozen_at_utc": "2026-10-06T20:06:00Z",
    }


def cohort() -> dict:
    a = "0x" + "aa" * 20
    b = "0x" + "bb" * 20
    return {
        "contract": "MAL_PONS_EARLY_BUYER_COHORT_FREEZE_V1",
        "case_id": "PCC-TEST",
        "cohort_window_end_utc": "2026-10-06T20:05:00Z",
        "frozen_at_utc": "2026-10-06T20:07:00Z",
        "target_n": 10,
        "cohort_size": 2,
        "cohort_wallets": [a, b],
        "first_buy_evidence": [
            {
                "wallet": a,
                "block_number": 101,
                "transaction_index": 1,
                "log_index": 2,
                "transaction_hash": "0xaaa",
                "event_timestamp_utc": "2026-10-06T20:00:20Z",
            },
            {
                "wallet": b,
                "block_number": 102,
                "transaction_index": 0,
                "log_index": 1,
                "transaction_hash": "0xbbb",
                "event_timestamp_utc": "2026-10-06T20:01:00Z",
            },
        ],
        "wallet_semantics": "PONS_CURVE_BUY_TOKEN_RECIPIENT",
        "prospective_credit_from_utc": "2026-10-06T20:06:00Z",
        "launch_time_action_credit": False,
        "authority": "RESEARCH_ONLY",
        "portfolio_action": False,
    }


def prior(outcome_id: str, wallet: str, maturity: str, five_x: bool, *, venue="pons-v2-bonding-curve") -> dict:
    return {
        "outcome_id": outcome_id,
        "wallet": wallet,
        "chain": "robinhood-chain",
        "venue": venue,
        "role": "EARLY_LAUNCH",
        "maturity_at_utc": maturity,
        "sellable_2x": five_x,
        "sellable_5x": five_x,
        "sellable_10x": False,
        "realizable_mfe_x": 6.0 if five_x else 1.3,
        "mae_fraction": 0.2 if five_x else 0.6,
        "liquidity_survived": True,
    }


def wallet_record(wallet: str, state: str, reviewed: str) -> dict:
    return {
        "contract": "WALLET_ALPHA_RECORD_V1",
        "record_status": "ACTIVE",
        "wallet": {"chain": "robinhood-chain", "address": wallet},
        "states": {
            "wallet_edge_state": state,
            "relationship_evidence_state": "UNKNOWN",
            "last_review_utc": reviewed,
        },
        "summary": {"history_completeness": "BOUNDED_LOCAL"},
    }


class PonsEarlyBuyerPrecursorTests(unittest.TestCase):
    def test_graph_preserves_recipient_semantics_and_no_retro_credit(self) -> None:
        graph = build_pons_early_buyer_graph(case(), cohort())
        self.assertEqual(graph["contract"], "MEME_ALPHA_PONS_EARLY_BUYER_GRAPH_v1")
        self.assertEqual(graph["cutoff_seconds"], 300)
        self.assertEqual(graph["signal_available_at_utc"], "2026-10-06T20:07:00Z")
        self.assertFalse(graph["launch_time_action_credit"])
        self.assertEqual(graph["buyers"][0]["wallet_role_class"], "PONS_TOKEN_RECIPIENT")
        self.assertFalse(graph["buyers"][0]["self_initiated_trade_proven"])
        self.assertFalse(graph["buyers"][0]["initiator_equivalence_proven"])

    def test_original_clean_g3_wrapper_rejects_pons_graph_but_generic_helper_accepts(self) -> None:
        graph = build_pons_early_buyer_graph(case(), cohort())
        with self.assertRaisesRegex(ValueError, "INVALID_BUYER_GRAPH"):
            compute_asof_wallet_quality(graph, [])
        rows = compute_asof_wallet_quality_for_graph(graph, [], min_prior_matured=1)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["chain"], "robinhood-chain")

    def test_future_outcome_and_other_venue_cannot_improve_pons_quality(self) -> None:
        graph = build_pons_early_buyer_graph(case(), cohort())
        a = graph["buyers"][0]["wallet"]
        outcomes = [
            prior("old1", a, "2026-10-05T20:00:00Z", True),
            prior("old2", a, "2026-10-05T21:00:00Z", False),
            prior("old3", a, "2026-10-05T22:00:00Z", True),
            prior("future", a, "2026-10-06T20:06:00Z", True),
            prior("other-venue", a, "2026-10-05T23:00:00Z", True, venue="uniswap-v4"),
        ]
        row = compute_asof_wallet_quality_for_graph(graph, outcomes, min_prior_matured=3)[0]
        self.assertTrue(row["qualified_history"])
        self.assertEqual(row["prior_matured_count"], 3)
        self.assertNotIn("future", row["source_outcome_ids"])
        self.assertNotIn("other-venue", row["source_outcome_ids"])

    def test_two_asof_edge_wallets_emit_multi_entity_convergence(self) -> None:
        graph = build_pons_early_buyer_graph(case(), cohort())
        a, b = [row["wallet"] for row in graph["buyers"]]
        outcomes = []
        for wallet in (a, b):
            outcomes += [
                prior(wallet + "-1", wallet, "2026-10-05T20:00:00Z", True),
                prior(wallet + "-2", wallet, "2026-10-05T21:00:00Z", False),
                prior(wallet + "-3", wallet, "2026-10-05T22:00:00Z", True),
            ]
        records = [
            wallet_record(a, "REPEATABLE_EDGE_CANDIDATE", "2026-10-06T19:00:00Z"),
            wallet_record(b, "REPEATABLE_EDGE_SUPPORTED", "2026-10-06T19:30:00Z"),
        ]
        packet = build_pons_wallet_precursor_packet(case(), cohort(), outcomes, records, [])
        self.assertEqual(packet["wallet_precursor_evidence"], "MULTI_ENTITY_CONVERGENCE")
        self.assertEqual(packet["effective_independent_edge_wallets"], 2)
        self.assertFalse(packet["authority"]["buy_now_promotion"])

    def test_strong_controller_collapses_two_edge_wallets_to_watch(self) -> None:
        graph = build_pons_early_buyer_graph(case(), cohort())
        a, b = [row["wallet"] for row in graph["buyers"]]
        outcomes = []
        for wallet in (a, b):
            outcomes += [
                prior(wallet + "-1", wallet, "2026-10-05T20:00:00Z", True),
                prior(wallet + "-2", wallet, "2026-10-05T21:00:00Z", False),
                prior(wallet + "-3", wallet, "2026-10-05T22:00:00Z", True),
            ]
        records = [
            wallet_record(a, "REPEATABLE_EDGE_CANDIDATE", "2026-10-06T19:00:00Z"),
            wallet_record(b, "REPEATABLE_EDGE_SUPPORTED", "2026-10-06T19:30:00Z"),
        ]
        links = [{
            "kind": "STRONG_CONTROLLER",
            "wallet_a": a,
            "wallet_b": b,
            "effective_at_utc": "2026-10-06T19:45:00Z",
        }]
        packet = build_pons_wallet_precursor_packet(case(), cohort(), outcomes, records, links)
        self.assertEqual(packet["wallet_precursor_evidence"], "WATCH")
        self.assertEqual(packet["effective_independent_edge_wallets"], 1)

    def test_future_wallet_registry_reputation_is_ignored(self) -> None:
        graph = build_pons_early_buyer_graph(case(), cohort())
        a = graph["buyers"][0]["wallet"]
        outcomes = [
            prior("1", a, "2026-10-05T20:00:00Z", True),
            prior("2", a, "2026-10-05T21:00:00Z", False),
            prior("3", a, "2026-10-05T22:00:00Z", True),
        ]
        records = [wallet_record(a, "REPEATABLE_EDGE_SUPPORTED", "2026-10-06T20:10:00Z")]
        packet = build_pons_wallet_precursor_packet(case(), cohort(), outcomes, records, [])
        self.assertEqual(packet["wallet_precursor_evidence"], "UNKNOWN")
        row = next(x for x in packet["wallet_registry_states_asof"] if x["wallet"] == a)
        self.assertEqual(row["wallet_edge_state"], "UNKNOWN")
        self.assertEqual(row["future_registry_records_ignored"], 1)


if __name__ == "__main__":
    unittest.main()
