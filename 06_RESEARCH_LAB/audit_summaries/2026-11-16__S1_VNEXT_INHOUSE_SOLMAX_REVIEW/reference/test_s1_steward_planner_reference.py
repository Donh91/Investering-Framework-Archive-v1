"""Offline adversarial policy matrix for S1 vNext planner."""
import unittest
from dataclasses import replace
from datetime import datetime,timezone
from s1_steward_planner_reference import Case, Plan, decide_case, plan_tick

SHA="a"*40

def case(**kw):
    d=dict(item_id="pr:2190",state="BUILD",risk="MEDIUM",source_fingerprint="x",
    priority=1,actionable=True,evidence_changed=True,touched_by_other_writer=False,
    privacy_proven=False,exact_head_ci_proven=False,independent_review_proven=False,
    lane_eligible=False,owner_present_required=False,tests_executed=False,
    source_authority_proven=True)
    d.update(kw)
    return Case(**d)

def decide(c):return decide_case(c,head=SHA,main=SHA,policy_blob=SHA)

class Tests(unittest.TestCase):
    def test_no_authority_positive(self):
        with self.assertRaises(ValueError):Plan("MERGE","a","pass","b",authorized=True)
    def test_source_unknown(self):self.assertEqual(decide(case(source_authority_proven=False)).reason,"SOURCE_NOT_AUTHENTICATED")
    def test_writer_lease(self):self.assertEqual(decide(case(touched_by_other_writer=True)).reason,"OTHER_WRITER_LEASE")
    def test_normal_codex(self):self.assertEqual(decide(case()).action,"REPAIR_OR_REQUEST_CODEX")
    def test_missing_executor(self):self.assertEqual(decide(case(native_tool_available=False)).reason,"EXECUTOR_TOOL_NOT_VERIFIED")
    def test_no_change(self):self.assertEqual(decide(case(evidence_changed=False)).reason,"NO_NEW_ACTIONABLE_EVIDENCE")
    def test_owner_card_for_high(self):
        p=decide(case(risk="HIGH_IMPACT",owner_present_required=True))
        self.assertEqual(p.action,"OWNER_CARD")
        self.assertEqual(p.owner_card["head"],SHA)
        self.assertEqual(p.owner_card["release_readiness"],"GATES_NOT_PROVEN")
        self.assertFalse(p.authorized)
    def test_owner_card_no_merge_token_even_all_checks(self):
        p=decide(case(risk="HIGH_IMPACT",owner_present_required=True,tests_executed=True,privacy_proven=True,exact_head_ci_proven=True,independent_review_proven=True))
        self.assertEqual(p.owner_card["release_readiness"],"ADVISORY_ALL_CHECKS_PROVEN")
        self.assertEqual(p.owner_card["s1_action"],"WAIT_FOR_NATIVE_OWNER_DECISION")
    def test_extreme_owner(self):self.assertEqual(decide(case(risk="EXTREME")).action,"OWNER_CARD")
    def test_test_missing(self):self.assertEqual(decide(case(state="TEST")).action,"RUN_TESTS_OR_DIAGNOSE")
    def test_test_green_requests_review(self):self.assertEqual(decide(case(state="TEST",tests_executed=True,exact_head_ci_proven=True)).action,"REQUEST_INDEPENDENT_REVIEW")
    def test_review_missing(self):self.assertEqual(decide(case(state="REVIEW")).action,"REQUEST_INDEPENDENT_REVIEW")
    def test_review_unavailable(self):self.assertEqual(decide(case(state="REVIEW",reviewer_available=False)).reason,"INDEPENDENT_REVIEWER_UNAVAILABLE_OWNER_FALLBACK")
    def test_review_done_other_gates_missing(self):self.assertEqual(decide(case(state="REVIEW",independent_review_proven=True)).reason,"OTHER_GATES_NOT_PROVEN")
    def test_release_incomplete(self):self.assertEqual(decide(case(state="RELEASE")).reason,"RELEASE_GATES_INCOMPLETE")
    def test_release_complete_still_not_merge(self):
        p=decide(case(state="RELEASE",privacy_proven=True,exact_head_ci_proven=True,tests_executed=True,independent_review_proven=True,lane_eligible=True))
        self.assertEqual(p.action,"PREFLIGHT_RELEASE")
        self.assertFalse(p.authorized)
    def test_blocked_unchanged_sleeps(self):self.assertEqual(decide(case(state="BLOCKED",evidence_changed=False)).reason,"UNCHANGED_BLOCKER")
    def test_blocked_trigger_changes(self):self.assertEqual(decide(case(state="BLOCKED",evidence_changed=True)).action,"RETRIAGE")
    def test_parked_not_auto_close(self):self.assertEqual(decide(case(state="PARKED",evidence_changed=False)).action,"NOOP")
    def test_observation_not_closure(self):self.assertEqual(decide(case(state="OBSERVE",natural_consumer_proven=False)).action,"OBSERVE")
    def test_proven_closure_advisory(self):self.assertEqual(decide(case(state="OBSERVE",natural_consumer_proven=True,merge_readback_proven=True)).action,"ADVISORY_CLOSE_PROOF")
    def test_priority_and_fairness(self):
        rows=[case(item_id="a",priority=10,active_incident=False),case(item_id="b",priority=50,active_incident=True),case(item_id="c",priority=1)]
        p=plan_tick(rows,head_by_item={x.item_id:SHA for x in rows},main=SHA,policy_blob=SHA,monday_readonly=False)
        self.assertEqual([x.item_id for x in p],["b","c","a"])
    def test_ignore_unchanged_and_move_on(self):
        rows=[case(item_id="a",state="BLOCKED",evidence_changed=False,priority=0),case(item_id="b",priority=1)]
        self.assertEqual([x.item_id for x in plan_tick(rows,head_by_item={"a":SHA,"b":SHA},main=SHA,policy_blob=SHA,monday_readonly=False)],["b"])
    def test_monday_hard_stop(self):
        self.assertEqual(plan_tick([case()],head_by_item={},main=SHA,policy_blob=SHA,monday_readonly=True)[0].reason,"MONDAY_READ_ONLY")
    def test_no_duplicate(self):
        self.assertEqual(len(plan_tick([case(),case()],head_by_item={},main=SHA,policy_blob=SHA,monday_readonly=False)),1)
    def test_3max(self):
        rows=[case(item_id=str(i)) for i in range(10)]
        self.assertEqual(len(plan_tick(rows,head_by_item={},main=SHA,policy_blob=SHA,monday_readonly=False)),3)

if __name__=='__main__': unittest.main()
