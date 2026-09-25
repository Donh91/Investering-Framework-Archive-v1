from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.api_agent import meme_alpha_robinhood_pons_v2 as r
from scripts.api_agent import meme_alpha_blockscout as bs


ASKR = "0xa92768863a55d8a0591709f7f5e594a249d36ea3"
CURVE = "0x18a08ece3e8c29df9ae497a09d2a08830561c59b"
DEPLOYER = "0x9d9258c2409c5cea1a8e24206a071ed34f3ca352"
LAUNCH_TX = "0xa5ffe87bd1e9b6b91f84bb237c2d6408a7df39cb0651f85760004712074585f3"
LAUNCH_BLOCK = 66_443_556
BASKR = "0x36d7a44ca29b4e1081ec9fdbfa2c5e156b8f5999"


def launch_log(
    token: str = ASKR,
    *,
    topic0: str = r.TOKEN_LAUNCHED_TOPIC0,
    emitter: str = r.PONS_V2_FACTORY,
) -> dict:
    return {
        "address": emitter,
        "topics": [
            topic0,
            r.padded_address_topic(token),
            r.padded_address_topic(CURVE),
            r.padded_address_topic(DEPLOYER),
        ],
        # The identity fixture deliberately does not invent event-data fields
        # that were not needed for the frozen ASKR first-seen proof.
        "data": "0x",
        "blockNumber": hex(LAUNCH_BLOCK),
        "blockHash": "0x" + "ab" * 32,
        "transactionHash": LAUNCH_TX,
        "transactionIndex": "0x1",
        "logIndex": "0x2",
    }


