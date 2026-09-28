import unittest

from scripts.experiments.build_experiment_yield_shadow import build_shadow


class ExperimentYieldShadowTests(unittest.TestCase):
    def test_shadow_classifies_without_production_authority(self):
        registry = {"rows": [
            {"experiment_id": "blocked", "state": "WAITING_FOR_DATA"},
            {"experiment_id": "dup", "state": "PROPOSED", "duplicate_of": "x"},
            {"experiment_id": "quiet", "state": "MATURED_INCONCLUSIVE", "observation_count": 0},
            {"experiment_id": "base", "state": "MATURED_SUPPORTED"},
        ]}
        result = build_shadow(registry, {"rows": []})
        rows = {r["experiment_id"]: r for r in result["rows"]}
        self.assertEqual(rows["blocked"]["shadow_state"], "OBSERVE")
        self.assertEqual(rows["dup"]["shadow_state"], "OBSERVE")
        self.assertEqual(rows["quiet"]["shadow_state"], "OBSERVE")
        self.assertEqual(rows["base"]["shadow_state"], "SHADOW_BASELINE")
        self.assertEqual(result["mode"], "SHADOW_OBSERVE_ONLY")
        self.assertTrue(result["promotion_policy"]["natural_observation_window_required"])
        self.assertFalse(result["promotion_policy"]["automatic_retirement_allowed"])
        self.assertFalse(result["authority"]["production_suppression"])

    def test_current_registry_candidates_are_not_silently_dropped(self):
        registry = {
            "candidate_count": 4,
            "duplicate_candidate_file_count": 3,
            "candidates": [
                {
                    "candidate_id": "EC-1",
                    "state": "INCUBATING",
                    "observation_count": 10,
                    "matured_outcome_count": 0,
                    "created_at_utc": "2026-09-01T00:00:00Z",
                },
                {
                    "candidate_id": "EC-2",
                    "state": "WAITING_FOR_MAPPING",
                    "observation_count": 1,
                    "matured_outcome_count": 0,
                    "created_at_utc": "2026-09-02T00:00:00Z",
                },
                {
                    "candidate_id": "EC-3",
                    "state": "MATURED_SUPPORTED",
                    "observation_count": 12,
                    "matured_outcome_count": 4,
                    "created_at_utc": "2026-09-03T00:00:00Z",
                },
                {
                    "candidate_id": "EC-4",
                    "state": "MATURED_INCONCLUSIVE",
                    "observation_count": 0,
                    "matured_outcome_count": 1,
                    "created_at_utc": "2026-09-04T00:00:00Z",
                },
            ],
        }
        result = build_shadow(registry, {"rows": []})
        self.assertEqual(result["summary"]["row_count"], 4)
        self.assertEqual(result["summary"]["registry_consistency"], "PASS")
        self.assertEqual(
            result["summary"]["state_counts"],
            {
                "INCUBATING": 1,
                "MATURED_INCONCLUSIVE": 1,
                "MATURED_SUPPORTED": 1,
                "WAITING_FOR_MAPPING": 1,
            },
        )
        self.assertEqual(result["summary"]["incubating_count"], 1)
        self.assertEqual(result["summary"]["waiting_count"], 1)
        self.assertEqual(result["summary"]["matured_count"], 2)
        self.assertEqual(result["summary"]["zero_observation_count"], 1)
        self.assertEqual(result["summary"]["with_matured_outcomes_count"], 2)
        self.assertEqual(result["summary"]["incubating_zero_matured_outcome_count"], 1)
        self.assertEqual(result["summary"]["duplicate_candidate_file_count"], 3)
        self.assertEqual(result["summary"]["oldest_candidate_created_at_utc"], "2026-09-01T00:00:00Z")
        self.assertEqual(result["summary"]["newest_candidate_created_at_utc"], "2026-09-04T00:00:00Z")
        self.assertFalse(result["research_debt_semantics"]["candidate_state_change"])
        self.assertFalse(result["research_debt_semantics"]["automatic_retirement"])

    def test_malformed_canonical_candidate_breaks_consistency_instead_of_being_silently_skipped(self):
        result = build_shadow(
            {
                "candidate_count": 2,
                "candidates": [
                    {"candidate_id": "EC-1", "state": "INCUBATING"},
                    None,
                ],
            },
            {"rows": []},
        )
        self.assertEqual(result["summary"]["row_count"], 1)
        self.assertEqual(result["summary"]["registry_raw_row_count"], 2)
        self.assertEqual(result["summary"]["registry_malformed_row_count"], 1)
        self.assertEqual(result["summary"]["registry_consistency"], "UNVERIFIED_OR_MISMATCH")

    def test_empty_canonical_candidates_do_not_fall_through_to_legacy_rows(self):
        result = build_shadow(
            {
                "candidate_count": 0,
                "candidates": [],
                "rows": [{"experiment_id": "LEGACY", "state": "MATURED_SUPPORTED"}],
            },
            {"rows": []},
        )
        self.assertEqual(result["summary"]["registry_source_field"], "candidates")
        self.assertEqual(result["summary"]["registry_raw_row_count"], 0)
        self.assertEqual(result["summary"]["row_count"], 0)
        self.assertEqual(result["summary"]["registry_consistency"], "PASS")

    def test_candidate_observability_never_changes_state_or_suppresses_production(self):
        candidate = {
            "candidate_id": "EC-wait",
            "state": "WAITING_FOR_DATA",
            "observation_count": 2,
            "matured_outcome_count": 0,
            "created_at_utc": "2026-09-01T00:00:00Z",
        }
        result = build_shadow({"candidate_count": 1, "candidates": [candidate]}, {"rows": []})
        row = result["rows"][0]
        self.assertEqual(row["experiment_id"], "EC-wait")
        self.assertEqual(row["shadow_state"], "OBSERVE")
        self.assertIn("BLOCKED_OR_WAITING", row["reasons"])
        self.assertFalse(row["production_suppression"])
        self.assertEqual(candidate["state"], "WAITING_FOR_DATA")
        self.assertFalse(result["promotion_policy"]["automatic_retirement_allowed"])
        self.assertFalse(result["promotion_policy"]["automatic_suppression_allowed"])

    def test_registry_count_mismatch_is_visible_not_repaired(self):
        result = build_shadow(
            {
                "candidate_count": 99,
                "candidates": [
                    {
                        "candidate_id": "EC-1",
                        "state": "INCUBATING",
                        "observation_count": 1,
                        "matured_outcome_count": 0,
                    }
                ],
            },
            {"rows": []},
        )
        self.assertEqual(result["summary"]["row_count"], 1)
        self.assertEqual(result["summary"]["registry_declared_candidate_count"], 99)
        self.assertEqual(result["summary"]["registry_consistency"], "UNVERIFIED_OR_MISMATCH")


if __name__ == "__main__":
    unittest.main()
