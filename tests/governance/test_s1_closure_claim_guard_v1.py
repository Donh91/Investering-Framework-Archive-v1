"""Adversarial Task 3 tests for the untrusted S1 closure claim guard."""
import copy
import unittest

from scripts.governance.s1_closure_claim_guard_v1 import S1_TASK_ID, inspect_claim


H = "a" * 40
M = "b" * 40


def complete_shape():
    return {
        "case_type": "original_merge",
        "origin": "natural_scheduled_s1",
        "task_id": S1_TASK_ID,
        "task_run_id": "task-run-native-crosscheck-pending",
        "task_started_at": "2026-11-05T21:14:41Z",
        "task_completed_at": "2026-11-05T21:15:39Z",
        "scheduled_for_utc": "2026-11-05T21:14:00Z",
        "task_provenance_source": "SELF_ATTESTED",
        "writer_lease": {"active": False, "ref": "lease-released-crosscheck-pending"},
        "merge_state_check": {"source": "GITHUB_REST", "checked_at_utc": "2026-11-05T21:14:55Z", "head_sha": H},
        "classifier": {"blob_sha": "c" * 40, "disposition": "READY_TO_MERGE", "output_sha256": "d" * 64},
        "pr": {
            "number": 1946,
            "original": True,
            "merged": True,
            "head_sha": H,
            "merge_sha": M,
            "merge_expected_head_sha": H,
            "main_blob_readback": True,
            "review_rules_checked": True,
            "merged_at": "2026-11-05T21:15:04Z",
            "merged_by": "Donh91",
        },
        "ci": {
            "event": "pull_request",
            "head_sha": H,
            "conclusion": "success",
            "executed_test_count": 18,
            "executed_test_ids": ["tests/governance/test_x.py::t%d" % i for i in range(18)],
        },
        # Untrusted shape labels must NEVER prove real native execution.
        "S1_VERIFIED": True,
        "receiver_ack": "ACCEPTED",
        "authenticated_execution": True,
        "consumer": "PROD_VERIFIED",
        "url": "https://github.com/fake/looks-valid",
    }


