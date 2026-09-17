from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.api_agent import meme_alpha_moonshot_scan_v2 as scanner


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "research" / "api_agent" / "meme_alpha" / "LIVE_OBSERVATION_INTEGRITY_CONTRACT_v1.json"


class LiveObservationIntegrityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(CONTRACT.read_text())

    def test_data_integrity_precedes_analysis_and_action(self) -> None:
        self.assertEqual(self.contract["required_order"], ["DATA_INTEGRITY", "ALPHA_ANALYSIS", "ACTION"])
        self.assertEqual(self.contract["conflict_state"], "DATA_CONFLICT")
        self.assertEqual(self.contract["degraded_state"], "DEGRADED_DATA")

    def test_critical_silent_substitutions_are_forbidden(self) -> None:
        rules = self.contract["invariants"]
        self.assertFalse(rules["unknown_is_zero"])
        self.assertFalse(rules["market_cap_may_fallback_to_fdv"])
        self.assertFalse(rules["fdv_may_be_labeled_market_cap"])
        self.assertFalse(rules["missing_chain_may_default_to_ethereum"])
        self.assertFalse(rules["unreviewed_chain_may_inherit_ethereum_anchor_semantics"])
        self.assertFalse(rules["social_or_web_observation_may_override_fresher_live_pool_state"])

    def test_rstr_regression_fixture_is_pinned(self) -> None:
        fixture = self.contract["regression_cases"][0]
        live = fixture["higher_priority_timestamped_observation"]
        self.assertEqual(fixture["id"], "RSTR-2026-09-16-STALE-MCAP")
        self.assertEqual(live["market_cap_usd"], 75000)
        self.assertEqual(live["liquidity_usd"], 26000)
        self.assertEqual(live["volume_24h_usd"], 68000)
        self.assertAlmostEqual(live["price_usd"], 0.00008572)

    def test_current_scanner_fails_closed_on_unreviewed_chain(self) -> None:
        self.assertEqual(scanner.SUPPORTED_NETWORKS, frozenset({"eth"}))
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_NETWORK_ADAPTER:arc"):
            scanner.fetch_new_pools("arc", 1)


if __name__ == "__main__":
    unittest.main()
