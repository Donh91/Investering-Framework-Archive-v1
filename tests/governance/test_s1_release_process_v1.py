"""S1 Release Process v1 (RP1) controls - Grok proposal 2026-11-12, advisory only.

Positive cases remove 'impossible evidence' HOLDs; negative cases prove nothing unsafe
becomes READY. Every output keeps authorized=False / externally_authenticated=False.
"""
import copy
import random
import unittest

from scripts.governance.s1_release_evidence_classifier_v1 import (
    classify_pr_disposition, derive_release_class, rp1_merge_state, rp1_rule_census)
from scripts.governance.s1_closure_claim_guard_v1 import inspect_claim
from scripts.governance.s1_diff_scan_v1 import scan_pr
from tests.governance.test_s1_closure_claim_guard_v1 import complete_shape

H, M, P, M0 = "a" * 40, "b" * 40, "c" * 40, "e" * 40


def ready(files=None):
    files = files or [{"path": "06_RESEARCH_LAB/audit_summaries/note.md", "status": "added"}]
    paths = [f["path"] for f in files]
    statuses = [{"path": f["path"], "status": f["status"], "head_exists": f["status"] not in ("removed", "deleted"),
                 **({"previous_filename": f["previous_filename"]} if f.get("previous_filename") else {})} for f in files]
    cur = {"head": H, "main": M, "policy": P, "source": H}
    r = {
        "release_process": "S1_RP_V1", "release_lane": "UNATTENDED_S1", "draft": False,
        "current": dict(cur), "evaluated": dict(cur), "risk": "LOW",
        "expected_changed_paths": paths, "changed_file_statuses": statuses,
        "changed_file_statuses_source": "GITHUB_PR_FILES", "changed_file_statuses_head_sha": H,
        "pr_changed_files_count": len(paths), "pr_changed_files_count_head_sha": H,  # RP1 05 / G3
        "owner_mandate": {"source": "AGENTS.md#0.2c", "effective_on_main": True, "agents_blob_sha": P},
        "owner_authorized": True,
        "native_rule_reads": {"branch_http": 200, "protected": False, "protection_enabled": False,
                              "protection_detail_http": 403, "rulesets_http": 200, "rulesets_pages_complete": True,
                              "rulesets": [{"id": 25307191, "enforcement": "disabled", "applies_to_main": True}]},
        "rule_census": [], "required_rules_enforced": True,
        "merge_layers": {"rest_http": 200, "rest_mergeable": True, "rest_mergeable_state": "clean"},
        "merge_state": "clean",
        "active_writer_lease": False,
        "writer_lease": {"basis": "EXPECTED_HEAD_MERGE_AND_STABLE_HEAD", "head_reads": [H, H], "foreign_active_leases": 0},
        "pr_run_census": {"head": H, "complete": True, "pending": 0, "failed": 0,
                          "job_names": ["Data Architecture Gate", "Storage Health Gate"]},
        "required_pr_job_names": ["Data Architecture Gate", "Storage Health Gate"],
        "pr_jobs": [{"name": n, "head": H, "event": "pull_request", "status": "completed", "conclusion": "success",
                     "executed_test_steps": 2} for n in ("Data Architecture Gate", "Storage Health Gate")],
        "unresolved_p0_p1": False, "source_science_gate": "NOT_APPLICABLE_BY_PATH",
        "independent_review_required": True,
        "review": {"state": "APPROVED", "independent": True,
                   "head": H, "policy": P, "source": H, "main": M},
    }
    inp = {
        "repo": "Donh91/Investering-Framework-Archive-v1",
        "head": H, "pr_head_sha": H, "changed_files_count_head_sha": H,
        "changed_files_count": len(files), "pages_complete": True,
        "title": "Public documentation", "body": "Public original PR, synthetic fixture",
        "files": [{
            "path": f["path"], "status": f["status"], "head_sha": H,
            "previous_filename": f.get("previous_filename"),
            "patch_complete": True, "patch": "+Public synthetic test fixture",
            "binary": False, "is_symlink": False,
            "content": None if f["status"] in ("removed", "deleted") else "Public content",
            "content_head_sha": H,
        } for f in files],
    }
    r["privacy_scan_input"] = inp
    r["privacy_check"] = scan_pr(inp)
    return r


