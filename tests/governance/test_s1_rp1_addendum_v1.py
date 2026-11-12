"""RP1 addendum v1 (Grok 2026-11-12): effective-rules census cross-check + RP1-only test-type residual (Fable M7)."""
import unittest

from scripts.governance.s1_release_evidence_classifier_v1 import classify_pr_disposition, rp1_rule_census
from tests.governance.test_s1_release_process_v1 import ready


def act(r):
    o = classify_pr_disposition(r)
    assert o["authorized"] is False and o["externally_authenticated"] is False
    return o["release_action"], o["reason"]


class EffectiveRules(unittest.TestCase):
    def with_eff(self, http=200, eff=None):
        r = ready(); r["native_rule_reads"].update(effective_rules_http=http, effective_rules=[] if eff is None else eff)
        return r

    def test_empty_effective_rules_agree_with_disabled_ruleset_ready(self):  # observed 2026-11-12: []
        r = self.with_eff()
        self.assertEqual(rp1_rule_census(r["native_rule_reads"]), ([], True))
        self.assertEqual(act(r)[0], "READY")

    def test_absent_key_is_legacy_behaviour(self):
        self.assertEqual(act(ready())[0], "READY")

    def test_effective_endpoint_unavailable_is_optional_corroboration(self):  # superseded by RP1 05
        for http in (400, 403, 404, 500, None, "CONNECTOR_REJECTED"):
            with self.subTest(http=http):
                o = classify_pr_disposition(self.with_eff(http=http))
                self.assertEqual(o["release_action"], "READY")
                self.assertEqual(o["rule_census_meta"]["effective_rules_endpoint"], "UNAVAILABLE")

    def test_effective_rule_contradicting_disabled_ruleset_rechecks(self):
        r = self.with_eff(eff=[{"type": "pull_request", "ruleset_id": 25307191}])
        self.assertIsNone(rp1_rule_census(r["native_rule_reads"]))
        self.assertEqual(act(r), ("RECHECK", "RULE_CENSUS_UNAVAILABLE"))

    def test_effective_rule_from_unlisted_parent_ruleset_rechecks(self):
        r = self.with_eff(eff=[{"type": "required_status_checks", "ruleset_id": 999}])
        self.assertEqual(act(r)[0], "RECHECK")

    def test_active_ruleset_and_matching_effective_rule_escalates(self):
        r = self.with_eff(eff=[{"type": "pull_request", "ruleset_id": 25307191}])
        r["native_rule_reads"]["rulesets"][0]["enforcement"] = "active"
        self.assertEqual(act(r), ("ESCALATE_OWNER", "RP1_ACTIVE_RULES_REQUIRE_NATIVE_COMPLIANCE"))

    def test_malformed_effective_rules_recheck(self):
        for eff in ({"x": 1}, [1], [{"type": "pull_request"}], [{"type": 3, "ruleset_id": 1}], "[]"):
            with self.subTest(eff=eff):
                r = ready(); r["native_rule_reads"].update(effective_rules_http=200, effective_rules=eff)
                self.assertEqual(act(r)[0], "RECHECK")

    def test_never_ready_on_active_census(self):
        r = self.with_eff(eff=[{"type": "deletion", "ruleset_id": 25307191}])
        r["native_rule_reads"]["rulesets"][0]["enforcement"] = "active"
        self.assertNotEqual(act(r)[0], "READY")


def code_with(path, scope="tests/research", ids=None):
    r = ready([{"path": "scripts/research/x_v1.py", "status": "added"}, {"path": path, "status": "added"}])
    r["source_science_gate"] = "PASS"
    r["pr_jobs"][0].update(executed_scope_paths=[scope], executed_scope_unmasked=True)
    if ids is not None:
        r["pr_jobs"][0]["executed_test_ids"] = ids
    return r


class TestTypeResidual(unittest.TestCase):  # Fable M7 residual inside RP1 (found 2026-11-12 10:30 CET)
    def test_nested_conftest_not_covered_holds(self):
        self.assertEqual(act(code_with("tests/research/conftest.py", scope="tests/elsewhere")),
                         ("HOLD", "CHANGED_TESTS_NOT_EXECUTED"))

    def test_nested_conftest_dir_scope_without_verified_load_id_holds(self):
        # Discovery -p can exclude a suite even when the directory exists.
        # A conftest/fixture is not a collected test file by default.
        self.assertEqual(act(code_with("tests/research/conftest.py")),
                         ("HOLD", "CHANGED_TESTS_NOT_EXECUTED"))

    def test_nested_conftest_exact_native_load_id_can_qualify(self):
        path = "tests/research/conftest.py"
        self.assertEqual(act(code_with(path, ids=[path]))[0], "READY")

    def test_shell_test_not_covered_by_pytest_scope_holds(self):
        for p in ("tests/research/run_x.sh", "scripts/research/test_x.sh"):
            with self.subTest(path=p):
                self.assertEqual(act(code_with(p, scope=p.rsplit("/", 1)[0])), ("HOLD", "CHANGED_TESTS_NOT_EXECUTED"))

    def test_shell_test_with_exact_executed_id_ready(self):
        p = "tests/research/run_x.sh"
        self.assertEqual(act(code_with(p, ids=[p]))[0], "READY")

    def test_plain_script_sh_outside_tests_is_not_a_test(self):
        self.assertEqual(act(code_with("scripts/research/build.sh", scope="tests/elsewhere"))[0], "READY")


if __name__ == "__main__":
    unittest.main()
