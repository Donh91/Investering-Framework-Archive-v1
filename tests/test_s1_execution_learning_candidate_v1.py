import unittest
from dataclasses import replace
from scripts.research.s1_execution_learning_candidate_v1 import Scope, Observation, assess

S = Scope(1289482022, 2314, "a"*40, ".github/workflows/gate.yml", "gate", "b"*40, "branch_update")
NOW = "2026-11-24T09:00:00Z"


def obs(n, **kw):
    return replace(Observation(S, n, 100+n, 1, "c"*64,
                               f"2026-11-24T08:{n:02d}:00Z", "FAILED"), **kw)


class D3Test(unittest.TestCase):
    def check(self, rows, state, count=0, **kw):
        args = dict(as_of_utc=NOW, history_complete=True)
        result = assess(S, rows, **(args | kw))
        self.assertEqual((result.state, result.consecutive_failed_attempts), (state, count))
        self.assertFalse(result.release_authorized)
        self.assertFalse(result.verified_closure)
        return result

    def test_two_failures_stop_unchanged_route(self):
        r = self.check([obs(2), obs(1)], "PROCESS_STALLED_CANDIDATE", 2)
        self.assertEqual(r.receipt_ids, (1, 2))

    def test_new_cause_resets_sequence(self):
        self.check([obs(1), obs(2), obs(3, cause_sha256="d"*64)], "SINGLE_FAILURE_OBSERVED", 1)

    def test_no_cross_scope_suppression(self):
        for scope in (replace(S, pr=2315), replace(S, head="d"*40), replace(S, repo_id=8),
                      replace(S, workflow=".github/workflows/other.yml"), replace(S, job="test"),
                      replace(S, method="inspect"), replace(S, contract_blob="e"*40)):
            with self.subTest(scope=scope):
                self.check([obs(1, scope=scope), obs(2)], "SINGLE_FAILURE_OBSERVED", 1)

    def test_duplicate_receipt_is_not_a_second_attempt(self):
        self.check([obs(1), obs(1)], "SINGLE_FAILURE_OBSERVED", 1)
        self.check([obs(1), obs(2, run_id=101)], "EVIDENCE_UNPROVEN")
        self.check([obs(1), obs(2, receipt_id=1)], "EVIDENCE_UNPROVEN")
        self.check([obs(1), obs(2, run_id=101, attempt=2)], "PROCESS_STALLED_CANDIDATE", 2)

    def test_readback_is_not_closure_and_resets(self):
        rows = [obs(1), obs(2), obs(3, outcome="ACTION_READBACK")]
        self.check(rows, "ROUTE_EXISTING_CLOSURE_OWNER")
        self.check(rows + [obs(4)], "SINGLE_FAILURE_OBSERVED", 1)

    def test_unknown_history_and_bad_data(self):
        self.check([], "NO_ATTEMPT_EVIDENCE")
        self.check([obs(1), obs(2)], "EVIDENCE_UNPROVEN", history_complete=False)
        self.check([obs(1), obs(2, outcome="UNKNOWN")], "EVIDENCE_UNPROVEN")
        for row in (obs(1, receipt_id=True), obs(1, run_id=0), obs(1, attempt=0),
                    obs(1, cause_sha256="bad"), obs(1, outcome="PASS"),
                    obs(1, observed_at_utc="2026-11-25T08:00:00Z"),
                    obs(1, observed_at_utc="bad"), obs(1, scope=replace(S, head="bad"))):
            with self.subTest(row=row): self.check([row], "EVIDENCE_UNPROVEN")
        self.check([obs(1), obs(2, observed_at_utc=obs(1).observed_at_utc)], "EVIDENCE_UNPROVEN")
        self.check([obs(1)]*101, "EVIDENCE_UNPROVEN")


if __name__ == "__main__":
    unittest.main()
