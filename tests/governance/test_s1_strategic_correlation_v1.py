"""Correlate original cases and existing Strategist proposals without dispatch."""
import unittest
from scripts.governance.s1_opportunity_recovery_v1 import (
    select_cases, strategic_question,
)

URL = "https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1877"
CASE = dict(case_id="Archive#1877", original_url=URL, owner="S1",
            evidence_fingerprint="fingerprint1234", priority="P1",
            status="ACTIONABLE", authority="OWNER_GOVERNED")


class StrategicCorrelationTests(unittest.TestCase):
    def test_permalink_is_same_original_case(self):
        copies = [
            CASE,
            {**CASE, "case_id": "duplicate", "original_url": URL + "/"},
            {**CASE, "case_id": "tracking", "original_url": URL + "?source=bridge"},
        ]
        self.assertEqual(len(select_cases(copies)), 1)

    def test_unknown_case_status_rejected(self):
        from scripts.governance.s1_opportunity_recovery_v1 import AdvisoryInputError
        with self.assertRaises(AdvisoryInputError):
            select_cases([{**CASE, "status": "MERGED_VERIFIED"}])

    def test_original_must_be_real_issue_or_pull_path(self):
        from scripts.governance.s1_opportunity_recovery_v1 import AdvisoryInputError
        bad = "https://github.com/Donh91/Investering-Framework-Archive-v1/tree/main"
        with self.assertRaises(AdvisoryInputError):
            select_cases([{**CASE, "original_url": bad}])

    def test_strategist_can_only_match_exact_proposal(self):
        case = {**CASE, "ambiguous_owner": True,
                "strategist_proposal_id": "proposal-exact"}
        brief = {
            "contract": "FRAMEWORK_STRATEGIST_BRIEF_v1",
            "authority": {"type": "ADVISORY_ONLY"},
            "input_status": "CURRENT",
            "intent_sha256": "1234567890",
            "generated_at_utc": "2026-11-02T08:00:00Z",
            "proposals": [
                {"id": "unrelated", "evidence_fingerprint": "other123"},
                {"id": "proposal-exact", "evidence_fingerprint": "different"},
            ],
        }
        output = strategic_question(case, brief)
        self.assertEqual(output["matched_existing_proposal_ids"], ["proposal-exact"])
        self.assertFalse(output["release_authority"])


if __name__ == "__main__":
    unittest.main()
