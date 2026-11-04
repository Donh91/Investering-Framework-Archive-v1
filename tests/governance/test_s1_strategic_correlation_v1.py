"""Correlate original cases and existing Strategist proposals without dispatch."""
import unittest
import json
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from scripts.governance.s1_opportunity_recovery_v1 import (
    select_cases, strategic_question,
)

URL = "https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1877"
CASE = dict(case_id="Archive#1877", original_url=URL, owner="S1",
            evidence_fingerprint="fingerprint1234", priority="P1",
            status="ACTIONABLE", authority="OWNER_GOVERNED")


class StrategicCorrelationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.now = datetime(2026, 11, 4, 12, tzinfo=timezone.utc)
        paths = {
            "strategic_intent": "00_FMOS/framework_strategist/STRATEGIC_INTENT_v1.json",
            "learning_memory": "research/framework_learning/LATEST_LEARNING_MEMORY.json",
            "weekly_delta": "research/framework_learning/LATEST_WEEKLY_LEARNING_DELTA.json",
            "self_improvement": "research/framework_learning/LATEST_SELF_IMPROVEMENT_V1.json",
            "health": "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
            "unconsumed": "research/framework_learning/LATEST_UNCONSUMED_INFORMATION.json",
            "staleness": "research/framework_learning/LATEST_METHOD_STALENESS_REGISTER.json",
            "weekly_forensics": "research/framework_learning/weekly_forensics/LATEST.json",
            "resource_budget": "research/framework_learning/resource_budget/LATEST.json",
        }
        receipts = {}
        for name, relative in paths.items():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"{}")
            receipts[name] = {"path": relative, "status": "CURRENT",
                              "sha256": sha256(b"{}").hexdigest()}
        self.brief = {
            "contract": "FRAMEWORK_STRATEGIST_BRIEF_v1",
            "owner": "EXISTING_FRAMEWORK_LEARNING_SUPERVISOR",
            "authority": {"type": "ADVISORY_ONLY", **dict.fromkeys((
                "canonical_effect", "portfolio_execution", "autonomous_grok_request",
                "autonomous_api_payment", "autonomous_merge", "new_queue"), False)},
            "input_status": "CURRENT", "intent_sha256": "intent-1234",
            "generated_at_utc": "2026-11-04T11:00:00Z",
            "source_receipts": receipts,
            "proposals": [{"id": "proposal-exact", "code": "OWNER_QUESTION",
                           "evidence_fingerprint": "different",
                           "dispatch_allowed": False, "automatic_grok_call": False,
                           "automatic_market_change": False}],
        }
        self.case = {**CASE, "ambiguous_owner": True,
                     "strategist_proposal_id": "proposal-exact"}
        self.brief_path = self.root / "research/framework_learning/strategist/LATEST.json"
        self.brief_path.parent.mkdir(parents=True, exist_ok=True)

    def evaluate(self, brief=None):
        packet = self.brief if brief is None else brief
        self.brief_path.write_text(json.dumps(packet))
        return strategic_question(self.case, packet, source_root=self.root, now=self.now)

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
        self.brief["proposals"].append({**self.brief["proposals"][0],
                                       "id": "unrelated", "evidence_fingerprint": "other123"})
        output = self.evaluate()
        self.assertEqual(output["state"], "READ_EXISTING_BRIEF")
        self.assertEqual(output["matched_existing_proposal_ids"], ["proposal-exact"])
        self.assertFalse(output["release_authority"])

    def test_current_label_without_reader_verification_is_not_acceptance(self):
        self.assertEqual(strategic_question(self.case, self.brief)["state"], "SOURCE_UNVERIFIED")
        self.assertEqual(strategic_question(self.case, None)["state"], "SOURCE_UNAVAILABLE")

    def test_source_changed_after_production(self):
        path = self.brief["source_receipts"]["health"]["path"]
        (self.root / path).write_bytes(b'{"changed":true}')
        result = self.evaluate()
        self.assertEqual(result["reason"], "SOURCE_MOVED")
        self.assertNotIn("matched_existing_proposal_ids", result)

    def test_stale_current_label(self):
        self.brief["generated_at_utc"] = "2026-11-01T11:00:00Z"
        self.assertEqual(self.evaluate()["reason"], "STALE")

    def test_authority_and_dispatch_escalation_rejected_by_existing_reader(self):
        for field in ("autonomous_merge", "dispatch_allowed"):
            with self.subTest(field=field):
                packet = deepcopy(self.brief)
                target = packet["authority"] if field == "autonomous_merge" else packet["proposals"][0]
                target[field] = True
                result = self.evaluate(packet)
                self.assertEqual(result["reason"], "AUTHORITY_VIOLATION")
                self.assertFalse(result["release_authority"])

    def test_supplied_brief_differs_from_verified_bytes(self):
        self.evaluate()
        supplied = deepcopy(self.brief)
        supplied["proposals"][0]["id"] = "replacement"
        result = strategic_question(self.case, supplied, source_root=self.root, now=self.now)
        self.assertEqual(result["reason"], "BRIEF_CHANGED")

    def test_missing_local_brief_fails_closed(self):
        result = strategic_question(self.case, self.brief, source_root=self.root, now=self.now)
        self.assertEqual(result["reason"], "UNAVAILABLE")
        self.assertEqual(result["state"], "SOURCE_UNAVAILABLE")
        self.assertFalse(result["release_authority"])


if __name__ == "__main__":
    unittest.main()
