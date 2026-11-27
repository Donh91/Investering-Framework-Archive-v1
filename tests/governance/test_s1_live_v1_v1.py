"""S1 LIVE v1 (owner-present enable PR): the narrow LIVE scope MERGE_LOW_NORMAL_ONLY, HOLD option (i), the canary cap, and
the gate-5 replacement rehearsal of the whole LIVE path in the fake-GitHub harness.

LIVE v1 may write exactly ONE action type: the sha-pinned MERGE of a LOW or MEDIUM PR whose review route is an exact-head
independent APPROVE receipt (route (b)), with that merge's records (intent, receipt, readback halt) and the settlement
of its own intents. Nothing else is written: no heartbeat, halt decision, recall, label, fallback candidate or review
dispatch. HOLD: the S1_EXECUTOR_HOLD value GitHub injects at job start, plus the live re-read of the switch on main before
every write (owner decision #173/7227941605, option (i)). Canary: at most K (switch, default 1) merges per UTC day.

Real code only: the executor's Run with the fakes of test_s1_executor_v1 (the brief is built by the real s1_tick_brief_v1).
"""
import copy
import json
import sys
import unittest
import urllib.error
from datetime import timedelta
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s1_decision_v1 as D  # noqa: E402
import s1_executor_v1 as E  # noqa: E402
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_decision_v1 as TD  # noqa: E402
import test_s1_executor_v1 as TE  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402
import yaml  # noqa: E402

HEAD, NOW = TE.HEAD, TE.NOW
SCOPE = "MERGE_LOW_NORMAL_ONLY"
SHIPPED = json.loads((ROOT / B.SWITCH).read_text(encoding="utf-8"))
EXEC_WORKFLOW = yaml.safe_load((ROOT / B.EXECUTOR_WORKFLOW_PATH).read_text(encoding="utf-8"))
BRIEF_WORKFLOW = yaml.safe_load((ROOT / B.WORKFLOW_PATH).read_text(encoding="utf-8"))


def v1(*more):
    """A LIVE v1 world: the narrow scope, today's heartbeat present, no Codex review, a Claude exact-head APPROVE receipt."""
    def mutate(w):
        w["switch"]["live_scope"] = SCOPE
        TE.BEAT(w)
        TD.no_codex(w)
        TD.claude_receipt()(w)
        for m in more:
            m(w)
    return mutate


def run(*more, live=None, env=None, mode="LIVE"):
    out, gh, native, d = TE.execute(mode=mode, mutate=v1(*more), policy=D.RECALL_POLICY, live=live, env=env)
    return out, gh, d


def receipt_today(pr=8, head="c" * 40, minutes=60):
    """An S1 merge receipt of another PR earlier today (what the canary counts)."""
    return lambda w: w["issue_comments"].append(TB.comment(90, f"S1_LANE_MERGE_v1\npr: {pr}\nhead: {head}\ncontract=44444444", TB.BOT, minutes))


