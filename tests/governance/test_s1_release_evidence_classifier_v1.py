"""Negative controls for staged release evidence classification."""
import copy
import unittest

from scripts.governance.s1_release_evidence_classifier_v1 import (
    classify_release_evidence,
    classify_pr_disposition,
    classify_pr_batch,
)


def fixture():
    head = "a" * 40
    return {
        "original_head": head,
        "required_pr_jobs": [{
            "head": head, "event": "pull_request",
            "status": "completed", "conclusion": "success",
            "executed_test_steps": 2,
        }],
        "merge_sha": "b" * 40,
        "main_sha": "c" * 40,
        "changed_main_blobs": [{
            "path": "scripts/governance/example.py",
            "expected_sha": "d" * 40, "actual_sha": "d" * 40,
        }],
        "natural_consumer": {
            "event": "natural", "run_url": "https://github.com/Donh91/example/actions/runs/1",
            "consumer_url": "https://github.com/Donh91/example",
            "source_id": "real-source", "delivered_source_id": "real-source",
            "clock_eligible": True,
        },
    }


class ReleaseEvidenceTests(unittest.TestCase):
    def stage(self, item):
        return classify_release_evidence(item)["stage"]

    def test_positive_is_still_unverified_without_external_auth(self):
        result = classify_release_evidence(fixture())
        self.assertEqual(result["stage"], "PROD_EVIDENCE_SUPPLIED_NEEDS_AUTHENTICATION")
        self.assertFalse(result["authorized"])
        self.assertFalse(result["externally_authenticated"])

    def test_no_head_fails(self):
        item = fixture()
        item["original_head"] = "a1"
        self.assertEqual(self.stage(item), "INVALID_INPUT")

    def test_green_but_skipped_is_not_ci(self):
        item = fixture()
        item["required_pr_jobs"][0]["executed_test_steps"] = 0
        self.assertEqual(self.stage(item), "CI_NOT_PROVEN")

    def test_manual_only_does_not_count_as_pr_ci(self):
        item = fixture()
        item["required_pr_jobs"][0]["event"] = "workflow_dispatch"
        self.assertEqual(self.stage(item), "CI_NOT_PROVEN")

    def test_old_head_run_not_accepted(self):
        item = fixture()
        item["required_pr_jobs"][0]["head"] = "f" * 40
        self.assertEqual(self.stage(item), "CI_NOT_PROVEN")

    def test_boolean_step_count_not_accepted(self):
        item = fixture()
        item["required_pr_jobs"][0]["executed_test_steps"] = True
        self.assertEqual(self.stage(item), "CI_NOT_PROVEN")

    def test_green_ci_not_merge(self):
        item = fixture()
        del item["merge_sha"]
        self.assertEqual(self.stage(item), "CI_ONLY")

    def test_main_blobs_required(self):
        item = fixture()
        item["changed_main_blobs"] = []
        self.assertEqual(self.stage(item), "MAIN_NOT_PROVEN")

    def test_main_blob_mismatch_fails(self):
        item = fixture()
        item["changed_main_blobs"][0]["actual_sha"] = "e" * 40
        self.assertEqual(self.stage(item), "MAIN_NOT_PROVEN")

    def test_no_natural_cycle_is_main_only(self):
        item = fixture()
        del item["natural_consumer"]
        self.assertEqual(self.stage(item), "MAIN_READBACK_SUPPLIED")

    def test_dispatch_cannot_pose_as_natural_cycle(self):
        item = fixture()
        item["natural_consumer"]["event"] = "workflow_dispatch"
        self.assertEqual(self.stage(item), "PRODUCTION_NOT_PROVEN")

    def test_source_clock_must_match_consumer(self):
        item = fixture()
        item["natural_consumer"]["delivered_source_id"] = "old-source"
        self.assertEqual(self.stage(item), "PRODUCTION_NOT_PROVEN")

    def test_expired_source_cannot_be_prod_verified(self):
        item = fixture()
        item["natural_consumer"]["clock_eligible"] = False
        self.assertEqual(self.stage(item), "PRODUCTION_NOT_PROVEN")