def code_ready():
    r = ready([{"path": "scripts/research/x_v1.py", "status": "added"},
               {"path": "tests/research/test_x_v1.py", "status": "added"}])
    r["source_science_gate"] = "PASS"
    r["pr_jobs"][0].update(executed_scope_paths=["tests/research"], executed_scope_unmasked=True,
                          executed_scope_patterns_complete=True,
                          executed_scope_discovery_patterns=["test_*.py", "*_test.py"])
    return r


def out(r):
    o = classify_pr_disposition(r)
    assert o["authorized"] is False and o["externally_authenticated"] is False
    return o


class Positive(unittest.TestCase):
    def test_docs_only_unattended_ready_without_impossible_tests(self):  # #2081 shape
        o = out(ready())
        self.assertEqual((o["disposition"], o["release_action"], o["release_class"]),
                         ("READY_TO_MERGE", "READY", "DOCS_ONLY"))

    def test_classic_protection_403_is_irrelevant_when_unprotected(self):
        census = rp1_rule_census(ready()["native_rule_reads"])
        self.assertEqual(census, ([], True))

    def test_low_code_changed_test_covered_by_step_scope(self):  # pytest -q <dir> prints no IDs
        self.assertEqual(out(code_ready())["release_action"], "READY")

    def test_review_reuse_across_disjoint_main_drift(self):
        r = ready()
        r.update(independent_review_required=True, review_requires_current_main=False,
                 review={"state": "APPROVED", "independent": True, "head": H, "policy": P, "source": H, "main": M0},
                 main_drift={"from_main": M0, "to_main": M, "complete": True,
                             "touched_paths": ["04_MARKET_LEARNING/handlekompas/state/latest.json"]})
        self.assertEqual(out(r)["release_action"], "READY")

    def test_rename_destination_executed(self):
        r = code_ready()
        r["changed_file_statuses"][1].update(status="renamed", previous_filename="tests/research/test_old.py")
        self.assertEqual(out(r)["release_action"], "READY")


