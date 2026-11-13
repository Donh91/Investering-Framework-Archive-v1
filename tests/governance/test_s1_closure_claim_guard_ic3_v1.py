"""IC-3 proposal tests: receipt fields required for a joinable, replayable S1 closure claim."""
import copy
import unittest

from scripts.governance.s1_closure_claim_guard_v1 import inspect_claim
from tests.governance.test_s1_closure_claim_guard_v1 import complete_shape


class TestIC3ReceiptFields(unittest.TestCase):
    def test_complete_v2_shape_is_still_only_candidate(self):
        out = inspect_claim(complete_shape())
        self.assertTrue(out["candidate_for_native_check"])
        self.assertFalse(out["s1_own_merged_verified"])
        self.assertTrue(out["native_verification_required"])

    def test_each_missing_field_demotes(self):
        cases = {
            "MISSING_SCHEDULED_FOR_UTC": lambda c: c.pop("scheduled_for_utc"),
            "TASK_PROVENANCE_SOURCE_NOT_DECLARED": lambda c: c.pop("task_provenance_source"),
            "WRITER_LEASE_STATE_NOT_SUPPLIED": lambda c: c["writer_lease"].update(active=None),
            "MERGE_STATE_SOURCE_NOT_BOUND": lambda c: c["merge_state_check"].update(source="CONNECTOR"),
            "CLASSIFIER_IO_NOT_BOUND": lambda c: c["classifier"].update(output_sha256="x"),
            "EXECUTED_TEST_IDS_NOT_SUPPLIED": lambda c: c["ci"].update(executed_test_ids=[]),
            "MERGE_ACTOR_NOT_SUPPLIED": lambda c: c["pr"].pop("merged_by"),
        }
        for reason, mutate in cases.items():
            with self.subTest(reason=reason):
                case = copy.deepcopy(complete_shape())
                mutate(case)
                out = inspect_claim(case)
                self.assertIn(reason, out["reasons"])
                self.assertFalse(out["candidate_for_native_check"])

    def test_merge_state_check_bound_to_other_head_fails(self):
        case = complete_shape()
        case["merge_state_check"]["head_sha"] = "e" * 40
        self.assertIn("MERGE_STATE_SOURCE_NOT_BOUND", inspect_claim(case)["reasons"])

    def test_started_before_schedule_fails(self):
        case = complete_shape()
        case["scheduled_for_utc"] = "2026-11-05T22:00:00Z"
        self.assertIn("TASK_STARTED_BEFORE_SCHEDULE", inspect_claim(case)["reasons"])

    def test_duplicate_test_ids_fail(self):
        case = complete_shape()
        case["ci"]["executed_test_ids"] = ["a", "a"]
        self.assertIn("EXECUTED_TEST_IDS_NOT_SUPPLIED", inspect_claim(case)["reasons"])

    def test_non_string_source_labels_are_rejected_not_crashes(self):
        for label in ([], {}, ["AUTOMATIONS_RUN_DETAILS"], {"x": True}, 42):
            for field, reason in (("task_provenance_source", "TASK_PROVENANCE_SOURCE_NOT_DECLARED"),
                                  ("merge_state_check", "MERGE_STATE_SOURCE_NOT_BOUND")):
                with self.subTest(label=repr(label), field=field):
                    case = complete_shape()
                    if field == "task_provenance_source":
                        case[field] = label
                    else:
                        case[field]["source"] = label
                    out = inspect_claim(case)
                    self.assertIn(reason, out["reasons"])
                    self.assertFalse(out["candidate_for_native_check"])
                    self.assertFalse(out["s1_own_merged_verified"])

    def test_executed_test_id_census_matches_native_count(self):
        for count, ids in (
            (18, ["only-one-test"]),
            (1, [f"test_{i}" for i in range(18)]),
            (19, [f"test_{i}" for i in range(18)]),
            (0, [f"test_{i}" for i in range(18)]),
            (True, [f"test_{i}" for i in range(18)]),
        ):
            with self.subTest(count=count, id_count=len(ids)):
                case = complete_shape()
                case["ci"]["executed_test_count"] = count
                case["ci"]["executed_test_ids"] = ids
                out = inspect_claim(case)
                self.assertIn("EXECUTED_TEST_IDS_COUNT_MISMATCH", out["reasons"])
                self.assertFalse(out["candidate_for_native_check"])
                self.assertFalse(out["s1_own_merged_verified"])

    def test_complete_test_id_census_is_only_candidate(self):
        case = complete_shape()
        out = inspect_claim(case)
        self.assertNotIn("EXECUTED_TEST_IDS_COUNT_MISMATCH", out["reasons"])
        self.assertTrue(out["candidate_for_native_check"])
        self.assertFalse(out["s1_own_merged_verified"])

    def test_self_attested_provenance_never_verifies(self):
        out = inspect_claim(complete_shape())
        self.assertEqual(out["classification"], "NATIVE_PROVENANCE_READBACK_REQUIRED")
        self.assertFalse(out["full_autonomy_verified"])


if __name__ == "__main__":
    unittest.main()
