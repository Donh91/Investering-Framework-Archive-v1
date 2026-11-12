"""IC-1 native changed-test evidence, including delete and rename negatives.

A GitHub file-status receipt is still untrusted until the original S1 operator
independently re-reads the actual PR at its exact HEAD. No release authority.
"""
import hashlib
import unittest

from scripts.governance.s1_release_evidence_classifier_v1 import classify_pr_disposition, classify_pr_batch
from tests.governance.test_s1_release_evidence_classifier_v1 import decision_fixture

H = "a" * 40


def source_receipt(path, cases, head=H):
    """Exact-head source receipt for ONE changed Python test module.

    IC-1 full execution (Codex P2, review thread 4549672840): every test case
    in the changed module's source must be executed, so each fixture now states
    which cases its changed module contains. `cases` is [(class or None, name)].
    """
    by_class = {}
    for cls, name in cases:
        by_class.setdefault(cls, []).append(name)
    chunks = []
    for cls, names in by_class.items():
        if cls is None:
            chunks.extend(f"def {name}():\n    pass\n" for name in names)
        else:
            chunks.append(f"class {cls}:\n" + "".join(
                f"    def {name}(self):\n        pass\n" for name in names))
    text = "\n".join(chunks)
    data = text.encode("utf-8")
    return {"path": path, "head_sha": head, "text": text,
            "blob_sha": hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()}


def _cases_named_by(executed):
    """Pre-existing fixtures model a one-case module: the case their executed ID names
    (or `test_case` when nothing ran). Multi-case modules are covered in
    test_s1_changed_test_full_execution_v1.py."""
    cases = []
    for test_id in executed:
        parts = test_id.split("::") if "::" in test_id else test_id.split(".")
        cls = parts[-2] if len(parts) > 1 and parts[-2][:1].isupper() else None
        cases.append((cls, parts[-1]))
    return cases or [(None, "test_case")]


def make_record(changes, executed=(), cases=None):
    record = decision_fixture("LOW")
    record["changed_test_sources"] = [
        source_receipt(change["path"], cases or _cases_named_by(executed))
        for change in changes
        if change["path"].endswith(".py")
        and change["path"].rsplit("/", 1)[-1].startswith("test_")
        and change["status"] not in ("removed", "deleted")]
    record["expected_changed_paths"] = [change["path"] for change in changes]
    record["changed_file_statuses_source"] = "GITHUB_PR_FILES"
    record["changed_file_statuses_head_sha"] = H
    record["changed_file_statuses"] = changes
    record["pr_changed_files_count"] = len(changes)
    record["pr_changed_files_count_head_sha"] = H
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


    def test_g3_missing_entire_path_manifest_with_claimed_native_evidence_fails(self):
        r = make_record([row("tests/a/test_a.py")],
                        executed=["tests/a/test_a.py::test_a"])
        del r["expected_changed_paths"]
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")
        r["expected_changed_paths"] = None
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_g3_truncated_but_consistent_census_falsifies_ready(self):
        r = make_record([row("scripts/example.py")])
        r["pr_changed_files_count"] = 2  # hidden test in another PR-files page
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")
        r = make_record([row("tests/a/test_a.py")],
                        executed=["tests/a/test_a.py::test_a"])
        r["pr_changed_files_count"] = 2
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_g3_missing_or_malformed_counts_and_stale_head_fail(self):
        for bad in (None, True, -1, 0, "2", [], {}, 3001):
            with self.subTest(count=repr(bad)):
                r = make_record([row("tests/a/test_a.py")],
                                executed=["tests/a/test_a.py::test_a"])
                r["pr_changed_files_count"] = bad
                self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")
        r = make_record([row("tests/a/test_a.py")],
                        executed=["tests/a/test_a.py::test_a"])
        del r["pr_changed_files_count"]
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")
        r = make_record([row("tests/a/test_a.py")],
                        executed=["tests/a/test_a.py::test_a"])
        r["pr_changed_files_count_head_sha"] = "f" * 40
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_g1_mode_changed_status_requires_test_execution(self):
        r = make_record([row("tests/a/test_a.py", "changed")], cases=[(None, "test_a")])
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TESTS_NOT_EXECUTED")
        r["pr_jobs"][0]["executed_test_ids"] = ["tests/a/test_a.py::test_a"]
        self.result(r, "READY_TO_MERGE")
        r["changed_file_statuses"][0]["head_exists"] = False
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_g1_unchanged_is_not_valid_github_pr_status(self):
        r = make_record([row("tests/a/test_a.py", "unchanged")],
                        executed=["tests/a/test_a.py::test_a"])
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_g3_native_non_test_census_cannot_silently_drop_file(self):
        r = make_record([row("scripts/example.py")])
        self.result(r, "READY_TO_MERGE")
        r["changed_file_statuses"].clear()
        self.result(r, "CI_NOT_EXECUTED", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_f2_release_governance_paths_never_downgrade_to_low(self):
        from scripts.governance.s1_release_evidence_classifier_v1 import _release_sensitive_path
        blocked = [
            "AGENTS.md", "CLAUDE.md",
            "00_FMOS/S1_NATIVE_RULE_CENSUS_AND_RELEASE_RECIPE_V1.md",
            "00_FMOS/S1_CLOSURE_ASSURANCE_STRATEGIC_RECOVERY_V1.md",
            ".agents/skills/s1-pr-repair-learning/SKILL.md",
            "schemas/S1_CLOSURE_ASSURANCE_V1.schema.json",
            ".github/workflows/critical.yml",
            "scripts/governance/s1_release_evidence_classifier_v1.py",
        ]
        for path in blocked:
            with self.subTest(path=path):
                self.assertTrue(_release_sensitive_path(path))
        self.assertFalse(_release_sensitive_path("docs/public-typo.md"))

    def test_f2_governance_pr_marked_low_is_rejected_by_native_general_gate(self):
        from scripts.governance.s1_general_release_evidence_v1 import classify
        from tests.governance.test_s1_general_release_evidence_v1 import valid
        for path in ("00_FMOS/S1_NATIVE_RULE_CENSUS_AND_RELEASE_RECIPE_V1.md",
                     ".agents/skills/s1-pr-repair-learning/SKILL.md",
                     "schemas/S1_CLOSURE_ASSURANCE_V1.schema.json"):
            with self.subTest(path=path):
                r = make_record([row(path)])
                r["s1_general_preflight_required"] = True
                r["s1_general_preflight"] = valid()
                # source/evidence IDs must actually agree for General preflight
                r["pr_jobs"][0]["executed_test_ids"] = ["positive", "guard-removal"]
                out = classify_pr_disposition(r)
                self.assertEqual(out["disposition"], "SOURCE_OR_SCIENCE_GATE")
                self.assertEqual(out["reason"], "HIGH_IMPACT_PATH_MARKED_LOW")

    def test_docs_only_does_not_gain_new_test_requirement(self):
        r = decision_fixture("LOW")
        r["expected_changed_paths"] = ["README.md"]
        self.result(r, "READY_TO_MERGE")


if __name__ == "__main__":
    unittest.main()
