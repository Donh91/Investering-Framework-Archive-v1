"""S1 executor liveness round (2026-11-27): the native SHADOW blocker and the pre-LIVE conditions L1, L2 and L4 of the
detached review of #2371 at f73c59f7 (Bridge #173/7215658391).

HOLD (P0, native): executor run 45986221512 job 140462413113 ended NOTHING_ACTIONABLE(skipped=hold_unreadable:start(403)).
That job's own log lists its token permissions as Actions, Contents, Issues, Metadata, PullRequests: read; GET
actions/variables/<name> needs a Variables permission, which a workflow cannot grant a GITHUB_TOKEN. SHADOW (no writes)
now decides on the hold GitHub injected into the job env at start; LIVE still reads it live and stays fail-closed.

L1 (FA-P2-02 recovery, Bridge #173/7215315226): the metronome dispatches for the ACTUAL publication (the brief run whose
own publish log says WRITTEN) unless an executor attempt EVALUATED it, is ACTIVE, or is UNKNOWN.

Real code only: the executor's Run on the existing fakes, and the real metronome functions over a fixed read world.
"""
import datetime as dt
import json
import sys
import unittest
import urllib.error
import urllib.request
from datetime import timedelta
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))
sys.path.insert(0, str(ROOT / "scripts" / "orchestration"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import framework_metronome_v1 as M  # noqa: E402
import s1_executor_v1 as E  # noqa: E402
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_executor_trigger_v1 as TT  # noqa: E402
import test_s1_executor_v1 as TE  # noqa: E402
import yaml  # noqa: E402

VAR = ("GET", f"actions/variables/{E.HOLD_VARIABLE}")
WOULD = "WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)"
EXEC_WORKFLOW = yaml.safe_load((ROOT / B.EXECUTOR_WORKFLOW_PATH).read_text(encoding="utf-8"))


class HoldFromTheJobStart(unittest.TestCase):
    def test_empty_hold_reaches_the_decision_without_a_variable_read(self):
        for kw in ({}, {"env": {"GITHUB_EVENT_NAME": "workflow_run", "S1_BRIEF_RUN_ID": "555", "S1_BRIEF_RUN_ATTEMPT": "1",
                                "S1_BRIEF_MAIN": TE.MAIN, "S1_BRIEF_EVENT": "schedule"}}):
            out, gh, _n, _r = TT.published(**kw)
            self.assertEqual((out["result"], out["mode"], out["health"], gh.writes), (WOULD, "SHADOW", "OK", []))
            self.assertNotIn(VAR, gh.calls)

    def test_the_native_403_no_longer_stops_a_shadow_decision(self):
        # replay of run 45986221512: the variables endpoint answers 403 to the job token at every read
        out, gh, _n, _r = TT.published(live=lambda w, gh, n: setattr(gh, "hold_error", 403))
        self.assertEqual((out["result"], out["mode"], gh.writes), (WOULD, "SHADOW", []))
        self.assertNotIn(VAR, gh.calls)

    def test_a_non_empty_hold_is_off_with_no_read_and_no_write(self):
        for hold in ("1", "0", "off", " "):
            out, gh, _n, _r = TT.published(env={"S1_EXECUTOR_HOLD": hold})
            self.assertEqual((out["result"], out["mode"], out["health"], gh.writes), ("EXECUTOR_OFF(hold:start)", "OFF", "HELD", []), repr(hold))
            self.assertNotIn(VAR, gh.calls)
            self.assertNotIn(("PAGES", f"issues/{B.OWNER_ISSUE}/comments"), gh.calls)       # stops before the ledger

    def test_a_missing_or_unreadable_hold_value_fails_closed(self):
        for value in (None, 0, ["x"]):
            r, gh, _n, body, _d = TT.setup()
            if value is None:
                r.env.pop(E.HOLD_VARIABLE)
            else:
                r.env[E.HOLD_VARIABLE] = value
            out = r.execute_published()
            self.assertEqual((out["result"], out["health"], gh.writes), (f"NOTHING_ACTIONABLE(skipped={E.HOLD_ENV_MISSING})", "UNVERIFIED", []), value)
            self.assertNotIn(VAR, gh.calls)

    def test_shadow_never_reads_the_hold_live(self):
        # a live value that would stop, and a live read that would fail: SHADOW sees neither (it writes nothing)
        for live in (lambda w, gh, n: setattr(gh, "hold", "stop"), lambda w, gh, n: setattr(gh, "hold_error", 403)):
            out, gh, _n, _d = TE.execute(mode="SHADOW", mutate=TE.BEAT, live=live)
            self.assertEqual((out["result"], gh.writes), (WOULD, []))
            self.assertNotIn(VAR, gh.calls)

    def test_live_is_refused_while_the_live_hold_read_answers_403(self):
        # LIVE gate: the token of this job cannot read repository variables, so LIVE stops at its first live read
        out, gh, _n, _d = TE.execute(mode="LIVE", mutate=TE.BEAT, live=lambda w, gh, n: setattr(gh, "hold_error", 403))
        self.assertEqual((out["result"], out["health"], gh.writes), ("NOTHING_ACTIONABLE(skipped=hold_unreadable:start(403))", "UNVERIFIED", []))
        out, gh, _n, _d = TE.execute(mode="LIVE", mutate=TE.BEAT, live=lambda w, gh, n: (setattr(gh, "hold_error", 403), setattr(gh, "hold_from", 2)))
        self.assertEqual((out["result"], gh.writes), ("NOTHING_ACTIONABLE(skipped=hold_unreadable:intent(403))", []))
        # 403 is never "not set"; only 404 is
        for code in (401, 403, 500):
            out, gh, _n, _d = TE.execute(mode="LIVE", mutate=TE.BEAT, live=lambda w, gh, n, c=code: setattr(gh, "hold_error", c))
            self.assertEqual((out["result"], gh.writes), (f"NOTHING_ACTIONABLE(skipped=hold_unreadable:start({code}))", []), code)

    def test_the_workflow_passes_the_hold_and_gains_no_permission(self):
        job = EXEC_WORKFLOW["jobs"]["execute"]
        self.assertEqual(job["steps"][-1]["env"]["S1_EXECUTOR_HOLD"], "${{ vars.S1_EXECUTOR_HOLD }}")
        self.assertEqual(job["permissions"], {"contents": "read", "actions": "read", "pull-requests": "read", "issues": "read"})
        self.assertEqual(EXEC_WORKFLOW["permissions"], {})
        switch = json.loads((ROOT / B.SWITCH).read_text(encoding="utf-8"))
        self.assertEqual((switch["executor"], switch["fallback_route"]), ("SHADOW", "OFF"))


class ReviewConditionsL2L4(unittest.TestCase):
    def test_n1_an_own_run_that_is_not_in_progress_is_not_bound(self):
        for status in ("completed", "queued", "waiting", None):
            r, gh, _n, _b, _d = TT.setup()
            gh.runs[TT.OWN]["status"] = status
            gh.exec_runs = [gh.runs[TT.OWN]]
            out = r.execute_published()
            self.assertEqual((out["result"], gh.writes), ("NO_DECISION(evaluated_unproven:own_run_binding)", []), status)

    def test_l4_a_window_of_more_than_30_runs_is_runs_page(self):
        r, gh, _n, _b, _d = TT.setup(exec_runs=[TT.earlier(4000 + i) for i in range(E.EXECUTOR_RUNS_PAGE - 1)])
        gh.exec_total = E.EXECUTOR_RUNS_PAGE + 1                                         # GitHub's count says one more page exists
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:runs_page)")
        r, gh, _n, _b, _d = TT.setup(exec_runs=[TT.earlier(4000 + i) for i in range(E.EXECUTOR_RUNS_PAGE)])   # 31 rows on one page
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:runs_page)")

    def test_an_attempt_that_failed_before_the_execute_step_did_not_evaluate(self):
        failed = {"status": "completed", "conclusion": "failure", "started_at": B.iso(TE.NOW),
                  "steps": [{"name": "Run actions/checkout@v4", "status": "completed", "conclusion": "failure"},
                            {"name": E.EXECUTE_STEP, "status": "completed", "conclusion": "skipped"}]}
        r, gh, _n, _b, _d = TT.setup(exec_runs=[TT.earlier(4321)])
        gh.exec_jobs[(4321, 1)] = failed
        self.assertEqual((r.execute_published()["result"], gh.writes), (WOULD, []))
        self.assertNotIn(("TEXT", "actions/jobs/1004321/logs"), gh.calls)
        # the execute step ran (or is not listed): its log is required
        for steps in ([{"name": E.EXECUTE_STEP, "status": "completed", "conclusion": "failure"}], [{"name": "other", "status": "completed", "conclusion": "failure"}]):
            r, gh, _n, _b, _d = TT.setup(exec_runs=[TT.earlier(4321)], logs={4321: "no health line"})
            gh.exec_jobs[(4321, 1)] = dict(failed, steps=steps)
            self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:health=4321.1)")
        self.assertEqual(E.EXECUTE_STEP, EXEC_WORKFLOW["jobs"]["execute"]["steps"][-1]["name"])
        self.assertEqual(M.EXECUTE_STEP, E.EXECUTE_STEP)                                 # the metronome classifies the same step


