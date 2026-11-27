"""Option B negative controls; fake GitHub only, no native bot-response claim."""
import unittest
from datetime import timedelta
from unittest import mock

import test_s1_executor_v1 as T
import s1_tick_brief_v1 as B
import s1_executor_v1 as E
import check_codex_review_finality as F


class ReviewDispatch(unittest.TestCase):
    def test_unproven_bot_is_not_request(self):
        row = {"id": 22, "user": dict(B.ACTIONS_BOT), "body": "@codex review"}
        self.assertFalse(F.request_row(row))
        self.assertTrue(F.request_row(row, {22}))
        self.assertFalse(F.request_row(dict(row, user={"login": "another[bot]", "type": "Bot"}), {22}))

    def test_exact_receipt_and_native_log(self):
        pr, head, run, attempt = 7, T.HEAD, 555, 1
        at = B.iso(T.NOW)
        def row(cid, token, intent=None, request=None):
            return {"id": cid, "user": dict(B.ACTIONS_BOT), "created_at": at, "updated_at": at,
                    "body": B.review_dispatch_body(token, pr, head, run, attempt, intent, request)}
        intent = row(1, B.REVIEW_INTENT)
        req = row(2, B.REVIEW_REQUEST, 1)
        receipt = row(3, B.REVIEW_RECEIPT, 1, 2)
        native = T.executor_run(run, T.NOW - timedelta(minutes=1), T.NOW + timedelta(minutes=1))
        line = ("S1_EXECUTOR_V1 mode=LIVE decision=8.1 action=NOOP result=REQUESTED_REVIEW writes=3:"
                + ",".join(f"{t}#{c}" for t, c in ((B.REVIEW_INTENT, 1), (B.REVIEW_REQUEST, 2), (B.REVIEW_RECEIPT, 3))))
        prove = lambda c, ledger, log=line, r=native: B.verified_bot_requests(head, pr, [c], ledger, lambda _: r, lambda _: log, T.NOW)
        self.assertEqual(prove(req, [intent, receipt]), {2})
        self.assertEqual(prove(req, [receipt]), set())
        self.assertEqual(prove(req, [intent, receipt], log=""), set())
        self.assertEqual(prove(dict(req, updated_at=B.iso(T.NOW + timedelta(seconds=1))), [intent, receipt]), set())
        self.assertEqual(prove(dict(req, body=req["body"].replace(head, "a" * 40)), [intent, receipt]), set())
        self.assertEqual(prove(req, [intent, receipt], r=dict(native, run_attempt=2)), set())
        self.assertTrue(B.review_dispatch_attempted([intent], pr, head))
        self.assertFalse(B.review_dispatch_attempted([intent], pr, "a" * 40))

    def test_gateway_refuses_unreserved_review(self):
        run, gh, _, body, d = T.setup()
        run.brief, run.decision, run.mode = B.parse_body(body), d, "LIVE"
        with self.assertRaises(E.Stop):
            run.write("review", pr=7, head=T.HEAD, intent=10)
        self.assertEqual(gh.writes, [])

    def test_live_probe_one_comment_and_receipt(self):
        def mutate(w):
            w["pr"][7]["comments"] = []
            w["switch"]["review_dispatch"] = "BOT_PROBE"
            w["switch"]["review_dispatch_probe"] = {"pr": 7, "head": T.HEAD}
        run, gh, _, body, d = T.setup(mutate=mutate, mode="LIVE", policy="CODEX_FINAL_REQUIRED")
        run.brief, run.decision, run.mode, run.body = B.parse_body(body), d, "LIVE", body
        run.ledger()
        self.assertEqual(d["action"], "NOOP")
        self.assertEqual(run.review_candidate(), (7, T.HEAD))
        result = run.dispatch_review([])
        self.assertTrue(result.startswith("REQUESTED_REVIEW"), result)
        self.assertEqual([x[1] for x in gh.writes], [f"issues/{B.OWNER_ISSUE}/comments", "issues/7/comments", f"issues/{B.OWNER_ISSUE}/comments"])
        self.assertTrue(B.review_dispatch_attempted(gh.w["issue_comments"], 7, T.HEAD))
        with self.assertRaises(E.Stop):
            run.dispatch_review(gh.w["issue_comments"])
        self.assertEqual(len(gh.writes), 3)

    def test_shadow_never_posts_even_with_probe_selected(self):
        run, gh, _, body, d = T.setup(mode="SHADOW")
        run.brief, run.decision, run.mode = B.parse_body(body), dict(d, action="NOOP", result="NOTHING_ACTIONABLE"), "SHADOW"
        run.brief["codex"] = {"available": True}
        run.files["switch"]["review_dispatch"] = "BOT_PROBE"
        run.files["switch"]["review_dispatch_probe"] = {"pr": 7, "head": T.HEAD}
        with mock.patch.object(run, "review_candidate", return_value=(7, T.HEAD)), mock.patch.object(run, "verify_review_request"):
            self.assertEqual(run.dispatch_review([]), f"WOULD_REQUEST_REVIEW(pr=7,head={T.HEAD[:8]})")
        self.assertEqual(gh.writes, [])


if __name__ == "__main__":
    unittest.main()
