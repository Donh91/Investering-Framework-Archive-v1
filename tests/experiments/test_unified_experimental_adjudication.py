import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "scripts" / "experiments"))
import unified_experimental_adjudication as adjudication


class UnifiedExperimentalAdjudicationTest(unittest.TestCase):
    def test_supported_candidate_routes_to_incremental_value_review_without_promotion(self):
        lifecycle = {
            "contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1",
            "candidates": [{"candidate_id": "EC-1", "title": "candidate", "kind": "SENSOR_COMBINATION", "state": "MATURED_SUPPORTED", "matured_outcome_count": 5, "scientific_score_eligible_outcome_count": 5, "replication_receipts": ["REPLICATED_FIRED"]}],
        }
        admissions = {"contract": "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1", "candidates": [{"candidate_id": "EC-1", "status": "QUALIFIED_FOR_FORWARD_TEST"}]}
        out = adjudication.build(lifecycle, admissions, {}, {}, "2026-08-24T07:05:00Z")
        self.assertFalse(out["canonical_effect"])
        self.assertFalse(out["portfolio_execution"])
        self.assertEqual(out["candidate_actions"][0]["selected_action"], "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW")

    def test_false_maturity_never_gives_support(self):
        row = {"candidate_id": "CENSORED", "state": "MATURED_SUPPORTED",
               "matured_outcome_count": 25, "scientific_score_eligible_outcome_count": 0}
        got = adjudication.candidate_action(row, {"status": "QUALIFIED_FOR_FORWARD_TEST"})
        self.assertEqual(got["selected_action"], "WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE")
        self.assertEqual(got["matured_outcome_count"], 25)
        self.assertEqual(got["scientific_score_eligible_outcome_count"], 0)

    def test_bad_eligible_counter_fails_closed(self):
        for bad in (None, "25", True, -1, 26):
            row = {"candidate_id": "BAD", "state": "MATURED_SUPPORTED",
                   "matured_outcome_count": 25, "scientific_score_eligible_outcome_count": bad}
            self.assertEqual(adjudication.candidate_action(row, None)["scientific_score_eligible_outcome_count"], 0)

    def test_duplicate_is_archived_without_new_execution_authority(self):
        lifecycle = {"contract": "EXPERIMENT_LIFECYCLE_REGISTRY_v1", "candidates": [{"candidate_id": "EC-2", "title": "duplicate", "kind": "SENSOR_COMBINATION", "state": "INCUBATING"}]}
        admissions = {"contract": "EXPERIMENT_SCIENTIFIC_ADMISSION_REGISTRY_v1", "candidates": [{"candidate_id": "EC-2", "status": "SEMANTIC_DUPLICATE_KEEP_SHADOW"}]}
        out = adjudication.build(lifecycle, admissions, {}, {}, "2026-08-24T07:05:00Z")
        self.assertEqual(out["candidate_actions"][0]["selected_action"], "ARCHIVE_ONLY_DUPLICATE")
        self.assertEqual(out["summary"]["escalation_review_count"], 0)


if __name__ == "__main__":
    unittest.main()
