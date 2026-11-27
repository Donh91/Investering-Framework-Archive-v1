"""Option B negative controls; fake GitHub only, no native bot-response claim."""
import copy
import unittest
from datetime import timedelta
from unittest import mock

import test_s1_executor_v1 as T
import s1_tick_brief_v1 as B
import s1_executor_v1 as E
import check_codex_review_finality as F


class ReviewDispatch(unittest.TestCase):
    def test_every_non_codex_request_still_counts_and_can_only_stop(self):
        """Claude fix (#2377 CI failure 1): ignoring an unproven bot request failed open (a pending request, the
        "nobody asked" offline signal and finality after the latest request all rest on it). Every non-Codex
        `@codex review` counts, as on main; the finality rule is main's, unchanged."""
        import inspect
        self.assertEqual(list(inspect.signature(F.decision).parameters), ["head", "comments", "reviews", "inline"])
        self.assertFalse(hasattr(F, "request_row"))
        head, done = T.HEAD, '<!-- codex-review-state:v1 {"code_review": {"commit_sha": "%s", "status": "completed"}} -->' % T.HEAD
        rows = [{"id": 1, "user": {"login": "Donh91", "type": "User"}, "body": "@codex review", "created_at": "2026-11-18T09:00:00Z", "updated_at": "2026-11-18T09:00:00Z"},
                {"id": 2, "user": dict(F.CODEX_USER) if hasattr(F, "CODEX_USER") else {"login": "chatgpt-codex-connector[bot]", "type": "Bot", "id": 199175422},
                 "body": done, "created_at": "2026-11-18T09:30:00Z", "updated_at": "2026-11-18T09:30:00Z"}]
        later_bot = {"id": 3, "user": dict(B.ACTIONS_BOT), "body": "@codex review", "created_at": "2026-11-18T10:00:00Z", "updated_at": "2026-11-18T10:00:00Z"}
        before, after = F.decision(head, rows, [], []), F.decision(head, rows + [later_bot], [], [])
        # a later unproven bot request can only take finality away, never give it
        self.assertFalse(after.get("technical_review_accepted") is True and before.get("technical_review_accepted") is not True)
        self.assertIsNot(after.get("technical_review_accepted"), True)

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

    def test_a_failed_dispatch_check_never_replaces_the_decision(self):
        """Claude fix: before its intent, a stop or an unreadable read in the review checks leaves the NOOP result and
        health of the decision as they are (SHADOW and LIVE); after the intent it is the alarm it always was."""
        for mode in ("SHADOW", "LIVE"):
            out, gh, _n, d = T.execute(mode=mode, mutate=lambda w: w.update(pulls=[], pr={}))
            run, gh2, _n2, body, _d = T.setup(mode=mode, mutate=lambda w: w.update(pulls=[], pr={}))
            lines = []
            run.out = lines.append
            for exc in (E.Stop("review_wait_2h", E.BLOCKED), E.Stop("review_quota_unreadable"), B.StopReading("API_BUDGET"), KeyError("x")):
                with mock.patch.object(E.Run, "dispatch_review", side_effect=exc):
                    run2, gh3, _n3, body3, _d3 = T.setup(mode=mode, mutate=lambda w: w.update(pulls=[], pr={}))
                    got = run2.execute(body3)
                # the same result, health and writes as the run without the dispatch (in LIVE: its heartbeat only)
                self.assertEqual((got["result"], got["health"], got["alarms"], [w[:2] for w in gh3.writes]),
                                 (out["result"], out["health"], [], [w[:2] for w in gh.writes]), (mode, exc))
                self.assertNotIn("issues/7/comments", [w[1] for w in gh3.writes])
                self.assertTrue(any(l.startswith("S1_EXECUTOR_REVIEW SKIPPED(") for l in got["lines"]), got["lines"])
        run, gh, _n, body, d = T.setup(mode="LIVE")
        run.writes.append(("comment", B.REVIEW_INTENT, 99))
        with mock.patch.object(E.Run, "dispatch_review", side_effect=E.Stop("review_head_changed", E.BLOCKED)):
            with self.assertRaises(E.Stop):
                run.review_or_skip([])

    def test_the_review_write_is_live_only_exact_and_once_per_run(self):
        for mode in ("SHADOW", "OFF", None):
            run, gh, _n, body, d = T.setup()
            run.brief, run.decision, run.mode = B.parse_body(body), dict(d, action="NOOP"), mode
            run.review_reservation, run.review_plan = (7, T.HEAD, 10), (7, T.HEAD, 555, 1)
            run.writes.append(("comment", B.REVIEW_INTENT, 10))
            with self.assertRaises(E.Stop) as stop:
                run.write("review", pr=7, head=T.HEAD, intent=10)
            self.assertEqual((stop.exception.reason, gh.writes), ("executor_not_live", []), mode)
        # the request text is the fixed body, bound to PR, head, run, attempt and intent
        self.assertEqual(B.review_dispatch_body(B.REVIEW_REQUEST, 7, T.HEAD, 555, 1, 10),
                         f"@codex review\n\nS1_CODEX_REVIEW_COMMENT_v1\npr: 7\nhead: {T.HEAD}\nexecutor: GITHUB run=555\nattempt: 1\nintent: 10")
        # per head: an earlier intent for this exact PR/head (an ambiguous POST included) stops every later run
        intent = {"id": 1, "user": dict(B.ACTIONS_BOT), "created_at": B.iso(T.NOW), "updated_at": B.iso(T.NOW),
                  "body": B.review_dispatch_body(B.REVIEW_INTENT, 7, T.HEAD, 540, 1)}
        self.assertTrue(B.review_dispatch_attempted([intent], 7, T.HEAD))
        self.assertFalse(B.review_dispatch_attempted([intent], 8, T.HEAD))

    def test_shadow_never_posts_even_with_probe_selected(self):
        run, gh, _, body, d = T.setup(mode="SHADOW")
        run.brief, run.decision, run.mode = B.parse_body(body), dict(d, action="NOOP", result="NOTHING_ACTIONABLE"), "SHADOW"
        run.brief["codex"] = {"available": True}
        run.files["switch"]["review_dispatch"] = "BOT_PROBE"
        run.files["switch"]["review_dispatch_probe"] = {"pr": 7, "head": T.HEAD}
        with mock.patch.object(run, "review_candidate", return_value=(7, T.HEAD)), mock.patch.object(run, "verify_review_dispatch"):
            self.assertEqual(run.dispatch_review([]), f"WOULD_REQUEST_REVIEW(pr=7,head={T.HEAD[:8]})")
        self.assertEqual(gh.writes, [])


