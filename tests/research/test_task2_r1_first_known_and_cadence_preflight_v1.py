"""Task 2 original first-issuance clock and private schedule metadata fail-closed tests."""
from __future__ import annotations
import copy
import unittest
from pathlib import Path
from scripts.research import task2_r1_first_known_and_cadence_preflight_v1 as source

ROOT=Path(__file__).resolve().parents[2]

class FirstKnownR1AndCadenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output=source.build(ROOT)

    def test_original_11_issued_first_case_selected_without_outcome_filter(self):
        r=self.output["first_issue_preflight"]
        self.assertEqual(r["original_attempts"],11)
        self.assertEqual(r["first_case_preselected_by_issue_clock_only"]["original_forecast_id"],
                         "CMP-20261012-904299b09eca")
        self.assertEqual(r["first_case_preselected_by_issue_clock_only"]["issued_utc"],
                         "2026-10-12T19:59:38Z")
        self.assertEqual(r["first_case_preselected_by_issue_clock_only"]["feature_fields_without_vendor_first_publication"],24)
        self.assertGreater(r["first_case_preselected_by_issue_clock_only"]["issue_minus_packet_commit_seconds"],0)
        self.assertEqual(len(r["original_11_case_clock_ledger"]),11)
        self.assertEqual(r["vendor_first_publication_authenticated_count"],0)

    def test_direct_sign_input_denominator_not_all_evidence_features(self):
        r=self.output["first_issue_preflight"]
        self.assertEqual(r["source_field_instances"],264)
        self.assertEqual(r["original_direction_delta_field_instances"],22)
        self.assertEqual(r["original_non_direct_sign_evidence_index_instances"],198)
        self.assertEqual(r["clock_counts"]["SETTLEMENT_IS_NOT_QUOTE_OBSERVATION"],22)
        self.assertEqual(r["user_delivery_known_count"],0)
        self.assertEqual(r["full_original_R1_PIT_admitted"],0)

    def test_missing_original_outcomes_remain_missing_no_after_cost_claim(self):
        o=self.output
        self.assertEqual(o["original_outcome_receipts"],{
            "retrospective_price_joined":824,"original_matured":314,
            "original_censored":500,"original_receipt_missing":10})
        self.assertFalse(o["prospective_frozen_new_cohort_registered"])
        self.assertFalse(o["economic_signal_or_trading_authority"])
        self.assertFalse(o["private_values_processed"])

    def test_actual_private_schedule_is_not_frozen_full_rate(self):
        d=self.output["private_round3_schedule_metadata"]
        self.assertEqual(d["combined_scheduled_runs_daily"],6)
        self.assertEqual(d["combined_nominal_target_runs_daily"],144)
        self.assertEqual(d["additional_scheduled_runs_per_30d_if_naively_restored"],4140)
        self.assertEqual(d["source_contracts"]["SC03_OKX_ETH_REALIZED_FUNDING_V1"]["nominal_target_runs_per_day"],96)
        self.assertIsNone(d["estimated_actions_minutes_from_schedule_alone"])
        self.assertFalse(d["round3_outcome_scoring_allowed"])
        self.assertFalse(d["restoring_nominal_cadence_approved_without_budget_measurement"])

    def test_no_silently_marked_legal_source_on_publication_gap(self):
        original=source.bound_json(ROOT,source.SOURCE_PATH)
        unverified=copy.deepcopy(original)
        chosen=unverified["rows"][0]["selected_feature_clocks"][0]
        chosen["declared_retrieved_at"]="2026-12-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError,"RETRIEVAL_AFTER_ORIGINAL_ISSUE"):
            source.source_matrix(unverified)

    def test_future_source_packet_fail_closed(self):
        original=source.bound_json(ROOT,source.SOURCE_PATH)
        modified=copy.deepcopy(original)
        modified["rows"][0]["source_packet"]["first_git_commit_at_utc"]="2026-12-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_SOURCE_PUBLISHED_AFTER_ISSUE"):
            source.source_matrix(modified)

    def test_duplicate_and_missing_feature_fail_closed(self):
        original=source.bound_json(ROOT,source.SOURCE_PATH)
        modified=copy.deepcopy(original)
        modified["rows"][0]["selected_feature_clocks"][0]["feature_id"]="btc_funding"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_FEATURE_ROSTER_DRIFT"):
            source.source_matrix(modified)

    def test_published_vendor_clock_stays_unverified_even_if_retroactively_filled(self):
        original=source.bound_json(ROOT,source.SOURCE_PATH)
        modified=copy.deepcopy(original)
        modified["rows"][0]["selected_feature_clocks"][0]["vendor_first_publication_at"]="2026-10-12T00:00:00Z"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_SOURCE_ROLE_OR_DELIVERY_DRIFT"):
            source.source_matrix(modified)

if __name__=="__main__":
    unittest.main()
