from __future__ import annotations

import unittest

from scripts.api_agent.meme_alpha_clean_g3 import (
    adjust_wallet_entities,
    build_current_token_buyer_graph,
    clean_g3_feature_summary,
    compute_asof_wallet_quality,
    freeze_clean_g3_shadow_packet,
)


def create_event() -> dict:
    return {
        "contract": "MEME_ALPHA_PUMP_CREATE_EVENT_v1",
        "event_timestamp": 1000,
        "event_timestamp_utc": "1970-01-01T00:16:40Z",
        "mint": "MintCleanG3",
        "quote_mint": "SOL",
    }


def trade(identity: str, *, ts: int, wallet: str, quote: int = 100, buy: bool = True) -> dict:
    return {
        "contract": "MEME_ALPHA_PUMP_TRADE_EVENT_v1",
        "source_record_or_event_identity": identity,
        "event_timestamp": ts,
        "event_timestamp_utc": f"1970-01-01T00:{ts // 60:02d}:{ts % 60:02d}Z",
        "slot": ts,
        "mint": "MintCleanG3",
        "quote_mint": "SOL",
        "user": wallet,
        "is_buy": buy,
        "quote_amount_raw": quote,
        "token_amount_raw": quote * 10,
    }


def prior(
    outcome_id: str,
    wallet: str,
    *,
    maturity: str,
    five_x: bool,
    ten_x: bool = False,
    chain: str = "solana",
    venue: str = "pump.fun",
    role: str = "EARLY_LAUNCH",
) -> dict:
    return {
        "outcome_id": outcome_id,
        "wallet": wallet,
        "chain": chain,
        "venue": venue,
        "role": role,
        "maturity_at_utc": maturity,
        "sellable_2x": five_x or ten_x,
        "sellable_5x": five_x,
        "sellable_10x": ten_x,
        "realizable_mfe_x": 6.0 if five_x else 1.4,
        "mae_fraction": 0.2 if five_x else 0.6,
        "liquidity_survived": True,
    }


