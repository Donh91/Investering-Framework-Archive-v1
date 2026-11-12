"""IC-1 native changed-test evidence, including delete and rename negatives.

A GitHub file-status receipt is still untrusted until the original S1 operator
independently re-reads the actual PR at its exact HEAD. No release authority.
"""
import unittest

from scripts.governance.s1_release_evidence_classifier_v1 import classify_pr_disposition, classify_pr_batch
from tests.governance.test_s1_release_evidence_classifier_v1 import decision_fixture

H = "a" * 40


def make_record(changes, executed=()):
    record = decision_fixture("LOW")
    record["expected_changed_paths"] = [change["path"] for change in changes]
    record["changed_file_statuses_source"] = "GITHUB_PR_FILES"
    record["changed_file_statuses_head_sha"] = H
    record["changed_file_statuses"] = changes
    record["pr_jobs"][0]["executed_test_ids"] = list(executed)
    return record


def row(path, status="modified", exists=True, previous=None):
    r = {"path": path, "status": status, "head_exists": exists}
    if previous is not None:
        r["previous_filename"] = previous
    return r


class IC1ChangedTestStatusTests(unittest.TestCase):
    def result(self, record, disposition, reason=None):
        out = classify_pr_disposition(record)
        self.assertEqual(out["disposition"], disposition)
        if reason:
            self.assertEqual(out["reason"], reason)
        self.assertFalse(out["authorized"])
        self.assertFalse(out["externally_authenticated"])
        return out

    def test_modified_test_with_generic_green_job_is_not_execution(self):
        r = make_record([row("tests/research/test_x.py")])
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TESTS_NOT_EXECUTED")

    def test_modified_test_with_native_named_test_ids_can_pass_advisory(self):
        r = make_record([row("tests/research/test_x.py")],
                        executed=["tests/research/test_x.py::Check::test_safety"])
        self.result(r, "READY_TO_MERGE")

    def test_complete_manifest_mixed_implementation_and_tests_is_accepted(self):
        r = make_record([
            row("scripts/example.py"),
            row("tests/test_example.py")
        ], executed=["tests/test_example.py::test_ok"])
        self.result(r, "READY_TO_MERGE")

    def test_complete_manifest_cannot_omit_implementation_entry(self):
        r = make_record([
            row("scripts/example.py"),
            row("tests/test_example.py")
        ], executed=["tests/test_example.py::test_ok"])
        r["changed_file_statuses"] = [row("tests/test_example.py")]
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_unittest_discovery_relative_to_native_start_directory(self):
        r = make_record([row("tests/learning/test_forecast_skill_study_v132.py")],
                        executed=["test_forecast_skill_study_v132.ForecastTests.test_ready"])
        r["pr_jobs"][0]["test_discovery_root"] = "tests/learning"
        self.result(r, "READY_TO_MERGE")

    def test_unittest_discovery_wrong_root_is_not_proof(self):
        r = make_record([row("tests/learning/test_forecast_skill_study_v132.py")],
                        executed=["test_forecast_skill_study_v132.ForecastTests.test_ready"])
        r["pr_jobs"][0]["test_discovery_root"] = "tests/other"
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TESTS_NOT_EXECUTED")

    def test_subdir_discovery_bare_unscoped_id_is_not_proof(self):
        r = make_record([row("tests/learning/test_forecast_skill_study_v132.py")],
                        executed=["test_forecast_skill_study_v132.ForecastTests.test_ready"])
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TESTS_NOT_EXECUTED")

    def test_unittest_dotted_case_is_accepted(self):
        r = make_record([row("tests/research/test_x.py")],
                        executed=["tests.research.test_x.Check.test_safety"])
        self.result(r, "READY_TO_MERGE")

    def test_partial_execution_fails(self):
        r = make_record([row("tests/a/test_a.py"), row("tests/b/test_b.py")],
                        executed=["tests/a/test_a.py::test_a"])
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TESTS_NOT_EXECUTED")

    def test_deleted_test_is_not_required_to_execute(self):
        r = make_record([row("tests/research/test_gone.py", "removed", False)])
        self.result(r, "READY_TO_MERGE")

    def test_deleted_with_false_head_existence_claim_fails(self):
        r = make_record([row("tests/research/test_gone.py", "removed", True)])
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_rename_requires_execution_of_new_destination_only(self):
        r = make_record([row("tests/research/test_new.py", "renamed", True,
                             previous="tests/research/test_old.py")],
                        executed=["tests/research/test_new.py::test_new"])
        self.result(r, "READY_TO_MERGE")

    def test_rename_old_only_is_not_execution_of_destination(self):
        r = make_record([row("tests/research/test_new.py", "renamed", True,
                             previous="tests/research/test_old.py")],
                        executed=["tests/research/test_old.py::test_old"])
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TESTS_NOT_EXECUTED")

    def test_malformed_changed_paths_fail_closed_without_crashing_other_prs(self):
        for malformed in ([], {}, ["nested"], {"path": "test_x.py"}, 7, True):
            with self.subTest(path=repr(malformed)):
                bad = make_record([row("tests/research/test_x.py")],
                                  executed=["tests/research/test_x.py::test_ok"])
                bad["expected_changed_paths"].append(malformed)
                good = make_record([row("tests/research/test_y.py")],
                                   executed=["tests/research/test_y.py::test_ok"])
                out = classify_pr_batch([bad, good])
                self.assertEqual(len(out), 2)
                self.assertEqual(out[0]["disposition"], "CI_NOT_EXECUTED")
                self.assertEqual(out[0]["reason"], "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")
                self.assertEqual(out[1]["disposition"], "READY_TO_MERGE")
                self.assertTrue(all(not x["authorized"] for x in out))

    def test_malformed_changed_path_spellings_rejected(self):
        for malformed in ("", " tests/test_x.py", "/tests/test_x.py",
                          "tests/../test_x.py"):
            with self.subTest(path=repr(malformed)):
                r = make_record([row("tests/research/test_x.py")],
                                executed=["tests/research/test_x.py::test_ok"])
                r["expected_changed_paths"].append(malformed)
                self.result(r, "CI_NOT_EXECUTED",
                            "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_malformed_json_status_type_never_crashes(self):
        for invalid in ([], {}, ["modified"], 7, True):
            with self.subTest(status=repr(invalid)):
                r = make_record([row("tests/research/test_x.py")])
                r["changed_file_statuses"][0]["status"] = invalid
                self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_malformed_previous_filename_does_not_qualify_rename(self):
        for bad in ([], {}, "tests/research/test_new.py", None):
            with self.subTest(previous=repr(bad)):
                r = make_record([row("tests/research/test_new.py", "renamed", True)])
                r["changed_file_statuses"][0]["previous_filename"] = bad
                self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_missing_native_change_status_fails_not_false_test_hold(self):
        r = make_record([row("tests/research/test_x.py")])
        del r["changed_file_statuses"]
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_manifest_head_binding_fails_closed(self):
        r = make_record([row("tests/research/test_x.py")])
        r["changed_file_statuses_head_sha"] = "f" * 40
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_manifest_cannot_silently_omit_second_changed_test(self):
        r = make_record([row("tests/a/test_a.py")],
                        executed=["tests/a/test_a.py::test_a"])
        r["expected_changed_paths"].append("tests/b/test_b.py")
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_duplicate_manifest_paths_fail_closed(self):
        r = make_record([row("tests/a/test_a.py")])
        r["changed_file_statuses"].append(row("tests/a/test_a.py"))
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_pytest_fixture_not_a_test_module(self):
        r = make_record([row("tests/conftest.py")])
        self.result(r, "READY_TO_MERGE")

    def test_docs_only_does_not_gain_new_test_requirement(self):
        r = decision_fixture("LOW")
        r["expected_changed_paths"] = ["README.md"]
        self.result(r, "READY_TO_MERGE")


if __name__ == "__main__":
    unittest.main()
