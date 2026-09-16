from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "06_RESEARCH_LAB" / "alpha_lab" / "2026-09-16__aegis-gap-audit__shadow.json"


class AegisGapAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = json.loads(AUDIT.read_text())

    def test_aegis_is_extract_not_clone(self) -> None:
        self.assertEqual(self.value["overall_disposition"], "EXTRACT")
        self.assertTrue(self.value["do_not_vendor_or_clone"])

    def test_execution_and_score_import_have_no_authority(self) -> None:
        authority = self.value["authority"]
        self.assertFalse(authority["changes_scoring_weights"])
        self.assertFalse(authority["automatic_trading"])
        rejected = {row["item"] for row in self.value["reject_or_do_not_copy"]}
        self.assertIn("MEMORY_ADJUSTMENT_INSIDE_SAFETY_SCORE", rejected)
        self.assertIn("SNIPER_EXECUTION_MODULES", rejected)

    def test_chain_aware_identity_is_required_before_memory_reuse(self) -> None:
        rejected = {row["item"] for row in self.value["reject_or_do_not_copy"]}
        self.assertIn("ADDRESS_ONLY_PRIMARY_KEYS", rejected)
        candidate = self.value["implementation_candidate"]
        self.assertEqual(candidate["disposition"], "MERGE_INTO_EXISTING_OWNER")
        self.assertIn("chain-aware evidence edges", candidate["objective"])


if __name__ == "__main__":
    unittest.main()
