"""Option C syntax, consumption and SHADOW negative controls."""
import copy
import unittest
from datetime import datetime, timedelta, timezone

import s1_owner_review_batch_v1 as O
import test_s1_review_dispatch_v1 as R


class OwnerBatch(unittest.TestCase):
    def setUp(self):
        self.at = datetime(2026, 11, 27, 10, tzinfo=timezone.utc)
        self.targets = [(7, "a"*40), (8, "b"*40)]
        self.plan = O.build_plan(self.targets, now=self.at, main="c"*40,
                                brief_run=2, brief_attempt=1, executor_run=3, executor_attempt=1)

    def row(self, plan=None, cid=1):
        return {"id": cid, "body": O.intent_body(plan or self.plan),
                "created_at": "2026-11-27T10:00:00Z", "updated_at": "2026-11-27T10:00:00Z"}

    def test_selection_is_not_authority(self):
        r = O.validate_selection(self.plan, "GO review #7 #8", dict(self.targets), self.at)
        self.assertTrue(r["selection_valid"])
        self.assertFalse(r["owner_authenticated"])
        self.assertFalse(r["write_authorized"])

    def test_wrong_head_subset_and_expiry(self):
        for message, heads, now in (("GO review #7", dict(self.targets), self.at),
                                     ("GO review #7 #8", {7:"e"*40, 8:"b"*40}, self.at),
                                     ("GO review #7 #8", dict(self.targets), self.at+timedelta(hours=24)),
                                     ("GO review #7 #8", dict(self.targets), self.at+timedelta(hours=13))):
            with self.assertRaises(ValueError):
                O.validate_selection(self.plan, message, heads, now)

    def test_plan_cannot_be_rehashed_by_editing_one_field(self):
        tampered = copy.deepcopy(self.plan)
        tampered["targets"][0]["head"] = "d"*40
        with self.assertRaises(ValueError):
            O.validate_plan(tampered, self.at)

    def test_one_use_and_competing_intent(self):
        self.assertTrue(O.check_reservation(self.plan, [], complete=True))
        self.assertTrue(O.check_reservation(self.plan, [self.row()], complete=True, own_intent_id=1))
        for comments, complete, own in (([self.row()], True, None), ([], False, None),
                                         ([], True, 1), ([self.row(), self.row(cid=2)], True, 1),
                                         ([dict(self.row(), updated_at="later")], True, 1)):
            with self.assertRaises(ValueError):
                O.check_reservation(self.plan, comments, complete=complete, own_intent_id=own)

    def test_prior_head_consumed_even_after_expiry(self):
        next_plan = O.build_plan(self.targets, now=self.at+timedelta(days=1), main="d"*40,
                                 brief_run=4, brief_attempt=1, executor_run=5, executor_attempt=1)
        with self.assertRaises(ValueError):
            O.check_reservation(next_plan, [self.row()], complete=True)

    def test_fixed_request_and_receipt(self):
        body = O.request_body(self.plan, 7, "a"*40, 1)
        self.assertTrue(body.startswith("@codex review\n"))
        self.assertIn("head: " + "a"*40, body)
        self.assertNotIn("@codex review", O.intent_body(self.plan))
        self.assertNotIn("@codex review", O.receipt_body(self.plan, 7, "a"*40, 1, 2))
        with self.assertRaises(ValueError):
            O.request_body(self.plan, 9, "a"*40, 1)

    def test_real_executor_shadow_only(self):
        out, gh, lines = R._probe("SHADOW", route="OWNER_ACTION")
        self.assertEqual(gh.writes, [])
        self.assertTrue(any(l.startswith(O.PLAN+" ") for l in lines), lines)
        self.assertTrue(out["result"].startswith("WOULD_OWNER_ACTION_REVIEW"))

    def test_wrong_probe_target_no_post(self):
        out, gh, _ = R._probe("LIVE", extra=lambda w: w["switch"].update(
            review_dispatch_probe={"pr": 999, "head": "f"*40}))
        self.assertFalse(any(x[1] == "issues/7/comments" for x in gh.writes))
        self.assertFalse(out["result"].startswith("REQUESTED_REVIEW"))

if __name__ == "__main__":
    unittest.main()