class MemeAlphaCleanG3Tests(unittest.TestCase):
    def test_buyer_graph_uses_native_buys_and_excludes_known_router_pool_program(self) -> None:
        events = [
            trade("e1", ts=1010, wallet="A", quote=100),
            trade("e2", ts=1020, wallet="ROUTER", quote=200),
            trade("e3", ts=1030, wallet="A", quote=50),
            trade("e4", ts=1040, wallet="B", quote=80, buy=False),
            trade("e5", ts=1070, wallet="LATE", quote=500),
            trade("e1", ts=1010, wallet="A", quote=100),
        ]
        graph = build_current_token_buyer_graph(
            create_event(), events, cutoff_seconds=60, excluded_addresses={"ROUTER"}
        )
        self.assertEqual(graph["native_buy_events_seen"], 3)
        self.assertEqual(graph["raw_unique_buy_addresses"], 2)
        self.assertEqual(graph["router_pool_program_excluded_addresses"], 1)
        self.assertEqual(graph["self_initiated_buyer_addresses"], 1)
        self.assertEqual(graph["buyers"][0]["wallet"], "A")
        self.assertEqual(graph["buyers"][0]["buy_count"], 2)
        self.assertEqual(graph["entity_count"], "UNKNOWN")
        self.assertFalse(graph["authority"]["buy_now_promotion"])

    def test_future_outcome_cannot_improve_asof_wallet_quality(self) -> None:
        graph = build_current_token_buyer_graph(
            create_event(), [trade("e1", ts=1010, wallet="A")], cutoff_seconds=60
        )
        outcomes = [
            prior("old1", "A", maturity="1970-01-01T00:10:00Z", five_x=True),
            prior("old2", "A", maturity="1970-01-01T00:11:00Z", five_x=False),
            prior("old3", "A", maturity="1970-01-01T00:12:00Z", five_x=True),
            prior("future", "A", maturity="1970-01-01T00:30:00Z", five_x=True, ten_x=True),
        ]
        rows = compute_asof_wallet_quality(graph, outcomes, min_prior_matured=3)
        self.assertEqual(rows[0]["prior_matured_count"], 3)
        self.assertEqual(rows[0]["sellable_5x_hits"], 2)
        self.assertEqual(rows[0]["sellable_10x_hits"], 0)
        self.assertTrue(rows[0]["qualified_history"])
        self.assertNotIn("future", rows[0]["source_outcome_ids"])

    def test_wallet_skill_is_chain_venue_and_role_local(self) -> None:
        graph = build_current_token_buyer_graph(
            create_event(), [trade("e1", ts=1010, wallet="A")], cutoff_seconds=60
        )
        outcomes = [
            prior("sol-pump", "A", maturity="1970-01-01T00:10:00Z", five_x=True),
            prior("bnb", "A", maturity="1970-01-01T00:10:00Z", five_x=True, chain="bnb"),
            prior("other-venue", "A", maturity="1970-01-01T00:10:00Z", five_x=True, venue="bags"),
            prior("phoenix", "A", maturity="1970-01-01T00:10:00Z", five_x=True, role="PHOENIX_REENTRY"),
        ]
        rows = compute_asof_wallet_quality(graph, outcomes, min_prior_matured=1)
        self.assertEqual(rows[0]["prior_matured_count"], 1)
        self.assertEqual(rows[0]["source_outcome_ids"], ["sol-pump"])

    def test_same_funder_is_relationship_evidence_not_identity_collapse(self) -> None:
        graph = build_current_token_buyer_graph(
            create_event(),
            [trade("e1", ts=1010, wallet="A"), trade("e2", ts=1011, wallet="B")],
            cutoff_seconds=60,
        )
        outcomes = []
        for wallet in ("A", "B"):
            outcomes.extend([
                prior(f"{wallet}-1", wallet, maturity="1970-01-01T00:10:00Z", five_x=True),
                prior(f"{wallet}-2", wallet, maturity="1970-01-01T00:11:00Z", five_x=False),
                prior(f"{wallet}-3", wallet, maturity="1970-01-01T00:12:00Z", five_x=True),
            ])
        rows = compute_asof_wallet_quality(graph, outcomes, min_prior_matured=3)
        adj = adjust_wallet_entities(rows, [
            {"kind": "SAME_FUNDER", "wallet": "A", "funder": "F", "effective_at_utc": "1970-01-01T00:15:00Z"},
            {"kind": "SAME_FUNDER", "wallet": "B", "funder": "F", "effective_at_utc": "1970-01-01T00:15:00Z"},
        ], cutoff_utc=graph["cutoff_utc"])
        self.assertEqual(adj["qualified_wallet_count"], 2)
        self.assertEqual(adj["same_funder_fraction_of_qualified"], 1.0)
        self.assertEqual(adj["effective_entity_count_strong_controller_only"], 2)
        self.assertFalse(adj["same_funder_collapses_identity"])

    def test_only_strong_controller_evidence_collapses_effective_entity(self) -> None:
        graph = build_current_token_buyer_graph(
            create_event(),
            [trade("e1", ts=1010, wallet="A"), trade("e2", ts=1011, wallet="B")],
            cutoff_seconds=60,
        )
        rows = compute_asof_wallet_quality(graph, [], min_prior_matured=1)
        adj = adjust_wallet_entities(rows, [
            {"kind": "STRONG_CONTROLLER", "wallet_a": "A", "wallet_b": "B", "effective_at_utc": "1970-01-01T00:15:00Z"},
        ], cutoff_utc=graph["cutoff_utc"])
        self.assertEqual(adj["raw_wallet_count"], 2)
        self.assertEqual(adj["effective_entity_count_strong_controller_only"], 1)
        self.assertEqual(adj["largest_strong_controller_entity_size"], 2)

    def test_future_relationship_evidence_is_ignored(self) -> None:
        graph = build_current_token_buyer_graph(
            create_event(),
            [trade("e1", ts=1010, wallet="A"), trade("e2", ts=1011, wallet="B")],
            cutoff_seconds=60,
        )
        rows = compute_asof_wallet_quality(graph, [], min_prior_matured=1)
        adj = adjust_wallet_entities(rows, [
            {"kind": "STRONG_CONTROLLER", "wallet_a": "A", "wallet_b": "B", "effective_at_utc": "1970-01-01T00:30:00Z"},
        ], cutoff_utc=graph["cutoff_utc"])
        self.assertEqual(adj["effective_entity_count_strong_controller_only"], 2)
        self.assertEqual(adj["strong_controller_edge_count"], 0)

    def test_shadow_packet_preserves_insufficient_history_as_unknown(self) -> None:
        graph = build_current_token_buyer_graph(
            create_event(), [trade("e1", ts=1010, wallet="A")], cutoff_seconds=60
        )
        rows = compute_asof_wallet_quality(graph, [], min_prior_matured=3)
        adj = adjust_wallet_entities(rows, [], cutoff_utc=graph["cutoff_utc"])
        summary = clean_g3_feature_summary(rows, adj)
        self.assertEqual(summary["clean_g3_status"], "INSUFFICIENT_PRIOR_HISTORY")
        packet = freeze_clean_g3_shadow_packet(
            buyer_graph=graph,
            g2_features=[],
            wallet_quality_rows=rows,
            entity_adjustment=adj,
        )
        self.assertEqual(packet["clean_g3_status"], "INSUFFICIENT_PRIOR_HISTORY")
        self.assertFalse(packet["authority"]["buy_now_promotion"])
        feature_map = {item["feature_name"]: item for item in packet["features"]}
        self.assertEqual(feature_map["mean_asof_shrunk_sellable_5x_rate"]["feature_value_at_cutoff"], "UNKNOWN")
        self.assertEqual(feature_map["mean_asof_shrunk_sellable_5x_rate"]["mutability_class"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
