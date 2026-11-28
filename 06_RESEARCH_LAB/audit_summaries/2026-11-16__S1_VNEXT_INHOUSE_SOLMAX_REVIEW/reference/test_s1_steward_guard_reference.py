"""Adversarial offline tests of the advisory-only S1 vNext reference guards."""
from __future__ import annotations
import copy
from datetime import datetime, timezone, timedelta
import unittest

from s1_steward_guard_reference import (
    REPO, HEALTH_PATH, S1_TASK, Finding, WorkItem, ObservedOperation,
    admit_workflow_run, latest_scheduled_health, independent_review_candidate,
    shortlist_work, disposition_suggestion, operation_key,
    reconcile_operation, classify_scheduled_run, verified_closure_classification,
)

SHA = "a" * 40
BLOB = "b" * 40
NOW = datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc)

def run(**kw):
    value = dict(id=42, path=HEALTH_PATH, event="schedule", head_branch="main",
        head_repository={"full_name": REPO}, status="completed", conclusion="success",
        created_at="2026-11-16T12:00:00Z", updated_at="2026-11-16T12:06:00Z")
    value.update(kw)
    return value

def review(**kw):
    value = dict(head_sha=SHA, verdict="APPROVE", is_edited=False, reviewer="CODEX",
        app_identity_verified=True, unresolved_findings=False)
    value.update(kw)
    return value

def op(**kw):
    value = dict(key="c" * 64, intent_exists=True, write_attempted=False,
       native_result_exists=False, readback_matches=False, current_head_matches=True,
       native_authenticity_verified=True)
    value.update(kw)
    return ObservedOperation(**value)

def closure(**kw):
    value = dict(task_id=S1_TASK, run_id="task-run-123", original_repo=REPO,
        pr_number=1, head_sha=SHA, merge_commit_sha=BLOB,
        route="DIRECT_SCHEDULED", native_task_event_verified=True,
        native_merge_verified=True, one_parent_squash=True,
        exact_head_readback=True, natural_consumer_verified=False)
    value.update(kw)
    return value

class Base(unittest.TestCase):
    def assertHold(self, finding, code=None):
        self.assertEqual(finding.disposition, "HOLD", finding)
        self.assertFalse(finding.authorized)
        if code: self.assertEqual(finding.code, code)
    def assertCandidate(self, finding, code=None):
        self.assertEqual(finding.disposition, "ADVISORY_CANDIDATE", finding)
        self.assertFalse(finding.authorized)
        if code: self.assertEqual(finding.code, code)

class TestFinding(Base):
    def test_no_positive_authority(self):
        with self.assertRaises(ValueError): Finding("APPROVE", "ANY", authorized=True)
    def test_advisory_only(self):
        self.assertFalse(Finding("ADVISORY_CANDIDATE", "CHECK").authorized)

class TestWorkflowAdmission(Base):
    def test_same_repo(self): self.assertCandidate(admit_workflow_run(run(event="workflow_run")), "SAME_REPOSITORY_WORKFLOW_RUN")
    def test_fork_named_main(self): self.assertHold(admit_workflow_run(run(event="workflow_run", head_repository={"full_name": "evildoer/fork"})), "FOREIGN_OR_MISSING_HEAD_REPOSITORY")
    def test_missing_repository(self): self.assertHold(admit_workflow_run(run(event="workflow_run", head_repository=None)))
    def test_empty_repository(self): self.assertHold(admit_workflow_run(run(event="workflow_run", head_repository={})))
    def test_other_branch(self): self.assertHold(admit_workflow_run(run(event="workflow_run", head_branch="release")))
    def test_pull_request_not_prod(self): self.assertHold(admit_workflow_run(run(event="pull_request")))
    def test_regular_schedule(self): self.assertCandidate(admit_workflow_run(run(event="schedule")))
    def test_dispatch(self): self.assertCandidate(admit_workflow_run(run(event="workflow_dispatch")))
    def test_wrong_schema(self): self.assertHold(admit_workflow_run(None))