class Negative(unittest.TestCase):
    def assertAction(self, r, action, reason=None):
        o = out(r)
        self.assertEqual(o["release_action"], action, o)
        if reason:
            self.assertEqual(o["reason"], reason)
        self.assertNotEqual(o["disposition"], "READY_TO_MERGE")

    def test_rename_out_of_workflow_dir_is_governance(self):
        r = ready([{"path": "docs/old-workflow.md", "status": "renamed", "previous_filename": ".github/workflows/x.yml"}])
        r["risk"] = "HIGH"
        self.assertAction(r, "ESCALATE_OWNER", "RP1_NOT_ELIGIBLE_UNATTENDED")

    def test_archive_control_doc_marked_low(self):  # #2057 shape
        self.assertAction(ready([{"path": "00_ARCHIVE_CONTROL/x/NOTE.md", "status": "added"}]),
                          "HOLD", "HIGH_IMPACT_PATH_MARKED_LOW")

    def test_workflow_deletion_never_unattended(self):  # #2071 shape
        r = ready([{"path": ".github/workflows/master-monday-w37-redispatch-once.yml", "status": "removed"}])
        r["risk"] = "HIGH"
        self.assertAction(r, "ESCALATE_OWNER", "RP1_NOT_ELIGIBLE_UNATTENDED")

    def test_agent_skill_and_paid_queue_never_unattended(self):
        for path in (".agents/skills/x/SKILL.md", "research/api_agent/research_lab_sol/QUEUE.json",
                     "05_CYCLE_NAVIGATOR/site/app.mjs", "LATEST_HANDOFF.json", "requirements.txt"):
            with self.subTest(path=path):
                r = ready([{"path": path, "status": "modified"}]); r["risk"] = "HIGH"
                self.assertAction(r, "ESCALATE_OWNER", "RP1_NOT_ELIGIBLE_UNATTENDED")

    def test_ruleset_pages_incomplete_rechecks(self):
        r = ready(); r["native_rule_reads"]["rulesets_pages_complete"] = False
        self.assertAction(r, "RECHECK", "RULE_CENSUS_UNAVAILABLE")

    def test_protected_branch_detail_403_escalates(self):  # RP1 05: known protection, unreadable requirements
        r = ready(); r["native_rule_reads"].update(protected=True, protection_enabled=True)
        self.assertAction(r, "ESCALATE_OWNER", "RP1_ACTIVE_RULES_REQUIRE_NATIVE_COMPLIANCE")

    def test_active_ruleset_escalates(self):
        r = ready(); r["native_rule_reads"]["rulesets"][0]["enforcement"] = "active"
        self.assertAction(r, "ESCALATE_OWNER", "RP1_ACTIVE_RULES_REQUIRE_NATIVE_COMPLIANCE")

    def test_evaluate_ruleset_is_logged_not_binding_but_census_must_match(self):
        r = ready(); r["native_rule_reads"]["rulesets"][0]["enforcement"] = "evaluate"
        self.assertAction(r, "HOLD", "RP1_EVIDENCE_MISMATCH")  # supplied [] hides the evaluate rule

    def test_mergeability_403_null_and_disagreement_recheck(self):
        for layers in ({"rest_http": 403}, {"rest_http": 200, "rest_mergeable": None, "rest_mergeable_state": "unknown"},
                       {"rest_http": 200, "rest_mergeable": True, "rest_mergeable_state": "clean", "git_merge_tree_exit": 1}):
            with self.subTest(layers=layers):
                r = ready(); r["merge_layers"] = layers
                self.assertAction(r, "RECHECK", "MERGEABILITY_UNKNOWN_RECHECK")
        self.assertEqual(rp1_merge_state({"rest_http": 200, "rest_mergeable": False, "rest_mergeable_state": "dirty",
                                          "git_merge_tree_exit": 1}), "conflicting")

    def test_supplied_clean_contradicting_layers_cannot_ready(self):
        r = ready(); r["merge_layers"] = {"rest_http": 200, "rest_mergeable": True, "rest_mergeable_state": "blocked"}
        self.assertAction(r, "RECHECK", "MERGEABILITY_COMPUTING_OR_RULE_BLOCKED")

    def test_lease_needs_two_stable_reads_and_no_foreign_lease(self):
        for lease in ({"basis": "EXPECTED_HEAD_MERGE_AND_STABLE_HEAD", "head_reads": [H], "foreign_active_leases": 0},
                      {"basis": "EXPECTED_HEAD_MERGE_AND_STABLE_HEAD", "head_reads": [H, "d" * 40], "foreign_active_leases": 0},
                      {"basis": "EXPECTED_HEAD_MERGE_AND_STABLE_HEAD", "head_reads": [H, H], "foreign_active_leases": 1},
                      {"basis": "SELF_DECLARED", "head_reads": [H, H], "foreign_active_leases": 0}):
            with self.subTest(lease=lease):
                r = ready(); r["writer_lease"] = lease
                self.assertAction(r, "RECHECK", "WRITER_LEASE_ACTIVE_OR_UNKNOWN")

    def test_ci_pending_rechecks_then_escalates(self):  # #2085/#2086 stuck queued
        r = ready(); r["pr_run_census"]["pending"] = 2
        self.assertAction(r, "RECHECK", "CI_PENDING_RECHECK")
        r["consecutive_rechecks"] = 3
        self.assertAction(r, "ESCALATE_OWNER", "CI_PENDING_RECHECK")

    def test_required_job_names_must_equal_run_census(self):
        r = ready(); r["required_pr_job_names"] = ["Data Architecture Gate"]
        self.assertAction(r, "RECHECK", "REQUIRED_JOB_CENSUS_MISSING")

    def test_ci_failed_holds(self):
        r = ready(); r["pr_run_census"]["failed"] = 1
        self.assertAction(r, "HOLD", "REQUIRED_CI_FAILED")

    def test_changed_test_not_executed_holds(self):  # #2082 shape
        r = code_ready(); r["pr_jobs"][0]["executed_scope_paths"] = ["tests/governance", "tests/lib"]
        self.assertAction(r, "HOLD", "CHANGED_TESTS_NOT_EXECUTED")

    def test_masked_or_whole_repo_scope_does_not_count(self):
        for patch in ({"executed_scope_unmasked": False}, {"executed_scope_paths": ["."]},
                      {"executed_scope_paths": ["../tests"]}):
            with self.subTest(patch=patch):
                r = code_ready(); r["pr_jobs"][0].update(patch)
                self.assertAction(r, "HOLD", "CHANGED_TESTS_NOT_EXECUTED")

    def test_missing_path_census_never_skips_changed_test_gate(self):  # Fable P5 D1 on #2088
        r = code_ready(); del r["expected_changed_paths"]
        self.assertAction(r, "RECHECK", "RP1_PATH_CENSUS_MISSING")
        r = code_ready(); r["changed_file_statuses"] = r["changed_file_statuses"][:1]
        self.assertAction(r, "RECHECK", "RP1_PATH_CENSUS_MISSING")

    def test_js_changed_test_requires_execution(self):  # Fable P5 D2 on #2088
        r = ready([{"path": "06_RESEARCH_LAB/tool/x.test.mjs", "status": "modified"}])
        r["source_science_gate"] = "PASS"
        self.assertAction(r, "HOLD", "CHANGED_TESTS_NOT_EXECUTED")
        r["pr_jobs"][1].update(executed_scope_paths=["06_RESEARCH_LAB/tool/x.test.mjs"], executed_scope_unmasked=True)
        self.assertEqual(out(r)["release_action"], "READY")

    def test_p1_unittest_directory_scope_not_equal_to_executed_pattern(self):
        r = ready([{"path": "tests/learning/test_legacy_knowledge_bootstrap.py", "status": "added"}])
        r["source_science_gate"] = "PASS"
        r["pr_jobs"][0].update(executed_scope_paths=["tests/learning"],
                               executed_scope_unmasked=True,
                               executed_scope_patterns_complete=True,
                               executed_scope_discovery_patterns=["test_forecast_*.py"])
        self.assertAction(r, "HOLD", "CHANGED_TESTS_NOT_EXECUTED")
        r["pr_jobs"][0]["executed_scope_discovery_patterns"] = ["test_legacy_*.py"]
        self.assertEqual(out(r)["release_action"], "READY")

    def test_p1_directory_scope_without_complete_patterns_cannot_ready(self):
        for fields in ({}, {"executed_scope_discovery_patterns": ["test_*.py"]},
                       {"executed_scope_patterns_complete": True},
                       {"executed_scope_patterns_complete": True,
                        "executed_scope_discovery_patterns": ["test_other_*.py"]}):
            with self.subTest(fields=fields):
                r = code_ready()
                r["pr_jobs"][0].pop("executed_scope_patterns_complete", None)
                r["pr_jobs"][0].pop("executed_scope_discovery_patterns", None)
                r["pr_jobs"][0].update(fields)
                self.assertAction(r, "HOLD", "CHANGED_TESTS_NOT_EXECUTED")

    def test_p1_paid_api_budget_enforcer_never_low(self):
        for path in ("scripts/api_agent/check_api_lane_budget.py",
                     "scripts/api_agent/research_lab_sol_dispatch.py",
                     "tests/api_agent/test_api_lane_budget.py"):
            with self.subTest(path=path):
                r = ready([{"path": path, "status": "modified"}])
                self.assertAction(r, "HOLD", "HIGH_IMPACT_PATH_MARKED_LOW")

    def test_p1_independent_review_cannot_substitute_for_privacy_scan(self):
        r = ready()
        r["privacy_check"]["method"] = "EXACT_HEAD_INDEPENDENT_REVIEW"
        self.assertAction(r, "HOLD", "RP1_PRIVACY_CHECK_MISSING")

    def test_privacy_check_required_unattended(self):  # #2084 shape
        for pc in (None, {"head": "d" * 40, "result": "NO_RESTRICTED_CONTENT", "method": "S1_DIFF_SCAN_V1"},
                   {"head": H, "result": "UNKNOWN", "method": "S1_DIFF_SCAN_V1"}):
            with self.subTest(pc=pc):
                r = ready(); r["privacy_check"] = pc
                self.assertAction(r, "HOLD", "RP1_PRIVACY_CHECK_MISSING")

    def test_p1_forged_privacy_result_without_real_scan_is_not_ready(self):
        r = ready()
        del r["privacy_scan_input"]
        self.assertAction(r, "HOLD", "RP1_PRIVACY_CHECK_MISSING")
        r = ready()
        r["privacy_scan_input"]["files"][0]["content"] = "PRIVATE_ALPHA_DESIGN"
        self.assertAction(r, "HOLD", "RP1_PRIVACY_CHECK_MISSING")
        r = ready()
        r["privacy_check"] = {"head": H, "result": "NO_RESTRICTED_CONTENT",
                              "method": "S1_DIFF_SCAN_V1"}
        self.assertAction(r, "HOLD", "RP1_PRIVACY_CHECK_MISSING")

    def test_p1_scan_without_separate_independent_review_is_not_ready(self):
        r = ready()
        r["independent_review_required"] = False
        self.assertAction(r, "HOLD", "RP1_STAGED_REVIEW_REQUIRED")
        r = ready()
        r["review"]["head"] = "d" * 40
        self.assertAction(r, "HOLD", "REQUIRED_INDEPENDENT_APPROVAL_MISSING_OR_STALE")

    def test_p1_native_scanner_inputs_must_match_full_original_manifest(self):
        r = ready()
        r["privacy_scan_input"]["files"][0]["status"] = "renamed"
        self.assertAction(r, "HOLD", "RP1_PRIVACY_CHECK_MISSING")

    def test_main_drift_must_be_disjoint_complete_and_low(self):
        base = ready()
        base.update(independent_review_required=True, review_requires_current_main=False,
                    review={"state": "APPROVED", "independent": True, "head": H, "policy": P, "source": H, "main": M0})
        for drift in (None,
                      {"from_main": M0, "to_main": M, "complete": False, "touched_paths": []},
                      {"from_main": M0, "to_main": M, "complete": True, "touched_paths": ["06_RESEARCH_LAB/audit_summaries/note.md"]},
                      {"from_main": M0, "to_main": M, "complete": True, "touched_paths": ["AGENTS.md"]},
                      {"from_main": "d" * 40, "to_main": M, "complete": True, "touched_paths": []}):
            with self.subTest(drift=drift):
                r = copy.deepcopy(base); r["main_drift"] = drift
                self.assertAction(r, "HOLD", "REVIEW_MAIN_DRIFT_UNVERIFIED")

    def test_mandate_must_be_effective_and_bound_to_policy_blob(self):
        for m in (None, {"source": "AGENTS.md#0.2c", "effective_on_main": False, "agents_blob_sha": P},
                  {"source": "AGENTS.md#0.2c", "effective_on_main": True, "agents_blob_sha": "d" * 40},
                  {"source": "chat", "effective_on_main": True, "agents_blob_sha": P}):
            with self.subTest(m=m):
                r = ready(); r["owner_mandate"] = m
                self.assertAction(r, "ESCALATE_OWNER", "OWNER_RELEASE_MANDATE_UNVERIFIED")

    def test_not_applicable_science_only_for_docs(self):
        r = code_ready(); r["source_science_gate"] = "NOT_APPLICABLE_BY_PATH"
        self.assertAction(r, "HOLD", "SOURCE_OR_SCIENCE_REQUIREMENT_UNMET")
        legacy = ready(); del legacy["release_process"]
        self.assertNotEqual(out(legacy)["disposition"], "READY_TO_MERGE")  # legacy never accepts NA

    def test_wrong_contract_string(self):
        r = ready(); r["release_process"] = "S1_RP_V2"
        self.assertAction(r, "HOLD", "RP1_LANE_INVALID")

    def test_owner_directed_high_reaches_existing_recovery_gate(self):
        r = ready([{"path": ".github/workflows/x.yml", "status": "removed"}])
        r.update(release_lane="OWNER_DIRECTED", risk="HIGH", source_science_gate="PASS")
        o = out(r)
        self.assertEqual((o["disposition"], o["release_action"]), ("INDEPENDENT_RECOVERY_UNVERIFIED", "ESCALATE_OWNER"))

    def test_terminal_block_escalates(self):
        r = ready(); r["pr_run_census"]["failed"] = 1; r["material_touches"] = 4
        self.assertAction(r, "ESCALATE_OWNER", "REQUIRED_CI_FAILED")

    def test_fuzz_no_mutation_creates_ready(self):
        rng = random.Random(20261112)
        base = ready()
        keys = sorted(k for k in base if k not in ("independent_review_required",))
        for _ in range(3000):
            r = copy.deepcopy(base)
            k = rng.choice(keys)
            choice = rng.randrange(4)
            if choice == 0:
                del r[k]
            elif choice == 1:
                r[k] = rng.choice([None, True, False, 0, "", [], {}, "x", H])
            elif choice == 2 and isinstance(r[k], dict) and r[k]:
                sub = rng.choice(sorted(r[k])); r[k][sub] = rng.choice([None, False, 0, "x", 403, [], H, "d" * 40])
            elif isinstance(r[k], list) and r[k]:
                r[k] = r[k][:-1]
            else:
                r[k] = None
            if r == base:
                continue  # value-preserving mutation
            o = out(r)
            if o["release_action"] == "READY":
                self.assertEqual(o["disposition"], "READY_TO_MERGE")
                # Only semantically neutral mutations may stay READY (e.g. deleting a disabled ruleset entry).
                # Observed neutral cases: classic-detail HTTP code / empty ruleset list on an UNPROTECTED
                # branch whose only ruleset is disabled. Authenticity of the reads stays S1's job.
                # RP1 05 (D4): an explicit active_writer_lease=None (no lease registry; optimistic concurrency
                # evidence still required by the RP1 gate) is the honest neutral form of False.
                self.assertTrue(k == "native_rule_reads" or (k == "active_writer_lease" and r.get(k) is None),
                                (k, r.get(k)))