class RobinhoodPonsV2AdapterTests(unittest.TestCase):
    def test_frozen_askr_fixture_decodes_exact_identity_without_enrichment(self) -> None:
        event = r.parse_token_launched_log(
            launch_log(),
            observed_at_unix=1_758_223_000,
            rpc_source="rpc.mainnet.chain.robinhood.com",
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event["chain"], "robinhood")
        self.assertEqual(event["chain_id"], 4663)
        self.assertEqual(event["token_ca"], ASKR)
        self.assertEqual(event["curve"], CURVE)
        self.assertEqual(event["deployer"], DEPLOYER)
        self.assertEqual(event["block_number"], LAUNCH_BLOCK)
        self.assertEqual(event["transaction_hash"], LAUNCH_TX)
        self.assertEqual(event["metadata_state"], "UNKNOWN")
        self.assertEqual(event["market_state"], "UNKNOWN")
        self.assertIsNone(event["token_name"])
        self.assertIsNone(event["token_symbol"])
        self.assertIsNone(event["market_cap_usd"])
        self.assertIsNone(event["fdv_usd"])
        self.assertEqual(event["data_integrity_status"], "PASS")
        self.assertFalse(event["authority"]["user_alert"])
        self.assertFalse(event["authority"]["adaptive_learning"])
        self.assertFalse(event["authority"]["automatic_trading"])

    def test_wrong_factory_is_rejected(self) -> None:
        log = launch_log(emitter="0x" + "1" * 40)
        self.assertIsNone(r.parse_token_launched_log(log))

    def test_wrong_topic0_is_rejected(self) -> None:
        log = launch_log(topic0="0x" + "2" * 64)
        self.assertIsNone(r.parse_token_launched_log(log))

    def test_exact_ca_is_identity_even_when_metadata_is_unknown(self) -> None:
        event = r.parse_token_launched_log(launch_log())
        assert event is not None
        self.assertTrue(r.exact_target_match(event, target_ca=ASKR))
        self.assertFalse(r.exact_target_match(event, target_ca=BASKR))

    def test_baskr_cannot_substring_match_askr(self) -> None:
        event = r.parse_token_launched_log(launch_log(BASKR))
        assert event is not None
        self.assertFalse(
            r.exact_target_match(
                event,
                target_symbol="ASKR",
                token_symbol="BASKR",
            )
        )
        self.assertFalse(
            r.exact_target_match(
                event,
                target_name="heyaskr",
                token_name="Baskr",
            )
        )

    def test_exact_symbol_match_is_allowed_only_as_exact_normalized_fallback(self) -> None:
        event = r.parse_token_launched_log(launch_log())
        assert event is not None
        self.assertTrue(r.exact_target_match(event, target_symbol="ASKR", token_symbol="$askr"))
        self.assertTrue(r.exact_target_match(event, target_name="hey askr", token_name="heyaskr"))

    def test_provider_call_fails_over_after_first_provider_failure(self) -> None:
        calls: list[tuple[str, str]] = []

        def fake_rpc(url: str, method: str, params: list, **_: object):
            calls.append((url, method))
            if "bad.example" in url:
                raise RuntimeError("HTTP_403")
            if method == "eth_chainId":
                return hex(r.CHAIN_ID)
            if method == "eth_getLogs":
                return []
            raise AssertionError(method)

        with patch.object(r, "rpc_call", side_effect=fake_rpc):
            result, source, errors = r.provider_call(
                ["https://bad.example/rpc", "https://good.example/rpc"],
                "eth_getLogs",
                [{"fromBlock": "0x1", "toBlock": "0x2"}],
            )

        self.assertEqual(result, [])
        self.assertEqual(source, "good.example")
        self.assertIn("bad.example", errors)
        self.assertIn(("https://good.example/rpc", "eth_chainId"), calls)
        self.assertIn(("https://good.example/rpc", "eth_getLogs"), calls)

    def test_wrong_chain_provider_is_never_accepted(self) -> None:
        def fake_rpc(url: str, method: str, params: list, **_: object):
            if method == "eth_chainId":
                return "0x1"
            return []

        with patch.object(r, "rpc_call", side_effect=fake_rpc):
            with self.assertRaisesRegex(RuntimeError, "ALL_ROBINHOOD_PROVIDERS_FAILED"):
                r.provider_call(["https://wrong.example/rpc"], "eth_getLogs", [{}])

    def test_scan_range_preserves_raw_launch_and_dedupes_overlap_identity(self) -> None:
        raw = launch_log()
        calls = 0

        def fake_provider_call(urls, method, params, **kwargs):
            nonlocal calls
            calls += 1
            self.assertEqual(method, "eth_getLogs")
            return [raw, raw], "fixture.rpc", {}

        preflight = {
            "providers": [
                {"provider": "fixture.rpc", "chain_id_ok": True, "head_block": LAUNCH_BLOCK + 10, "state": "HEALTHY", "error": None},
                {"provider": "backup.rpc", "chain_id_ok": True, "head_block": LAUNCH_BLOCK + 9, "state": "HEALTHY", "error": None},
            ],
            "configured_provider_count": 2,
            "healthy_provider_count": 2,
            "provider_redundancy_proven": True,
            "minimum_healthy_head": LAUNCH_BLOCK + 9,
            "maximum_healthy_head": LAUNCH_BLOCK + 10,
        }
        with patch.object(r, "provider_preflight", return_value=preflight), patch.object(r, "provider_call", side_effect=fake_provider_call):
            batch = r.scan_range(
                ["https://fixture.rpc"],
                LAUNCH_BLOCK,
                LAUNCH_BLOCK,
                token_ca=ASKR,
            )

        self.assertEqual(calls, 1)
        self.assertEqual(batch["event_count"], 1)
        self.assertEqual(batch["events"][0]["token_ca"], ASKR)
        self.assertEqual(batch["target_ca"], ASKR)
        self.assertEqual(batch["providers_used"], ["fixture.rpc"])
        self.assertEqual(batch["source_health"]["health_class"], "HEALTHY_NONEMPTY")
        self.assertFalse(batch["source_health"]["absence_is_evidence"])
        self.assertFalse(batch["authority"]["user_alert"])


    def test_healthy_zero_requires_redundant_provider_and_cursor_health(self) -> None:
        preflight = {
            "providers": [
                {"provider": "a.rpc", "chain_id_ok": True, "head_block": 200, "state": "HEALTHY", "error": None},
                {"provider": "b.rpc", "chain_id_ok": True, "head_block": 201, "state": "HEALTHY", "error": None},
            ],
            "configured_provider_count": 2,
            "healthy_provider_count": 2,
            "provider_redundancy_proven": True,
            "minimum_healthy_head": 200,
            "maximum_healthy_head": 201,
        }
        with patch.object(r, "provider_preflight", return_value=preflight), patch.object(
            r, "provider_call", return_value=([], "a.rpc", {})
        ):
            batch = r.scan_range(["https://a.rpc", "https://b.rpc"], 100, 110)
        self.assertEqual(batch["source_health"]["health_class"], "HEALTHY_ZERO")
        self.assertTrue(batch["source_health"]["absence_is_evidence"])

    def test_single_provider_zero_is_partial_not_absence_evidence(self) -> None:
        preflight = {
            "providers": [
                {"provider": "a.rpc", "chain_id_ok": True, "head_block": 200, "state": "HEALTHY", "error": None},
            ],
            "configured_provider_count": 1,
            "healthy_provider_count": 1,
            "provider_redundancy_proven": False,
            "minimum_healthy_head": 200,
            "maximum_healthy_head": 200,
        }
        with patch.object(r, "provider_preflight", return_value=preflight), patch.object(
            r, "provider_call", return_value=([], "a.rpc", {})
        ):
            batch = r.scan_range(["https://a.rpc"], 100, 110)
        self.assertEqual(batch["source_health"]["health_class"], "PARTIAL")
        self.assertFalse(batch["source_health"]["absence_is_evidence"])

    def test_cursor_ahead_of_verified_head_is_partial(self) -> None:
        preflight = {
            "providers": [
                {"provider": "a.rpc", "chain_id_ok": True, "head_block": 105, "state": "HEALTHY", "error": None},
                {"provider": "b.rpc", "chain_id_ok": True, "head_block": 106, "state": "HEALTHY", "error": None},
            ],
            "configured_provider_count": 2,
            "healthy_provider_count": 2,
            "provider_redundancy_proven": True,
            "minimum_healthy_head": 105,
            "maximum_healthy_head": 106,
        }
        with patch.object(r, "provider_preflight", return_value=preflight), patch.object(
            r, "provider_call", return_value=([], "a.rpc", {})
        ):
            batch = r.scan_range(["https://a.rpc", "https://b.rpc"], 100, 110)
        self.assertEqual(batch["source_health"]["health_class"], "PARTIAL")
        self.assertFalse(batch["source_health"]["absence_is_evidence"])

    def test_padded_address_topic_is_exact_indexed_topic_shape(self) -> None:
        topic = r.padded_address_topic(ASKR)
        self.assertEqual(len(topic), 66)
        self.assertTrue(topic.endswith(ASKR[2:]))