class TestHealth(Base):
    def test_good(self): self.assertCandidate(latest_scheduled_health([[run()]], observed_at=NOW, exhausted=True), "SCHEDULED_HEALTH_SUCCESS")
    def test_latest_failed_not_masked(self):
        pages=[[run(id=4,created_at="2026-11-16T13:00:00Z",updated_at="2026-11-16T13:05:00Z",conclusion="failure"), run(id=3)]]
        self.assertHold(latest_scheduled_health(pages, observed_at=NOW, exhausted=True), "LATEST_HEALTH_NOT_SUCCESS")
    def test_latest_pending_not_green(self):
        self.assertHold(latest_scheduled_health([[run(status="in_progress")]], observed_at=NOW, exhausted=True), "LATEST_HEALTH_NOT_TERMINAL")
    def test_skipped_not_success(self): self.assertHold(latest_scheduled_health([[run(conclusion="skipped")]], observed_at=NOW, exhausted=True))
    def test_stale(self): self.assertHold(latest_scheduled_health([[run(created_at="2026-11-14T10:00:00Z",updated_at="2026-11-14T10:04:00Z")]], observed_at=NOW, exhausted=True), "HEALTH_FINISH_NOT_FRESH")
    def test_truncated(self): self.assertHold(latest_scheduled_health([[run()]], observed_at=NOW, exhausted=False), "PAGINATION_NOT_PROVEN")
    def test_boundary_crossed_is_enough(self):
        rows=[run(id=2),run(id=1, path="other", created_at="2026-11-14T10:00:00Z",updated_at="2026-11-14T10:04:00Z")]
        self.assertCandidate(latest_scheduled_health([rows], observed_at=NOW, exhausted=False))
    def test_out_of_order(self):
        rows=[run(id=1,created_at="2026-11-15T12:00:00Z"),run(id=2,created_at="2026-11-16T12:00:00Z")]
        self.assertHold(latest_scheduled_health([rows], observed_at=NOW, exhausted=True), "PAGES_NOT_NEWEST_FIRST")
    def test_duplicate_id(self): self.assertHold(latest_scheduled_health([[run(id=4),run(id=4,created_at="2026-11-15T12:00:00Z")]], observed_at=NOW, exhausted=True),"DUPLICATED_RUN_PAGE")
    def test_pr_ci_lookalike(self):
        self.assertHold(latest_scheduled_health([[run(event="pull_request")]],observed_at=NOW,exhausted=True),"NO_SCHEDULED_MAIN_HEALTH_RUN")
    def test_dispatch_lookalike(self):
        self.assertHold(latest_scheduled_health([[run(event="workflow_dispatch")]],observed_at=NOW,exhausted=True))
    def test_other_path(self): self.assertHold(latest_scheduled_health([[run(path=".github/workflows/gate.yml")]],observed_at=NOW,exhausted=True))
    def test_other_branch(self): self.assertHold(latest_scheduled_health([[run(head_branch="feature")]],observed_at=NOW,exhausted=True))
    def test_future_run(self): self.assertHold(latest_scheduled_health([[run(created_at="2026-11-17T22:00:00Z")]],observed_at=NOW,exhausted=True),"INVALID_RUN_CLOCK")
    def test_malformed(self): self.assertHold(latest_scheduled_health([[{"id":"fake"}]],observed_at=NOW,exhausted=True),"MALFORMED_RUN_PAGE")
    def test_empty(self): self.assertHold(latest_scheduled_health([],observed_at=NOW,exhausted=True),"NO_RUNS")

class TestReview(Base):
    def test_codex(self): self.assertCandidate(independent_review_candidate(head=SHA,author_roles=["USER"],review=review(),native_identity_attested=True,native_head_attested=True))
    def test_codex_self(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["CODEX"],review=review(),native_identity_attested=True,native_head_attested=True),"CODEX_AUTHOR_OR_UNKNOWN")
    def test_codex_unknown_author(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["UNKNOWN"],review=review(),native_identity_attested=True,native_head_attested=True))
    def test_codex_unresolved(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["USER"],review=review(unresolved_findings=True),native_identity_attested=True,native_head_attested=True))
    def test_codex_fake_app(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["USER"],review=review(app_identity_verified=False),native_identity_attested=True,native_head_attested=True))
    def test_specialist_is_not_independent(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["USER"],review=review(reviewer="S1_SPECIALIST"),native_identity_attested=True,native_head_attested=True),"SPECIALIST_SELF_CHECK_NOT_INDEPENDENT")
    def test_old_head(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["USER"],review=review(head_sha=BLOB),native_identity_attested=True,native_head_attested=True))
    def test_request_changes(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["USER"],review=review(verdict="REQUEST_CHANGES"),native_identity_attested=True,native_head_attested=True))
    def test_edited(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["USER"],review=review(is_edited=True),native_identity_attested=True,native_head_attested=True))
    def test_no_native_provenance(self): self.assertHold(independent_review_candidate(head=SHA,author_roles=["USER"],review=review(),native_identity_attested=False,native_head_attested=True),"UNBOUND_NATIVE_REVIEW_PROVENANCE")
    def test_claude_valid_candidate(self):
        c=review(reviewer="CLAUDE",independence="INDEPENDENT_DETACHED",request_id="100",report_path="report.md",report_blob=BLOB,bridge_commit=BLOB,lane_eligible="YES")
        self.assertCandidate(independent_review_candidate(head=SHA,author_roles=["USER"],review=c,native_identity_attested=True,native_head_attested=True))
    def test_claude_self(self):
        c=review(reviewer="CLAUDE",independence="INDEPENDENT_DETACHED",request_id="100",report_path="r",report_blob=BLOB,bridge_commit=BLOB,lane_eligible="YES")
        self.assertHold(independent_review_candidate(head=SHA,author_roles=["CLAUDE"],review=c,native_identity_attested=True,native_head_attested=True))
    def test_claude_not_lane(self):
        c=review(reviewer="CLAUDE",independence="INDEPENDENT_DETACHED",request_id="100",report_path="r",report_blob=BLOB,bridge_commit=BLOB,lane_eligible="not asserted")
        self.assertHold(independent_review_candidate(head=SHA,author_roles=["USER"],review=c,native_identity_attested=True,native_head_attested=True),"CLAUDE_LANE_NOT_ASSERTED")