class RenameAndPointerControls(unittest.TestCase):
    def test_test_renamed_out_of_discovery_holds(self):  # Fable P5 D3 on #2088
        r = code_ready()
        r["expected_changed_paths"] = ["tests/research/helper_x.py"]; r["pr_changed_files_count"] = 1
        r["changed_file_statuses"] = [{"path": "tests/research/helper_x.py", "status": "renamed", "head_exists": True,
                                       "previous_filename": "tests/research/test_x_v1.py"}]
        o = out(r)
        self.assertEqual((o["reason"], o["release_action"]), ("CHANGED_TEST_RENAMED_OUT_OF_DISCOVERY", "HOLD"))
        legacy = {k: v for k, v in r.items() if k not in ("release_process", "release_lane", "draft", "owner_mandate",
                                                           "native_rule_reads", "merge_layers", "writer_lease",
                                                           "pr_run_census", "privacy_check")}
        self.assertEqual(out(legacy)["reason"], "CHANGED_TEST_RENAMED_OUT_OF_DISCOVERY")

    def test_latest_pointer_is_public_data_integrity(self):  # #2060 shape
        self.assertEqual(derive_release_class([{"path": "04_MARKET_LEARNING/shadow_registry/LATEST.json", "status": "modified"}]),
                         "PUBLIC_DATA_INTEGRITY")


