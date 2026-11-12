"""IC-1 full changed-test execution: one executed ID never credits a whole changed module.

Codex P2 on original #2088 (review thread 4549672840): `_changed_test_execution_issue`
accepted any single executed test ID with a matching module prefix as proof for every
test in a changed test file. These cases require every test case derived from the
changed file's exact-head source to be executed. Advisory only, no release authority:
the source text, blob sha and executed IDs are caller-supplied and must be read natively by S1.
"""
import hashlib
import unittest
from pathlib import Path

from scripts.governance.s1_release_evidence_classifier_v1 import classify_pr_disposition, classify_pr_batch
from tests.governance.test_s1_release_evidence_classifier_v1 import decision_fixture

H = "a" * 40
MOD = "tests/research/test_release_guard_example.py"
DOTTED = "tests.research.test_release_guard_example"
CLS = "ReleaseGuardTests"
NAMES = (
    "test_f2_release_governance_paths_never_downgrade_to_low",
    "test_g3_truncated_but_consistent_census_falsifies_ready",
    "test_docs_only_does_not_gain_new_test_requirement",
)
SOURCE = (
    "import unittest\n\n\n"
    f"class {CLS}(unittest.TestCase):\n"
    + "".join(f"    def {n}(self):\n        self.assertTrue(True)\n\n" for n in NAMES)
)
REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_TEST = "tests/governance/test_s1_changed_test_execution_ic1_v1.py"
REAL_IMPL = "scripts/governance/s1_release_evidence_classifier_v1.py"


def blob_sha(text):
    data = text.encode("utf-8")
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def source(path, text, head=H):
    return {"path": path, "head_sha": head, "blob_sha": blob_sha(text), "text": text}


def row(path, status="modified", exists=True, previous=None):
    r = {"path": path, "status": status, "head_exists": exists}
    if previous is not None:
        r["previous_filename"] = previous
    return r


def make_record(changes, executed=(), sources=()):
    record = decision_fixture("LOW")
    record["expected_changed_paths"] = [change["path"] for change in changes]
    record["changed_file_statuses_source"] = "GITHUB_PR_FILES"
    record["changed_file_statuses_head_sha"] = H
    record["changed_file_statuses"] = changes
    record["pr_changed_files_count"] = len(changes)
    record["pr_changed_files_count_head_sha"] = H
    record["pr_jobs"][0]["executed_test_ids"] = list(executed)
    if sources is not None:
        record["changed_test_sources"] = list(sources)
    return record


def py_id(name, cls=CLS, path=MOD):
    return f"{path}::{cls}::{name}" if cls else f"{path}::{name}"


def ut_id(name, cls=CLS, dotted=DOTTED):
    return f"{dotted}.{cls}.{name}"


