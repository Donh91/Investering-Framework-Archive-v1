import unittest
from datetime import datetime, timedelta, timezone
import test_s1_executor_v1 as T
import test_s1_review_dispatch_v1 as R
import s1_owner_review_batch_v1 as C


class OwnerBatch(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 27, 19, 45, tzinfo=timezone.utc)
        self.heads = {7: "a"*40, 8: "b"*40}
        self.batch = C.proposal(targets=list(self.heads.items()), main="c"*40,
                                contract="d"*40, run=12, attempt=1,
                                generated_at="2026-11-27T19:40:00Z", now=self.now)
        self.go = "GO review #7 #8 batch="+self.batch["batch"]

    def test_positive_subset_and_receipt(self):
        self.assertEqual(C.select_go(self.batch, self.go, now=self.now,
                                     current_heads=self.heads, consumed=set()), list(self.heads.items()))
        receipt = C.receipt_fields(self.batch, 7, self.heads[7], intent_id=21, request_id=22)
        self.assertFalse(receipt["merge_authority"])
        self.assertFalse(receipt["review_authority"])

    def test_expiry_and_replay(self):
        for now, consumed in ((self.now+timedelta(hours=24), set()),
                              (self.now, {(7,self.heads[7])}), (self.now, None)):
            with self.assertRaises(ValueError):
                C.select_go(self.batch, self.go, now=now, current_heads=self.heads, consumed=consumed)

    def test_wrong_head_wrong_batch_duplicate_and_foreign_target(self):
        for cmd, heads in ((self.go, {**self.heads, 7:"e"*40}),
                           (self.go.replace(self.batch["batch"], "0"*64), self.heads),
                           (self.go.replace("#8", "#7"), self.heads),
                           (self.go.replace("#8", "#9"), self.heads)):
            with self.assertRaises(ValueError):
                C.select_go(self.batch, cmd, now=self.now, current_heads=heads, consumed=set())

    def test_tampered_expiry_and_day(self):
        with self.assertRaises(ValueError):
            C.select_go(dict(self.batch, expires_at="2026-12-01T00:00:00Z"), self.go,
                        now=self.now, current_heads=self.heads, consumed=set())
        self.assertFalse(C.daily_slot("2026-11-27T18:45:00Z"))
        self.assertTrue(C.daily_slot("2026-07-27T18:45:00Z"))

    def test_wrong_probe_target_never_posts(self):
        out, gh, _ = R._probe("LIVE", live=lambda w, gh, n:
            w["switch"].update(review_dispatch_probe={"pr": 8, "head": T.HEAD}))
        self.assertNotIn("issues/7/comments", [x[1] for x in gh.writes])
        self.assertNotIn("issues/8/comments", [x[1] for x in gh.writes])
        self.assertFalse(out["result"].startswith("REQUESTED_REVIEW"))


if __name__ == "__main__":
    unittest.main()
