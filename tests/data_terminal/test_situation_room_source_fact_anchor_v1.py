"""Original News Intelligence #1888, strictly shadow primary fact corroboration.

Offline only. Actual Nov7 owner receipt is read as provenance, never overwritten
or retroactively credited as an earlier primary source/consumer delivery.
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.data_terminal import situation_room_shadow_bridge as bridge

ROOT = Path(__file__).resolve().parents[2]
OWNER = ROOT / "03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/2026/11/2026-11-07.json"


class NewsOriginalSourceFactAnchorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(OWNER.read_text())
        cls.discovery = cls.original["current_unverified_discoveries"][0]
        cls.primary = cls.original["events"][0]
        assert cls.primary["verification_status"] == "PRIMARY_SOURCE_VERIFIED"

    def test_real_original_nov7_treasury_fact_preserved_without_loose_title_match(self):
        self.assertIsNone(bridge.owner_primary_match(self.discovery, [self.primary]))
        result = bridge.source_bound_fact_anchor_match(self.discovery, [self.primary])
        self.assertIsNotNone(result)
        self.assertEqual(result["verification_method"], "OWNER_PRIMARY_EVENT_FACT_ANCHORS")
        self.assertEqual(result["primary_event_id"], self.primary["event_id"])
        self.assertEqual(result["verification_status"], "PRIMARY_EVENT_CORROBORATED")
        self.assertTrue(result["fact_anchor_research_only_no_retroactive_pit"])
        self.assertLess(result["match_score"], 1.0)

    def test_different_number_or_country_fails_even_with_same_agency(self):
        for wrong in (
            self.discovery["title"].replace("eight", "nine"),
            self.discovery["title"].replace("Iran", "Venezuela"),
            self.discovery["title"].replace("Canadian", "American"),
        ):
            with self.subTest(wrong=wrong):
                changed = dict(self.discovery, title=wrong)
                self.assertIsNone(bridge.source_bound_fact_anchor_match(changed, [self.primary]))

    def test_nonprimary_unknown_digest_or_lookalike_domain_fails_closed(self):
        for mutation in ("not_verified", "no_sha", "no_end", "lookalike_domain"):
            event = copy.deepcopy(self.primary)
            if mutation == "not_verified":
                event["verification_status"] = "PENDING_PRIMARY_VERIFICATION"
            elif mutation == "no_sha":
                event["source_receipts"][0]["sha256"] = None
            elif mutation == "no_end":
                event["source_receipts"][0]["retrieval_end_utc"] = None
            else:
                event["source_receipts"][0]["url"] = "https://home.treasury.gov.evil.example/news/press"
            with self.subTest(mutation=mutation):
                self.assertIsNone(bridge.source_bound_fact_anchor_match(self.discovery, [event]))

    def test_duplicate_official_family_and_future_event_fail_closed(self):
        duplicate = copy.deepcopy(self.primary)
        duplicate["event_id"] = "EVT_ANOTHER_SOURCE"
        self.assertIsNone(bridge.source_bound_fact_anchor_match(
            self.discovery, [self.primary, duplicate]))
        future = copy.deepcopy(self.primary)
        future["event_time_utc"] = "2026-11-08T00:00:00Z"
        self.assertIsNone(bridge.source_bound_fact_anchor_match(self.discovery, [future]))

    def test_local_owner_source_run_is_shadow_only_and_no_network_is_needed(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            output = Path(tmp) / "shadow"
            source.mkdir()
            owner_path = source / "owner.json"
            owner_path.write_text(json.dumps(self.original))
            (source / "LATEST.json").write_text(json.dumps({"path": str(owner_path)}))
            with patch.object(bridge, "linked_primary_match", side_effect=AssertionError("NETWORK_NOT_REQUIRED")):
                result = bridge.run(source, output, timeout=1)
            self.assertEqual(result["status"], "SHADOW_HANDOFF_READY")
            self.assertEqual(len(result["verified_shadow_context"]), 1)
            self.assertEqual(result["verified_shadow_context"][0]["primary_event_id"], self.primary["event_id"])
            self.assertFalse(result["authority_firewall"]["canonical_effect"])
            self.assertFalse(result["authority_firewall"]["portfolio_effect"])
            self.assertEqual(bridge.run(source, output, timeout=1)["status"], "NO_CHANGE")
            # Test only temporary files; original archived source is never mutated.


if __name__ == "__main__":
    unittest.main()
