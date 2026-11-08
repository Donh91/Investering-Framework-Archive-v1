"""Positive and adversarial checks for review-only S1 evidence classifier."""
import unittest
from scripts.governance.s1_general_release_evidence_v1 import classify

def valid():
    h = "a" * 40
    return dict(head=h, main="b"*40, review_head=h, owner_head=h, ci_head=h,
        owner_authenticated=True, effective_write=True, one_editor_lease=True,
        rules_verified=True, native_reviews_satisfied=True,
        source_and_science_satisfied=True, high_impact=False,
        remote_write_state="CONFIRMED", main_unchanged=True,
        required_tests=["positive", "guard-removal"], executed_tests=["positive", "guard-removal"],
        ci_pr_event=True, ci_success=True)

class TestS1GeneralEvidence(unittest.TestCase):
    def test_full_packet_is_still_advisory(self):
        result=classify(valid())
        self.assertEqual(result["status"], "EVIDENCE_COMPLETE_RECHECK_NATIVE")
        self.assertFalse(result["release_authorized"])
    def test_missing_or_skipped_seven_tests(self):
        s=valid();s["required_tests"] += [f"hre-{i}" for i in range(7)]
        self.assertEqual(classify(s)["reason"], "RELEASE_CI_NOT_EXECUTED")
    def test_changed_head(self):
        s=valid();s["review_head"]="c"*40
        self.assertEqual(classify(s)["reason"], "STALE_HEAD_BINDING")
    def test_unverified_owner(self):
        s=valid();s["owner_authenticated"]=False
        self.assertEqual(classify(s)["reason"], "OWNER_MANDATE_UNVERIFIED")
    def test_competing_editor(self):
        s=valid();s["one_editor_lease"]=False
        self.assertEqual(classify(s)["reason"], "EDITOR_LEASE_UNVERIFIED")
    def test_partial_write(self):
        s=valid();s["remote_write_state"]="WRITE_ATTEMPTED"
        self.assertEqual(classify(s)["reason"], "PARTIAL_OR_UNKNOWN_REMOTE_WRITE")
    def test_advanced_main(self):
        s=valid();s["main_unchanged"]=False
        self.assertEqual(classify(s)["reason"], "MAIN_MOVED_REVALIDATE")
    def test_unreadable_rules(self):
        s=valid();s["rules_verified"]=False
        self.assertEqual(classify(s)["reason"], "ENFORCED_RULES_UNKNOWN")
    def test_missing_native_approval(self):
        s=valid();s["native_reviews_satisfied"]=False
        self.assertEqual(classify(s)["reason"], "NATIVE_REVIEW_GATE_UNSATISFIED")
    def test_high_impact_without_custody(self):
        s=valid();s["high_impact"]=True
        self.assertEqual(classify(s)["reason"], "HIGH_IMPACT_CUSTODY_UNATTESTED")
    def test_green_without_pr_event(self):
        s=valid();s["ci_pr_event"]=False
        self.assertEqual(classify(s)["reason"], "EXACT_HEAD_PR_CI_UNVERIFIED")
    def test_missing_manifest(self):
        s=valid();s["required_tests"]=[]
        self.assertEqual(classify(s)["reason"], "REQUIRED_TEST_MANIFEST_UNVERIFIED")

if __name__ == "__main__":
    unittest.main()
