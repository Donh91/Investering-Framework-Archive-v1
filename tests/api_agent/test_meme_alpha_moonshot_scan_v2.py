from __future__ import annotations

import unittest

from scripts.api_agent import meme_alpha_moonshot_scan_v2 as s


def token_item(token_id: str, symbol: str, name: str) -> dict:
    return {"id": token_id, "attributes": {"symbol": symbol, "name": name}}


def pool_resource(base: str, quote: str) -> dict:
    return {
        "id": "eth_0xpool",
        "attributes": {
            "address": "0xpool",
            "pool_created_at": "2026-09-14T15:00:00Z",
            "reserve_in_usd": "20000",
            "market_cap_usd": "100000",
            "fdv_usd": "120000",
            "base_token_price_usd": "2.0",
            "quote_token_price_usd": "0.5",
            "transactions": {
                "h1": {"buys": 12, "sells": 4},
                "m5": {"buys": 3, "sells": 1},
            },
            "volume_usd": {"h1": "4000", "m5": "500"},
            "price_change_percentage": {"h1": "25", "h6": "100"},
        },
        "relationships": {
            "base_token": {"data": {"id": base}},
            "quote_token": {"data": {"id": quote}},
            "dex": {"data": {"id": "uniswap_v3"}},
        },
    }


class TargetTokenStage0Tests(unittest.TestCase):
    def test_base_target_captures_base_price_and_transaction_semantics(self) -> None:
        target = "0x" + "1" * 40
        stable = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        base_id, quote_id = "eth_" + target, "eth_" + stable
        included = {
            base_id: token_item(base_id, "X", "X token"),
            quote_id: token_item(quote_id, "USDC", "USD Coin"),
        }
        event = s.normalize_pool(pool_resource(base_id, quote_id), included, network="eth", now_unix=1789402200)
        self.assertEqual(event["network"], "eth")
        self.assertEqual(event["token_ca"], target)
        self.assertEqual(event["token_role"], "base")
        self.assertEqual(event["token_price_usd"], 2.0)
        self.assertEqual(event["buys_h1"], 12)
        self.assertEqual(event["sells_h1"], 4)
        self.assertEqual(event["market_cap_usd"], 100000.0)
        self.assertEqual(event["fdv_usd"], 120000.0)
        self.assertEqual(event["valuation_status"], "MARKET_CAP_AND_FDV")
        self.assertEqual(event["price_change_h1_pct"], 25.0)
        self.assertTrue(event["target_price_change_resolved"])
        self.assertEqual(event["data_integrity_status"], "PASS")
        self.assertEqual(event["data_integrity_unknown_fields"], [])
        self.assertTrue(event["market_cap_fdv_substitution_forbidden"])
        self.assertTrue(event["observed_at_utc"].endswith("Z"))

    def test_quote_target_swaps_transactions_but_does_not_fabricate_price_change_or_valuation(self) -> None:
        wrapped = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        target = "0x" + "2" * 40
        base_id, quote_id = "eth_" + wrapped, "eth_" + target
        included = {
            base_id: token_item(base_id, "WETH", "Wrapped Ether"),
            quote_id: token_item(quote_id, "Y", "Y token"),
        }
        event = s.normalize_pool(pool_resource(base_id, quote_id), included, network="eth", now_unix=1789402200)
        self.assertEqual(event["token_ca"], target)
        self.assertEqual(event["token_role"], "quote")
        self.assertEqual(event["token_price_usd"], 0.5)
        self.assertEqual(event["buys_h1"], 4)
        self.assertEqual(event["sells_h1"], 12)
        self.assertEqual(event["buys_m5"], 1)
        self.assertEqual(event["sells_m5"], 3)
        self.assertIsNone(event["market_cap_usd"])
        self.assertIsNone(event["fdv_usd"])
        self.assertEqual(event["valuation_status"], "UNKNOWN")
        self.assertIsNone(event["price_change_h1_pct"])
        self.assertIsNone(event["price_change_h6_pct"])
        self.assertFalse(event["target_price_change_resolved"])

    def test_fdv_is_never_silently_substituted_for_missing_market_cap(self) -> None:
        target = "0x" + "3" * 40
        stable = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        base_id, quote_id = "eth_" + target, "eth_" + stable
        included = {
            base_id: token_item(base_id, "Z", "Z token"),
            quote_id: token_item(quote_id, "USDC", "USD Coin"),
        }
        resource = pool_resource(base_id, quote_id)
        resource["attributes"]["market_cap_usd"] = None
        resource["attributes"]["fdv_usd"] = "120000"
        event = s.normalize_pool(resource, included, network="eth", now_unix=1789402200)
        self.assertIsNone(event["market_cap_usd"])
        self.assertEqual(event["fdv_usd"], 120000.0)
        self.assertEqual(event["valuation_status"], "FDV_ONLY")
        self.assertIsNone(event["liquidity_to_market_cap_pct"])

    def test_missing_live_price_and_liquidity_are_unknown_not_zero(self) -> None:
        target = "0x" + "4" * 40
        stable = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        base_id, quote_id = "eth_" + target, "eth_" + stable
        included = {
            base_id: token_item(base_id, "Q", "Q token"),
            quote_id: token_item(quote_id, "USDC", "USD Coin"),
        }
        resource = pool_resource(base_id, quote_id)
        resource["attributes"]["base_token_price_usd"] = None
        resource["attributes"]["reserve_in_usd"] = None
        event = s.normalize_pool(resource, included, network="eth", now_unix=1789402200)
        self.assertIsNone(event["token_price_usd"])
        self.assertIsNone(event["liquidity_usd"])
        self.assertEqual(event["data_integrity_status"], "DEGRADED_DATA")
        self.assertEqual(event["data_integrity_unknown_fields"], ["token_price_usd", "liquidity_usd"])
        self.assertIsNone(event["volume_to_liquidity_h1"])

    def test_same_ticker_does_not_change_exact_ca_target_selection(self) -> None:
        a = "0x" + "a" * 40
        b = "0x" + "b" * 40
        base_id, quote_id = "eth_" + a, "eth_" + b
        included = {
            base_id: token_item(base_id, "FUSE", "Fuse"),
            quote_id: token_item(quote_id, "FUSE", "Fuse"),
        }
        event = s.normalize_pool(pool_resource(base_id, quote_id), included, network="eth", now_unix=1789402200)
        self.assertEqual(event["token_ca"], a)
        self.assertNotEqual(event["token_ca"], b)

    def test_unreviewed_network_cannot_inherit_ethereum_identity_semantics(self) -> None:
        a = "0x" + "a" * 40
        b = "0x" + "b" * 40
        base_id, quote_id = "arc_" + a, "arc_" + b
        included = {
            base_id: token_item(base_id, "USDC", "USD Coin"),
            quote_id: token_item(quote_id, "MEME", "Meme"),
        }
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_NETWORK_ADAPTER:arc"):
            s.normalize_pool(pool_resource(base_id, quote_id), included, network="arc", now_unix=1789402200)


if __name__ == "__main__":
    unittest.main()
