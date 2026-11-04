"""Opportunity, research reactivation and Strategist governance tests."""
import unittest
from scripts.governance.s1_opportunity_recovery_v1 import (
    AdvisoryInputError, reactivated, select_cases, select_cases_isolated, strategic_question,
)

URL = "https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1877"
CASE = dict(case_id="Archive#1877", original_url=URL, owner="S1",
            evidence_fingerprint="sha-source-12345", priority="P1",
            status="ACTIONABLE", authority="OWNER_GOVERNED")


def blocker():
    return {**CASE, "status": "BLOCKED_WITH_TRIGGER", "material_trigger": {
        "kind": "executed_ci", "previous": "old-data-1234",
        "current": "old-data-1234", "native_evidence_url": URL,
    }}


class OpportunityTests(unittest.TestCase):
    def test_native_actions_run_and_job_reactivate_ci_only(self):
        for suffix in ("/actions/runs/123", "/actions/runs/123/job/456"):
            row = blocker()
            row["material_trigger"].update(current="new-data-1234", native_evidence_url=
                "https://github.com/Donh91/Investering-Framework-Archive-v1" + suffix)
            self.assertTrue(reactivated(row))
            row["material_trigger"]["kind"] = "clock"
            self.assertFalse(reactivated(row))

    def test_forged_or_malformed_actions_url_not_reactivation(self):
        for url in ("https://github.com.evil/Donh91/repo/actions/runs/123",
                    "https://github.com/Donh91/repo/actions/runs/abc",
                    "https://github.com/Other/repo/actions/runs/123",
                    "https://github.com/Donh91/repo/actions/runs/123/../../1"):
            row = blocker(); row["material_trigger"].update(current="new-data-1234", native_evidence_url=url)
            self.assertFalse(reactivated(row))

    def test_invalid_case_isolated_without_hiding_repair(self):
        out = select_cases_isolated([{}, CASE, None, {**CASE, "priority": "bad"}])
        self.assertEqual(len(out["selected"]), 1)
        self.assertEqual(len(out["invalid_cases"]), 3)
        self.assertTrue(all(row["other_prs_may_continue"] for row in out["invalid_cases"]))
        self.assertFalse(out["release_authority"])
        with self.assertRaises(AdvisoryInputError):
            select_cases([{}, CASE])  # legacy strict API unchanged

    def test_static_blocker_skipped(self):
        self.assertEqual(select_cases([blocker()]), [])

    def test_new_real_trigger(self):
        row = blocker()
        row["material_trigger"]["current"] = "new-data-1234"
        self.assertTrue(reactivated(row))
        self.assertEqual(select_cases([row])[0]["trigger"], "MATERIAL")

    def test_clock_does_not_reactivate(self):
        row = blocker()
        row["material_trigger"]["kind"] = "clock"
        row["material_trigger"]["current"] = "new-data-1234"
        self.assertFalse(reactivated(row))

    def test_p0_strictly_precedes_score(self):
        p0 = {**CASE, "case_id": "urgent",
              "original_url": URL.replace("1877", "1156"),
              "priority": "P0", "impact": 1}
        low = {**CASE, "impact": 5}
        self.assertEqual(select_cases([low, p0])[0]["case_id"], "urgent")

    def test_dedupe_original_work(self):
        self.assertEqual(len(select_cases([CASE, {**CASE, "case_id": "duplicate"}])), 1)

    def test_no_lease_or_broken_safety(self):
        self.assertEqual(select_cases([{**CASE, "active_head_editor": True}]), [])
        self.assertEqual(select_cases([{**CASE, "safety_gate": "FAILED"}]), [])

    def test_never_authorizes_merge(self):
        result = select_cases([{**CASE, "ready_for_preflight": True}])
        self.assertFalse(result[0]["release_authority"])
        self.assertEqual(result[0]["decision"], "VERIFY_CURRENT_GATES")

    def test_invalid_priority_and_volume(self):
        with self.assertRaises(AdvisoryInputError):
            select_cases([{**CASE, "priority": "P-9"}])
        with self.assertRaises(AdvisoryInputError):
            select_cases([CASE], maximum=4)

    def test_strategist_must_be_advisory(self):
        problem = {**CASE, "ambiguous_owner": True}
        good = {"contract": "FRAMEWORK_STRATEGIST_BRIEF_v1",
                "authority": {"type": "ADVISORY_ONLY"},
                "input_status": "CURRENT", "intent_sha256": "abc123",
                "generated_at_utc": "2026-11-02T10:00:00Z"}
        self.assertEqual(strategic_question(problem, good)["state"], "SOURCE_UNVERIFIED")
        with self.assertRaises(AdvisoryInputError):
            strategic_question(problem, {**good, "authority": {"type": "MERGE"}})

    def test_missing_strategist_is_not_approval(self):
        result = strategic_question({**CASE, "cross_domain_conflict": True}, None)
        self.assertEqual(result["state"], "SOURCE_UNAVAILABLE")
        self.assertFalse(result["release_authority"])

    def test_static_hold_cannot_occupy_slots(self):
        p0 = {**blocker(), "priority": "P0"}
        selected = select_cases([p0, CASE])
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["case_id"], CASE["case_id"])


if __name__ == "__main__":
    unittest.main()
