"""P3/P4 source-bound eight-lane Wave3 no-action-claim scientific controls."""
import copy
import unittest
from pathlib import Path
from scripts.research import task2_rpl_wave3_action_value_sensitivity_v1 as r

ROOT=Path(__file__).resolve().parents[2]

class Task2Wave3ActionValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence=r.build(ROOT)

    def test_source_matured_two_negative_rows_sustain_class_imbalance(self):
        o=self.evidence["P4_eight_independent_questions"]["W3_L04_shared_row_cost_sensitivity"]
        self.assertEqual((o["source_matured_labels"],o["source_positive"],o["source_negative"]),(23,21,2))
        self.assertEqual(o["C02_correct_old"],[9,20])
        self.assertEqual(o["C02_correct_new"],[9,23])
        self.assertEqual(o["newly_matured_since_old_cutoff"],3)
        self.assertEqual(o["fixed_28_day_calendar_blocks"],1)
        self.assertIsNone(o["independent_market_shock_n"])

    def test_hypothetical_break_even_fp_cost_needs_7x_missed_positive(self):
        o=self.evidence["P4_eight_independent_questions"]["W3_L04_shared_row_cost_sensitivity"]
        self.assertEqual(o["C02_vs_always_positive_break_even_FP_to_FN_ratio_old"],5.5)
        self.assertEqual(o["C02_vs_always_positive_break_even_FP_to_FN_ratio_new"],7)
        self.assertEqual(o["C07_vs_always_positive_break_even_FP_to_FN_ratio_new"],10.5)
        self.assertFalse(o["after_cost_profit_established"])

    def test_unit_loss_c02_and_always_positive_change_rank_only_above_7x(self):
        v=self.evidence["P4_eight_independent_questions"]["W3_L04_shared_row_cost_sensitivity"]["candidate_loss_table"]
        self.assertEqual(v["C02_BREADTH"]["unit_loss_if_fp_equals_fn"],14)
        self.assertEqual(v["B0_ALWAYS_POSITIVE"]["unit_loss_if_fp_equals_fn"],2)
        self.assertEqual(v["C02_BREADTH"]["unit_loss_if_fp_5x_fn"],14)
        self.assertEqual(v["B0_ALWAYS_POSITIVE"]["unit_loss_if_fp_5x_fn"],10)
        self.assertEqual(v["C02_BREADTH"]["unit_loss_if_fp_8x_fn"],14)
        self.assertEqual(v["B0_ALWAYS_POSITIVE"]["unit_loss_if_fp_8x_fn"],16)
        self.assertEqual(v["C07_SIMPLE_3"]["unit_loss_if_fp_8x_fn"],21)

    def test_wrong_or_incomplete_confusion_matrix_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"MATRIX_DENOMINATOR_CHANGED"):
            r.errors({"n":6,"tp":1,"tn":1,"fp":1,"fn":2})
        with self.assertRaisesRegex(ValueError,"INVALID_HYPOTHETICAL_LOSS"):
            r.errors({"n":4,"tp":1,"tn":1,"fp":1,"fn":1},fp_loss=-1)
        with self.assertRaisesRegex(ValueError,"UNMATCHED_ALWAYS_POSITIVE_BASELINE"):
            r.fp_to_fn_break_even({"n":3,"tp":0,"tn":0,"fp":0,"fn":3},
                                  {"n":3,"tp":3,"tn":0,"fp":0,"fn":0})

    def test_original_latency_sign_flips_by_strategy_not_universal_rule(self):
        p=self.evidence["P3_latency_strategies"]
        a=p["historical_derived_scenarios"]
        self.assertAlmostEqual(a["DEPLOYMENT_EXPANDING"]["extra_day_return_change_pp"],-22.522831)
        self.assertAlmostEqual(a["JOINT_TRANSMISSION"]["extra_day_return_change_pp"],8.353662)
        self.assertTrue(p["different_strategies_show_opposite_one_day_delay_effect"])
        self.assertFalse(p["tested_against_executable_after_cost_HOLD"])

    def test_no_user_delivery_and_no_no_warning_denominator_stays_unknown(self):
        p=self.evidence["P3_action_eligibility"]
        self.assertEqual(p["original_11_R1_issuances"],11)
        self.assertEqual(p["R1_original_user_deliveries_authenticated"],0)
        self.assertEqual(p["original_824_price_joined"],824)
        self.assertEqual(p["original_814_outcome_receipts"],814)
        self.assertEqual(p["M1_C2_original_false_alarm_dates"],2)
        self.assertEqual(p["M1_C2_original_signal_dates"],14)
        self.assertIsNone(p["M1_C2_population_false_positive_rate"])
        self.assertFalse(p["matched_HOLD_after_cost_utility_scored"])

    def test_eight_distinct_lanes_preserve_original_owner_and_no_promotion(self):
        v=self.evidence
        self.assertEqual(v["original_owner_issue"],1596)
        self.assertEqual(len(v["P4_eight_independent_questions"]),8)
        self.assertEqual(v["scientific_verdict"],"NO_NEW_PROVEN_INCREMENTAL_OR_AFTER_COST_EDGE")
        self.assertTrue(v["research_only"])
        self.assertFalse(v["round3_private_values_used"])
        self.assertFalse(v["model_promotion_authorized"])
        self.assertFalse(v["portfolio_execution_authorized"])
        self.assertFalse(v["forecast_reissued"])

    def test_private_source_provenance_not_mixed_with_public_models(self):
        ids=self.evidence["original_public_source_blob_ids"]
        self.assertRegex(ids["original_r1"],r"^[0-9a-f]{40}$")
        self.assertRegex(ids["shared_outcomes"],r"^[0-9a-f]{40}$")
        self.assertEqual(ids["M4_original_latency_csv"],r.LATENCY_BLOB)
        self.assertNotIn("Donh91/secrets",str(ids))

if __name__=="__main__":
    unittest.main()