class LegacyCompatibility(unittest.TestCase):
    def test_legacy_record_has_no_class_and_same_gate_order(self):
        r = ready(); del r["release_process"]; r["source_science_gate"] = "PASS"
        o = out(r)
        self.assertIsNone(o["release_class"])
        self.assertEqual((o["disposition"], o["release_action"]), ("READY_TO_MERGE", "READY"))

    def test_derive_class_most_restrictive_wins(self):
        self.assertEqual(derive_release_class([{"path": "a/b.md", "status": "added"},
                                               {"path": "scripts/governance/s1_x.py", "status": "modified"}]),
                         "GOVERNANCE_WORKFLOW")
        self.assertIsNone(derive_release_class([{"path": "../x.md", "status": "added"}]))
        self.assertIsNone(derive_release_class([]))


class ClaimGuardTimeBound(unittest.TestCase):  # Fable P5 D5 on #2087
    def test_check_after_merge_or_before_start_demotes(self):
        for when in ("2026-11-05T21:15:30Z", "2026-11-05T21:10:00Z", "2019-01-01T00:00:00Z"):
            with self.subTest(when=when):
                case = complete_shape(); case["merge_state_check"]["checked_at_utc"] = when
                o = inspect_claim(case)
                self.assertIn("MERGE_STATE_CHECK_TIME_UNBOUND", o["reasons"])
                self.assertFalse(o["candidate_for_native_check"])

    def test_check_inside_run_before_merge_ok(self):
        o = inspect_claim(complete_shape())
        self.assertNotIn("MERGE_STATE_CHECK_TIME_UNBOUND", o["reasons"])


if __name__ == "__main__":
    unittest.main()
