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


class ARP02OriginalOwnerNativeCostControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from scripts.research import arp02_hre_price_control_cost_sensitivity_v1 as cost
        cls.cost = cost
        cls.observation = cost.build(ROOT)

    def test_source_pin_and_actual_original_owner(self):
        self.assertEqual(self.observation["original_owner"], "Archive#1553")
        self.assertEqual(self.observation["source_blob_sha1"],
                         "2f46169590ae208f724d783c70a545bfceb228fb")
        self.assertEqual(self.observation["market_event_families_selected_retrospectively"], 5)
        self.assertTrue(self.observation["overlapping_cutoffs_are_not_independent"])

    def test_original_hre_false_alarm_vs_missed_window_cost_arithmetic(self):
        btc = self.observation["assets"]["BTCUSDT"]
        eth = self.observation["assets"]["ETHUSDT"]
        self.assertEqual((btc["extra_false_alarms"], btc["fewer_missed_outcome_windows"]), (9, 3))
        self.assertEqual((eth["extra_false_alarms"], eth["fewer_missed_outcome_windows"]), (15, 7))
        self.assertEqual((btc["delta_equal_unit_classification_loss"],
                          eth["delta_equal_unit_classification_loss"]), (6, 8))
        self.assertEqual((btc["overlapping_daily_cutoff_count"],
                          eth["overlapping_daily_cutoff_count"]), (418, 418))

    def test_original_study_never_promotes_risk_trading_or_independence(self):
        o = self.observation
        self.assertTrue(o["unit_loss_is_not_trade_cost"])
        self.assertFalse(o["actual_issued_warning_or_delivery_proven"])
        self.assertFalse(o["economic_paper_outcome_proven"])
        self.assertFalse(o["official_threshold_or_model_change_authorized"])
        self.assertIsNone(o["number_of_independent_market_shocks_certified"])


if __name__=="__main__":
    unittest.main()