def _probe(mode, route="BOT_PROBE", live=None, extra=None):
    """The real execute() path on the probe world: an eligible, green, unreviewed LOW head with no request."""
    def mutate(w):
        w["pr"][7]["comments"] = []
        w["switch"]["review_dispatch"] = route
        w["switch"]["review_dispatch_probe"] = {"pr": 7, "head": T.HEAD} if route == "BOT_PROBE" else None
        if extra:
            extra(w)
    run, gh, native, body, d = T.setup(mutate=mutate, mode=mode, policy="CODEX_FINAL_REQUIRED", live=live)
    lines = []
    run.out = lines.append
    return run.execute(body), gh, lines


class ReviewDispatchEndToEnd(unittest.TestCase):
    """Claude adversarial checks of #2377 on the real execute() path (fake GitHub only; no native bot-response claim)."""

    def test_live_requests_once_and_a_second_run_never_again(self):
        out, gh, _l = _probe("LIVE")
        self.assertTrue(out["result"].startswith("REQUESTED_REVIEW(pr=7,"), out["result"])
        tokens = [B.first_line_token(x[2]["body"]) for x in gh.writes if x[0] == "POST"]
        self.assertEqual(tokens.count(B.REVIEW_INTENT), 1)
        self.assertEqual(sum(1 for x in gh.writes if x[1] == "issues/7/comments"), 1)
        # a later run on the same world (the intent and the request exist): no second request at this head
        out2, gh2, lines = _probe("LIVE", extra=lambda w: (w["issue_comments"].extend(copy.deepcopy(gh.w["issue_comments"])),
                                                             w["pr"][7]["comments"].extend(copy.deepcopy(gh.w["pr"][7]["comments"]))))
        self.assertNotIn("issues/7/comments", [x[1] for x in gh2.writes])
        self.assertFalse(out2["result"].startswith("REQUESTED_REVIEW"), out2["result"])

    def test_shadow_and_the_shipped_switch_never_write(self):
        for mode, route in (("SHADOW", "BOT_PROBE"), ("SHADOW", "BOT_VERIFIED"), ("SHADOW", "SHADOW"), ("LIVE", "SHADOW")):
            out, gh, _l = _probe(mode, route)
            self.assertTrue(out["result"].startswith("WOULD_REQUEST_REVIEW(pr=7,") or out["result"].startswith("WOULD_OWNER_ACTION"), (mode, route, out["result"]))
            self.assertNotIn("issues/7/comments", [x[1] for x in gh.writes], (mode, route))
            self.assertFalse([x for x in gh.writes if x[0] == "POST" and B.first_line_token(x[2]["body"]) in (B.REVIEW_INTENT, B.REVIEW_RECEIPT)])
            if mode == "SHADOW":
                self.assertEqual(gh.writes, [])
        for route in ("OFF", None, "banana"):                                             # missing or unknown is OFF: no dispatch at all
            out, gh, _l = _probe("LIVE", route)
            self.assertFalse(out["result"].startswith(("REQUESTED_REVIEW", "WOULD_REQUEST")), route)

    def test_the_two_hour_wait_and_owner_gated_paths_stop_it_and_keep_the_decision(self):
        young = lambda w, gh, n: [c["commit"]["committer"].update(date=B.iso(T.NOW)) for c in w["pr"][7]["commits"] if c.get("sha") == T.HEAD]
        gated = lambda w, gh, n: w["pr"][7]["files"].append(dict(w["pr"][7]["files"][0], filename=".github/workflows/x.yml"))
        for name, live in (("head younger than 2 h", young), ("a workflow path", gated)):
            out, gh, lines = _probe("LIVE", live=live)
            self.assertNotIn("issues/7/comments", [x[1] for x in gh.writes], name)
            self.assertFalse(out["result"].startswith(("REQUESTED_REVIEW", "WOULD_REQUEST")), (name, out["result"]))
            self.assertTrue(any(l.startswith("S1_EXECUTOR_REVIEW SKIPPED(") for l in lines), (name, lines))

    def test_the_read_budget_of_a_shadow_dispatch_is_bounded(self):
        out, gh, _l = _probe("SHADOW")
        reads = sum(1 for kind, _p in gh.calls if kind in ("GET", "PAGES", "TEXT", "GRAPHQL"))
        self.assertTrue(out["result"].startswith("WOULD_REQUEST_REVIEW"), out["result"])
        self.assertLess(reads, E.EXECUTE_API_CALLS)
        self.assertLessEqual(reads, 80, reads)                                          # measured: one candidate per run
        self.assertNotIn(("GET", f"actions/variables/{E.HOLD_VARIABLE}"), gh.calls)     # SHADOW never reads the hold live


if __name__ == "__main__":
    unittest.main()
