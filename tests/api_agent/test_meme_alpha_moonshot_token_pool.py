from __future__ import annotations

import unittest

from scripts.api_agent.meme_alpha_moonshot_token_pool import collapse_token_pools


CONFIG = {
    "scanner": {"absolute_minimum_liquidity_usd": 5000},
    "microstructure": {"minimum_successful_sells": 3},
}


def event(token: str, pool: str, *, age: float, liquidity: float, sells: int, volume: float = 0.0) -> dict:
    return {
        "network": "eth",
        "token_ca": token,
        "pool_address": pool,
        "pool_id": "eth_" + pool,
        "pool_created_at": "2026-09-14T15:00:00Z",
        "age_minutes": age,
        "liquidity_usd": liquidity,
        "volume_h1_usd": volume,
        "buys_h1": 10,
        "sells_h1": sells,
    }


class TokenPoolIdentityTests(unittest.TestCase):
    def test_same_ca_collapses_to_one_token_observation(self) -> None:
        token = "0x" + "1" * 40
        rows = collapse_token_pools([
            event(token, "0xweak", age=12, liquidity=900, sells=5, volume=5000),
            event(token, "0xstrong", age=20, liquidity=25000, sells=4, volume=3000),
        ], CONFIG)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["pool_address"], "0xstrong")
        self.assertEqual(rows[0]["observed_pool_count"], 2)
        self.assertEqual(len(rows[0]["observed_pool_set"]), 2)

    def test_token_age_uses_oldest_observed_pool_not_new_secondary_pool(self) -> None:
        token = "0x" + "2" * 40
        rows = collapse_token_pools([
            event(token, "0xnew", age=5, liquidity=30000, sells=8),
            event(token, "0xold", age=300, liquidity=10000, sells=3),
        ], CONFIG)
        self.assertEqual(rows[0]["pool_address"], "0xnew")
        self.assertEqual(rows[0]["age_minutes"], 300)

    def test_distinct_contracts_never_merge_on_ticker_or_name(self) -> None:
        a = event("0x" + "a" * 40, "0xa", age=10, liquidity=20000, sells=5)
        b = event("0x" + "b" * 40, "0xb", age=10, liquidity=20000, sells=5)
        a["symbol"] = b["symbol"] = "FUSE"
        a["name"] = b["name"] = "Fuse"
        rows = collapse_token_pools([a, b], CONFIG)
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]["token_identity"], rows[1]["token_identity"])


if __name__ == "__main__":
    unittest.main()