# ----------------------------------------------------------------------------------------------- L1: the 8 scenarios
T0, brun, erun, Reader, hline = TT.T0, TT.brun, TT.erun, TT.Reader, TT.hline
NOW = T0 + dt.timedelta(minutes=31)
D = brun(21, rid=10)                                                                     # the real publication, completed :25


def due(briefs, execs, reader, now=NOW):
    return M.s1exec_due(now, briefs, execs, reader)


class RecoveryScenarios(unittest.TestCase):
    def test_1_a_push_fallback_after_a_real_publication(self):
        f = brun(24, event="push", took=2, rid=11)                                       # built nothing, completed :26
        ewr = erun(26, event="workflow_run", rid=20)                                     # its executor: the published brief is D's
        rd = Reader(pubs={11: "NONE"}, attempts={(20, 1): {"log": hline(20, 1, "11", result="NO_DECISION(published_run=10)")}})
        self.assertEqual(due([D, f], [ewr], rd), (True, "DUE"))                          # D was never evaluated: re-dispatch
        # before this round: the newest successful run (F) and "an executor run since" suppressed it
        self.assertIn(("jobs", 11, None), rd.calls)
        # once the dispatched run evaluated D, nothing more
        rd.attempts[(21, 1)] = {"log": hline(21, 1, "10")}
        self.assertEqual(due([D, f], [ewr, erun(32, rid=21)], rd, now=NOW + dt.timedelta(minutes=3)), (False, "ALREADY_EVALUATED"))

    def test_2_a_failed_executor_before_evaluation(self):
        before = {"job": {"conclusion": "failure", "steps": [{"name": "Run actions/checkout@v4", "status": "completed", "conclusion": "failure"},
                                                             {"name": M.EXECUTE_STEP, "status": "completed", "conclusion": "skipped"}]}}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): before})), (True, "DUE"))
        # it failed inside the execute step (a crash, no health line, or a crash line naming no brief): UNKNOWN, no blind retry
        inside = {"job": {"conclusion": "failure", "steps": [{"name": M.EXECUTE_STEP, "status": "completed", "conclusion": "failure"}]}, "log": "Traceback"}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): inside})), (False, "EVALUATION_UNKNOWN"))
        crash = {"log": hline(20, 1, None, result="EXECUTOR_CRASHED(KeyError)")}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): crash})), (False, "EVALUATION_UNKNOWN"))

    def test_3_a_source_outage(self):
        self.assertEqual(due([D], [], Reader(pubs={10: None})), (False, "PUBLICATION_UNKNOWN"))
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): None})), (False, "EVALUATION_UNKNOWN"))
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): {"log": None}})), (False, "EVALUATION_UNKNOWN"))
        rd = Reader()
        rd.jobs = mock.Mock(side_effect=TimeoutError("READ_BUDGET_EXCEEDED"))           # through the isolating reader
        self.assertEqual(due([D], [], M.S1ExecReader(rd)), (False, "PUBLICATION_UNKNOWN"))

    def test_4_a_delayed_runner(self):
        self.assertEqual(due([D], [erun(26, status="queued", rid=20)], Reader()), (False, "TARGET_ACTIVE"))
        # it ran late: a stale verdict for D is still D's evaluation (never a second one)
        stale = {"log": hline(20, 1, "10", result="BRIEF_STALE(age_min=21)")}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): stale})), (False, "ALREADY_EVALUATED"))

    def test_5_a_changed_published_issue(self):
        # the executor could not prove D's issue any more: its NO_DECISION for D is UNKNOWN, not a reason to retry
        edited = {"log": hline(20, 1, None, result="NO_DECISION(brief_run=10:edited_outside_run)")}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): edited})), (False, "EVALUATION_UNKNOWN"))
        refused = {"log": hline(20, 1, "10", result="NO_DECISION(evaluated_unproven:health=19.1)")}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): refused})), (False, "EVALUATION_UNKNOWN"))
        # a NEWER publication replaced it: that one is the target, and the old executor run was about D
        d2 = brun(27, rid=12)
        self.assertEqual(due([D, d2], [erun(26, rid=20)], Reader(), now=NOW + dt.timedelta(minutes=2)), (True, "DUE"))
        # the other attempt's brief_attempt must be the publication's
        other_attempt = {"log": hline(20, 1, "10", brief_attempt="2")}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): other_attempt})), (True, "DUE"))

    def test_6_duplicate_or_cancelled_attempts(self):
        cancelled_unstarted = {"job": {"conclusion": "cancelled", "steps": [], "started_at": None}}
        rerun = dict(erun(26, rid=20), run_attempt=2)
        rd = Reader(attempts={(20, 1): cancelled_unstarted, (20, 2): {"log": hline(20, 2, "10")}})
        self.assertEqual(due([D], [rerun], rd), (False, "ALREADY_EVALUATED"))
        rd = Reader(attempts={(20, 1): cancelled_unstarted, (20, 2): cancelled_unstarted})
        self.assertEqual(due([D], [rerun], rd), (True, "DUE"))
        started = {"job": {"conclusion": "cancelled", "started_at": B.iso(TE.NOW), "steps": [{"name": M.EXECUTE_STEP, "status": "completed", "conclusion": "cancelled"}]}, "log": None}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): started})), (False, "EVALUATION_UNKNOWN"))
        # two evaluations (a duplicate): still ALREADY_EVALUATED, and the rows' order does not matter
        rd = Reader(attempts={(20, 1): {"log": hline(20, 1, "10")}, (21, 1): {"log": hline(21, 1, "10", result="NO_DECISION(already_evaluated=20.1)")}})
        self.assertEqual(due([D], [erun(27, rid=21), erun(26, rid=20)], rd), (False, "ALREADY_EVALUATED"))
        # the read bound: more attempts than S1EXEC_ATTEMPT_READS is UNKNOWN
        many = [dict(erun(26, rid=20), run_attempt=M.S1EXEC_ATTEMPT_READS + 1)]
        self.assertEqual(due([D], many, Reader(attempts={(20, n): "nojob" for n in range(1, 9)})), (False, "EVALUATION_UNKNOWN"))

    def test_7_the_20_minute_window(self):
        self.assertEqual(due([D], [], Reader(), now=T0 + dt.timedelta(minutes=46)), (False, "BRIEF_TOO_OLD"))
        # the only publication is stale; a fresh fallback run that built nothing is no publication: expire, never re-run
        old = brun(5, rid=9)
        fresh_fallback = brun(24, event="workflow_run", took=1, rid=11)
        self.assertEqual(due([old, fresh_fallback], [], Reader(pubs={11: "NONE"})), (False, "NO_FRESH_PUBLICATION"))
        # at most S1EXEC_PUBLICATION_READS fresh runs are inspected
        runs = [brun(22 + i, event="push", took=1, rid=30 + i) for i in range(M.S1EXEC_PUBLICATION_READS)] + [brun(21, rid=10)]
        self.assertEqual(due(runs, [], Reader(pubs={30 + i: "NONE" for i in range(5)})), (False, "NO_FRESH_PUBLICATION"))

    def test_8_an_active_run(self):
        self.assertEqual(due([D], [erun(29, status="in_progress", rid=20)], Reader()), (False, "TARGET_ACTIVE"))
        active_job = {"job": {"status": "in_progress", "conclusion": None}}
        self.assertEqual(due([D], [erun(26, rid=20)], Reader(attempts={(20, 1): active_job})), (False, "TARGET_ACTIVE"))

    def test_the_publication_is_the_brief_runs_own_written_line(self):
        class Fixed:
            def __init__(self, text, publish=None):
                self.text = text
                self.publish = publish or {"id": 7, "name": "publish", "status": "completed", "conclusion": "success"}

            def jobs(self, run_id, attempt):
                return [{"name": "build", "status": "completed", "conclusion": "success"}, self.publish]

            def log(self, job_id):
                return self.text
        for text, want in (("S1_TICK_BRIEF_PUBLISHED issue=3 run=10 result=WRITTEN reason=created\n", "WRITTEN"),
                           ("x S1_TICK_BRIEF_PUBLISHED issue=12 run=10 result=WRITTEN reason=replaced\n", "WRITTEN"),
                           ("S1_TICK_BRIEF_NOT_PUBLISHED issue=3 run=10 result=SKIPPED reason=newer_brief_published\n", "NONE"),
                           ("S1_TICK_BRIEF_PUBLISHED issue=3 run=99 result=WRITTEN reason=created\n", M.UNKNOWN),    # another run's line
                           ("S1_TICK_BRIEF_PUBLISHED issue=3 run=10 result=WRITTEN reason=a\nS1_TICK_BRIEF_PUBLISHED issue=3 run=10 result=WRITTEN reason=b\n", M.UNKNOWN),
                           (None, M.UNKNOWN)):
            self.assertEqual(M.publication_of(Fixed(text), D), want, text)
        self.assertEqual(M.publication_of(Fixed("", {"name": "publish", "status": "completed", "conclusion": "skipped"}), D), "NONE")
        self.assertEqual(M.publication_of(Fixed("", {"name": "publish", "status": "in_progress", "conclusion": None}), D), M.UNKNOWN)

    def test_the_new_reads_are_actions_read_routes_and_never_forward_the_token(self):
        gh, sent = M.Github("x"), []

        class Answer:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self, *a):
                return json.dumps({"total_count": 0, "jobs": []}).encode()

        with mock.patch.object(M.urllib.request, "urlopen", lambda req, timeout=None: sent.append(req.full_url) or Answer()):
            self.assertEqual(gh.jobs(45986221512, None), [])
            self.assertEqual(gh.jobs(45986221512, 2), [])
        self.assertEqual(sent, [f"https://api.github.com/repos/{M.REPO}/actions/runs/45986221512/jobs?per_page=30",
                                f"https://api.github.com/repos/{M.REPO}/actions/runs/45986221512/attempts/2/jobs?per_page=30"])
        for route in (f"/repos/{M.REPO}/actions/runs/1/logs", f"/repos/{M.REPO}/actions/variables/S1_EXECUTOR_HOLD", f"/repos/{M.REPO}/issues"):
            with self.assertRaises(ValueError):
                gh._req("GET", route)
        h = M._LogRedirect()
        req = urllib.request.Request("https://api.github.com/x", headers={"Authorization": "Bearer t"})
        follow = h.redirect_request(req, None, 302, "Found", {}, "https://productionresultssa1.blob.core.windows.net/log?sig=1")
        self.assertNotIn("authorization", {k.casefold() for k in list(follow.headers) + list(follow.unredirected_hdrs)})
        with self.assertRaises(ValueError):
            h.redirect_request(req, None, 302, "Found", {}, "https://evil.example.com/log")
        metro = yaml.safe_load((ROOT / ".github/workflows/framework-metronome.yml").read_text(encoding="utf-8"))
        self.assertEqual(metro["permissions"], {"actions": "write", "contents": "read", "deployments": "read"})   # unchanged


if __name__ == "__main__":
    unittest.main()
