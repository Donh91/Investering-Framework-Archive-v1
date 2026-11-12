"""RP1 patch 05 (Grok 2026-11-12): tiered rule census with OPTIONAL effective-rules endpoint,
ruleset target/conditions evaluation, G3 changed_files count, G1 'changed' status, honest lease=None.
Context: ChatGPT connector gets HTTP 400 on GET /rules/branches/main (Bridge #179 6819982483)."""
import copy
import unittest

from scripts.governance.s1_release_evidence_classifier_v1 import classify_pr_disposition, rp1_rule_census
from tests.governance.test_s1_release_process_v1 import H, ready, code_ready

ESC = ("ESCALATE_OWNER", "RP1_ACTIVE_RULES_REQUIRE_NATIVE_COMPLIANCE")
RCK = ("RECHECK", "RULE_CENSUS_UNAVAILABLE")
PCM = ("RECHECK", "RP1_PATH_CENSUS_MISSING")


def run(r):
    o = classify_pr_disposition(r)
    assert o["authorized"] is False and o["externally_authenticated"] is False
    return o


def act(r):
    o = run(r)
    return o["release_action"], o["reason"]


def live_reads(eff_http=400):
    """Shape of the 2026-11-12 native reads (raw/ in the Bridge report): owner type User, default branch main,
    one DISABLED ~DEFAULT_BRANCH ruleset, unprotected main, classic detail 401/403, effective rules per client."""
    return {"branch_http": 200, "protected": False, "protection_enabled": False, "protection_detail_http": 403,
            "rulesets_http": 200, "rulesets_pages_complete": True, "rulesets_includes_parents": True,
            "repo_owner_type": "User", "default_branch": "main",
            "rulesets": [{"id": 25307191, "enforcement": "disabled", "target": "branch", "source_type": "Repository",
                          "detail_http": 200,
                          "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}}}],
            "effective_rules_http": eff_http, "effective_rules": [] if eff_http == 200 else None}


def with_reads(reads, census=None):
    r = ready(); r["native_rule_reads"] = reads
    if census is not None:
        r["rule_census"] = census
    return r


def active_rs(**kw):
    rs = {"id": 77, "enforcement": "active", "target": "branch", "source_type": "Repository", "detail_http": 200,
          "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}}}
    rs.update(kw)
    return rs


class EffectiveRulesOptional(unittest.TestCase):
    def test_unavailable_and_no_rules_unprotected_census_ok_ready(self):
        for http in (400, 401, 403, 404, 500, None, "CONNECTOR_REJECTED"):
            for rulesets in ([], live_reads()["rulesets"]):
                with self.subTest(http=http, n=len(rulesets)):
                    reads = live_reads(); reads.update(effective_rules_http=http, effective_rules=None, rulesets=rulesets)
                    self.assertEqual(rp1_rule_census(reads), ([], True))
                    o = run(with_reads(reads))
                    self.assertEqual(o["release_action"], "READY")
                    self.assertEqual(o["rule_census_meta"]["effective_rules_endpoint"], "UNAVAILABLE")
                    self.assertEqual(o["rule_census_meta"]["org_rulesets"], "NOT_APPLICABLE_USER_OWNED_REPO")

    def test_live_shape_both_readable_and_agree_ready(self):
        o = run(with_reads(live_reads(eff_http=200)))
        self.assertEqual(o["release_action"], "READY")
        self.assertEqual(o["rule_census_meta"]["effective_rules_endpoint"], "READ_AGREES_WITH_PRIMARY")

    def test_unavailable_plus_active_ruleset_on_main_is_evaluated_not_ignored(self):
        reads = live_reads(); reads["rulesets"].append(active_rs())
        self.assertEqual(act(with_reads(reads)), ESC)

    def test_unavailable_plus_active_ruleset_with_unreadable_detail_assumed_applies(self):
        for rs in (active_rs(detail_http=403, conditions=None), {"id": 78, "enforcement": "active", "target": "branch"},
                   {"id": 79, "enforcement": "active", "applies_to_main": False}):  # legacy shape: unverifiable False
            with self.subTest(rs=rs):
                reads = live_reads(); reads["rulesets"] = [rs]
                self.assertEqual(act(with_reads(reads)), ESC)

    def test_both_readable_and_disagree_rechecks(self):
        for eff in ([{"type": "pull_request", "ruleset_id": 25307191}],  # disabled per (a), active per (b)
                    [{"type": "required_status_checks", "ruleset_id": 999}]):  # parent ruleset invisible to (a)
            with self.subTest(eff=eff):
                reads = live_reads(eff_http=200); reads["effective_rules"] = eff
                o = run(with_reads(reads))
                self.assertEqual((o["release_action"], o["reason"]), RCK)

    def test_disagreement_with_binding_primary_still_escalates(self):
        reads = live_reads(eff_http=200); reads["rulesets"].append(active_rs())  # (b) says [] but (a) binding
        o = run(with_reads(reads))
        self.assertEqual((o["release_action"], o["reason"]), ESC)
        self.assertEqual(o["rule_census_meta"]["effective_rules_endpoint"], "READ_DISAGREES_WITH_PRIMARY")

    def test_both_readable_agree_on_active_escalates(self):
        reads = live_reads(eff_http=200); reads["rulesets"].append(active_rs())
        reads["effective_rules"] = [{"type": "pull_request", "ruleset_id": 77}]
        self.assertEqual(act(with_reads(reads)), ESC)

    def test_malformed_200_effective_rechecks(self):
        for eff in ({"x": 1}, [1], [{"type": "pull_request"}], "[]", None):
            with self.subTest(eff=eff):
                reads = live_reads(eff_http=200); reads["effective_rules"] = eff
                self.assertEqual(act(with_reads(reads)), RCK)


class PrimaryTierFailures(unittest.TestCase):
    def test_rulesets_error_rechecks(self):
        for http in (400, 403, 404, 500, None):
            with self.subTest(http=http):
                reads = live_reads(eff_http=200); reads["rulesets_http"] = http
                self.assertEqual(act(with_reads(reads)), RCK)

    def test_branch_error_incomplete_pages_or_parents_excluded_recheck(self):
        for k, v in (("branch_http", 403), ("rulesets_pages_complete", False), ("rulesets_includes_parents", False),
                     ("protected", None), ("rulesets", None), ("protection_enabled", True)):
            with self.subTest(k=k):
                reads = live_reads(); reads[k] = v
                self.assertEqual(act(with_reads(reads)), RCK)

    def test_unknown_target_or_enforcement_rechecks(self):
        for rs in (dict(active_rs(), target="weird"), dict(active_rs(), enforcement="on")):
            with self.subTest(rs=rs):
                reads = live_reads(); reads["rulesets"] = [rs]
                self.assertEqual(act(with_reads(reads)), RCK)

    def test_supplied_applies_false_contradicting_conditions_rechecks(self):
        reads = live_reads(); reads["rulesets"] = [active_rs(applies_to_main=False)]
        self.assertEqual(act(with_reads(reads)), RCK)

    def test_protection_present_never_ignored(self):
        reads = live_reads(); reads.update(protected=True, protection_enabled=True)
        self.assertEqual(act(with_reads(reads)), ESC)  # detail 403 => binding, unverifiable
        reads.update(protection_detail_http=200, protection_requirements=["required_status_checks"])
        self.assertEqual(act(with_reads(reads)), ESC)
        reads.update(protection_requirements=[])
        self.assertEqual(act(with_reads(reads)), ESC)


class TargetsAndConditions(unittest.TestCase):
    def case(self, rs, default_branch="main"):
        reads = live_reads(); reads["rulesets"] = [rs]; reads["default_branch"] = default_branch
        return act(with_reads(reads))

    def test_not_applicable_active_rulesets_are_skipped(self):
        for rs in (active_rs(target="tag"),
                   active_rs(conditions={"ref_name": {"include": ["refs/heads/release/*"], "exclude": []}}),
                   active_rs(conditions={"ref_name": {"include": ["~ALL"], "exclude": ["refs/heads/main"]}})):
            with self.subTest(rs=rs):
                self.assertEqual(self.case(rs)[0], "READY")
        self.assertEqual(self.case(active_rs(), default_branch="trunk")[0], "READY")

    def test_applicable_or_ambiguous_active_rulesets_escalate(self):
        for rs in (active_rs(conditions={"ref_name": {"include": ["refs/heads/ma*"], "exclude": []}}),
                   active_rs(conditions={"ref_name": {"include": ["~ALL"], "exclude": ["refs/heads/ma*"]}}),  # wildcard exclude ignored
                   active_rs(conditions={"ref_name": {"include": ["refs/heads/main"]}}),
                   active_rs(target="push"), active_rs(target="repository"),
                   active_rs(source_type="Organization",
                             conditions={"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []},
                                         "repository_name": {"include": ["~ALL"], "exclude": []}}),
                   active_rs(conditions={"ref_name": "garbage"})):
            with self.subTest(rs=rs):
                self.assertEqual(self.case(rs), ESC)
        self.assertEqual(self.case(active_rs(), default_branch=None), ESC)  # unknown default => assume main

    def test_evaluate_ruleset_on_main_is_censused_non_binding(self):
        reads = live_reads(); reads["rulesets"] = [active_rs(enforcement="evaluate")]
        census = rp1_rule_census(reads)[0]
        self.assertEqual([(c["id"], c["binding"], c["enforcement"]) for c in census], [(77, False, "evaluate")])
        self.assertEqual(act(with_reads(reads))[1], "RP1_EVIDENCE_MISMATCH")  # supplied [] hides it
        self.assertEqual(act(with_reads(reads, census=census))[0], "READY")


class G3ChangedFilesCount(unittest.TestCase):
    def truncated(self):
        r = code_ready()  # 2 changed files; the PR-files page omitted the test file
        r["expected_changed_paths"] = ["scripts/research/x_v1.py"]
        r["changed_file_statuses"] = [s for s in r["changed_file_statuses"] if s["path"] == "scripts/research/x_v1.py"]
        r["pr_changed_files_count"] = 2
        return r

    def test_truncated_consistent_census_is_not_ready(self):
        self.assertEqual(act(self.truncated()), PCM)

    def test_count_missing_wrong_head_or_type_rechecks(self):
        for k, v in (("pr_changed_files_count", None), ("pr_changed_files_count", "2"), ("pr_changed_files_count", 3),
                     ("pr_changed_files_count", True), ("pr_changed_files_count_head_sha", "d" * 40)):
            with self.subTest(k=k, v=v):
                r = code_ready(); r[k] = v
                self.assertEqual(act(r), PCM)
        r = code_ready(); del r["pr_changed_files_count"]
        self.assertEqual(act(r), PCM)

    def test_unlistable_over_3000_rechecks(self):
        r = ready([{"path": "docs/n%d.md" % i, "status": "added"} for i in range(3001)])
        self.assertEqual(act(r), PCM)

    def test_complete_count_ready(self):
        self.assertEqual(act(code_ready())[0], "READY")


class G1ChangedStatus(unittest.TestCase):
    def rec(self, status, exists=True, rp1=True):
        r = code_ready()
        for s in r["changed_file_statuses"]:
            if s["path"].startswith("tests/"):
                s["status"], s["head_exists"] = status, exists
        if not rp1:
            for k in ("release_process", "release_lane", "draft", "owner_mandate", "native_rule_reads",
                      "merge_layers", "writer_lease", "pr_run_census", "privacy_check"):
                r.pop(k)
        return r

    def test_rp1_changed_mode_status_with_head_exists_ready(self):
        self.assertEqual(act(self.rec("changed"))[0], "READY")

    def test_changed_without_head_or_unchanged_rechecks(self):
        self.assertEqual(act(self.rec("changed", exists=False)), ("RECHECK", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"))
        self.assertEqual(act(self.rec("unchanged")), ("RECHECK", "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED"))

    def test_legacy_changed_semantics_unchanged(self):
        self.assertEqual(run(self.rec("changed", rp1=False))["reason"], "CHANGED_TEST_NATIVE_STATUS_UNVERIFIED")


class HonestLease(unittest.TestCase):  # ChatGPT #1156 6819641191 A / D4: optimistic concurrency, not a lease
    def test_explicit_unknown_lease_with_occ_evidence_ready(self):
        r = ready(); r["active_writer_lease"] = None
        self.assertEqual(act(r)[0], "READY")

    def test_absent_or_true_or_weak_occ_not_ready(self):
        r = ready(); del r["active_writer_lease"]
        self.assertEqual(act(r)[1], "WRITER_LEASE_ACTIVE_OR_UNKNOWN")
        r = ready(); r["active_writer_lease"] = True
        self.assertEqual(act(r)[1], "WRITER_LEASE_ACTIVE_OR_UNKNOWN")
        r = ready(); r["active_writer_lease"] = None; r["writer_lease"]["head_reads"] = [H]
        self.assertEqual(act(r)[1], "WRITER_LEASE_ACTIVE_OR_UNKNOWN")
        r = ready(); r["active_writer_lease"] = 0
        self.assertEqual(act(r)[1], "WRITER_LEASE_ACTIVE_OR_UNKNOWN")

    def test_legacy_none_still_blocked(self):
        r = ready(); r["source_science_gate"] = "PASS"; r["active_writer_lease"] = None
        for k in ("release_process", "release_lane", "draft", "owner_mandate", "native_rule_reads",
                  "merge_layers", "writer_lease", "pr_run_census", "privacy_check"):
            r.pop(k)
        self.assertEqual(run(r)["reason"], "WRITER_LEASE_ACTIVE_OR_UNKNOWN")


if __name__ == "__main__":
    unittest.main()