class TestS1ClosureClaimGuard(unittest.TestCase):
    def test_complete_shape_is_only_candidate_never_verified(self):
        out = inspect_claim(complete_shape())
        self.assertEqual(out["classification"], "NATIVE_PROVENANCE_READBACK_REQUIRED")
        self.assertTrue(out["candidate_for_native_check"])
        self.assertFalse(out["s1_own_merged_verified"])
        self.assertFalse(out["full_autonomy_verified"])
        self.assertFalse(out["prod_verified"])
        self.assertEqual(out["eligible_denominator"], "UNKNOWN")

    def test_interactive_merge_is_not_s1_credit(self):
        case = complete_shape()
        case["origin"] = "owner_interactive"
        out = inspect_claim(case)
        self.assertIn("NOT_NATURALLY_SCHEDULED_S1_ORIGIN", out["reasons"])
        self.assertFalse(out["candidate_for_native_check"])

    def test_other_task_id_fails_closed(self):
        case = complete_shape()
        case["task_id"] = "another-automation"
        self.assertIn("WRONG_OR_MISSING_EXISTING_TASK_ID", inspect_claim(case)["reasons"])

    def test_exact_head_binding_required(self):
        case = complete_shape()
        case["pr"]["merge_expected_head_sha"] = M
        self.assertIn("EXPECTED_HEAD_NOT_BOUND", inspect_claim(case)["reasons"])

    def test_skipped_or_zero_step_ci_is_rejected(self):
        for count, event in [(0, "pull_request"), (18, "workflow_dispatch")]:
            with self.subTest(count=count, event=event):
                case = complete_shape()
                case["ci"]["executed_test_count"] = count
                case["ci"]["event"] = event
                self.assertIn("EXACT_HEAD_SUBSTANTIVE_PR_CI_NOT_SUPPLIED",
                              inspect_claim(case)["reasons"])

    def test_ci_on_stale_head_rejected(self):
        case = complete_shape()
        case["ci"]["head_sha"] = M
        self.assertIn("EXACT_HEAD_SUBSTANTIVE_PR_CI_NOT_SUPPLIED",
                      inspect_claim(case)["reasons"])

    def test_merge_outside_scheduled_interval_rejected(self):
        case = complete_shape()
        case["pr"]["merged_at"] = "2026-11-05T22:15:04Z"
        self.assertIn("NATIVE_MERGE_TIME_NOT_WITHIN_SCHEDULED_RUN",
                      inspect_claim(case)["reasons"])

    def test_naive_timestamp_rejected(self):
        case = complete_shape()
        case["task_started_at"] = "2026-11-05T21:14:41"
        self.assertIn("NATIVE_MERGE_TIME_NOT_WITHIN_SCHEDULED_RUN",
                      inspect_claim(case)["reasons"])

    def test_main_readback_is_required(self):
        case = complete_shape()
        case["pr"]["main_blob_readback"] = False
        self.assertIn("MAIN_BLOB_READBACK_NOT_SUPPLIED", inspect_claim(case)["reasons"])

    def test_missing_original_pr_denies_claim(self):
        case = complete_shape()
        case["pr"]["original"] = False
        self.assertIn("ORIGINAL_MERGED_STATE_NOT_SUPPLIED", inspect_claim(case)["reasons"])

    def test_shape_only_label_never_authenticates(self):
        case = complete_shape()
        case["pr"]["merged"] = False
        case["S1_VERIFIED"] = "EXECUTED_VERIFIED"
        case["receiver_ack"] = "ACK"
        self.assertFalse(inspect_claim(case)["s1_own_merged_verified"])

    def test_research_pass_is_not_production_patch(self):
        case = {"case_type": "research_only", "receipt": "PASS",
                "verdict": "INSUFFICIENT_EVIDENCE", "patches": 0}
        result = inspect_claim(case)
        self.assertEqual(result["classification"], "ADVISORY_RESEARCH_ONLY")
        self.assertFalse(result["s1_own_merged_verified"])

    def test_legitimate_partial_and_no_case_not_fake_failure(self):
        partial = inspect_claim({"case_type": "partial_publication"})
        none = inspect_claim({"case_type": "no_eligible_case"})
        self.assertEqual(partial["classification"], "PARTIAL_PUBLICATION_NOT_COMPLETION")
        self.assertEqual(none["classification"], "NO_ELIGIBLE_CASE_OBSERVED")
        self.assertEqual(none["eligible_denominator"], "UNKNOWN")

    def test_unhashable_case_type_fails_closed_without_traceback(self):
        # Valid JSON arrays/objects must not crash the advisory claim checker.
        for malformed in ([], {}, ["original_merge"], {"kind": "original_merge"}, 1, False):
            with self.subTest(case_type=repr(malformed)):
                case = complete_shape()
                case["case_type"] = malformed
                result = inspect_claim(case)
                self.assertEqual(result["classification"], "UNSUPPORTED_S1_OWN_CLOSURE_CLAIM")
                self.assertIn("CASE_TYPE_NOT_ORIGINAL_MERGE", result["reasons"])
                self.assertFalse(result["candidate_for_native_check"])
                self.assertFalse(result["s1_own_merged_verified"])
                self.assertFalse(result["full_autonomy_verified"])
                self.assertFalse(result["prod_verified"])

    def test_extreme_timezone_conversion_fails_closed_without_traceback(self):
        # Aware ISO dates near datetime's min/max parse, but UTC offset can overflow.
        for extreme in ("0001-01-01T00:00:00+14:00",
                        "9999-12-31T23:59:59-14:00"):
            for field in ("task_started_at", "task_completed_at"):
                with self.subTest(value=extreme, field=field):
                    case = complete_shape()
                    case[field] = extreme
                    result = inspect_claim(case)
                    self.assertIn("NATIVE_MERGE_TIME_NOT_WITHIN_SCHEDULED_RUN",
                                  result["reasons"])
                    self.assertFalse(result["candidate_for_native_check"])
                    self.assertFalse(result["s1_own_merged_verified"])
                    self.assertFalse(result["full_autonomy_verified"])
                    self.assertFalse(result["prod_verified"])

    def test_no_mutation(self):
        case = complete_shape()
        original = copy.deepcopy(case)
        inspect_claim(case)
        self.assertEqual(case, original)

    def test_non_json_object_rejected(self):
        with self.assertRaises(ValueError):
            inspect_claim([])


if __name__ == "__main__":
    unittest.main()