class TestWorkSelection(Base):
    def mk(self,k,**kw):
        a=dict(key=k,head_sha=SHA,priority=1,current_state="BUILD",risk="LOW",new_evidence=True,actionable=True,native_source_verified=True)
        a.update(kw)
        return WorkItem(**a)
    def test_priority_and_cap(self):
        a=[self.mk(str(i),priority=i) for i in range(5,0,-1)]
        self.assertEqual([x.key for x in shortlist_work(a)],["1","2","3"])
    def test_unknown_source_not_eligible(self): self.assertFalse(shortlist_work([self.mk("a",native_source_verified=False)]))
    def test_unchanged_blocker_sleep(self): self.assertFalse(shortlist_work([self.mk("a",new_evidence=False)]))
    def test_other_writer(self): self.assertFalse(shortlist_work([self.mk("a",has_other_writer=True)]))
    def test_dedupe(self): self.assertEqual(len(shortlist_work([self.mk("a"),self.mk("a")])),1)
    def test_bad_head(self): self.assertFalse(shortlist_work([self.mk("a",head_sha="123")] ))
    def test_invalid_cap(self):
        with self.assertRaises(ValueError): shortlist_work([],max_deep=7)

class TestClose(Base):
    def test_stale_is_not_closure(self): self.assertHold(disposition_suggestion(proposed="CLOSED_NOISE",risk="LOW",age_days=999,signals=[]),"NO_INDEPENDENT_OBJECTIVE_CLOSURE_PROOF")
    def test_two_fake_signals(self):
        s=[{"kind":"stale_parked"},{"kind":"stale_final_park"}]
        self.assertHold(disposition_suggestion(proposed="CLOSED_NOISE",risk="LOW",age_days=90,signals=s))
    def test_strong_signal_still_needs_native(self):
        s=[dict(kind="SUPERSEDED_BLOBS_PROVEN",native_objective_proof=True,source_url="https://github.com/example/x",source_sha=SHA,independent_origin=True)]
        self.assertHold(disposition_suggestion(proposed="CLOSED_NOISE",risk="LOW",age_days=30,signals=s),"OBJECTIVE_PROOF_REQUIRES_NATIVE_CLOSER")
    def test_high_never_auto_closed(self): self.assertHold(disposition_suggestion(proposed="CLOSED_NOISE",risk="HIGH",age_days=999,signals=[]),"HIGH_RISK_CLOSE_OWNER_REQUIRED")
    def test_extreme_never_auto_closed(self): self.assertHold(disposition_suggestion(proposed="CLOSED_NOISE",risk="EXTREME",age_days=999,signals=[]))
    def test_owner_decision_only_advisory(self): self.assertCandidate(disposition_suggestion(proposed="CLOSED_NOISE",risk="LOW",age_days=1,signals=[],owner_decision_verified=True))

