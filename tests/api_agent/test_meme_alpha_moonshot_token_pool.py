from __future__ import annotations

import unittest

from scripts.api_agent.meme_alpha_moonshot_token_pool import collapse_token_pools


CONFIG = {
    "scanner": {"absolute_minimum_liquidity_usd": 5000},
    "microstructure": {"minimum_successful_sells": 3},
}


def event(token: str, pool: str, *, age: float, liquidity: float, sells: int, volume: float = 0.0, buys: int = 10, network: str = "eth") -> dict:
    return {
        "network": network,
        "token_ca": token,
        "pool_address": pool,
        "pool_id": network + "_" + pool,
        "pool_created_at": "2026-09-14T15:00:00Z",
        "age_minutes": age,
        "liquidity_usd": liquidity,
        "volume_h1_usd": volume,
        "buys_h1": buys,
        "sells_h1": sells,
        "token_role": "base",
        "token_price_usd": 1.0,
        "market_cap_usd": None,
        "fdv_usd": 100000.0,
        "valuation_status": "FDV_ONLY",
        "data_integrity_status": "PASS",
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
        self.assertIsNone(rows[0]["market_cap_usd"])
        self.assertEqual(rows[0]["fdv_usd"], 100000.0)

    def test_token_age_uses_oldest_observed_pool_not_new_secondary_pool(self) -> None:
        token = "0x" + "2" * 40
        rows = collapse_token_pools([
            event(token, "0xnew", age=5, liquidity=30000, sells=8),
            event(token, "0xold", age=300, liquidity=10000, sells=3),
        ], CONFIG)
        self.assertEqual(rows[0]["pool_address"], "0xnew")
        self.assertEqual(rows[0]["age_minutes"], 300)

    def test_secondary_pool_activity_cannot_reset_birth_velocity_clock(self) -> None:
        token = "0x" + "3" * 40
        rows = collapse_token_pools([
            event(token, "0xnew", age=5, liquidity=30000, sells=8, buys=60, volume=60000),
            event(token, "0xold", age=300, liquidity=10000, sells=3, buys=0, volume=0),
        ], CONFIG)
        row = rows[0]
        self.assertEqual(row["age_minutes"], 300)
        # 60 buys are divided by the token clock capped at 60m, not by the new pool's 5m age.
        self.assertAlmostEqual(row["buyer_velocity_per_minute"], 1.0)
        self.assertAlmostEqual(row["transaction_velocity_per_minute"], 71 / 60)
        self.assertAlmostEqual(row["volume_to_liquidity_h1"], 60000 / 40000)
        self.assertEqual(row["microstructure_basis"], "TOKEN_AGE_WITH_MULTI_POOL_AGGREGATION")

    def test_canonical_execution_pool_keeps_own_sell_evidence(self) -> None:
        token = "0x" + "4" * 40
        rows = collapse_token_pools([
            event(token, "0xjunk", age=4, liquidity=1000, sells=100, buys=100),
            event(token, "0xcanon", age=40, liquidity=25000, sells=4, buys=5),
        ], CONFIG)
        row = rows[0]
        self.assertEqual(row["pool_address"], "0xcanon")
        self.assertEqual(row["sells_h1"], 4)
        self.assertEqual(row["buys_h1"], 5)
        self.assertEqual(row["token_aggregate_sells_h1"], 104)

    def test_distinct_contracts_never_merge_on_ticker_or_name(self) -> None:
        a = event("0x" + "a" * 40, "0xa", age=10, liquidity=20000, sells=5)
        b = event("0x" + "b" * 40, "0xb", age=10, liquidity=20000, sells=5)
        a["symbol"] = b["symbol"] = "FUSE"
        a["name"] = b["name"] = "Fuse"
        rows = collapse_token_pools([a, b], CONFIG)
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]["token_identity"], rows[1]["token_identity"])

    def test_same_evm_address_on_two_chains_is_two_identities(self) -> None:
        token = "0x" + "c" * 40
        rows = collapse_token_pools([
            event(token, "0xeth", age=10, liquidity=20000, sells=5, network="eth"),
            event(token, "0xarc", age=10, liquidity=20000, sells=5, network="arc"),
        ], CONFIG)
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["token_identity"] for row in rows}, {f"eth:{token}", f"arc:{token}"})

    def test_missing_chain_never_defaults_to_ethereum(self) -> None:
        row = event("0x" + "d" * 40, "0xmissing", age=10, liquidity=20000, sells=5)
        row.pop("network")
        rows = collapse_token_pools([row], CONFIG)
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