class RobinhoodBlockscoutEnrichmentTests(unittest.TestCase):
    def test_blockscout_pro_is_preferred_without_persisting_secret(self) -> None:
        seen: list[str] = []

        def getter(url: str, *, timeout: int):
            seen.append(url)
            return 200, {"ok": True}

        payload, health = bs.blockscout_get(
            "/api/v2/stats",
            api_key="proapi_TEST_SECRET",
            getter=getter,
        )
        self.assertEqual(payload, {"ok": True})
        self.assertEqual(health["transport"], "PRO_UNIFIED")
        self.assertTrue(health["authenticated"])
        self.assertIn("apikey=proapi_TEST_SECRET", seen[0])
        self.assertNotIn("proapi_TEST_SECRET", str(health))

    def test_blockscout_public_fallback_is_explicit_after_pro_failure(self) -> None:
        def getter(url: str, *, timeout: int):
            if url.startswith(bs.PRO_ROOT):
                return 401, {"message": "bad key"}
            return 200, {"items": []}

        payload, health = bs.blockscout_get(
            f"/api/v2/addresses/{ASKR}/transactions",
            api_key="proapi_BAD",
            getter=getter,
        )
        self.assertEqual(payload, {"items": []})
        self.assertEqual(health["transport"], "PUBLIC_CHAIN_FALLBACK")
        self.assertTrue(health["fallback_used"])
        self.assertEqual(len(health["prior_failures"]), 1)
        self.assertNotIn("proapi_BAD", str(health))

    def test_blockscout_askr_exact_ca_launch_enrichment(self) -> None:
        address_payload = {
            "hash": ASKR,
            "is_contract": True,
            "is_verified": True,
            "proxy_type": None,
            "name": "PonsV2LauncherToken",
            "creator_address_hash": {"hash": "0x3711ceA4feaDE896C913C68F01Eda97Cb06D1A42"},
            "creation_transaction_hash": LAUNCH_TX,
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
        tx_payload = {
            "hash": LAUNCH_TX,
            "block_number": LAUNCH_BLOCK,
            "timestamp": "2026-09-18T18:35:17.000000Z",
            "method": "launchAndBuy",
            "from": {"hash": DEPLOYER},
            "to": {"hash": "0xe33E9E479dF8802cb0866d5d05258bEc4cF62948"},
            "decoded_input": {
                "parameters": [
                    {
                        "name": "params",
                        "value": [
                            "heyaskr",
                            "ASKR",
                            "ipfs://fixture",
                            "A free market for AI, funded by crypto.",
                            ["https://x.com/heyaskr", "https://t.me/heyaskr", "", "", ""],
                            DEPLOYER,
                            "200",
                            False,
                            "0x" + "1" * 64,
                            "0x" + "2" * 64,
                        ],
                    },
                    {"name": "pairToken", "value": "0x0000000000000000000000000000000000000000"},
                    {"name": "quoteIn", "value": "100000000000000000"},
                    {"name": "recipient", "value": DEPLOYER},
                    {"name": "snipeTaxExemptions", "value": []},
                ]
            },
            "token_transfers": [
                {
                    "from": {"hash": CURVE},
                    "to": {"hash": DEPLOYER},
                    "token": {"address_hash": ASKR, "decimals": "18"},
                    "total": {"value": "54586381541924592009003939", "decimals": "18"},
                }
            ],
        }

        def getter(url: str, *, timeout: int):
            if f"/api/v2/addresses/{ASKR}" in url:
                return 200, address_payload
            if f"/api/v2/transactions/{LAUNCH_TX}" in url:
                return 200, tx_payload
            raise AssertionError(url)

        row = bs.launch_origin_snapshot(ASKR, api_key="proapi_TEST", getter=getter)
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


if __name__ == "__main__":
    unittest.main()
