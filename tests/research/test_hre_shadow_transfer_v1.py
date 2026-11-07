"""HRE learned-hypothesis transfer remains research-only and original-owner-bound."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/"research/historical_reality_engine/SHADOW_LEARNING_TRANSFER_CANDIDATES_v1.json"
SOL=ROOT/"research/historical_reality_engine/SOL_MAX_FINITE_RESEARCH_DELEGATION_FEASIBILITY_v1.md"

class ShadowTransferRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(FILE.read_text())
        cls.sol=SOL.read_text()

    def test_no_market_authority(self):
        self.assertEqual(self.d["contract"],"HRE_SHADOW_LEARNING_TRANSFER_CANDIDATES_V1")
        self.assertEqual(self.d["active_live_hypothesis_count"],0)
        self.assertIn("NO_MARKET_MODEL_PORTFOLIO_WRITES",self.d["authority"])
        self.assertIn("OFF",self.d["current_round3_boundary"])

    def test_original_owner_and_reproducible_falsification(self):
        ids=[h["id"] for h in self.d["hypotheses"]]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertGreaterEqual(len(ids),3)
        for h in self.d["hypotheses"]:
            for field in ("original_owner_issue","baseline","challenger","primary_endpoint",
                          "negative_controls","holdout","promotion","scientific_status","next"):
                self.assertTrue(h[field],f"{h['id']}: {field}")
            self.assertIn("#",h["original_owner_issue"])
            self.assertFalse(h["status"].startswith("PRODUCTION_"))

    def test_no_already_credible_alpha_or_scored_2020_original(self):
        for h in self.d["hypotheses"]:
            self.assertNotEqual(h["scientific_status"],"PROVEN_MARKET_EDGE")
            self.assertNotEqual(h["status"],"ORIGINAL_ISSUED_2020")

    def test_financial_delegation_not_enabled(self):
        self.assertIn("NOT_DEPLOYED",self.sol)
        for token in ("#1476","USD3","USD40","USD4","one active","no paid POST retry", "Option C (reject)"):
            self.assertIn(token.lower(),self.sol.lower())

    def test_only_existing_owners(self):
        self.assertIn("1596",self.d["source_owner"])
        self.assertTrue(all(h["source_evidence"].startswith("research/historical_reality_engine/") for h in self.d["hypotheses"]))

if __name__=="__main__":
    unittest.main()
