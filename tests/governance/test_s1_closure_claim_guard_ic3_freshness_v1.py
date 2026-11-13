"""IC-3 freshness (Claude review of #2087 @ 8ee9c450): stale or post-merge evidence demotes."""
import copy
import unittest

from scripts.governance.s1_closure_claim_guard_v1 import inspect_claim
from tests.governance.test_s1_closure_claim_guard_v1 import complete_shape


def run(mutate):
    case = copy.deepcopy(complete_shape())
    mutate(case)
    return inspect_claim(case)


class TestIC3Freshness(unittest.TestCase):
    def test_baseline_still_candidate(self):
        self.assertTrue(inspect_claim(complete_shape())["candidate_for_native_check"])

    def test_stale_merge_state_check_demotes(self):
        out = run(lambda c: c["merge_state_check"].update(checked_at_utc="2020-01-01T00:00:00Z"))
        self.assertIn("MERGE_STATE_CHECK_STALE_OR_AFTER_MERGE", out["reasons"])
        self.assertFalse(out["candidate_for_native_check"])

    def test_merge_state_check_after_merge_demotes(self):
        out = run(lambda c: c["merge_state_check"].update(checked_at_utc="2030-01-01T00:00:00Z"))
        self.assertIn("MERGE_STATE_CHECK_STALE_OR_AFTER_MERGE", out["reasons"])

    def test_check_before_task_start_demotes(self):
        out = run(lambda c: c["merge_state_check"].update(checked_at_utc="2026-11-05T21:14:30Z"))
        self.assertIn("MERGE_STATE_CHECK_STALE_OR_AFTER_MERGE", out["reasons"])

    def test_schedule_far_before_start_demotes(self):
        out = run(lambda c: c.update(scheduled_for_utc="2026-10-26T21:14:00Z"))
        self.assertIn("TASK_START_NOT_BOUND_TO_SCHEDULE", out["reasons"])
        self.assertFalse(out["candidate_for_native_check"])

    def test_schedule_lag_within_hour_ok(self):
        out = run(lambda c: c.update(scheduled_for_utc="2026-11-05T20:20:00Z"))
        self.assertNotIn("TASK_START_NOT_BOUND_TO_SCHEDULE", out["reasons"])


if __name__ == "__main__":
    unittest.main()
