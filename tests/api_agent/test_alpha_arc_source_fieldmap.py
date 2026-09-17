from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIELDMAP = ROOT / "research" / "api_agent" / "meme_alpha" / "ARC_SOURCE_FIELDMAP_v1.json"


class ArcSourceFieldmapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = json.loads(FIELDMAP.read_text())
        self.sources = {row["id"]: row for row in self.value["sources"]}

    def test_fieldmap_is_shadow_only_and_cannot_activate_arc(self) -> None:
        authority = self.value["authority"]
        self.assertTrue(authority["research_only"])
        self.assertFalse(authority["cross_chain_activation"])
        self.assertFalse(authority["canonical_market_state"])
        self.assertFalse(authority["automatic_alert_authority"])
        self.assertFalse(authority["automatic_trading"])

    def test_direct_discovery_precedes_derived_wallet_labels(self) -> None:
        sequence = self.value["recommended_adapter_sequence"]
        self.assertEqual(sequence[0]["source"], "ARC_SCREENER")
        self.assertEqual(self.sources["ARCTOOLS"]["candidate_fields"]["top100_insider_label"], "REJECT_FIELD")
        self.assertEqual(self.sources["ARCTOOLS"]["candidate_fields"]["token_score"], "REJECT_FIELD")

    def test_unverified_arc_support_is_not_promoted(self) -> None:
        self.assertEqual(self.sources["CIELO_TRENDING"]["candidate_fields"]["arc_network_support"], "UNVERIFIED")
        self.assertEqual(self.sources["BASEDBOT_ARC"]["candidate_fields"]["arc_new_pair_feed"], "UNVERIFIED")

    def test_next_action_routes_to_existing_cross_chain_owner(self) -> None:
        action = self.value["next_eligible_action"]
        self.assertEqual(action["owner"], "#1017")
        self.assertIn("SHADOW_ONLY", action["action"])


if __name__ == "__main__":
    unittest.main()