class FullChangedTestExecutionTests(unittest.TestCase):
    def result(self, record, disposition, reason=None):
        out = classify_pr_disposition(record)
        self.assertEqual(out["disposition"], disposition, out["reason"])
        if reason:
            self.assertEqual(out["reason"], reason)
        self.assertFalse(out["authorized"])
        self.assertFalse(out["externally_authenticated"])
        return out

    def blocked(self, record, reason="CHANGED_TESTS_NOT_EXECUTED"):
        return self.result(record, "CI_NOT_EXECUTED", reason)

    # --- the 1-of-3 falsifier -------------------------------------------------
    def test_one_of_three_pytest_id_does_not_credit_module(self):
        self.blocked(make_record([row(MOD)], [py_id(NAMES[2])], [source(MOD, SOURCE)]))

    def test_one_of_three_unittest_id_does_not_credit_module(self):
        self.blocked(make_record([row(MOD)], [ut_id(NAMES[2])], [source(MOD, SOURCE)]))

    def test_two_of_three_does_not_credit_module(self):
        self.blocked(make_record([row(MOD)], [py_id(NAMES[0]), py_id(NAMES[2])],
                                 [source(MOD, SOURCE)]))

    def test_each_single_missing_case_blocks(self):
        for missing in NAMES:
            with self.subTest(missing=missing):
                ids = [py_id(n) for n in NAMES if n != missing]
                self.blocked(make_record([row(MOD)], ids, [source(MOD, SOURCE)]))

    def test_codex_repro_own_two_file_manifest_one_executed_id(self):
        text = (REPO_ROOT / REAL_TEST).read_text(encoding="utf-8")
        r = make_record(
            [row(REAL_IMPL), row(REAL_TEST, "added")],
            [f"{REAL_TEST}::IC1ChangedTestStatusTests::test_docs_only_does_not_gain_new_test_requirement"],
            [source(REAL_TEST, text)])
        # Fable R4 B1: #2088's own files are governance paths, so a LOW label is refused first.
        self.result(r, "SOURCE_OR_SCIENCE_GATE", "HIGH_IMPACT_PATH_MARKED_LOW")
        # The IC-1 property itself, on the same source under paths that are not governance.
        impl, test = "scripts/research/relocated_impl.py", "tests/research/test_relocated_ic1.py"
        r = make_record(
            [row(impl), row(test, "added")],
            [f"{test}::IC1ChangedTestStatusTests::test_docs_only_does_not_gain_new_test_requirement"],
            [source(test, text)])
        self.blocked(r)

    def test_three_of_three_is_accepted_advisory(self):
        for make_id in (py_id, ut_id):
            with self.subTest(form=make_id.__name__):
                self.result(make_record([row(MOD)], [make_id(n) for n in NAMES],
                                        [source(MOD, SOURCE)]), "READY_TO_MERGE")

    def test_parametrized_and_subtest_suffixes_count_for_their_own_case_only(self):
        ids = [py_id(NAMES[0]) + "[case0]", ut_id(NAMES[1]) + " (path='AGENTS.md')", py_id(NAMES[2])]
        self.result(make_record([row(MOD)], ids, [source(MOD, SOURCE)]), "READY_TO_MERGE")
        self.blocked(make_record([row(MOD)], ids[:2], [source(MOD, SOURCE)]))

    # --- coarse or look-alike IDs never credit ---------------------------------
    def test_module_file_and_class_level_ids_are_not_execution(self):
        for coarse in (DOTTED, MOD, f"{MOD}::{CLS}", f"{DOTTED}.{CLS}", MOD + "::", DOTTED + "."):
            with self.subTest(executed=coarse):
                self.blocked(make_record([row(MOD)], [coarse], [source(MOD, SOURCE)]))

    def test_name_prefix_or_extension_of_a_case_is_not_that_case(self):
        base = [py_id(NAMES[0]), py_id(NAMES[2])]
        for near in (py_id("test_g3"), py_id(NAMES[1] + "_extra"), py_id(NAMES[1], cls="Other"),
                     py_id(NAMES[1], path="tests/other/test_release_guard_example.py"),
                     NAMES[1], f"{CLS}.{NAMES[1]}"):
            with self.subTest(executed=near):
                self.blocked(make_record([row(MOD)], base + [near], [source(MOD, SOURCE)]))

    def test_cases_may_be_split_across_required_jobs_but_not_unrequired_jobs(self):
        r = make_record([row(MOD)], [py_id(NAMES[0])], [source(MOD, SOURCE)])
        second = dict(r["pr_jobs"][0], name="test-2", executed_test_ids=[py_id(NAMES[1]), py_id(NAMES[2])])
        r["pr_jobs"].append(second)
        self.blocked(r)  # test-2 is not a required job
        r["required_pr_job_names"].append("test-2")
        self.result(r, "READY_TO_MERGE")

    def test_discovery_root_scoped_ids_need_every_case_and_the_right_root(self):
        path = "tests/learning/test_forecast_skill_study_v132.py"
        text = "class ForecastTests:\n    def test_ready(self):\n        pass\n    def test_blocked(self):\n        pass\n"
        ids = ["test_forecast_skill_study_v132.ForecastTests.test_ready",
               "test_forecast_skill_study_v132.ForecastTests.test_blocked"]
        r = make_record([row(path)], ids, [source(path, text)])
        r["pr_jobs"][0]["test_discovery_root"] = "tests/learning"
        self.result(r, "READY_TO_MERGE")
        r["pr_jobs"][0]["executed_test_ids"] = ids[:1]
        self.blocked(r)
        r["pr_jobs"][0]["executed_test_ids"] = ids
        r["pr_jobs"][0]["test_discovery_root"] = "tests/other"
        self.blocked(r)

    def test_module_level_and_async_cases_are_required(self):
        text = ("def test_plain():\n    pass\n\nasync def test_async():\n    pass\n\n"
                "def helper():\n    pass\n\nclass T:\n    async def test_method(self):\n        pass\n"
                "    def helper(self):\n        pass\n")
        all_ids = [py_id("test_plain", cls=None), py_id("test_async", cls=None), py_id("test_method", cls="T")]
        self.result(make_record([row(MOD)], all_ids, [source(MOD, text)]), "READY_TO_MERGE")
        for drop in all_ids:
            with self.subTest(missing=drop):
                self.blocked(make_record([row(MOD)], [i for i in all_ids if i != drop], [source(MOD, text)]))

    # --- source binding ---------------------------------------------------------
    def test_changed_test_without_source_fails_closed(self):
        ids = [py_id(n) for n in NAMES]
        for sources in (None, []):
            with self.subTest(sources=repr(sources)):
                self.blocked(make_record([row(MOD)], ids, sources), "CHANGED_TEST_SOURCE_UNVERIFIED")

    def test_second_changed_test_without_source_fails_closed(self):
        other = "tests/research/test_other.py"
        r = make_record([row(MOD), row(other)], [py_id(n) for n in NAMES] + [f"{other}::test_x"],
                        [source(MOD, SOURCE)])
        self.blocked(r, "CHANGED_TEST_SOURCE_UNVERIFIED")

    def test_source_not_bound_to_head_or_blob_fails_closed(self):
        ids = [py_id(NAMES[0])]
        trimmed = SOURCE.split("    def " + NAMES[1])[0]
        bad_sources = {
            "stale head": source(MOD, SOURCE, head="f" * 40),
            "text shorter than claimed blob": {**source(MOD, SOURCE), "text": trimmed},
            "missing blob sha": {k: v for k, v in source(MOD, trimmed).items() if k != "blob_sha"},
            "sha256 instead of git blob sha": {**source(MOD, trimmed),
                                               "blob_sha": hashlib.sha256(trimmed.encode()).hexdigest()},
            "non-text": {**source(MOD, trimmed), "text": trimmed.encode()},
        }
        for label, bad in bad_sources.items():
            with self.subTest(case=label):
                self.blocked(make_record([row(MOD)], ids, [bad]), "CHANGED_TEST_SOURCE_UNVERIFIED")

    def test_malformed_source_lists_fail_closed_without_crashing_other_prs(self):
        ids = [py_id(n) for n in NAMES]
        good = source(MOD, SOURCE)
        for malformed in ({}, "text", 7, True, [good, good], [good, []], [[]], [7],
                          [source("tests/research/test_not_in_pr.py", SOURCE)],
                          [{**good, "path": []}], [{**good, "path": {}}]):
            with self.subTest(sources=repr(malformed)[:60]):
                bad = make_record([row(MOD)], ids)
                bad["changed_test_sources"] = malformed
                ok = make_record([row(MOD)], ids, [good])
                out = classify_pr_batch([bad, ok])
                self.assertEqual(out[0]["disposition"], "CI_NOT_EXECUTED")
                self.assertEqual(out[0]["reason"], "CHANGED_TEST_SOURCE_UNVERIFIED")
                self.assertEqual(out[1]["disposition"], "READY_TO_MERGE")
                self.assertTrue(all(not x["authorized"] for x in out))

    def test_source_for_removed_test_is_contradictory_evidence(self):
        gone = "tests/research/test_gone.py"
        r = make_record([row(gone, "removed", False)], [], [source(gone, SOURCE)])
        self.blocked(r, "CHANGED_TEST_SOURCE_UNVERIFIED")
        self.result(make_record([row(gone, "removed", False)]), "READY_TO_MERGE")

    def test_sources_alone_claim_native_evidence_and_need_the_full_census(self):
        r = decision_fixture("LOW")
        r["expected_changed_paths"] = ["README.md"]
        r["changed_test_sources"] = []
        self.blocked(r, "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    def test_unparseable_or_caseless_changed_test_module_is_not_credited(self):
        for label, text in (("syntax error", "def test_x(:\n    pass\n"),
                            ("no cases", "import unittest\nX = 1\n"),
                            ("only nested cases", "def outer():\n    def test_inner():\n        pass\n"),
                            ("empty", "")):
            with self.subTest(case=label):
                r = make_record([row(MOD)], [py_id("test_x", cls=None), MOD, DOTTED], [source(MOD, text)])
                self.blocked(r, "CHANGED_TEST_CASES_NOT_DERIVABLE")

    def test_renamed_test_requires_every_case_at_the_destination(self):
        old = "tests/research/test_old_name.py"
        r = make_record([row(MOD, "renamed", True, previous=old)],
                        [py_id(n, path=old) for n in NAMES] + [py_id(NAMES[0])], [source(MOD, SOURCE)])
        self.blocked(r)
        r["pr_jobs"][0]["executed_test_ids"] = [py_id(n) for n in NAMES]
        self.result(r, "READY_TO_MERGE")

    # --- non-Python runnable tests ----------------------------------------------
    def test_changed_js_and_shell_tests_need_their_exact_executed_id(self):
        for path in ("tests/web/render.test.mjs", "tests/web/test-render.mjs",
                     "05_CYCLE_NAVIGATOR/site/vnext-live/test-swing-rotation-readback.mjs",
                     "tests/ops/test_backup_restore.sh", "scripts/ops/tests/restore_drill.sh",
                     "tests/web/render.spec.ts"):
            with self.subTest(path=path):
                self.blocked(make_record([row(path)]))
                self.blocked(make_record([row(path)], [path.rsplit("/", 1)[0], path + ".bak",
                                                      path.rsplit("/", 1)[0] + "/"]))
                self.result(make_record([row(path)], [path]), "READY_TO_MERGE")
                self.result(make_record([row(path)], [path + "::renders"]), "READY_TO_MERGE")

    def test_legacy_record_with_only_a_js_test_needs_the_native_census(self):
        r = decision_fixture("LOW")
        r["expected_changed_paths"] = ["tests/web/render.test.mjs"]
        self.blocked(r, "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")

    # --- unchanged #2088 behaviour ------------------------------------------------
    def test_non_test_files_and_fixtures_gain_no_requirement(self):
        for path in ("scripts/example.py", "tests/conftest.py", "tests/helpers/util.py",
                     "docs/guide.md", "scripts/tool.mjs", "scripts/run.sh"):
            with self.subTest(path=path):
                self.result(make_record([row(path)]), "READY_TO_MERGE")

    def test_docs_only_legacy_record_without_census_is_unchanged(self):
        r = decision_fixture("LOW")
        r["expected_changed_paths"] = ["README.md"]
        self.result(r, "READY_TO_MERGE")

    def test_mixed_implementation_and_test_needs_every_case(self):
        r = make_record([row("scripts/example.py"), row(MOD)], [py_id(NAMES[0])], [source(MOD, SOURCE)])
        self.blocked(r)
        r["pr_jobs"][0]["executed_test_ids"] = [py_id(n) for n in NAMES]
        self.result(r, "READY_TO_MERGE")


if __name__ == "__main__":
    unittest.main()
