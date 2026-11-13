"""Fable R4 B1: the path guard is the first gate of the open-PR lane for every LOW record.

At #2088 `4981211a` `_release_sensitive_path` was consulted only inside the
advisory-review validator and the S1-general branch, so a LOW record with
`independent_review_required: false` (the D2 waiver state) or with a native
APPROVED review classified READY_TO_MERGE with `AGENTS.md` as its only changed
path. These cases pin the repaired behaviour. Advisory only, no release authority.
"""
import copy
import unittest

from scripts.governance.s1_release_evidence_classifier_v1 import (
    _release_sensitive_path, classify_pr_batch, classify_pr_disposition,
)

H, M, P, S = "a" * 40, "b" * 40, "c" * 40, "d" * 40
CUR = {"head": H, "main": M, "policy": P, "source": S}
GUARDED = (
    "AGENTS.md", "CLAUDE.md", ".github/workflows/data-architecture-gate.yml", ".agents/skills/x/SKILL.md",
    "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json", "00_FMOS/S1_NATIVE_RULE_CENSUS_AND_RELEASE_RECIPE_V1.md",
    "01_CORE_FRAMEWORK/governance/guard.md", "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md",
    "schemas/S1_CLOSURE_ASSURANCE_V1.schema.json", "scripts/governance/s1_release_evidence_classifier_v1.py",
    "tests/governance/test_s1_release_evidence_classifier_v1.py", "scripts/governance/check_codex_review_finality.py",
)
ORDINARY = "docs/guide.md"
EXECUTED = "scripts/data_governance/storage_health_gate.py"  # run by required job storage-health


def job(name):
    return {"name": name, "head": H, "event": "pull_request", "status": "completed",
            "conclusion": "success", "executed_test_steps": 1}


def low_record(paths, **over):
    """The Fable R4 Q1 reproducer record: every gate other than the path guard is supplied as satisfied."""
    r = {"repo_full_name": "Donh91/Investering-Framework-Archive-v1", "pr_number": 9999,
         "current": dict(CUR), "evaluated": dict(CUR), "risk": "LOW", "expected_changed_paths": list(paths),
         "active_writer_lease": False, "merge_state": "clean", "rule_census": [], "required_rules_enforced": True,
         "unresolved_p0_p1": False, "owner_authorized": True, "source_science_gate": "PASS",
         "required_pr_job_names": ["gate", "storage-health"], "pr_jobs": [job("gate"), job("storage-health")],
         "independent_review_required": False}
    r.update(over)
    return r


def native_review():
    return {"state": "APPROVED", "independent": True, **CUR}


def disp(record):
    out = classify_pr_disposition(copy.deepcopy(record))
    assert out["authorized"] is False and out["externally_authenticated"] is False
    return out["disposition"], out["reason"]


BLOCK = ("SOURCE_OR_SCIENCE_GATE", "HIGH_IMPACT_PATH_MARKED_LOW")
READY = ("READY_TO_MERGE", "CURRENT_REQUIRED_EVIDENCE_SUPPLIED")