class Rehearsal(unittest.TestCase):
    """Gate 5 replacement: the full LIVE v1 path in the fake harness."""

    def test_1_merge(self):
        out, gh, d = run()
        self.assertEqual((d["action"], d["merge"]["review"], d["merge"]["risk"]), ("MERGE", "CLAUDE", "LOW"))
        self.assertTrue(out["result"].startswith("MERGED(n=1,"), out["result"])
        self.assertEqual(TE.tokens(gh), ["S1_LANE_MERGE_INTENT_v1", "MERGE", "S1_LANE_MERGE_v1"])
        put = [x for x in gh.writes if x[0] == "PUT"]
        self.assertEqual(put, [("PUT", "pulls/7/merge", {"merge_method": "squash", "sha": HEAD})])   # sha-pinned squash
        self.assertEqual(out["health"], "OK")

    def test_2_refused_merge_is_settled_by_the_next_run_and_never_tried_again(self):
        w = TD.thin_world("LIVE", D.RECALL_POLICY)
        v1()(w)
        results, puts = [], 0
        for hour in range(3):
            now = NOW + timedelta(minutes=2)
            own = 555 + hour
            done = {str(r): TE.executor_run(r, created=NOW - timedelta(minutes=1), status="completed") for r in range(555, own)}
            run555 = TE.executor_run(555, created=NOW - timedelta(minutes=1), status="in_progress") if hour == 0 else done["555"]
            brief = B.build_brief(dict(copy.deepcopy(w), codex_feed=TD.codex_feed_of(w), executor_runs=dict(done, **{"555": run555}),
                                       merge_proofs={"7": {"number": 7, "merged": False, "merge_commit_sha": None, "head_sha": HEAD, "state": "open"}}))
            body, decision = B.render_issue(brief)
            gh, native = TE.FakeGitHub(w, now), TE.FakeNative(w)
            gh.runs.update({int(k): copy.deepcopy(v) for k, v in done.items()})
            gh.runs[555] = copy.deepcopy(run555)
            if hour:
                gh.runs[own] = TE.executor_run(own, created=NOW, status="in_progress", updated=now)
            gh.exec_runs = [gh.runs[own]]
            gh.issue_body = body
            gh.fail_merge = urllib.error.HTTPError("u", 405, "Not Allowed", {}, None)
            gh.next_id = 7000 + 10 * hour
            files = {"switch": w["switch"], "contract": w["contract"], "policy": TB.POLICY, "gate_isolation": "LIVE", "bindings": TB.BINDINGS,
                     "budgets": TB.BUDGETS, "push_filters": copy.deepcopy(w.get("push_filters"))}
            out = E.Run(gh, native, dict(TE.ENV, GITHUB_RUN_ID=str(own)), files, now_fn=lambda: now, out=lambda line: None).execute(body)
            puts += sum(1 for x in gh.writes if x[0] == "PUT")
            results.append((out["result"], TE.tokens(gh)))
        self.assertEqual(puts, 1)                                                        # ONE merge call, ever, for this head
        self.assertEqual(results[0], ("MERGE_REFUSED(405)", ["S1_LANE_MERGE_INTENT_v1", "MERGE"]))
        self.assertEqual(results[1], ("SETTLED(ABSENT(7001))", ["S1_OP_DONE_v1"]))       # the settlement is in the v1 scope
        self.assertEqual(results[2], ("NOTHING_ACTIONABLE(skipped=7:C9:attempted_head)", []))

    def test_3_hold_set_is_off_with_no_read_and_no_write(self):
        for hold in ("1", " ", "0"):
            out, gh, _d = run(env={"S1_EXECUTOR_HOLD": hold})
            self.assertEqual((out["result"], out["mode"], out["health"], gh.writes), ("EXECUTOR_OFF(hold:start)", "OFF", "HELD", []), repr(hold))
        out, gh, _d = run(env={"S1_EXECUTOR_HOLD": None})                                # unreadable: never "no hold"
        self.assertEqual((out["result"], gh.writes), (f"NOTHING_ACTIONABLE(skipped={E.HOLD_ENV_MISSING})", []))
        # the switch on main changed after the job started (no longer the LIVE one this run verified): no write
        out, gh, _d = run(live=lambda w, g, n: w["pins_actual"].update({B.SWITCH: "0" * 40}))
        self.assertEqual(gh.writes, [])
        self.assertNotIn(("GET", f"actions/variables/{E.HOLD_VARIABLE}"), gh.calls)       # the 403 endpoint is never read

    def test_4_canary_cap_reached_is_a_noop(self):
        out, gh, _d = run(receipt_today())
        self.assertEqual((out["result"], out["health"], gh.writes), ("NOTHING_ACTIONABLE(skipped=canary:cap(day=1,k=1))", "HELD", []))
        # yesterday's merge does not count; an intent today does (it may have merged)
        out, gh, _d = run(receipt_today(minutes=60 * 30))
        self.assertTrue(out["result"].startswith("MERGED("), out["result"])
        intent_today = lambda w: w["issue_comments"].append(TB.comment(91, f"S1_LANE_MERGE_INTENT_v1\npr: 9\nhead: {'d' * 40}\ncontract=44444444", TB.OWNER, 30))
        out, gh, _d = run(intent_today)
        self.assertEqual((out["result"], gh.writes), ("NOTHING_ACTIONABLE(skipped=canary:cap(day=1,k=1))", []))
        # K from the switch; a bad canary block fails closed
        out, gh, _d = run(receipt_today(), lambda w: w["switch"].update(canary={"max_merges_per_utc_day": 2}))
        self.assertTrue(out["result"].startswith("MERGED("), out["result"])
        for bad in ({"max_merges_per_utc_day": -1}, {"max_merges_per_utc_day": "1"}, {"max_merges_per_utc_day": True}, "1", None):
            out, gh, _d = run(lambda w, bad=bad: w["switch"].update(canary=bad))
            self.assertEqual((out["result"], gh.writes), ("NOTHING_ACTIONABLE(skipped=canary:config)", []), bad)
        out, gh, _d = run(lambda w: w["switch"].update(canary={"max_merges_per_utc_day": 0}))
        self.assertEqual(gh.writes, [])

    def test_5_high_or_unreceipted_pr_is_never_merged(self):
        # a merge decision on route (a) (a completed Codex review, no receipt) is out of the v1 scope: no write
        out, gh, _n, d = TE.execute(mode="LIVE", mutate=lambda w: (w["switch"].update(live_scope=SCOPE), TE.BEAT(w)))
        self.assertEqual((d["action"], d["merge"]["review"]), ("MERGE", "CODEX"))
        self.assertEqual((out["result"], gh.writes), ("NOTHING_ACTIONABLE(skipped=live_scope:route=CODEX)", []))
        # the scope's risk rule (the decision never MERGEs HIGH on route (b); the executor checks it again on its own)
        r, gh, _n, body, d = TE.setup(mode="LIVE", mutate=v1(), policy=D.RECALL_POLICY)
        r.brief, r.decision = B.parse_body(body), d
        for risk in ("HIGH", "HIGH_IMPACT", "EXTREME", "UNCLEAR", "OWNER_GATED"):
            with self.assertRaises(E.Stop) as stop:
                r.check_scope(dict(d["merge"], risk=risk), {"route": "CLAUDE", "risk": risk}, [])
            self.assertEqual((stop.exception.reason, stop.exception.kind), (f"live_scope:risk={risk}", E.BLOCKED))
        with self.assertRaises(E.Stop):                                                  # the decision says LOW, this run's proof says HIGH
            r.check_scope(d["merge"], {"route": "CLAUDE", "risk": "HIGH"}, [])
        r.check_scope(dict(d["merge"], risk="MEDIUM"), {"route": "CLAUDE", "risk": "MEDIUM"}, [])
        self.assertEqual(r.scope_cleared, (7, HEAD))

    def test_6_stale_head_or_stale_decision_is_never_merged(self):
        out, gh, _d = run(live=lambda w, g, n: g.pull["head"].update(sha="c" * 40))
        self.assertNotIn("PUT", [x[0] for x in gh.writes])
        self.assertFalse(out["result"].startswith("MERGED"), out["result"])
        out, gh, _n, _d = TE.execute(mode="LIVE", mutate=v1(), policy=D.RECALL_POLICY, minutes=D.EXECUTE_MAX_AGE_MINUTES + 1)
        self.assertEqual((out["result"], gh.writes), ("BRIEF_STALE(age_min=21)", []))
        # the head moved after the intent: the intent is the alarm, no merge call
        out, gh, _d = run(live=lambda w, g, n: setattr(g, "after_intent", lambda g2: g2.pull["head"].update(sha="c" * 40)))
        self.assertEqual(TE.tokens(gh), ["S1_LANE_MERGE_INTENT_v1"])
        self.assertTrue(out["result"].startswith("MERGE_ABORTED_AFTER_INTENT("), out["result"])


