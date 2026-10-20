"""Negative controls for Task2 exploratory data availability (not performance)."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.research.task2_existing_data_coverage import (
    DEFAULT_SOURCE, audit, git_blob_sha,
)

EXPECTED_SOURCE_BLOB = "9e728b835de294e5777222c171a89874a69dae95"


class ExistingDataCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = Path(DEFAULT_SOURCE).read_bytes()
        cls.source = json.loads(cls.raw)

    def test_exact_original_frozen_blob_identity(self):
        self.assertEqual(git_blob_sha(self.raw), EXPECTED_SOURCE_BLOB)

    def test_all_11_attempts_and_all_264_features_are_kept(self):
        result = audit(self.source, EXPECTED_SOURCE_BLOB)
        self.assertEqual(result["original_forecast_attempts"], 11)
        self.assertEqual(result["feature_observations"], 264)
        self.assertEqual(result["unique_feature_ids"], 24)
        self.assertEqual(result["original_12h_outcomes_at_pinned_snapshot"],
                         {"PRESENT": 9, "ABSENT_AT_ORIGINAL_SNAPSHOT": 2})
        self.assertEqual(result["explicit_local_retrieval_clocks"], 99)
        self.assertEqual(result["raw_capture_dependency_groups"], 7)
        self.assertEqual(result["source_packet_dependency_groups"], 10)

    def test_no_prediction_skill_or_after_cost_claim_can_leak(self):
        result = audit(self.source, EXPECTED_SOURCE_BLOB)
        self.assertEqual(result["status"], "EXPLORATORY_RESEARCH_ONLY_NOT_AN_EDGE_ESTIMATE")
        self.assertEqual(result["original_user_delivery_clocks"], 0)
        self.assertEqual(result["certified_independent_event_family_assignments"], 0)
        self.assertEqual(result["scientifically_admitted_forecasts"], 0)
        self.assertFalse(result["release"]["R2_certified"])
        self.assertFalse(result["release"]["portfolio_action"])
        self.assertEqual(result["unanswered_value_question"],
                         "NO_FEATURE_FAMILY_LIFT_MEASURED")
        exported = json.dumps(result)
        self.assertNotIn("original_direction_result_only_not_admitted", exported)
        self.assertNotIn("source_features", exported)

    def test_source_attempt_deletion_is_not_silent(self):
        tampered = copy.deepcopy(self.source)
        tampered["rows"].pop()
        with self.assertRaisesRegex(ValueError, "ORIGINAL_ATTEMPT_DENOMINATOR_CONFLICT"):
            audit(tampered, EXPECTED_SOURCE_BLOB)

    def test_missing_outcome_must_stay_in_original_denominator(self):
        tampered = copy.deepcopy(self.source)
        row = next(x for x in tampered["rows"]
                   if x["original_outcome_status"] == "ABSENT_AT_ORIGINAL_SNAPSHOT")
        row["original_outcome_status"] = "PRESENT"
        with self.assertRaisesRegex(ValueError, "ORIGINAL_COHORT_DENOMINATOR_CHANGED"):
            audit(tampered, EXPECTED_SOURCE_BLOB)

    def test_duplicate_forecast_id_rejected(self):
        tampered = copy.deepcopy(self.source)
        tampered["rows"][1]["forecast_id"] = tampered["rows"][0]["forecast_id"]
        with self.assertRaisesRegex(ValueError, "ORIGINAL_FORECAST_ID_DUPLICATE"):
            audit(tampered, EXPECTED_SOURCE_BLOB)

    def test_after_issue_feature_retrieval_rejected(self):
        tampered = copy.deepcopy(self.source)
        row = tampered["rows"][0]
        feature = next(f for f in row["selected_feature_clocks"]
                       if f["declared_retrieved_at"] is not None)
        feature["declared_retrieved_at"] = "2099-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "FEATURE_RETRIEVAL_AFTER_ORIGINAL_ISSUE"):
            audit(tampered, EXPECTED_SOURCE_BLOB)

    def test_future_publication_cannot_be_promoted_from_reconstruction(self):
        tampered = copy.deepcopy(self.source)
        tampered["rows"][0]["selected_feature_clocks"][0][
            "vendor_first_publication_at"] = "2026-10-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_VENDOR_CLOCK_CANNOT_BE_PROMOTED"):
            audit(tampered, EXPECTED_SOURCE_BLOB)

    def test_feature_clock_missing_and_wrong_settlement_semantics_rejected(self):
        tampered = copy.deepcopy(self.source)
        feature = next(f for f in tampered["rows"][0]["selected_feature_clocks"]
                       if f["observation_clock_status"].startswith("ARCHIVE_CLOCK_PREISSUE"))
        feature["declared_retrieved_at"] = None
        with self.assertRaisesRegex(ValueError, "RETRIEVAL_CLOCK_MISSING_DESPITE_LABEL"):
            audit(tampered, EXPECTED_SOURCE_BLOB)
        tampered = copy.deepcopy(self.source)
        funding = next(f for f in tampered["rows"][0]["selected_feature_clocks"]
                       if f["feature_id"] == "btc_funding")
        funding["declared_retrieved_at"] = "2026-10-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "FEATURE_RETRIEVAL_SEMANTICS_CONFLICT"):
            audit(tampered, EXPECTED_SOURCE_BLOB)

    def test_all_feature_families_cover_same_attempt_universe(self):
        result = audit(self.source, EXPECTED_SOURCE_BLOB)
        self.assertTrue(all(g["feature_observations"] ==
                            len(g["feature_ids"]) * 11 for g in result["families"]))
        self.assertTrue(all(g["information_lift_vs_matched_price_only"] is None
                            for g in result["families"]))


if __name__ == "__main__":
    unittest.main()
