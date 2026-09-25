from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.api_agent import meme_alpha_blockscout as b


ASKR = "0xa92768863a55d8a0591709f7f5e594a249d36ea3"
TX = "0xa5ffe87bd1e9b6b91f84bb237c2d6408a7df39cb0651f85760004712074585f3"
RECIPIENT = "0x9d9258c2409c5cea1a8e24206a071ed34f3ca352"
CURVE = "0x18a08ece3e8c29df9ae497a09d2a08830561c59b"


def address_payload():
    return {
        "hash": ASKR,
        "is_contract": True,
        "is_verified": True,
        "proxy_type": None,
        "name": "PonsV2LauncherToken",
        "creator_address_hash": "0x3711ceA4feaDE896C913C68F01Eda97Cb06D1A42",
        "creation_transaction_hash": TX,
        "token": {
            "address_hash": ASKR,
            "name": "heyaskr",
            "symbol": "ASKR",
            "decimals": "18",
            "total_supply": "1000000000000000000000000000",
            "holders_count": "2552",
            "exchange_rate": "0.00413856",
            "volume_24h": "1401405.21",
        },
    }


def tx_payload():
    return {
        "hash": TX,
        "block_number": 66443556,
        "timestamp": "2026-09-18T18:35:17.000000Z",
        "method": "launchAndBuy",
        "from": RECIPIENT,
        "to": "0xe33E9E479dF8802cb0866d5d05258bEc4cF62948",
        "decoded_input": {
            "parameters": [
                {
                    "name": "params",
                    "value": [
                        "heyaskr",
                        "ASKR",
                        "ipfs://x",
                        "A free market for AI, funded by crypto.",
                        ["https://x.com/heyaskr", "https://t.me/heyaskr", "", "", ""],
                        RECIPIENT,
                        "200",
                        False,
                        "0x" + "1" * 64,
                        "0x" + "2" * 64,
                    ],
                },
                {"name": "launchConfigId", "value": "0"},
                {"name": "pairToken", "value": "0x0000000000000000000000000000000000000000"},
                {"name": "quoteIn", "value": "100000000000000000"},
                {"name": "recipient", "value": RECIPIENT},
                {"name": "snipeTaxExemptions", "value": []},
            ]
        },
        "token_transfers": [
            {
                "from": CURVE,
                "to": RECIPIENT,
                "token": {"address_hash": ASKR, "decimals": "18"},
                "total": {"value": "54586381541924592009003939", "decimals": "18"},
            }
        ],
    }


class MemeAlphaBlockscoutTests(unittest.TestCase):
    def test_pro_unified_is_preferred_and_key_is_not_in_receipt(self):
        seen = []

        def getter(url, *, timeout):
            seen.append(url)
            return 200, {"ok": True}

        payload, health = b.blockscout_get(
            "/api/v2/stats",
            api_key="proapi_SECRET",
            getter=getter,
        )
        self.assertEqual(payload, {"ok": True})
        self.assertEqual(health["transport"], "PRO_UNIFIED")
        self.assertTrue(health["authenticated"])
        self.assertIn("apikey=proapi_SECRET", seen[0])
        self.assertNotIn("proapi_SECRET", str(health))

    def test_public_chain_fallback_is_used_after_pro_failure(self):
        seen = []

        def getter(url, *, timeout):
            seen.append(url)
            if url.startswith(b.PRO_ROOT):
                return 401, {"message": "bad key"}
            return 200, {"items": []}

        payload, health = b.blockscout_get(
            "/api/v2/addresses/" + ASKR + "/transactions",
            api_key="proapi_BAD",
            getter=getter,
        )
        self.assertEqual(payload, {"items": []})
        self.assertEqual(health["transport"], "PUBLIC_CHAIN_FALLBACK")
        self.assertTrue(health["fallback_used"])
        self.assertEqual(len(health["prior_failures"]), 1)
        self.assertNotIn("proapi_BAD", str(health))

    def test_launch_origin_snapshot_reconstructs_askr_fields(self):
        def getter(url, *, timeout):
            if "/api/v2/addresses/" in url:
                return 200, address_payload()
            if "/api/v2/transactions/" in url:
                return 200, tx_payload()
            raise AssertionError(url)

        row = b.launch_origin_snapshot(ASKR, api_key="proapi_TEST", getter=getter)
        self.assertEqual(row["token_ca"], ASKR)
        self.assertTrue(row["address"]["is_contract"])
        self.assertTrue(row["address"]["is_verified"])
        self.assertEqual(row["token"]["symbol"], "ASKR")
        self.assertEqual(row["token"]["total_supply"], 1_000_000_000)
        self.assertEqual(row["launch"]["method"], "launchAndBuy")
        self.assertAlmostEqual(row["launch"]["quote_in_native"], 0.1)
        self.assertAlmostEqual(row["launch"]["initial_tokens_received"], 54_586_381.54192459, places=6)
        self.assertAlmostEqual(row["launch"]["initial_buy_pct_supply"], 5.458638154192459, places=9)
        self.assertEqual(row["launch"]["snipe_exemption_count"], 0)
        self.assertIn("https://x.com/heyaskr", row["launch"]["embedded_project_socials"])
        self.assertFalse(row["authority"]["project_ownership_proven"])
        self.assertEqual(row["source_health"]["overall"], "PASS")

    def test_missing_key_with_public_fallback_disabled_fails_closed(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "BLOCKSCOUT_API_KEY_MISSING"):
                b.blockscout_get(
                    "/api/v2/stats",
                    api_key=None,
                    allow_public_fallback=False,
                    getter=lambda *_args, **_kwargs: (200, {}),
                )

    def test_invalid_address_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "INVALID_EVM_ADDRESS"):
            b.launch_origin_snapshot("ASKR", getter=lambda *_a, **_k: (200, {}))


if __name__ == "__main__":
    unittest.main()