class NothingElseIsWritten(unittest.TestCase):
    def test_a_noop_with_a_heartbeat_due_writes_nothing(self):
        # the shape of every native SHADOW decision since 2026-11-27 13:00Z: NOOP, nothing actionable, heartbeat due
        out, gh, _n, d = TE.execute(mode="LIVE", mutate=lambda w: (w["switch"].update(live_scope=SCOPE), w.update(pulls=[], pr={})))
        self.assertEqual(d["action"], "NOOP")
        self.assertEqual(gh.writes, [])
        self.assertIn("S1_EXECUTOR_HEARTBEAT WOULD_HEARTBEAT", out["lines"])

    def test_the_gateway_refuses_every_other_write_class(self):
        r, gh, _n, body, d = TE.setup(mode="LIVE", mutate=v1(), policy=D.RECALL_POLICY)
        r.brief, r.decision, r.mode = B.parse_body(body), d, "LIVE"
        bodies = {"heartbeat": "S1_HEARTBEAT_v1 main=a contract=44444444", "candidate": "S1_FALLBACK_CANDIDATE_v1\npr: 7",
                  "recall": "S1_CODEX_RECALL_PENDING_v1\npr: 7", "clear": "S1_CODEX_RECALL_CLEARED_v1\npr: 7",
                  "review intent": B.review_dispatch_body(B.REVIEW_INTENT, 7, HEAD, 555, 1),
                  "an OP_DONE outside the reconcile": "S1_OP_DONE_v1\nintent: 1\nresult: ABSENT",
                  "a halt with no merge of this run": "S1_LANE_HALTED PR=- head=-",
                  "a receipt with no merge of this run": "S1_LANE_MERGE_v1\npr: 7",
                  "an intent this run did not clear": "S1_LANE_MERGE_INTENT_v1\npr: 7"}
        for name, text in bodies.items():
            with self.assertRaises(E.Stop, msg=name) as stop:
                r.write("comment", body=text)
            self.assertTrue(stop.exception.reason.startswith("live_scope:"), (name, stop.exception.reason))
        for kind, kw in (("label", {"pr": 7, "add": True}), ("review", {"pr": 7, "head": HEAD, "intent": 1}), ("merge", {"pr": 7, "sha": HEAD})):
            with self.assertRaises(E.Stop) as stop:
                r.write(kind, **kw)
            self.assertTrue(stop.exception.reason.startswith("live_scope:"), (kind, stop.exception.reason))
        self.assertEqual(gh.writes, [])

    def test_an_unknown_or_missing_scope_writes_nothing(self):
        for scope in (None, "", "banana", "MERGE"):
            out, gh, _n, d = TE.execute(mode="LIVE", mutate=v1(lambda w, s=scope: w["switch"].update(live_scope=s) if s is not None else w["switch"].pop("live_scope")),
                                    policy=D.RECALL_POLICY)
            self.assertEqual((out["result"], gh.writes), ("NOTHING_ACTIONABLE(skipped=live_scope_unknown)", []), scope)

    def test_shadow_shows_the_v1_gates_and_writes_nothing(self):
        out, gh, _d = run(mode="SHADOW")
        self.assertEqual((out["result"], gh.writes), ("WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CLAUDE)", []))
        out, gh, _d = run(receipt_today(), mode="SHADOW")
        self.assertEqual((out["result"], gh.writes), ("NOTHING_ACTIONABLE(skipped=canary:cap(day=1,k=1))", []))


