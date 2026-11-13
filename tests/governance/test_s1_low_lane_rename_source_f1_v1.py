"""Grok R5RT-F1 (Bridge PR #183), wired as a native test: the B1 LOW-lane path guard (B_2088) ignores rename SOURCES.

Run against the #2088 worktree with B_2088 (B1_PLUS_Q2_combined + TEST-DIFF) applied:
    R5_WT_2088=/path/to/wt python -m pytest -q test_r5rt_f1_b1_rename_source.py
GitHub's PR-files API lists a rename as ONE entry whose `filename` is the destination
and whose `previous_filename` is the source; `changed_files` counts it once. A record
built faithfully from that native shape therefore carries the governance source path
only in `changed_file_statuses[].previous_filename`, never in `expected_changed_paths`.
"""
import copy
import importlib.util
import os
import sys
import unittest
from pathlib import Path

WT = Path(os.environ.get("R5_WT_2088", "."))
sys.path.insert(0, str(WT))
_spec = importlib.util.spec_from_file_location(
    "r5rt_classifier", WT / "scripts/governance/s1_release_evidence_classifier_v1.py")
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

H, M, P, S = "a" * 40, "b" * 40, "c" * 40, "d" * 40
CUR = {"head": H, "main": M, "policy": P, "source": S}


def job(name):
    return {"name": name, "head": H, "event": "pull_request", "status": "completed",
            "conclusion": "success", "executed_test_steps": 1}


def native_rename_record(src, dst, **over):
    """LOW record, every non-path gate satisfied (same shape as B_2088's own low_record),
    plus a COMPLETE native IC-1 census for a single rename, as GitHub reports it."""
    r = {"repo_full_name": "Donh91/Investering-Framework-Archive-v1", "pr_number": 9999,
         "current": dict(CUR), "evaluated": dict(CUR), "risk": "LOW",
         "expected_changed_paths": [dst],
         "changed_file_statuses_source": "GITHUB_PR_FILES", "changed_file_statuses_head_sha": H,
         "changed_file_statuses": [{"path": dst, "status": "renamed", "head_exists": True,
                                    "previous_filename": src}],
         "pr_changed_files_count": 1, "pr_changed_files_count_head_sha": H,
         "active_writer_lease": False, "merge_state": "clean", "rule_census": [],
         "required_rules_enforced": True, "unresolved_p0_p1": False, "owner_authorized": True,
         "source_science_gate": "PASS", "required_pr_job_names": ["gate", "storage-health"],
         "pr_jobs": [job("gate"), job("storage-health")], "independent_review_required": False}
    r.update(over)
    return r


def disp(record):
    out = C.classify_pr_disposition(copy.deepcopy(record))
    return out["disposition"], out["reason"]


RENAMES = (
    ("AGENTS.md", "docs/archive/AGENTS_2026-11.md"),
    ("scripts/governance/s1_release_evidence_classifier_v1.py", "scripts/research/legacy_release_classifier.py"),
    ("00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json", "docs/archive/required_jobs_old.json"),
    ("CLAUDE.md", "docs/archive/claude_notes.md"),
)
EXECUTED = "scripts/data_governance/storage_health_gate.py"  # executed by required job storage-health


class RenameSourceBypassesB1(unittest.TestCase):
    def test_control_destination_into_governance_is_blocked(self):
        # B1 does see the destination: renaming INTO a governance path is blocked.
        self.assertEqual(disp(native_rename_record("docs/x.md", "AGENTS.md")),
                         ("SOURCE_OR_SCIENCE_GATE", "HIGH_IMPACT_PATH_MARKED_LOW"))

    def test_control_plain_delete_of_governance_path_is_blocked(self):
        r = native_rename_record("AGENTS.md", "AGENTS.md")
        r["changed_file_statuses"] = [{"path": "AGENTS.md", "status": "removed", "head_exists": False}]
        self.assertEqual(disp(r), ("SOURCE_OR_SCIENCE_GATE", "HIGH_IMPACT_PATH_MARKED_LOW"))

    def test_rename_out_of_a_governance_path_is_never_ready(self):
        for src, dst in RENAMES:
            with self.subTest(src=src):
                self.assertTrue(C._release_sensitive_path(src))
                self.assertFalse(C._release_sensitive_path(dst))
                self.assertNotEqual(disp(native_rename_record(src, dst))[0], "READY_TO_MERGE")

    def test_malformed_native_rename_status_manifest_rejects_only_affected_pr(self):
        for invalid in (1, True, {}, "renamed", None):
            with self.subTest(invalid=invalid):
                bad = native_rename_record("docs/private.md", "docs/public.md")
                bad["changed_file_statuses"] = invalid
                good = native_rename_record("docs/from.md", "docs/to.md")
                result = C.classify_pr_batch([bad, good])
                self.assertEqual(len(result), 2)
                self.assertEqual(result[0]["reason"], "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")
                self.assertNotEqual(result[0]["disposition"], "READY_TO_MERGE")
                self.assertEqual(result[1]["disposition"], "READY_TO_MERGE")
                self.assertFalse(result[1]["authorized"])

    def test_rename_out_of_a_manifest_executed_path_is_never_ready(self):
        r = native_rename_record(EXECUTED, "scripts/research/old_storage_health_gate.py",
                                 governance_paths_from_main_manifest=[EXECUTED])
        self.assertNotEqual(disp(r)[0], "READY_TO_MERGE")


if __name__ == "__main__":
    unittest.main()