class TestIdempotence(Base):
    def test_stable_identity(self):
        k=operation_key(repo=REPO,work_id="pr:2",head=SHA,action="REQUEST_REVIEW",contract_blob=BLOB)
        self.assertEqual(k,operation_key(repo=REPO,work_id="pr:2",head=SHA,action="REQUEST_REVIEW",contract_blob=BLOB))
        self.assertNotEqual(k,operation_key(repo=REPO,work_id="pr:3",head=SHA,action="REQUEST_REVIEW",contract_blob=BLOB))
    def test_reject_mutable_head(self):
        with self.assertRaises(ValueError): operation_key(repo=REPO,work_id="pr:2",head="main",action="MERGE",contract_blob=BLOB)
    def test_result_already_applied(self): self.assertCandidate(reconcile_operation(op(native_result_exists=True,readback_matches=True)),"OPERATION_ALREADY_APPLIED")
    def test_result_mismatch(self): self.assertHold(reconcile_operation(op(native_result_exists=True,readback_matches=False)),"HALT_RESULT_READBACK_MISMATCH")
    def test_ambiguous_post(self): self.assertHold(reconcile_operation(op(write_attempted=True)),"AMBIGUOUS_WRITE_RECONCILE_REQUIRED")
    def test_source_drift(self): self.assertHold(reconcile_operation(op(current_head_matches=False)),"SOURCE_DRIFT_RESTART")
    def test_forged_intent(self): self.assertHold(reconcile_operation(op(native_authenticity_verified=False)),"NO_NATIVE_PROVENANCE")
    def test_no_intent(self): self.assertCandidate(reconcile_operation(op(intent_exists=False)),"NEW_ACTION_MAY_BE_PREFLIGHTED")

class TestScheduler(Base):
    def mk(self, **kw):
        d=dict(task_id=S1_TASK,scheduled_for="2026-11-16T13:45:00Z",started_at="2026-11-16T13:45:10Z",completed_at="2026-11-16T13:46:00Z",recorded_status="completed")
        d.update(kw);return d
    def test_success(self): self.assertCandidate(classify_scheduled_run(self.mk()))
    def test_57m_delay(self): self.assertHold(classify_scheduled_run(self.mk(started_at="2026-11-16T14:42:21Z",completed_at="2026-11-16T14:45:22Z")),"SCHEDULE_DISPATCH_DELAY")
    def test_wrong_task(self): self.assertHold(classify_scheduled_run(self.mk(task_id="duplicate")),"WRONG_TASK_ID")
    def test_stale_result(self): self.assertHold(classify_scheduled_run(self.mk(recorded_status="in_progress",completed_at=None)),"RUN_NOT_FINISHED")
    def test_failed(self): self.assertHold(classify_scheduled_run(self.mk(recorded_status="failed")),"SCHEDULER_TASK_FAILED")
    def test_missing_clock(self): self.assertHold(classify_scheduled_run(self.mk(started_at=None)),"RUN_CLOCK_UNVERIFIED")
    def test_completed_missing_end(self): self.assertHold(classify_scheduled_run(self.mk(completed_at=None)),"COMPLETION_WITHOUT_CLOCK")
    def test_inprogress_with_end(self): self.assertHold(classify_scheduled_run(self.mk(recorded_status="in_progress")),"RUN_STATUS_CLOCK_MISMATCH")

class TestClosure(Base):
    def test_merge_only(self): self.assertCandidate(verified_closure_classification(closure()),"S1_MERGE_ONLY_CONSUMER_UNPROVEN")
    def test_consumer(self): self.assertCandidate(verified_closure_classification(closure(natural_consumer_verified=True)),"S1_MERGE_AND_CONSUMER_CANDIDATE")
    def test_owner_interactive_cannot_credit(self): self.assertHold(verified_closure_classification(closure(route="INTERACTIVE_OWNER")),"NOT_UNATTENDED_S1")
    def test_missing_native_task(self): self.assertHold(verified_closure_classification(closure(native_task_event_verified=False)),"TASK_OR_MERGE_NOT_NATIVE_VERIFIED")
    def test_no_squash(self): self.assertHold(verified_closure_classification(closure(one_parent_squash=False)),"MERGE_READBACK_NOT_PROVEN")
    def test_stale_readback(self): self.assertHold(verified_closure_classification(closure(exact_head_readback=False)))
    def test_fake_delegated(self): self.assertHold(verified_closure_classification(closure(route="SCHEDULED_DELEGATED")),"DELEGATED_CHAIN_UNPROVEN")
    def test_true_delegated(self):
        fields=dict(route="SCHEDULED_DELEGATED",distinct_receiver_verified=True,receiver_job_executed=True,artifact_digest_bound=True,s1_consumed_result=True)
        self.assertCandidate(verified_closure_classification(closure(**fields)))
    def test_wrong_task(self): self.assertHold(verified_closure_classification(closure(task_id="x")),"NOT_SOLE_S1")

if __name__ == "__main__": unittest.main(verbosity=2)