class AsShipped(unittest.TestCase):
    def test_the_switch_and_the_job_permissions_move_together(self):
        self.assertEqual((SHIPPED["executor"], SHIPPED["live_scope"], SHIPPED["canary"]["max_merges_per_utc_day"]), ("LIVE", SCOPE, 1))
        self.assertEqual((SHIPPED["fallback_route"], SHIPPED["review_dispatch"], SHIPPED["review_dispatch_probe"]), ("OFF", "SHADOW", None))
        self.assertEqual(E.LIVE_SCOPES[SCOPE], {"routes": ("CLAUDE",), "risks": ("LOW", "MEDIUM")})
        self.assertEqual(EXEC_WORKFLOW["permissions"], {})
        self.assertEqual(EXEC_WORKFLOW["jobs"]["execute"]["permissions"],
                         {"contents": "write", "actions": "read", "pull-requests": "write", "issues": "write"})   # no actions: write
        for name, job in BRIEF_WORKFLOW["jobs"].items():                               # the brief workflow gains nothing
            self.assertNotIn("write", [v for k, v in job["permissions"].items() if k in ("contents", "pull-requests", "actions")], name)

    def test_every_action_is_pinned_by_commit_sha_and_no_pull_request_target(self):
        for wf in (EXEC_WORKFLOW, BRIEF_WORKFLOW):
            uses = [s["uses"] for job in wf["jobs"].values() for s in job["steps"] if s.get("uses")]
            self.assertTrue(uses)
            for ref in uses:
                self.assertRegex(ref, r"^actions/(checkout|setup-python)@[0-9a-f]{40}$")
        for path in (B.EXECUTOR_WORKFLOW_PATH, B.WORKFLOW_PATH):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertNotIn("pull_request_target", text)
            self.assertNotIn("secrets.", text)
            self.assertIn("actions/checkout@11d5960a326750d5838078e36cf38b85af677262", text)   # v4.4.0 = the v4 tag (git ls-remote, 2026-11-27)
            self.assertIn("actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065", text)   # v5.6.0 = the v5 tag

    def test_no_live_variables_read_remains(self):
        source = (ROOT / "scripts/governance/s1_executor_v1.py").read_text(encoding="utf-8")
        self.assertNotIn('gh.get(f"actions/variables', source)


if __name__ == "__main__":
    unittest.main()
