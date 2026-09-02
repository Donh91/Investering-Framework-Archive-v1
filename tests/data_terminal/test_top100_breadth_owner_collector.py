import importlib.util
import json
import pathlib
import tempfile
import unittest

PATH = pathlib.Path("scripts/data_terminal/top100_breadth_owner_collector.py")
ARCHIVED_RAW = pathlib.Path(
    "03_DAILY_CAPTURE_LOGS/breadth_rich/2026/08/2026-08-30/raw_source_payload.json"
)
SPEC = importlib.util.spec_from_file_location("breadth_owner", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def payload(count: int = 100) -> bytes:
    return json.dumps([{
        "id": f"asset-{index}",
        "symbol": f"a{index}",
        "name": f"Asset {index}",
        "market_cap": 1_000_000 - index,
        "current_price": 100 + index,
        "price_change_percentage_24h": 1 if index % 2 == 0 else -1,
    } for index in range(count)]).encode()


def blockchaincenter_payload(score_override: dict[str, int] | None = None) -> bytes:
    targets = {"30": 18, "90": 20, "365": 17}
    latest_scores = {horizon: round(100 * outperformers / 49) for horizon, outperformers in targets.items()}
    if score_override:
        latest_scores.update(score_override)
    changes, histories, stats = {}, {}, {}
    for horizon, outperformers in targets.items():
        returns = {"BTC": "0.10"}
        returns.update({f"ALT{index:02d}": "0.20" if index < outperformers else "0.00" for index in range(49)})
        changes[horizon] = returns
        histories[horizon] = {"2026-08-24": latest_scores[horizon] - 1, "2026-08-25": latest_scores[horizon]}
        stats[horizon] = {
            "altseasondays": 10, "bitcoinseasondays": 20, "avg_alt_run": 5, "avg_btc_run": 6,
            "max_alt_run": 12, "max_btc_run": 14, "days_since_last_alt": 30, "days_since_last_btc": 4,
            "longest_no_alt_streak": 100, "longest_no_btc_streak": 80,
            "current_alt_run_length": 0, "current_btc_run_length": 0,
        }
    props = {"score": histories, "stats": stats, "latestScores": latest_scores, "change": changes}
    flight = "5:" + json.dumps(["$", "$Ltest", None, props], separators=(",", ":"))
    script = f"self.__next_f.push([1,{json.dumps(flight)}])"
    return f"<html><body><script>{script}</script></body></html>".encode()


def coinmarketcap_payload(score: int = 35) -> bytes:
    document = {"props": {"pageProps": {"pageSharedData": {"altcoinIndex": score}}}, "buildId": "test-build-v1"}
    return (
        '<html><body><script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(document, separators=(",", ":"))
        + "</script></body></html>"
    ).encode()


class Top100BreadthOwnerTests(unittest.TestCase):
    def test_parse_and_hash(self):
        constituents, exclusions, aggregate = MODULE.parse(payload())
        self.assertEqual(len(constituents), 100)
        self.assertEqual(aggregate["advancers"], 50)
        self.assertEqual(len(aggregate["membership_hash"]), 64)
        self.assertEqual(exclusions, [])

    def test_incomplete(self):
        with self.assertRaises(MODULE.E):
            MODULE.parse(payload(99))

    def test_duplicate(self):
        rows = json.loads(payload())
        rows[1]["id"] = rows[0]["id"]
        with self.assertRaises(MODULE.E):
            MODULE.parse(json.dumps(rows).encode())

    def test_stable_exclusion(self):
        rows = json.loads(payload())
        rows[0]["symbol"] = "usdt"
        rows.append({
            "id": "extra", "symbol": "extra", "name": "Extra", "market_cap": 1,
            "current_price": 1, "price_change_percentage_24h": 1,
        })
        constituents, exclusions, _ = MODULE.parse(json.dumps(rows).encode())
        self.assertTrue(any(row["reason"] == "STABLECOIN" for row in exclusions))
        self.assertEqual(len(constituents), 100)

    def test_validated_live_stablecoin_leaks_are_excluded_and_backfilled(self):
        rows = json.loads(payload(104))
        stablecoins = (
            ("usd1-wlfi", "usd1", "USD1"),
            ("global-dollar", "usdg", "Global Dollar"),
            ("ripple-usd", "rlusd", "Ripple USD"),
            ("gho", "gho", "GHO"),
        )
        for row, (asset_id, symbol, name) in zip(rows, stablecoins):
            row.update(id=asset_id, symbol=symbol, name=name)
        constituents, exclusions, _ = MODULE.parse(json.dumps(rows).encode())
        self.assertEqual(len(constituents), 100)
        self.assertEqual({row["asset_id"] for row in constituents}.intersection(x[0] for x in stablecoins), set())
        excluded = {row["asset_id"]: row for row in exclusions}
        self.assertEqual(set(excluded), {x[0] for x in stablecoins})
        for asset_id, _, _ in stablecoins:
            self.assertEqual(excluded[asset_id]["reason"], "STABLECOIN")
            self.assertEqual(excluded[asset_id]["taxonomy_identifier"], MODULE.STABLECOIN_TAXONOMY_ID)
            self.assertEqual(excluded[asset_id]["taxonomy_version"], MODULE.STABLECOIN_TAXONOMY_VERSION)
        self.assertEqual(constituents[-1]["asset_id"], "asset-103")

    def test_taxonomy_provenance_is_explicit_and_deterministic(self):
        _, _, aggregate = MODULE.parse(payload())
        taxonomy = MODULE.owner_interface(aggregate, "2026-09-01T00:00:00Z")["universe"][
            "stablecoin_exclusion_taxonomy"
        ]
        self.assertEqual(taxonomy["identifier"], "CMC_FROZEN_BREADTH_V2_EXACT_STABLE_SYMBOLS")
        self.assertEqual(taxonomy["version"], "2026-07-12")
        self.assertEqual(taxonomy["exact_symbol_count"], len(MODULE.STABLE_SYMBOLS))
        self.assertEqual(taxonomy["exact_symbols"], sorted(MODULE.STABLE_SYMBOLS))
        self.assertEqual(len(taxonomy["exact_symbols_sha256"]), 64)
        self.assertEqual(taxonomy["validated_source"]["commit"], "7f338cfbac1da29682fea9bb5772e47fb4af421a")
        self.assertFalse(taxonomy["live_source_tags_available"])

    def test_protocol_association_and_ambiguous_classes_are_not_guessed_as_stablecoins(self):
        rows = json.loads(payload())
        rows[0].update(id="maker", symbol="mkr", name="Maker Stablecoin Protocol")
        rows[1].update(id="blackrock-buidl", symbol="buidl", name="Tokenized Treasury Fund")
        rows[2].update(id="tether-gold", symbol="xaut", name="Tether Gold")
        rows[3].update(id="wrapped-bitcoin", symbol="wbtc", name="Wrapped Bitcoin")
        constituents, exclusions, _ = MODULE.parse(json.dumps(rows).encode())
        eligible = {row["asset_id"] for row in constituents}
        self.assertTrue({"maker", "blackrock-buidl", "tether-gold", "wrapped-bitcoin"}.issubset(eligible))
        self.assertFalse(any(row["reason"] == "STABLECOIN" for row in exclusions))

    def test_archived_reproduction_raw_has_zero_validated_stable_symbols_after_parse(self):
        constituents, exclusions, _ = MODULE.parse(ARCHIVED_RAW.read_bytes())
        self.assertEqual(len(constituents), 100)
        self.assertFalse({row["symbol"].upper() for row in constituents}.intersection(MODULE.STABLE_SYMBOLS))
        excluded_symbols = {row["symbol"].upper() for row in exclusions if row["reason"] == "STABLECOIN"}
        self.assertTrue({"USD1", "USDG", "RLUSD", "GHO"}.issubset(excluded_symbols))

    def test_blockchaincenter_payload_reconciles_all_horizons(self):
        context = MODULE.build_rotation_context(blockchaincenter_payload(), "2026-08-25T07:15:00Z")
        self.assertEqual(context["status"], "PASS")
        self.assertEqual(context["headline"]["published_score"], 41)
        self.assertEqual(context["horizons"]["30"]["outperforming_btc_count"], 18)
        self.assertEqual(context["horizons"]["90"]["outperforming_btc_count"], 20)
        self.assertEqual(context["horizons"]["365"]["outperforming_btc_count"], 17)
        self.assertEqual(context["horizons"]["90"]["score_reconciliation"], "PASS_EXACT")
        self.assertFalse(context["authority"]["binding"])
        self.assertFalse(context["authority"]["shared_row_tournament_eligible"])

    def test_blockchaincenter_score_mismatch_fails_closed(self):
        with self.assertRaises(MODULE.E) as raised:
            MODULE.build_rotation_context(blockchaincenter_payload({"90": 42}), "2026-08-25T07:15:00Z")
        self.assertEqual(raised.exception.status, "BLOCKCHAINCENTER_RECONCILIATION_FAIL")

    def test_coinmarketcap_label_is_lower_grade_method_crosscheck(self):
        context = MODULE.build_coinmarketcap_context(coinmarketcap_payload(35), "2026-08-25T07:15:00Z")
        self.assertEqual(context["published_score"], 35)
        self.assertEqual(context["evidence_grade"], "PUBLISHED_LABEL_ONLY")
        self.assertEqual(context["component_reconciliation"], "NOT_AVAILABLE_FROM_CAPTURED_PAGE")
        self.assertFalse(context["authority"]["binding"])

    def test_rotation_source_failure_does_not_invalidate_primary_breadth(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            owner = MODULE.run(
                payload(), root, "2026-08-25T07:15:00Z",
                rotation_error={"failure_state": "NETWORK_ERROR", "message": "timed out"},
                coinmarketcap_error={"failure_state": "HTTP_ERROR", "message": "blocked"},
            )
            self.assertEqual(owner["rotation_context"]["status"], "DEGRADED")
            self.assertEqual(owner["rotation_method_crosscheck"]["status"], "DEGRADED")
            self.assertEqual(owner["universe"]["identifier"], MODULE.BREADTH_UNIVERSE_ID)
            self.assertEqual(owner["universe"]["membership_hash"], owner["aggregate"]["membership_hash"])
            self.assertEqual(owner["evidence_semantics"]["evidence_role"], "PROXY_ONLY")
            self.assertEqual(owner["evidence_semantics"]["canonical_large_cap_breadth"], "UNCONFIRMED")
            self.assertEqual(owner["evidence_semantics"]["canonical_broad_alt_breadth"], "UNCONFIRMED")
            self.assertFalse(owner["evidence_semantics"]["canonical_compatible"])
            self.assertEqual(MODULE.verify(root)["status"], "PASS")
            receipt = json.loads((root / "receipt.json").read_text())
            self.assertEqual(receipt["status"], "PASS")
            self.assertEqual(receipt["rotation_context_status"], "DEGRADED")
            self.assertEqual(receipt["rotation_crosscheck_status"], "DEGRADED")

    def test_run_replays_compressed_source_raw_and_detects_tamper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            MODULE.run(
                payload(), root, "2026-08-25T07:15:00Z",
                rotation_payload=blockchaincenter_payload(), coinmarketcap_payload=coinmarketcap_payload(),
            )
            self.assertEqual(MODULE.verify(root)["status"], "PASS")
            self.assertTrue((root / "raw_blockchaincenter_altcoin_season.html.gz").is_file())
            self.assertTrue((root / "raw_coinmarketcap_altcoin_season.html.gz").is_file())
            (root / "owner_snapshot.json").write_text("{}")
            self.assertEqual(MODULE.verify(root)["status"], "FAIL")

    def test_reused_output_removes_stale_raw_and_self_manifest_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            MODULE.run(
                payload(), root, "2026-08-25T07:15:00Z",
                rotation_payload=blockchaincenter_payload(), coinmarketcap_payload=coinmarketcap_payload(),
            )
            MODULE.run(
                payload(), root, "2026-08-25T11:15:00Z",
                rotation_error={"failure_state": "NETWORK_ERROR", "message": "timed out"},
                coinmarketcap_error={"failure_state": "NETWORK_ERROR", "message": "timed out"},
            )
            self.assertFalse((root / "raw_blockchaincenter_altcoin_season.html.gz").exists())
            self.assertFalse((root / "raw_coinmarketcap_altcoin_season.html.gz").exists())
            manifest = json.loads((root / "artifact_manifest.json").read_text())
            self.assertNotIn("artifact_manifest.json", {row["path"] for row in manifest["members"]})
            self.assertEqual(MODULE.verify(root)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