class LowLanePathGuardTests(unittest.TestCase):
    def test_control_ordinary_low_path_is_still_ready(self):
        self.assertEqual(disp(low_record([ORDINARY])), READY)
        self.assertEqual(disp(low_record([ORDINARY], independent_review_required=True, review=native_review())), READY)

    def test_r4_b1b_review_not_required_never_ready_for_a_guarded_path(self):
        for path in GUARDED:
            with self.subTest(path=path):
                self.assertTrue(_release_sensitive_path(path))
                self.assertEqual(disp(low_record([path])), BLOCK)

    def test_r4_b1b_native_approved_review_never_ready_for_a_guarded_path(self):
        for path in GUARDED:
            with self.subTest(path=path):
                rec = low_record([path], independent_review_required=True, review=native_review())
                self.assertEqual(disp(rec), BLOCK)

    def test_one_guarded_path_among_ordinary_ones_blocks(self):
        self.assertEqual(disp(low_record([ORDINARY, "README.md", "AGENTS.md"])), BLOCK)
        self.assertEqual(disp(low_record(["AGENTS.md", ORDINARY])), BLOCK)

    def test_guard_answers_before_review_ci_lease_and_merge_state(self):
        for change in ({"independent_review_required": None}, {"independent_review_required": True},
                       {"pr_jobs": []}, {"active_writer_lease": None}, {"merge_state": "conflicting"},
                       {"owner_authorized": False}, {"unresolved_p0_p1": True},
                       {"evaluated": {**CUR, "head": "0" * 40}}):
            with self.subTest(change=sorted(change)):
                self.assertEqual(disp(low_record(["AGENTS.md"], **change)), BLOCK)

    def test_every_low_record_needs_a_clean_path_census_before_ready(self):
        rec = low_record([ORDINARY]); del rec["expected_changed_paths"]
        self.assertEqual(disp(rec), ("EXTERNAL_DEPENDENCY", "LOW_NATIVE_PATH_CENSUS_MISSING"))
        for bad in (None, [], "docs/guide.md", [None], [""], [" docs/guide.md"], ["/docs/guide.md"],
                    ["docs/../AGENTS.md"], [ORDINARY, ORDINARY], [7], [{"path": ORDINARY}]):
            with self.subTest(paths=bad):
                self.assertNotEqual(disp(low_record([ORDINARY], expected_changed_paths=bad))[0], "READY_TO_MERGE")

    def test_malformed_spelling_of_a_guarded_path_is_never_ready(self):
        for bad in ([" AGENTS.md"], ["AGENTS.md "], ["./AGENTS.md", "x/../AGENTS.md"], ["docs/../AGENTS.md"]):
            with self.subTest(paths=bad):
                self.assertNotEqual(disp(low_record(bad))[0], "READY_TO_MERGE")

    def test_b2_manifest_executed_paths_are_guarded_when_the_caller_supplies_them(self):
        self.assertFalse(_release_sensitive_path(EXECUTED))
        rec = low_record([EXECUTED], governance_paths_from_main_manifest=[EXECUTED, "tests/x/test_y.py"])
        self.assertEqual(disp(rec), BLOCK)
        self.assertEqual(disp(low_record([ORDINARY], governance_paths_from_main_manifest=[EXECUTED])), READY)
        self.assertEqual(disp(low_record([ORDINARY], governance_paths_from_main_manifest=[])), READY)

    def test_b2_unusable_manifest_path_list_is_never_ready(self):
        for bad in ("scripts/x.py", {"a": 1}, [None], [""], ["/abs"], ["a/../b"], [EXECUTED, EXECUTED], 7):
            with self.subTest(manifest=bad):
                out = disp(low_record([ORDINARY], governance_paths_from_main_manifest=bad))
                self.assertEqual(out, ("EXTERNAL_DEPENDENCY", "GOVERNANCE_MANIFEST_PATHS_UNUSABLE"))

    def test_manifest_path_list_is_material_to_the_fingerprint(self):
        a = classify_pr_disposition(low_record([ORDINARY], governance_paths_from_main_manifest=[EXECUTED]))
        b = classify_pr_disposition(low_record([ORDINARY], governance_paths_from_main_manifest=[]))
        self.assertNotEqual(a["fingerprint"], b["fingerprint"])

    def test_high_records_keep_their_own_lane(self):
        """The guard is for the LOW label only: a HIGH record with a governance path goes on to the recovery gates."""
        out = disp(low_record(["AGENTS.md"], risk="HIGH"))
        self.assertEqual(out[0], "INDEPENDENT_RECOVERY_UNVERIFIED")

    def test_merged_and_closed_readbacks_are_not_reclassified(self):
        rec = low_record(["AGENTS.md"], closed=True)
        self.assertEqual(disp(rec)[1], "CLOSED_WITHOUT_SUPERSESSION_PROOF")

    def test_batch_isolation_is_kept(self):
        rows = classify_pr_batch([low_record(["AGENTS.md"]), low_record([ORDINARY])])
        self.assertEqual([row["disposition"] for row in rows], ["SOURCE_OR_SCIENCE_GATE", "READY_TO_MERGE"])
        self.assertTrue(all(row["other_prs_may_continue"] for row in rows))


if __name__ == "__main__":
    unittest.main()
