"""Scientific/contract checks for Task 2 eight-lane archival replay."""
import unittest
from pathlib import Path
from scripts.research import task2_rpl8_source_replay_v1 as rpl

ROOT = Path(__file__).resolve().parents[2]

class Task2RPL8ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = rpl.build(ROOT)

    def test_eight_independent_research_questions_are_reported_without_promotion(self):
        out=self.report
        self.assertEqual(out["contract"],rpl.CONTRACT)
        self.assertEqual(len(out["lanes"]),8)
        self.assertTrue(out["no_new_automation"])
        self.assertTrue(out["no_restricted_source_read"])
        self.assertTrue(out["no_market_or_model_changes"])
        self.assertTrue(out["no_new_api_calls"])
        self.assertFalse(any(out["scientific_admission"][k] for k in
                ("original_pit_verified","prospective_incremental_information_edge",
                 "after_cost_investor_edge","round3_analysis_authorized")))
        for l in out["lanes"].values():
            self.assertNotIn("COMPLETE_VERIFIED",l["state"])

    def test_c02_correct_count_includes_true_negatives_not_just_tp(self):
        original=self.report["lanes"]["L04_shared_row"]
        old=original["frozen_earlier_7d"]["C02_BREADTH"]
        new=original["frozen_later_7d"]["C02_BREADTH"]
        self.assertEqual((old["n"],old["tp"],old["tn"],old["correct_total"]),
                         (20,7,2,9))
        self.assertEqual((new["n"],new["tp"],new["tn"],new["correct_total"]),
                         (23,7,2,9))
        self.assertEqual(original["newly_matured"],3)
        self.assertEqual(new["balanced_accuracy_pct"],66.667)
        base=original["frozen_later_7d"]["B0_ALWAYS_POSITIVE"]
        self.assertEqual(base["correct_total"],21)
        self.assertEqual(base["balanced_accuracy_pct"],50)
        self.assertEqual(original["independent_28d_blocks"],1)

    def test_horizon_accuracy_not_invented_when_no_directional_forecast(self):
        h=self.report["lanes"]["L02_original_horizon"]
        self.assertEqual((h["original_issuances"],h["directional_12h"]), (70,49))
        self.assertEqual((h["directional_72h"],h["directional_168h"]), (0,0))
        self.assertEqual(h["long_horizon_hit_rate"],"UNDEFINED_NO_DIRECTIONAL_ISSUES")
        self.assertFalse(self.report["scientific_admission"]["original_pit_verified"])

    def test_censored_denominator_and_null_findings_are_preserved(self):
        a=self.report["lanes"]["L08_warning_action_delivery"]
        self.assertEqual((a["eligible_price_joined_predictions"],
                          a["registered_original_receipts"],
                          a["original_censored"],a["original_matured"],
                          a["missing_original_receipt"]), (824,814,500,314,10))
        self.assertFalse(a["user_message_delivery_proven"])
        self.assertFalse(a["after_cost_executable_action_proven"])
        d=self.report["lanes"]["L07_derivatives_18month"]
        self.assertEqual(d["pinned_source_files"],72)
        self.assertLess(d["mean_price_minus_derivatives_brier"],0)
        lo,hi=d["95pct_month_bootstrap_interval"]
        self.assertLess(lo,0)
        self.assertGreater(hi,0)

    def test_bh_descriptive_not_valid_confirmatory_inference(self):
        m=self.report["lanes"]["L03_M1_frequency_placebo"]
        self.assertGreaterEqual(m["exploratory_test_cells"],40)
        self.assertFalse(m["BH_valid_independent_eligible_hypothesis_family"])
        self.assertFalse(m["after_selection_discovery_or_edge_claim"])
        self.assertAlmostEqual(m["C2_30d_reported_exploratory_p"],.058)
        self.assertAlmostEqual(m["C_family_30d_reported_exploratory_p"],.006)
        self.assertLess(m["one_more_day_deployment_return_delta_pp"],0)

    def test_invalid_confusion_matrix_fails_closed(self):
        self.assertEqual(rpl.balanced({"tp":7,"fn":14,"tn":2,"fp":0}),66.667)
        with self.assertRaisesRegex(ValueError,"MATRIX_DENOMINATOR_MISMATCH"):
            rpl.measures({"n":21,"tp":7,"tn":2,"fp":0,"fn":14,"accuracy_pct":45})

if __name__=="__main__":
    unittest.main()