def decision_fixture(risk="HIGH"):
    current = dict(head="a" * 40, main="b" * 40, policy="c" * 40, source="b" * 40)
    return {
        "current": current, "evaluated": dict(current), "risk": risk,
        "active_writer_lease": False, "merge_state": "clean",
        "required_rules_enforced": True, "rule_census": [], "unresolved_p0_p1": False, "owner_authorized": True,
        "source_science_gate": "PASS", "independent_review_required": True,
        "review": {**current, "state": "APPROVED", "independent": True},
        "required_pr_job_names": ["test"],
        "pr_jobs": [{"name": "test", "head": current["head"], "event": "pull_request",
                     "status": "completed", "conclusion": "success", "executed_test_steps": 2}],
        "now_utc": "2026-11-04T10:00:00Z", "recovery_max_age_seconds": 3600,
        "safepoint_source": current["source"], "vault_access": 404,
        "recovery": {
            "source": current["source"], "snapshot": "d" * 40,
            "tree": "e" * 40, "workflow": "f" * 40,
            "manifest_sha256": "a" * 64,
            "receipt_url": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1593#issuecomment-1",
            "observed_at_utc": "2026-11-04T09:50:00Z", "technical_recovery": True,
            "independent_custody": True, "separation": True, "native_release_permission": False,
        },
        "release_assessment": {**current, "snapshot": "d" * 40,
            "manifest_sha256": "a" * 64, "release_permission": True,
            "independent": True, "observed_at_utc": "2026-11-04T09:55:00Z",
            "attestation_url": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1593#issuecomment-2"},
    }


def merged_fixture():
    r = decision_fixture()
    r.update(merged=True, expected_changed_paths=["scripts/example.py"])
    r["merge"] = {"head": r["current"]["head"], "sha": "1" * 40,
                  "observed_main": r["current"]["main"], "main_contains_merge": True,
                  "rollback_sha": "2" * 40,
                  "blobs": [{"path": "scripts/example.py", "expected_sha": "3" * 40,
                             "actual_sha": "3" * 40}]}
    return r


class DeterministicDispositionTests(unittest.TestCase):
    def check(self, r, disposition, reason=None):
        out = classify_pr_disposition(r)
        self.assertEqual(out["disposition"], disposition)
        if reason:
            self.assertEqual(out["reason"], reason)
        self.assertFalse(out["authorized"])
        self.assertFalse(out["externally_authenticated"])
        self.assertTrue(out["other_prs_may_continue"])
        for field in ("binding_requirement", "responsible_owner", "reactivation_trigger"):
            self.assertTrue(out[field])
        return out

    def test_vault404_with_complete_recovery(self):
        self.check(decision_fixture(), "READY_TO_MERGE")

    def test_vault404_missing_recovery_scoped_by_risk(self):
        for risk, expected in (("HIGH", "INDEPENDENT_RECOVERY_UNVERIFIED"), ("LOW", "READY_TO_MERGE")):
            with self.subTest(risk=risk):
                r = decision_fixture(risk); del r["recovery"]
                self.check(r, expected)

    def test_successful_restore_stale_source(self):
        r = decision_fixture(); r["recovery"]["source"] = "0" * 40
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "RECOVERY_SOURCE_STALE")

    def test_successful_restore_unattested_custody(self):
        r = decision_fixture(); r["recovery"]["independent_custody"] = False
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "CUSTODY_UNATTESTED")

    def test_successful_restore_release_false(self):
        r = decision_fixture(); r["release_assessment"]["release_permission"] = False
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "RECOVERY_RELEASE_NOT_PERMITTED")

    def test_complete_recovery_still_never_authenticates_or_authorizes(self):
        out = self.check(decision_fixture(), "READY_TO_MERGE")
        self.assertEqual(out["evidence_status"], "SUPPLIED_RECORD_REQUIRES_NATIVE_AUTHENTICATION")

    def test_native_false_is_expected_but_not_aggregated_permission(self):
        r = decision_fixture()
        self.assertIs(r["recovery"]["native_release_permission"], False)
        self.check(r, "READY_TO_MERGE")
        del r["release_assessment"]
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "RECOVERY_RELEASE_NOT_PERMITTED")

    def test_native_true_or_self_same_receipt_cannot_grant_release(self):
        r = decision_fixture(); r["recovery"]["native_release_permission"] = True
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "NATIVE_TECHNICAL_RECEIPT_AUTHORITY_INVALID")
        r = decision_fixture(); r["release_assessment"]["attestation_url"] = r["recovery"]["receipt_url"]
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "RELEASE_ASSESSMENT_BINDING_UNVERIFIED")

    def test_aggregated_permission_bound_to_exact_current_state(self):
        for key in ("head", "main", "policy", "source", "snapshot", "manifest_sha256"):
            r = decision_fixture(); r["release_assessment"][key] = "0" * 40
            self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "RELEASE_ASSESSMENT_BINDING_UNVERIFIED")
        r = decision_fixture(); r["release_assessment"]["independent"] = False
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "RELEASE_ASSESSMENT_BINDING_UNVERIFIED")
        r = decision_fixture(); r["release_assessment"]["observed_at_utc"] = "2026-11-03T00:00:00Z"
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "RELEASE_ASSESSMENT_STALE")

    def test_batch_isolates_missing_telemetry_and_preserves_authority_boundary(self):
        result = classify_pr_batch([None, decision_fixture("LOW")])
        self.assertEqual([row["disposition"] for row in result], ["INTERNAL_REPAIRABLE", "READY_TO_MERGE"])
        self.assertTrue(all(not row["authorized"] for row in result))

    def test_read_only_cli_is_concrete_existing_s1_entrypoint(self):
        import json, subprocess, sys
        from pathlib import Path
        script = Path(__file__).resolve().parents[2] / "scripts/governance/s1_release_evidence_classifier_v1.py"
        result = subprocess.run([sys.executable, str(script)], input=json.dumps([decision_fixture("LOW")]),
                                text=True, capture_output=True, check=True)
        output = json.loads(result.stdout)
        self.assertFalse(output["authorized"])
        self.assertEqual(output["results"][0]["disposition"], "READY_TO_MERGE")

    def test_head_changes_after_green_ci(self):
        r = decision_fixture(); r["current"]["head"] = "0" * 40
        self.check(r, "INTERNAL_REPAIRABLE", "EVALUATION_BINDING_CHANGED")

    def test_green_skipped_test_job(self):
        r = decision_fixture(); r["pr_jobs"][0]["executed_test_steps"] = 0
        self.check(r, "CI_NOT_EXECUTED")

    def test_manual_workflow_cannot_replace_pr_event(self):
        r = decision_fixture(); r["pr_jobs"][0]["event"] = "workflow_dispatch"
        self.check(r, "CI_NOT_EXECUTED")

    def test_repairable_original_branch_conflict(self):
        r = decision_fixture(); r["merge_state"] = "conflicting"
        self.check(r, "MERGE_CONFLICT", "ORIGINAL_BRANCH_CONFLICT")
        r["merge_state"] = "clean"
        self.check(r, "READY_TO_MERGE")

    def test_main_changes_between_validation_and_merge(self):
        r = decision_fixture(); r["current"]["main"] = "0" * 40
        self.check(r, "INTERNAL_REPAIRABLE", "EVALUATION_BINDING_CHANGED")

    def test_other_actor_merge_observed_without_merging_again(self):
        r = merged_fixture(); r["merge"]["actor"] = "OTHER_INTEGRATOR"
        out = self.check(r, "MERGED_VERIFIED")
        self.assertTrue(out["production_observation_pending"])

    def test_grok_commented_is_not_required_approval(self):
        r = decision_fixture(); r["review"]["state"] = "COMMENTED"
        self.check(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_required_independent_approved_missing(self):
        r = decision_fixture(); del r["review"]
        self.check(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_independent_approved_not_required_by_policy(self):
        r = decision_fixture(); r["independent_review_required"] = False; del r["review"]
        self.check(r, "READY_TO_MERGE")

    def test_disabled_binding_ruleset(self):
        r = decision_fixture(); r["rule_census"] = [{"binding": True, "enforcement": "disabled"}]
        self.check(r, "EXTERNAL_DEPENDENCY", "REQUIRED_RULES_NOT_ENFORCED")

    def test_disabled_nonbinding_ruleset_and_empty_census_do_not_create_new_gate(self):
        r = decision_fixture(); r["rule_census"] = [{"binding": False, "enforcement": "disabled"}]
        self.check(r, "READY_TO_MERGE")
        r["rule_census"] = []
        self.check(r, "READY_TO_MERGE")
        del r["rule_census"]
        self.check(r, "EXTERNAL_DEPENDENCY", "REQUIRED_RULE_CENSUS_MISSING")

    def test_concrete_p1_still_open(self):
        r = decision_fixture(); r["unresolved_p0_p1"] = True
        self.check(r, "INTERNAL_REPAIRABLE", "BLOCKING_FINDING_OPEN_OR_UNKNOWN")

    def test_physical_site_review_owner_waiver(self):
        r = decision_fixture(); r["physical_site_review_required"] = True
        self.check(r, "EXTERNAL_DEPENDENCY", "PHYSICAL_REVIEW_REQUIRED")
        r["owner_physical_review_waiver"] = True
        self.check(r, "READY_TO_MERGE")

    def test_blocked_p0_does_not_block_independent_candidate(self):
        blocked = decision_fixture(); blocked["priority"] = "P0"; del blocked["recovery"]
        self.check(blocked, "INDEPENDENT_RECOVERY_UNVERIFIED")
        self.check(decision_fixture("LOW"), "READY_TO_MERGE")

    def test_identical_blocker_twelve_ticks_no_repeated_receipt(self):
        r = decision_fixture(); del r["recovery"]; r["material_touches"] = 4
        previous = self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED")
        for minute in range(1, 13):
            r["now_utc"] = f"2026-11-04T10:{minute:02d}:00Z"
            r["previous_fingerprint"] = previous["fingerprint"]
            out = self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED")
            self.assertFalse(out["emit_receipt"])
            self.assertFalse(out["reactivated"])
            self.assertTrue(out["terminal_until_material_change"])

    def test_new_executed_ci_or_recovery_reactivates(self):
        for missing in ("pr_jobs", "recovery"):
            r = decision_fixture(); saved = r.pop(missing); r["material_touches"] = 4
            prior = classify_pr_disposition(r); r[missing] = saved
            r["previous_fingerprint"] = prior["fingerprint"]
            out = self.check(r, "READY_TO_MERGE")
            self.assertTrue(out["reactivated"])
            self.assertFalse(out["terminal_until_material_change"])

    def test_issue_timestamp_or_observation_clock_cannot_reactivate(self):
        r = decision_fixture(); r["recovery"]["independent_custody"] = False
        prior = classify_pr_disposition(r)
        r["previous_fingerprint"] = prior["fingerprint"]
        r["issue_updated_at"] = "2026-11-04T09:59:00Z"
        r["recovery"]["observed_at_utc"] = "2026-11-04T09:59:00Z"
        out = self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED")
        self.assertFalse(out["reactivated"])
        self.assertFalse(out["emit_receipt"])

    def test_merge_success_main_readback_failure(self):
        r = merged_fixture(); r["merge"]["blobs"][0]["actual_sha"] = "0" * 40
        self.check(r, "EXTERNAL_DEPENDENCY", "MERGE_MAIN_READBACK_UNVERIFIED")

    def test_pages_deployed_stale_source_is_pending_production(self):
        r = merged_fixture(); r["production"] = {"natural": True, "source": "0" * 40,
            "fresh": False, "public_readback": True}
        out = self.check(r, "MERGED_VERIFIED", "POST_FIX_OBSERVATION")
        self.assertTrue(out["production_observation_pending"])

    def test_natural_current_source_readback_is_separate_supplied_stage(self):
        r = merged_fixture(); r["production"] = {"natural": True, "source": r["current"]["source"],
            "fresh": True, "public_readback": True}
        out = self.check(r, "MERGED_VERIFIED", "NATURAL_PRODUCTION_EVIDENCE_SUPPLIED")
        self.assertFalse(out["production_observation_pending"])

    def test_computing_mergeability_is_not_a_conflict_or_repair_permission(self):
        r = decision_fixture(); r["merge_state"] = "unknown"
        self.check(r, "EXTERNAL_DEPENDENCY", "MERGEABILITY_COMPUTING_OR_RULE_BLOCKED")

    def test_other_writer_active_lease(self):
        r = decision_fixture(); r["active_writer_lease"] = True
        self.check(r, "EXTERNAL_DEPENDENCY", "WRITER_LEASE_ACTIVE_OR_UNKNOWN")

    def test_github_or_platform_denial_no_route_bypass(self):
        r = decision_fixture(); r["platform_denied"] = True
        out = self.check(r, "EXTERNAL_DEPENDENCY", "PLATFORM_ACTION_DENIED")
        self.assertIn("no alternate-route evasion", out["reactivation_trigger"])

    def test_identity_age_and_separation_negative_controls(self):
        cases = [("snapshot", "short"), ("manifest_sha256", "short"),
                 ("receipt_url", "https://github.com.evil/Donh91/x"),
                 ("observed_at_utc", "2026-11-03T00:00:00Z"),
                 ("observed_at_utc", "2026-11-05T00:00:00Z"),
                 ("observed_at_utc", "2026-02-30T00:00:00Z"), ("separation", False)]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                r = decision_fixture(); r["recovery"][key] = value
                self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED")

    def test_required_job_census_and_boolean_count(self):
        for key, value in (("required_pr_job_names", []), ("required_pr_job_names", ["test", "missing"]), ("pr_jobs", [])):
            r = decision_fixture(); r[key] = value; self.check(r, "CI_NOT_EXECUTED")
        r = decision_fixture(); r["pr_jobs"][0]["executed_test_steps"] = True
        self.check(r, "CI_NOT_EXECUTED")

    def test_policy_source_and_review_binding_changes(self):
        for key in ("policy", "source"):
            r = decision_fixture(); r["current"][key] = "0" * 40
            self.check(r, "INTERNAL_REPAIRABLE")
        r = decision_fixture(); r["review"]["head"] = "0" * 40
        self.check(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_review_reuse_only_if_current_policy_explicitly_allows(self):
        r = decision_fixture(); r["review"]["main"] = "0" * 40
        self.check(r, "REVIEW_REQUIRED_BY_POLICY")
        r["review_requires_current_main"] = False
        self.check(r, "READY_TO_MERGE")
        r["review"]["head"] = "0" * 40
        self.check(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_closed_superseded_and_source_gate(self):
        r = decision_fixture(); r["closed"] = True
        self.check(r, "EXTERNAL_DEPENDENCY")
        r["supersession"] = {"verified": True, "commit": "0" * 40,
                            "url": "https://github.com/Donh91/repo/pull/1"}
        self.check(r, "CLOSED_SUPERSEDED")
        r = decision_fixture(); r["source_science_gate"] = "ABSTAIN_PENDING_POLICY"
        self.check(r, "SOURCE_OR_SCIENCE_GATE")

    def test_missing_owner_mandate_and_invalid_url_fail_closed(self):
        r = decision_fixture(); del r["owner_authorized"]
        self.check(r, "EXTERNAL_DEPENDENCY", "OWNER_RELEASE_MANDATE_UNVERIFIED")
        r = decision_fixture(); r["recovery"]["receipt_url"] = "https://["
        self.check(r, "INDEPENDENT_RECOVERY_UNVERIFIED", "RECOVERY_IDENTITY_INCOMPLETE")



class ClaudeOwnerReviewAdmissionTests(unittest.TestCase):
    """Source-bound Claude advisory can meet S1's INTERNAL review only, not platform rules."""

    def base(self, risk="LOW", independence="INDEPENDENT"):
        r = decision_fixture(risk)
        r["review"] = {}
        r["repo_full_name"] = "Donh91/Investering-Framework-Archive-v1"
        r["pr_number"] = 2057
        r["expected_changed_paths"] = ["scripts/research/nonproduction_evidence.py"]
        r["native_rules_verified"] = True
        r["native_approval_required"] = False
        h = r["current"]["head"]
        r["claude_review"] = {
            "contract": "CLAUDE_REVIEW_v1",
            "verdict": "APPROVE", "repo": r["repo_full_name"], "pr": r["pr_number"],
            "head_sha": h, "requested_head_sha": h,
            "head": h, "policy": r["current"]["policy"],
            "source": r["current"]["source"], "main": r["current"]["main"],
            "risk_class": "HIGH_IMPACT" if risk == "HIGH" else risk,
            "report_sha256": "c" * 64, "body_sha256": "d" * 64,
            "independence": independence,
            "comment_id": 111111,
            "comment_url": "https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/173#issuecomment-111111",
            "body_readback_verified": True, "report_readback_verified": True,
        }
        return r

    def assert_still_advisory(self, r, expected):
        out = classify_pr_disposition(r)
        self.assertEqual(out["disposition"], expected, out)
        self.assertFalse(out["authorized"])
        self.assertFalse(out["externally_authenticated"])
        return out

    def test_independent_low_approved_exact_head(self):
        self.assert_still_advisory(self.base(), "READY_TO_MERGE")

    def test_self_authored_low_owner_exception_only(self):
        self.assert_still_advisory(self.base(independence="SELF_AUTHORED_DESIGN"), "READY_TO_MERGE")
        self.assert_still_advisory(self.base("MEDIUM", "SELF_AUTHORED_DESIGN"), "REVIEW_REQUIRED_BY_POLICY")

    def test_independent_medium_all_other_gates_remain(self):
        self.assert_still_advisory(self.base("MEDIUM"), "REVIEW_REQUIRED_BY_POLICY")

    def test_native_branch_approvals_never_replaced(self):
        for val in (True, None, "false", 0):
            r = self.base()
            r["native_approval_required"] = val
            self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_native_rules_not_verified_fails_closed(self):
        r = self.base()
        r["native_rules_verified"] = False
        self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_changed_head_and_mismatched_request_fail_closed(self):
        for field in ("head_sha", "requested_head_sha"):
            r = self.base()
            r["claude_review"][field] = "f" * 40
            self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_missing_or_fake_attestations_fail_closed(self):
        for field, value in (("report_sha256", "short"), ("body_sha256", None),
                             ("body_readback_verified", False),
                             ("report_readback_verified", "true"),
                             ("comment_url", "https://github.com.evil/pull/173#issuecomment-111111"),
                             ("verdict", "REQUEST_CHANGES"), ("pr", 2050)):
            r = self.base()
            r["claude_review"][field] = value
            self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_high_impact_needs_owner_ok_in_addition_to_custody(self):
        r = self.base("HIGH")
        self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")
        r["high_impact_owner_approval"] = {
            "approved": True,
            "repo": r["repo_full_name"],
            "pr": r["pr_number"],
            "head_sha": r["current"]["head"],
            "evidence_url": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-111111",
        }
        self.assert_still_advisory(r, "READY_TO_MERGE")
        r["recovery"]["independent_custody"] = False
        self.assert_still_advisory(r, "INDEPENDENT_RECOVERY_UNVERIFIED")

    def test_ci_and_source_gates_cannot_be_bypassed(self):
        r = self.base()
        r["pr_jobs"][0]["executed_test_steps"] = 0
        self.assert_still_advisory(r, "CI_NOT_EXECUTED")
        r = self.base()
        r["source_science_gate"] = "UNKNOWN"
        self.assert_still_advisory(r, "SOURCE_OR_SCIENCE_GATE")

    def test_review_identity_absent_routes_to_owner_without_waiver(self):
        r = self.base()
        r["claude_review"] = {}
        r["independent_reviewer_available"] = False
        out = self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")
        self.assertEqual(out["reason"], "INDEPENDENT_REVIEWER_IDENTITY_ABSENT")
        self.assertEqual(out["responsible_owner"], "REPOSITORY_OWNER")
        r["independent_reviewer_available"] = None
        out = self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")
        self.assertEqual(out["reason"], "REQUIRED_INDEPENDENT_APPROVAL_MISSING_OR_STALE")

    def test_malformed_risk_is_blocked_without_exception(self):
        for invalid in (None, 0, [], {}, True):
            with self.subTest(invalid=invalid):
                r = self.base()
                r["risk"] = invalid
                self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_claude_policy_source_and_main_binding_cannot_go_stale(self):
        for key in ("policy", "source", "main"):
            with self.subTest(key=key):
                r = self.base()
                r["claude_review"][key] = "f" * 40
                self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")
        r = self.base()
        r["review_requires_current_main"] = False
        r["claude_review"]["main"] = "f" * 40
        self.assert_still_advisory(r, "READY_TO_MERGE")
        r["claude_review"]["source"] = "f" * 40
        self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_claude_boolean_pr_is_not_number_one(self):
        r = self.base()
        r["pr_number"] = 1
        r["claude_review"]["pr"] = True
        self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_unrecognized_medium_risk_cannot_evade_high_impact_guards(self):
        r = self.base("MEDIUM")
        self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")
        r["review"] = {**r["current"], "state": "APPROVED", "independent": True}
        self.assert_still_advisory(r, "INTERNAL_REPAIRABLE")

    def test_high_impact_owner_approval_must_bind_repo_pr_head_and_url(self):
        r = self.base("HIGH")
        good = {
            "approved": True, "repo": r["repo_full_name"],
            "pr": r["pr_number"], "head_sha": r["current"]["head"],
            "evidence_url": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-111111",
        }
        r["high_impact_owner_approval"] = good
        self.assert_still_advisory(r, "READY_TO_MERGE")
        for field, bad in (
            ("approved", 1), ("repo", "Donh91/other"), ("pr", True),
            ("pr", 2058), ("head_sha", "f" * 40),
            ("evidence_url", "https://github.com.evil/Donh91/repo/issues/1")
        ):
            with self.subTest(field=field, bad=bad):
                tampered = copy.deepcopy(r)
                tampered["high_impact_owner_approval"][field] = bad
                self.assert_still_advisory(tampered, "REVIEW_REQUIRED_BY_POLICY")
        for invalid in (True, False, None, "approved", []):
            with self.subTest(invalid=invalid):
                tampered = copy.deepcopy(r)
                tampered["high_impact_owner_approval"] = invalid
                self.assert_still_advisory(tampered, "REVIEW_REQUIRED_BY_POLICY")


    def test_grok_g1_owner_comment_url_must_be_original_or_canonical(self):
        r = self.base("HIGH")
        r["high_impact_owner_approval"] = {
            "approved": True, "repo": r["repo_full_name"],
            "pr": r["pr_number"], "head_sha": r["current"]["head"],
            "evidence_url": "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-111111",
        }
        self.assert_still_advisory(r, "READY_TO_MERGE")
        invalid = (
            "https://github.com/Donh91/unrelated-repo/blob/main/README.md",
            r["claude_review"]["comment_url"],
            "https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2058#issuecomment-111111",
            "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156",
            "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156#issuecomment-0",
            "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156?foo=bar#issuecomment-111111",
        )
        for url in invalid:
            with self.subTest(url=url):
                x = copy.deepcopy(r)
                x["high_impact_owner_approval"]["evidence_url"] = url
                self.assert_still_advisory(x, "REVIEW_REQUIRED_BY_POLICY")
        r["high_impact_owner_approval"]["evidence_url"] = (
            "https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2057#issuecomment-111111")
        self.assert_still_advisory(r, "READY_TO_MERGE")

    def test_grok_g2_low_risk_self_authored_path_guard_without_general_optin(self):
        r = self.base("LOW", "SELF_AUTHORED_DESIGN")
        self.assert_still_advisory(r, "READY_TO_MERGE")
        for path in ("AGENTS.md", ".github/workflows/risky.yml",
                     "01_CORE_FRAMEWORK/governance/guard.md",
                     "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md",
                     "scripts/governance/s1_release_evidence_classifier_v1.py",
                     "scripts/governance/s1_general_release_evidence_v1.py",
                     "scripts/governance/s1_native_handoff_auth_v1.py",
                     "scripts/governance/s1_agent_handoff_receipts_v1.py",
                     "scripts/governance/check_codex_review_finality.py",
                     "tests/governance/test_s1_general_release_evidence_v1.py"):
            with self.subTest(path=path):
                x = copy.deepcopy(r)
                x["expected_changed_paths"] = [path]
                self.assert_still_advisory(x, "REVIEW_REQUIRED_BY_POLICY")

    def test_claude_advisory_path_census_must_exist_and_be_well_formed(self):
        for paths in (None, [], ["../escape.py"], ["safe.py", "safe.py"], [None]):
            with self.subTest(paths=paths):
                r = self.base()
                r["expected_changed_paths"] = paths
                self.assert_still_advisory(r, "REVIEW_REQUIRED_BY_POLICY")

    def test_native_independent_approval_still_works(self):
        r = self.base()
        r["review"] = decision_fixture("LOW")["review"]
        r["claude_review"] = None
        r["native_approval_required"] = True
        self.assert_still_advisory(r, "READY_TO_MERGE")


if __name__ == "__main__":
    unittest.main()


class S1GeneralIntegrationTests(unittest.TestCase):
    """A single existing S1 advisory CLI, not a second permission engine."""

    def packet(self):
        r = decision_fixture("LOW")
        r["independent_review_required"] = False
        h = r["current"]["head"]
        m = r["current"]["main"]
        r["expected_changed_paths"] = ["scripts/governance/example.py"]
        r["s1_general_preflight_required"] = True
        r["s1_general_preflight"] = {
            "head": h, "main": m, "review_head": h, "owner_head": h,
            "ci_head": h, "owner_authenticated": True,
            "effective_write": True, "one_editor_lease": True,
            "rules_verified": True, "native_reviews_satisfied": True,
            "source_and_science_satisfied": True, "high_impact": False,
            "remote_write_state": "CONFIRMED", "main_unchanged": True,
            "required_tests": ["positive", "guard-removal"],
            "executed_tests": ["positive", "guard-removal"],
            "ci_pr_event": True, "ci_success": True,
        }
        r["pr_jobs"][0]["executed_test_ids"] = ["positive", "guard-removal"]
        return r

    def check(self, mutate, reason):
        record = self.packet()
        mutate(record)
        result = classify_pr_disposition(record)
        self.assertEqual(result["reason"], reason)
        self.assertFalse(result["authorized"])

    def test_matched_native_jobs_still_only_advisory(self):
        result = classify_pr_disposition(self.packet())
        self.assertEqual(result["disposition"], "READY_TO_MERGE")
        self.assertFalse(result["authorized"])
        self.assertFalse(result["externally_authenticated"])

    def test_missing_preflight_must_fail_closed(self):
        self.check(lambda r: r.pop("s1_general_preflight"), "S1_GENERAL_INVALID_SNAPSHOT")

    def test_stale_main_must_fail_closed(self):
        self.check(lambda r: r["s1_general_preflight"].update(main="c"*40),
                   "S1_GENERAL_NATIVE_BINDING_MISMATCH")

    def test_inconsistent_risk_cannot_downgrade_custody(self):
        self.check(lambda r: r["s1_general_preflight"].update(high_impact=True, independent_custody=True),
                   "S1_GENERAL_NATIVE_BINDING_MISMATCH")

    def test_forged_extra_executed_test(self):
        self.check(lambda r: r["s1_general_preflight"]["executed_tests"].append("extra"),
                   "S1_GENERAL_TEST_PROOF_MISMATCH")

    def test_required_test_absent_in_native_jobs(self):
        self.check(lambda r: r["pr_jobs"][0].update(executed_test_ids=["positive"]),
                   "S1_GENERAL_TEST_PROOF_MISMATCH")

    def test_duplicate_native_job_refused(self):
        self.check(lambda r: r["pr_jobs"].append(dict(r["pr_jobs"][0])),
                   "S1_GENERAL_NATIVE_JOB_NOT_EXECUTED")

    def test_stale_native_job_refused(self):
        self.check(lambda r: r["pr_jobs"][0].update(head="c"*40),
                   "S1_GENERAL_NATIVE_JOB_NOT_EXECUTED")

    def test_skipped_job_is_not_evidence(self):
        self.check(lambda r: r["pr_jobs"][0].update(conclusion="skipped"),
                   "S1_GENERAL_NATIVE_JOB_NOT_EXECUTED")

    def test_invalid_native_test_identity(self):
        for invalid in (None, 7, "", [], {}):
            with self.subTest(invalid=invalid):
                self.check(lambda r, value=invalid: r["pr_jobs"][0].update(executed_test_ids=[value]),
                           "S1_GENERAL_NATIVE_TEST_IDS_UNVERIFIED")

    def test_duplicate_or_padded_native_job_id(self):
        for ids in (["positive", "positive", "guard-removal"], ["positive ", "guard-removal"]):
            with self.subTest(ids=ids):
                self.check(lambda r, v=ids: r["pr_jobs"][0].update(executed_test_ids=v),
                           "S1_GENERAL_NATIVE_TEST_IDS_UNVERIFIED")

    def test_workflow_marked_low_fails_closed(self):
        self.check(lambda r: r.update(expected_changed_paths=[".github/workflows/recovery.yml"]),
                   "HIGH_IMPACT_PATH_MARKED_LOW")

    def test_canonical_governance_marked_low_fails_closed(self):
        for path in ("AGENTS.md", "01_CORE_FRAMEWORK/governance/policy.md",
                     "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md"):
            with self.subTest(path=path):
                self.check(lambda r, value=path: r.update(expected_changed_paths=[value]),
                           "HIGH_IMPACT_PATH_MARKED_LOW")

    def test_missing_or_bad_native_path_census(self):
        for paths in (None, [], ["../escape.py"], ["a.py", "a.py"], [None]):
            with self.subTest(paths=paths):
                self.check(lambda r, value=paths: r.update(expected_changed_paths=value),
                           "S1_GENERAL_NATIVE_PATH_CENSUS_MISSING")

    def test_each_required_substantive_job_needs_native_test_ids(self):
        def change(r):
            r["required_pr_job_names"] = ["ci", "guard"]
            r["pr_jobs"] = [
                dict(r["pr_jobs"][0], name="ci"),
                dict(r["pr_jobs"][0], name="guard", executed_test_ids=[]),
            ]
        self.check(change, "S1_GENERAL_NATIVE_TEST_IDS_UNVERIFIED")

    def test_general_manifest_change_rekeys_same_advisory_state(self):
        r = self.packet()
        initial = classify_pr_disposition(r)
        self.assertEqual(initial["disposition"], "READY_TO_MERGE")
        updated = self.packet()
        updated["s1_general_preflight"]["required_tests"] = ["positive"]
        updated["previous_fingerprint"] = initial["fingerprint"]
        result = classify_pr_disposition(updated)
        self.assertEqual(result["disposition"], "READY_TO_MERGE")
        self.assertFalse(result["authorized"])
        self.assertNotEqual(result["fingerprint"], initial["fingerprint"])
        self.assertTrue(result["emit_receipt"])

    def test_general_opt_in_removed_rekeys_same_advisory_state(self):
        r = self.packet()
        initial = classify_pr_disposition(r)
        legacy = self.packet()
        del legacy["s1_general_preflight"]
        del legacy["s1_general_preflight_required"]
        legacy["previous_fingerprint"] = initial["fingerprint"]
        result = classify_pr_disposition(legacy)
        self.assertEqual(result["disposition"], "READY_TO_MERGE")
        self.assertNotEqual(result["fingerprint"], initial["fingerprint"])
        self.assertTrue(result["emit_receipt"])

    def test_untrusted_opt_in_type(self):
        self.check(lambda r: r.update(s1_general_preflight_required=1),
                   "S1_GENERAL_OPT_IN_UNVERIFIED")

    def test_no_preflight_optin_cannot_silently_skip(self):
        self.check(lambda r: r.update(s1_general_preflight_required=False),
                   "S1_GENERAL_OPT_IN_UNVERIFIED")

    def test_legacy_existing_calls_preserved(self):
        r = self.packet()
        del r["s1_general_preflight"]
        del r["s1_general_preflight_required"]
        self.assertEqual(classify_pr_disposition(r)["disposition"], "READY_TO_MERGE")
