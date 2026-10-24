from __future__ import annotations

import unittest

from scripts.data_ping.auto_market_state import capitalization_transmission_proxy, etf, normalize_breadth, select_current_breadth, stablecoin


class AutoMarketStateIntegrityTests(unittest.TestCase):
    @staticmethod
    def _predecessor_snapshot(tmp_root, *, scenario):
        import json
        import os
        import subprocess
        from pathlib import Path
        from scripts.data_ping.auto_market_state import canon, h
        from scripts.data_ping.truth_integrity import GitCliSnapshot

        base = Path(tmp_root)
        home = "04_MARKET_LEARNING/entry_signals/auto_market_state"
        target = home + "/runs/2026/10/01/120000_test.json"
        alternate = home + "/runs/2026/10/01/130000_test.json"
        pointer_path = home + "/LATEST.json"

        def packet(price):
            value = {
                "contract": "AUTO_MARKET_STATE_PACKET_v1",
                "packet_generated_at_utc": "2026-10-01T12:00:00Z",
                "normalized_state": {"scalar_values": {"btc_usdt": price}},
            }
            value["packet_sha256"] = h(canon(value))
            return value

        primary = packet(99)
        other = packet(101)
        pointer = {
            "contract": "AUTO_MARKET_STATE_LATEST_POINTER_v1",
            "packet_path": target,
            "packet_sha256": primary["packet_sha256"],
        }
        if scenario == "pointer_mismatch":
            pointer["packet_sha256"] = "0" * 64
        elif scenario == "pointer_digest_missing":
            pointer.pop("packet_sha256")
        elif scenario == "pointer_digest_malformed":
            pointer["packet_sha256"] = "not-a-sha"
        elif scenario == "modified_payload":
            primary["normalized_state"]["scalar_values"]["btc_usdt"] = 101
        elif scenario == "wrong_target":
            pointer["packet_path"] = alternate
        elif scenario == "wrong_pointer_contract":
            pointer["contract"] = "WRONG_POINTER_CONTRACT"
        elif scenario == "wrong_packet_contract":
            primary["contract"] = "WRONG_PACKET_CONTRACT"
            primary["packet_sha256"] = h(canon({k: v for k, v in primary.items() if k != "packet_sha256"}))
            pointer["packet_sha256"] = primary["packet_sha256"]
        elif scenario == "missing_target":
            primary = None
        elif scenario == "traversal":
            pointer["packet_path"] = "../outside.json"

        files = {target: primary, alternate: other, pointer_path: pointer}
        if scenario == "no_pointer":
            files.pop(pointer_path)
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_AUTHOR_NAME="Task2 Test", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                   GIT_COMMITTER_NAME="Task2 Test", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        def git(*args):
            return subprocess.run(["git", "-c", "core.hooksPath=" + os.devnull, *args],
                                  cwd=base, env=env, check=True, capture_output=True)
        git("init", "--quiet")
        for name, value in files.items():
            if value is None:
                continue
            file = base / name
            file.parent.mkdir(parents=True, exist_ok=True)
            raw = canon(value)
            if scenario == "malformed_pointer" and name == pointer_path:
                raw = b"not-json"
            if scenario == "malformed_target" and name == target:
                raw = b"not-json"
            file.write_bytes(raw)
        git("add", "--all")
        git("commit", "-m", "Synthetic predecessor fixture")
        return GitCliSnapshot.open_repo(base, ref="HEAD")

    def test_predecessor_real_git_identity_negative_matrix(self):
        import tempfile
        from scripts.data_ping.auto_market_state import prior_packet, delta
        invalid = (
            "pointer_mismatch", "pointer_digest_missing",
            "pointer_digest_malformed", "modified_payload", "wrong_target",
            "wrong_pointer_contract", "wrong_packet_contract",
            "missing_target", "traversal", "malformed_target", "malformed_pointer",
        )
        for scenario in invalid:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as td:
                snapshot = self._predecessor_snapshot(td, scenario=scenario)
                found, health = prior_packet(snapshot)
                self.assertIsNone(found, f"{scenario}: corrupted predecessor must never be consumed")
                self.assertEqual(health["status"], "UNAVAILABLE", f"{scenario}: {health}")
                self.assertIsNone(delta(100, None), f"{scenario}: no numeric delta from corrupt input")

    def test_existing_pointer_with_corrupt_git_blob_is_not_first_packet(self):
        import subprocess
        import tempfile
        from pathlib import Path
        from scripts.data_ping.auto_market_state import prior_packet

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            snapshot = self._predecessor_snapshot(td, scenario="valid")
            pointer_path = "04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json"
            blob = subprocess.check_output(
                ["git", "rev-parse", "HEAD:" + pointer_path],
                cwd=root, text=True,
            ).strip()
            object_file = root / ".git" / "objects" / blob[:2] / blob[2:]
            self.assertTrue(object_file.is_file())
            original_bytes = object_file.read_bytes()
            try:
                # The entry EXISTS in the immutable tree but its object is
                # corrupt. This is not a legitimate first-packet absence.
                object_file.write_bytes(b"corrupted-synthetic-object")
                found, health = prior_packet(snapshot)
                self.assertIsNone(found)
                self.assertEqual(health["status"], "UNAVAILABLE")
                self.assertNotEqual(health["status"], "NOT_AVAILABLE_FIRST_PACKET")
            finally:
                object_file.write_bytes(original_bytes)

    def test_predecessor_real_git_valid_and_first_packet_controls(self):
        import tempfile
        from scripts.data_ping.auto_market_state import prior_packet, delta
        with tempfile.TemporaryDirectory() as td:
            snapshot = self._predecessor_snapshot(td, scenario="valid")
            found, health = prior_packet(snapshot)
            self.assertEqual(health["status"], "AVAILABLE")
            self.assertEqual(delta(100, found["normalized_state"]["scalar_values"]["btc_usdt"])["pct"] > 0, True)
        with tempfile.TemporaryDirectory() as td:
            snapshot = self._predecessor_snapshot(td, scenario="no_pointer")
            found, health = prior_packet(snapshot)
            self.assertIsNone(found)
            self.assertEqual(health["status"], "NOT_AVAILABLE_FIRST_PACKET")

    def test_c5e_breadth_owner_contract_and_timestamp_alias_are_accepted(self):
        membership = "b" * 64
        value = {
            "contract": "C5E_TOP100_BREADTH_OWNER_v1_2",
            "retrieval_timestamp": "2026-10-04T13:00:00Z",
            "universe": {
                "identifier": "COINGECKO_MARKET_CAP_TOP100_FILTERED_EX_STABLECOINS_v1",
                "version": "TOP100_FILTERED_STABLE_EXCLUSION_RICH_BREADTH_v1_2",
                "constituent_count": 100,
                "membership_hash": membership,
            },
            "aggregate": {
                "constituent_count": 100,
                "advancers": 66,
                "decliners": 29,
                "flat": 5,
                "advance_ratio": 0.66,
                "membership_hash": membership,
            },
            "evidence_semantics": {
                "evidence_role": "PROXY_ONLY",
                "canonical_compatible": False,
                "canonical_large_cap_breadth": "UNCONFIRMED",
                "canonical_broad_alt_breadth": "UNCONFIRMED",
            },
        }
        out, health = normalize_breadth(
            value,
            now_utc=__import__("datetime").datetime(2026, 10, 4, 13, 30, tzinfo=__import__("datetime").timezone.utc),
        )
        self.assertIsNotNone(out)
        self.assertEqual(health["status"], "PASS")
        self.assertEqual(health["source_contract"], "C5E_TOP100_BREADTH_OWNER_v1_2")
        self.assertEqual(health["retrieved_at_utc"], "2026-10-04T13:00:00Z")

    def test_freshest_same_family_breadth_point_wins_without_double_vote(self):
        rich = {
            "retrieved_at_utc": "2026-09-30T14:59:03Z",
            "aggregate": {
                "advance_ratio": 0.33,
                "advancers": 33,
                "decliners": 65,
                "flat": 2,
                "constituent_count": 100,
            },
            "universe": {"membership_hash": "rich-hash", "constituent_count": 100},
        }
        live = {
            "advancers": 74,
            "decliners": 24,
            "flat": 2,
            "constituent_count": 100,
            "membership_hash": "live-hash",
            "observation": {"retrieval_timestamp_utc": "2026-09-30T17:59:20Z"},
            "evidence_semantics": {"evidence_role": "PROXY_ONLY"},
        }
        out = select_current_breadth(rich, live)
        self.assertIsNotNone(out)
        self.assertEqual(out["source"], "LIVE_ANCHOR_BREADTH_REFERENCE")
        self.assertAlmostEqual(out["advance_ratio"], 0.74)
        self.assertEqual(out["advancers"], 74)
        self.assertEqual(out["selection_semantics"], "FRESHEST_SAME_FAMILY_POINT_ONLY_NO_DOUBLE_VOTE")
        self.assertFalse(out["temporal_comparison"]["independent_vote"])
        self.assertTrue(out["temporal_comparison"]["same_upstream_family"])
        self.assertEqual(out["temporal_comparison"]["older_source"], "RICH_BREADTH_OWNER")
        self.assertEqual(out["temporal_comparison"]["newer_source"], "LIVE_ANCHOR_BREADTH_REFERENCE")

    def test_timestamped_rich_breadth_beats_untimestamped_live_reference(self):
        rich = {
            "retrieved_at_utc": "2026-09-30T14:59:03Z",
            "aggregate": {"advance_ratio": 0.42, "advancers": 42, "decliners": 56, "constituent_count": 100},
        }
        live = {"advancers": 80, "decliners": 18, "constituent_count": 100}
        out = select_current_breadth(rich, live)
        self.assertEqual(out["source"], "RICH_BREADTH_OWNER")
        self.assertAlmostEqual(out["advance_ratio"], 0.42)

    def test_capitalization_transmission_proxy_is_measured_but_zero_authority(self):
        constituents = []
        for rank in range(1, 101):
            constituents.append({
                "asset_id": "bitcoin" if rank == 1 else "ethereum" if rank == 2 else f"asset-{rank}",
                "symbol": "btc" if rank == 1 else "eth" if rank == 2 else f"a{rank}",
                "filtered_rank": rank,
                "market_cap_usd": float(101-rank) * 1_000_000,
                "change_24h_pct": float(rank - 50) / 10.0,
            })
        breadth = {
            "retrieved_at_utc": "2026-09-30T18:00:00Z",
            "universe": {"identifier": "TEST_TOP100", "membership_hash": "membership"},
            "aggregate": {"membership_hash": "membership"},
            "constituents": constituents,
        }
        out = capitalization_transmission_proxy(breadth)
        self.assertEqual(out["contract"], "CAPITALIZATION_TRANSMISSION_PROXY_v2")
        self.assertEqual(out["bucket_semantics"], "FILTERED_TOP100_RANK_WINDOWS_EXPLICIT_NON_BETA_EXCLUSIONS_PROXY_ONLY")
        self.assertEqual(out["non_beta_exclusion_policy"]["scope"], "DOWNSTREAM_PROXY_ONLY_OWNER_UNIVERSE_UNCHANGED")
        self.assertEqual(out["excluded_non_beta_count"], 0)
        self.assertFalse(out["authority"]["binding"])
        self.assertFalse(out["authority"]["canonical_rotation"])
        self.assertEqual(out["authority"]["execution_weight"], 0)

        large = out["buckets"]["LARGE_ALT_PROXY"]
        mid = out["buckets"]["MID_ALT_PROXY"]
        small = out["buckets"]["SMALL_ALT_PROXY"]
        micro = out["buckets"]["MICROCAP_PROXY"]
        self.assertEqual(large["constituent_count"], 18)
        self.assertEqual(mid["constituent_count"], 30)
        self.assertEqual(small["constituent_count"], 50)
        self.assertEqual(large["membership"][0]["filtered_rank"], 3)
        self.assertEqual(large["membership"][-1]["filtered_rank"], 20)
        self.assertEqual(mid["membership"][0]["filtered_rank"], 21)
        self.assertEqual(small["membership"][-1]["filtered_rank"], 100)
        self.assertEqual(micro["status"], "UNAVAILABLE")
        self.assertEqual(micro["coverage"], "BELOW_TOP100_SOURCE_UNIVERSE_NOT_OBSERVED")
        self.assertGreaterEqual(large["advance_ratio_24h"], 0.0)
        self.assertLessEqual(large["advance_ratio_24h"], 1.0)

    def test_capitalization_proxy_excludes_explicit_non_beta_assets_without_reranking(self):
        breadth = {
            "retrieved_at_utc": "2026-10-01T06:00:00Z",
            "universe": {"identifier": "TEST_TOP100", "membership_hash": "same-owner-membership"},
            "constituents": [
                {"asset_id": "bitcoin", "symbol": "btc", "filtered_rank": 1, "market_cap_usd": 100.0, "change_24h_pct": 1.0},
                {"asset_id": "ethereum", "symbol": "eth", "filtered_rank": 2, "market_cap_usd": 90.0, "change_24h_pct": 2.0},
                {"asset_id": "figure-heloc", "symbol": "figr_heloc", "filtered_rank": 8, "market_cap_usd": 80.0, "change_24h_pct": 9.0},
                {"asset_id": "crypto-large", "symbol": "cl", "filtered_rank": 9, "market_cap_usd": 79.0, "change_24h_pct": -1.0},
                {"asset_id": "tether-gold", "symbol": "xaut", "filtered_rank": 31, "market_cap_usd": 60.0, "change_24h_pct": 0.1},
                {"asset_id": "crypto-mid", "symbol": "cm", "filtered_rank": 32, "market_cap_usd": 59.0, "change_24h_pct": 3.0},
                {"asset_id": "bfusd", "symbol": "bfusd", "filtered_rank": 60, "market_cap_usd": 40.0, "change_24h_pct": 0.0},
                {"asset_id": "crypto-small", "symbol": "cs", "filtered_rank": 61, "market_cap_usd": 39.0, "change_24h_pct": 4.0},
            ],
        }
        out = capitalization_transmission_proxy(breadth)
        self.assertEqual(out["source_membership_hash"], "same-owner-membership")
        self.assertEqual(out["excluded_non_beta_count"], 3)
        excluded = {row["asset_id"]: row for row in out["excluded_non_beta_assets"]}
        self.assertEqual(excluded["figure-heloc"]["exclusion_class"], "TOKENIZED_CREDIT_RWA")
        self.assertEqual(excluded["tether-gold"]["exclusion_class"], "TOKENIZED_COMMODITY")
        self.assertEqual(excluded["bfusd"]["exclusion_class"], "STABLE_VALUE_ASSET")

        large = out["buckets"]["LARGE_ALT_PROXY"]
        mid = out["buckets"]["MID_ALT_PROXY"]
        small = out["buckets"]["SMALL_ALT_PROXY"]
        self.assertEqual(large["raw_rank_window_constituent_count"], 2)
        self.assertEqual(large["excluded_non_beta_count"], 1)
        self.assertEqual([row["asset_id"] for row in large["membership"]], ["crypto-large"])
        self.assertEqual(large["membership"][0]["filtered_rank"], 9)
        self.assertEqual(mid["raw_rank_window_constituent_count"], 2)
        self.assertEqual([row["asset_id"] for row in mid["membership"]], ["crypto-mid"])
        self.assertEqual(mid["membership"][0]["filtered_rank"], 32)
        self.assertEqual(small["raw_rank_window_constituent_count"], 2)
        self.assertEqual([row["asset_id"] for row in small["membership"]], ["crypto-small"])
        self.assertEqual(small["membership"][0]["filtered_rank"], 61)
        self.assertFalse(out["authority"]["binding"])
        self.assertEqual(out["authority"]["execution_weight"], 0)

    def test_capitalization_proxy_does_not_smuggle_btc_eth_into_alt_bucket(self):
        breadth = {
            "constituents": [
                {"asset_id": "bitcoin", "symbol": "btc", "filtered_rank": 1, "market_cap_usd": 10.0, "change_24h_pct": 5.0},
                {"asset_id": "ethereum", "symbol": "eth", "filtered_rank": 2, "market_cap_usd": 9.0, "change_24h_pct": 4.0},
                {"asset_id": "alt-3", "symbol": "a3", "filtered_rank": 3, "market_cap_usd": 8.0, "change_24h_pct": 3.0},
            ],
            "universe": {"identifier": "TEST", "membership_hash": "m"},
        }
        out = capitalization_transmission_proxy(breadth)
        large = out["buckets"]["LARGE_ALT_PROXY"]
        self.assertEqual(large["constituent_count"], 1)
        self.assertEqual([row["asset_id"] for row in large["membership"]], ["alt-3"])
        self.assertEqual(out["btc_return_24h_pct"], 5.0)
        self.assertEqual(out["eth_return_24h_pct"], 4.0)

    def test_stablecoin_normalization_preserves_source_and_retrieval_time(self):
        out, health = stablecoin({
            "contract": "DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1",
            "global": {
                "total_usd": 300_000_000_000.0,
                "change_1d_pct": 0.1,
                "change_7d_pct": 1.0,
                "change_30d_pct": 2.0,
                "timestamp": 1790726400,
            },
            "retrieved_at_utc": "2026-09-30T11:13:52Z",
            "evidence_semantics": {"evidence_role": "SUPPLY_LIQUIDITY", "deployment_confirmation": "NOT_ESTABLISHED"},
            "authority": {"binding": False, "canonical_acceptance": False, "state_change": False, "portfolio_action": False},
        })
        self.assertEqual(health["status"], "PASS")
        self.assertEqual(out["retrieved_at_utc"], "2026-09-30T11:13:52Z")
        self.assertIsNotNone(out["source_timestamp"])

    def test_etf_normalization_preserves_retrieval_time(self):
        out, health = etf({
            "contract": "DAILY_SETTLED_ETF_CALIBRATION_v2",
            "session_date": "2026-09-29",
            "retrieved_at_utc": "2026-09-30T12:27:59Z",
            "rows": [
                {"asset": "BTC", "session_final": True, "total_parity": True, "reported_total": 66.2},
                {"asset": "ETH", "session_final": True, "total_parity": True, "reported_total": -2.8},
            ],
        })
        self.assertEqual(health["status"], "PASS")
        self.assertEqual(out["retrieved_at_utc"], "2026-09-30T12:27:59Z")
        self.assertEqual(out["btc_reported_total_musd"], 66.2)
        self.assertEqual(out["eth_reported_total_musd"], -2.8)


if __name__ == "__main__":
    unittest.main()
