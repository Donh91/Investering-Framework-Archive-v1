"""S1 executor trigger round (2026-11-26): every successful published schedule or workflow_dispatch brief gets ONE executor
evaluation, also when the metronome dispatched the brief with the workflow token (GitHub creates no workflow_run event for
such a run, so the executor never started: one run since #2337, and that one skipped).

Real code, fixtures only: the executor's Run with the fake GitHub and git of test_s1_executor_v1 (the brief is built by the
real s1_tick_brief_v1 from the same world), and the real metronome decision and tick with a fake client.
"""
import copy
import datetime as dt
import io
import json
import sys
import unittest
import urllib.error
from contextlib import redirect_stdout
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
import test_s1_executor_v1 as TE  # noqa: E402
import yaml  # noqa: E402

MAIN, NOW = TE.MAIN, TE.NOW
OWN = 9000                                   # this executor run (newer than every earlier executor run below)
# a dispatched executor run: no triggering run, so the S1_BRIEF_* the workflow passes from github.event.workflow_run are empty
DISPATCH_ENV = {"GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_RUN_ID": str(OWN), "S1_BRIEF_RUN_ID": "", "S1_BRIEF_RUN_ATTEMPT": "",
                "S1_BRIEF_MAIN": "", "S1_BRIEF_EVENT": ""}
EXEC_WORKFLOW = yaml.safe_load((ROOT / B.EXECUTOR_WORKFLOW_PATH).read_text(encoding="utf-8"))
METRO_WORKFLOW = yaml.safe_load((ROOT / ".github/workflows/framework-metronome.yml").read_text(encoding="utf-8"))


def brief_run(brief, **kw):
    """GET actions/runs/<brief run id> as GitHub answers it after the brief run completed (the brief was generated inside
    the run, the issue was published inside it)."""
    made = B.stamp(brief["generated_at"])
    return dict({"id": brief["run_id"], "path": B.WORKFLOW_PATH, "event": brief["event"], "head_branch": "main", "head_sha": brief["main"],
                 "run_attempt": brief["run_attempt"], "status": "completed", "conclusion": "success",
                 "run_started_at": B.iso(made - timedelta(minutes=1)), "updated_at": B.iso(made + timedelta(minutes=2)),
                 "created_at": B.iso(made - timedelta(minutes=1)), "repository": {"full_name": B.REPO}, "head_repository": {"full_name": B.REPO},
                 "triggering_actor": {"login": "github-actions[bot]"}, "actor": {"login": "github-actions[bot]"}}, **kw)


def health(brief_run_id, result="WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)", attempt="1", **extra):
    doc = dict({"v": 1, "state": "OK", "run": "__RID__", "attempt": "__ATTEMPT__", "mode": "SHADOW", "action": "NOOP", "result": result, "brief_run": brief_run_id}, **extra)
    if attempt is not None:
        doc["brief_attempt"] = attempt
    return "2026-11-18T10:43:00Z S1_EXECUTOR_HEALTH " + json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n"


def earlier(run_id, minutes_ago=1, **kw):
    """An earlier completed executor run on main (s1-executor.yml)."""
    return TE.executor_run(run_id, created=NOW - timedelta(minutes=minutes_ago), updated=NOW - timedelta(minutes=minutes_ago), **kw)


def setup(env=None, run=None, mutate=None, logs=None, exec_runs=None, issue_updated=None, mode="SHADOW", **kw):
    """The executor as a dispatched run (default) after brief run 555 completed; `run` changes the native brief run."""
    r, gh, native, body, decision = TE.setup(mode=mode, mutate=mutate, env=dict(DISPATCH_ENV, **(env or {})), **kw)
    brief = B.parse_body(body)
    gh.runs[555] = brief_run(brief, **(run or {}))
    own = int(r.env["GITHUB_RUN_ID"])
    gh.runs[own] = TE.executor_run(own, created=NOW, status="in_progress", event=r.env["GITHUB_EVENT_NAME"],
                                    run_attempt=int(r.env["GITHUB_RUN_ATTEMPT"]))
    gh.issue_updated = issue_updated or B.iso(B.stamp(brief["generated_at"]) + timedelta(minutes=1))
    gh.exec_runs = [gh.runs[own]] + list(exec_runs or [])
    gh.w["exec_logs"] = {
        key: (value.replace("__RID__", str(key[0] if isinstance(key, tuple) else key))
                    .replace("__ATTEMPT__", str(key[1] if isinstance(key, tuple) else 1))
              if isinstance(value, str) else value)
        for key, value in (logs or {}).items()
    }
    return r, gh, native, body, decision


def published(**kw):
    r, gh, native, body, decision = setup(**kw)
    return r.execute_published(), gh, native, r


def reads(gh, path):
    return [c for c in gh.calls if c[1] == path]


class DispatchedRunResolvesFromThePublishedBrief(unittest.TestCase):
    def test_workflow_dispatch_resolves_the_brief_run_and_evaluates_it_in_shadow(self):
        out, gh, native, r = published()
        self.assertEqual((out["mode"], out["result"], gh.writes), ("SHADOW", "WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)", []))
        self.assertEqual(len(reads(gh, "actions/runs/555")), 1)                         # the brief run, read natively
        self.assertIn(("head_commit",), native.calls)                                    # this checkout is the brief's main
        self.assertEqual((r.env["S1_BRIEF_RUN_ID"], r.env["S1_BRIEF_RUN_ATTEMPT"], r.env["S1_BRIEF_MAIN"], r.env["S1_BRIEF_EVENT"]),
                         ("555", "1", MAIN, "schedule"))
        line = json.loads(next(x for x in out["lines"] if x.startswith("S1_EXECUTOR_HEALTH ")).split(" ", 1)[1])
        self.assertEqual((line["brief_run"], line["brief_attempt"], line["state"]), ("555", "1", "OK"))   # what the next run's idempotency reads

    def test_a_bot_dispatched_brief_run_qualifies(self):
        # the metronome dispatches the brief with the workflow token: event workflow_dispatch, actor github-actions[bot]
        out, gh, _n, r = published(mutate=lambda w: w["run"].update(event="workflow_dispatch"))
        self.assertEqual(gh.runs[555]["triggering_actor"]["login"], "github-actions[bot]")
        self.assertEqual((out["result"], r.env["S1_BRIEF_EVENT"], gh.writes), ("WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)", "workflow_dispatch", []))

    def test_push_and_workflow_run_fallback_briefs_qualify_like_scheduled_ones(self):
        """F2 closed: the brief's push and workflow_run fallback builds publish the same brief from the same native reads
        (13 of the 62 briefs published 2026-11-25..26 were push builds). Both paths evaluate them."""
        for event in ("push", "workflow_run"):
            with self.subTest(event):
                out, gh, _n, r = published(mutate=lambda w, e=event: w["run"].update(event=e))
                self.assertEqual((out["result"], r.env["S1_BRIEF_EVENT"], gh.writes), ("WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)", event, []))
                out, gh, _n, _r = published(mutate=lambda w, e=event: w["run"].update(event=e),
                                            env={"GITHUB_EVENT_NAME": "workflow_run", "S1_BRIEF_RUN_ID": "555", "S1_BRIEF_RUN_ATTEMPT": "1",
                                                 "S1_BRIEF_MAIN": MAIN, "S1_BRIEF_EVENT": event})
                self.assertEqual((out["result"], gh.writes), ("WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)", []))
        # the native run's event must be the brief's own, and an event the brief workflow does not have never qualifies
        out, gh, _n, _r = published(run={"event": "push"})
        self.assertEqual((out["result"], gh.writes), ("NO_DECISION(brief_run=555:run_binding)", []))
        out, gh, _n, _r = published(mutate=lambda w: w["run"].update(event="pull_request"))
        self.assertEqual((out["result"], gh.writes), ("NO_DECISION(brief_run=555:run_binding)", []))
        self.assertEqual(reads(gh, "issues/1156/comments"), [])                          # nothing read past the resolution
        # a fallback run that built nothing: its workflow_run executor run names it, the published brief is another run's
        out, gh, _n, _r = published(env={"GITHUB_EVENT_NAME": "workflow_run", "S1_BRIEF_RUN_ID": "556", "S1_BRIEF_RUN_ATTEMPT": "1",
                                        "S1_BRIEF_MAIN": MAIN, "S1_BRIEF_EVENT": "push"})
        self.assertEqual((out["result"], gh.writes), ("NO_DECISION(published_run=555)", []))
        self.assertEqual(reads(gh, "actions/workflows/s1-executor.yml/runs"), [])          # no evaluation reads for it
        # a dispatched run that names a brief run itself (S1_BRIEF_* not empty) is not proven, whatever it names
        for key in E.BRIEF_ENV:
            out, gh, _n, _r = published(env={key: {"S1_BRIEF_RUN_ID": "555", "S1_BRIEF_RUN_ATTEMPT": "1", "S1_BRIEF_MAIN": MAIN,
                                                   "S1_BRIEF_EVENT": "schedule"}[key]})
            self.assertEqual((out["result"], gh.writes), ("BRIEF_UNVERIFIED(run_binding)", []), key)
        # an executor run on a schedule or a push is still refused before any read (no such trigger)
        for event in ("schedule", "push", "pull_request"):
            out, gh, _n, _r = published(env={"GITHUB_EVENT_NAME": event})
            self.assertEqual((out["result"], gh.writes), ("BRIEF_UNVERIFIED(run_binding)", []), event)
        # the workflow_run path: an event that is not the brief's own (or none) is refused
        for event in ("push", "workflow_run", "pull_request", ""):
            out, gh, _n, _r = published(env={"GITHUB_EVENT_NAME": "workflow_run", "S1_BRIEF_RUN_ID": "555", "S1_BRIEF_RUN_ATTEMPT": "1",
                                            "S1_BRIEF_MAIN": MAIN, "S1_BRIEF_EVENT": event})
            self.assertEqual((out["result"], gh.writes), ("BRIEF_UNVERIFIED(run_binding)", []), event)

    def test_a_non_success_foreign_or_edited_brief_run_gives_no_decision(self):
        cases = {
            "failed": ({"conclusion": "failure"}, "run_not_success"),
            "cancelled": ({"conclusion": "cancelled"}, "run_not_success"),
            "still running": ({"status": "in_progress", "conclusion": None}, "run_in_progress"),
            "another branch": ({"head_branch": "feature"}, "run_binding"),
            "a fork's head": ({"head_repository": {"full_name": "someone/fork"}}, "run_binding"),
            "another repository": ({"repository": {"full_name": "someone/fork"}}, "run_binding"),
            "another workflow": ({"path": ".github/workflows/lookalike.yml"}, "run_binding"),
            "another head": ({"head_sha": "c" * 40}, "run_binding"),
            "a re-run attempt": ({"run_attempt": 2}, "run_binding"),
            "another run id": ({"id": 556}, "run_binding"),
        }
        for name, (change, why) in cases.items():
            with self.subTest(name):
                out, gh, _n, _r = published(run=change)
                self.assertEqual((out["result"], gh.writes), (f"NO_DECISION(brief_run=555:{why})", []))
                self.assertEqual(reads(gh, "issues/1156/comments"), [])
        # the issue edited after the run ended
        r, gh, _n, body, _d = setup()
        gh.issue_updated = B.iso(B.stamp(gh.runs[555]["updated_at"]) + timedelta(minutes=5))
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(brief_run=555:edited_outside_run)")
        # the run cannot be read
        r, gh, _n, body, _d = setup()
        del gh.runs[555]
        gh.get = (lambda orig: lambda path, params=None: (_ for _ in ()).throw(urllib.error.HTTPError(path, 404, "Not Found", {}, None))
                  if path == "actions/runs/555" else orig(path, params))(gh.get)
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(brief_run=555:unreadable:HTTPError)")
        # this checkout is not the brief's main (the resolve step was skipped or main moved): not the code that built it
        r, gh, native, body, _d = setup()
        native.head_commit = lambda: "c" * 40
        out = r.execute_published()
        self.assertEqual((out["result"], gh.writes), ("NO_DECISION(brief_run=555:checkout)", []))
        native.head_commit = lambda: (_ for _ in ()).throw(RuntimeError("git"))
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(brief_run=555:checkout)")
        # execute() on a body without the issue it came from (the CLI's execute <file>): nothing proves the run
        r, gh, _n, body, _d = setup()
        self.assertEqual(r.execute(body)["result"], "NO_DECISION(brief_run=555:issue_unread)")
        # every one of these is a NO_DECISION health line, which the brief's watchdog skips (no decision published)
        self.assertTrue(B.no_decision_log(health("555", result="NO_DECISION(brief_run=555:run_not_success)")))

    def test_resolve_step_outputs_only_a_qualified_brief_main(self):
        r, gh, _n, _b, _d = setup()
        self.assertEqual(r.resolve_main(), MAIN)
        r, gh, _n, _b, _d = setup(run={"conclusion": "failure"})
        self.assertIsNone(r.resolve_main())
        r, gh, _n, _b, _d = setup(mutate=lambda w: w["run"].update(event="pull_request"))
        self.assertIsNone(r.resolve_main())
        r, gh, _n, _b, _d = setup(mutate=lambda w: w["run"].update(event="push"))
        self.assertEqual(r.resolve_main(), MAIN)                                         # F2 closed
        r, gh, _n, _b, _d = setup()
        gh.issue_body = "garbage"
        self.assertIsNone(r.resolve_main())
        self.assertEqual(gh.writes, [])
        # the CLI mode: only a dispatched run of this repository resolves; nothing else is read or written
        for env in ({"GITHUB_EVENT_NAME": "workflow_run"}, {"GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REPOSITORY": "someone/fork"}):
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(E.resolve_brief_main(env), 0)
            self.assertTrue(buf.getvalue().startswith("S1_EXECUTOR_RESOLVE none"), env)
        # through main(): exit 0 and never a health line, also when resolving raises (the execute job's log must hold
        # exactly the one health line of execute-published)
        for patch in ({}, {"resolve_brief_main": mock.Mock(side_effect=RuntimeError("boom"))}):
            buf = io.StringIO()
            with mock.patch.dict(E.os.environ, {"GITHUB_EVENT_NAME": "workflow_run"}), mock.patch.multiple(E, **patch) if patch else mock.patch.dict({}), redirect_stdout(buf):
                self.assertEqual(E.main(["s1_executor_v1.py", "resolve-brief-main"]), 0)
            self.assertIn("S1_EXECUTOR_RESOLVE none", buf.getvalue())
            self.assertNotIn("S1_EXECUTOR_HEALTH", buf.getvalue())


class OneEvaluationPerBriefRun(unittest.TestCase):
    def test_an_already_evaluated_brief_is_never_evaluated_again(self):
        for name, line in {"a dispatched evaluation": health("555"), "a workflow_run evaluation before this round (no attempt)": health("555", attempt=None),
                           "an evaluation that stopped": health("555", result="NOTHING_ACTIONABLE(skipped=lane:C7:switch_off)")}.items():
            with self.subTest(name):
                out, gh, _n, _r = published(exec_runs=[earlier(4321)], logs={4321: line})
                self.assertEqual((out["result"], gh.writes), ("NO_DECISION(already_evaluated=4321.1)", []))
                self.assertEqual(reads(gh, "issues"), [("GET", "issues")])              # execute_published's one read; no publication re-read, no ledger
                self.assertEqual(reads(gh, "issues/1156/comments"), [])
        # the same for a workflow_run executor run that comes after a dispatched evaluation of its brief
        out, gh, _n, _r = published(env={"GITHUB_EVENT_NAME": "workflow_run", "S1_BRIEF_RUN_ID": "555", "S1_BRIEF_RUN_ATTEMPT": "1",
                                        "S1_BRIEF_MAIN": MAIN, "S1_BRIEF_EVENT": "schedule"},
                                   exec_runs=[earlier(4321, event="workflow_dispatch")], logs={4321: health("555")})
        self.assertEqual((out["result"], gh.writes), ("NO_DECISION(already_evaluated=4321.1)", []))

    def test_earlier_runs_that_did_not_evaluate_this_brief_do_not_count(self):
        logs = {4321: health("554"),                                                          # another brief run
                4322: health("555", result="NO_DECISION(published_run=555)"),               # no decision for it
                4323: health("555", attempt="2"),                                            # another attempt of it
                4324: "no health line at all"}
        runs = [earlier(4321), earlier(4322), earlier(4323),
                earlier(4324, minutes_ago=200),                                              # ended before the brief was generated
                earlier(4325, conclusion="skipped"),                                         # a skipped workflow_run (push brief)
                TE.executor_run(9100, created=NOW, status="queued", event="workflow_dispatch")]   # newer, waiting for this run
        r, gh, _n, _b, _d = setup(exec_runs=runs, logs=logs)
        gh.exec_jobs[(9100, 1)] = {"status": "queued", "conclusion": None, "steps": []}       # waits for the group: read, not counted
        out = r.execute_published()
        self.assertEqual((out["result"], gh.writes), ("WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)", []))
        self.assertEqual(sorted(c[1] for c in gh.calls if c[1].startswith("actions/jobs/100")),
                         ["actions/jobs/1004321/logs", "actions/jobs/1004322/logs", "actions/jobs/1004323/logs"])
        self.assertIn(("PAGES", "actions/runs/9100/attempts/1/jobs"), gh.calls)

    def test_an_earlier_run_that_cannot_be_read_is_not_proven_unevaluated(self):
        cases = {
            "no health line": ({4321: "killed"}, [earlier(4321)], "evaluated_unproven:health=4321.1"),
            "two health lines": ({4321: health("1") + health("2")}, [earlier(4321)], "evaluated_unproven:health=4321.1"),
            "a crash line (no brief named)": ({4321: "S1_EXECUTOR_HEALTH " + json.dumps({"result": "EXECUTOR_CRASHED(KeyError)", "state": "DEGRADED"})},
                                               [earlier(4321)], "evaluated_unproven:brief_run=4321.1"),
            "a bad attempt number": ({}, [earlier(4321, run_attempt=0)], "evaluated_unproven:runs_unreadable"),
            "too many runs in the window": ({}, [earlier(4300 + i) for i in range(E.EVALUATION_READS + 1)], "evaluated_unproven:too_many_runs"),
            "a full page inside the window": ({}, [earlier(1000 + i) for i in range(E.EXECUTOR_RUNS_PAGE)], "evaluated_unproven:runs_page"),
        }
        for name, (logs, runs, why) in cases.items():
            with self.subTest(name):
                out, gh, _n, _r = published(exec_runs=runs, logs=logs)
                self.assertEqual((out["result"], gh.writes), (f"NO_DECISION({why})", []))
        r, gh, _n, _b, _d = setup()
        gh.exec_runs = "garbage"
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:runs_unreadable)")

    def test_fa_p1_01_reruns_and_order(self):
        """ChatGPT FA-P1-01 (#2371 at b09e0003): a rerun keeps its run id, and the concurrency group is not FIFO by id."""
        rerun = {"GITHUB_RUN_ATTEMPT": "2"}
        own_row = lambda **kw: TE.executor_run(OWN, created=NOW, status="in_progress", event="workflow_dispatch", run_attempt=2, **kw)
        # a rerun (attempt 2) sees attempt 1's evaluation of the same brief
        r, gh, _n, _b, _d = setup(env=rerun, logs={(OWN, 1): health("555")})
        gh.exec_runs = [own_row()]
        self.assertEqual((r.execute_published()["result"], gh.writes), (f"NO_DECISION(already_evaluated={OWN}.1)", []))
        # A missing own row is now explicit evidence of an incomplete census, regardless of prior attempts.
        r, gh, _n, _b, _d = setup(env=rerun, logs={(OWN, 1): health("555")})
        gh.exec_runs = []
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:own_run_census)")
        # a rerun whose attempt 1 decided nothing for this brief evaluates it (once)
        r, gh, _n, _b, _d = setup(env=rerun, logs={(OWN, 1): health("555", result="NO_DECISION(published_run=554)")})
        gh.exec_runs = [own_row()]
        self.assertTrue(r.execute_published()["result"].startswith("WOULD_MERGE("))
        # an unreadable earlier attempt fails closed: its jobs list, or its log
        r, gh, _n, _b, _d = setup(env=rerun)
        gh.exec_runs, gh.exec_jobs[(OWN, 1)] = [own_row()], None
        self.assertEqual(r.execute_published()["result"], f"NO_DECISION(evaluated_unproven:jobs={OWN}.1)")
        r, gh, _n, _b, _d = setup(env=rerun, logs={(OWN, 1): None})
        gh.exec_runs = [own_row()]
        self.assertEqual(r.execute_published()["result"], f"NO_DECISION(evaluated_unproven:health={OWN}.1)")
        # another run whose LATEST attempt is NO_DECISION, while its attempt 1 evaluated the brief
        out, gh, _n, _r = published(exec_runs=[earlier(4321, run_attempt=2)],
                                    logs={(4321, 1): health("555"), (4321, 2): health("555", result="NO_DECISION(already_evaluated=4321.1)")})
        self.assertEqual(out["result"], "NO_DECISION(already_evaluated=4321.1)")
        # out of order: a HIGHER run id ran first and evaluated the brief
        out, gh, _n, _r = published(exec_runs=[TE.executor_run(9500, created=NOW - timedelta(minutes=2), updated=NOW - timedelta(minutes=1))],
                                    logs={9500: health("555")})
        self.assertEqual((out["result"], gh.writes), ("NO_DECISION(already_evaluated=9500.1)", []))
        # another run in progress: a started execute job is not proven; one waiting for the group with no step is not counted
        for job, want in (({"status": "in_progress", "conclusion": None, "steps": [{"status": "in_progress"}]}, "NO_DECISION(evaluated_unproven:job_active=9100.1)"),
                          ({"status": "queued", "conclusion": None, "steps": []}, "WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)"),
                          ({"status": "waiting", "conclusion": None}, "WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)")):
            r, gh, _n, _b, _d = setup(exec_runs=[TE.executor_run(9100, created=NOW, status="in_progress", event="workflow_dispatch")])
            gh.exec_jobs[(9100, 1)] = job
            self.assertEqual((r.execute_published()["result"], gh.writes), (want, []), job["status"])
        # the read bound: more than EVALUATION_READS attempts in the window is not proven (1 list + 2 * 6 reads at most)
        out, gh, _n, _r = published(exec_runs=[earlier(4321, run_attempt=E.EVALUATION_READS + 1)])
        self.assertEqual(out["result"], "NO_DECISION(evaluated_unproven:too_many_runs)")
        out, gh, _n, _r = published(exec_runs=[earlier(4300 + i) for i in range(E.EVALUATION_READS)], logs={4300 + i: health("554") for i in range(6)})
        evaluation = [c for c in gh.calls if "s1-executor.yml/runs" in c[1] or "/attempts/" in c[1] or c[1].startswith("actions/jobs/100")]
        self.assertEqual((out["result"].startswith("WOULD_MERGE("), len(evaluation)), (True, 1 + 2 * E.EVALUATION_READS))

    def test_fa_p1_03_old_dispatch_and_missing_census_fail_closed(self):
        for trigger in ("workflow_dispatch", "workflow_run"):
            env = {"GITHUB_EVENT_NAME": trigger}
            if trigger == "workflow_run":
                env.update(S1_BRIEF_RUN_ID="555", S1_BRIEF_RUN_ATTEMPT="1", S1_BRIEF_MAIN=MAIN, S1_BRIEF_EVENT="schedule")
            for attempt in (1, 2):
                r, gh, _n, _b, _d = setup(env=dict(env, GITHUB_RUN_ATTEMPT=str(attempt)))
                gh.runs[OWN]["created_at"] = B.iso(NOW - timedelta(days=3))
                gh.exec_runs = [earlier(12000 + i, minutes_ago=60 + i) for i in range(E.EXECUTOR_RUNS_PAGE)]
                out = r.execute_published()
                self.assertEqual((out["result"], gh.writes), ("NO_DECISION(executor_run_outside_brief_window)", []))
                self.assertEqual(reads(gh, "actions/workflows/s1-executor.yml/runs"), [])
        for field, invalid in (("run_attempt", None), ("event", "push"), ("head_branch", "other"),
                               ("path", B.WORKFLOW_PATH), ("created_at", None)):
            r, gh, _n, _b, _d = setup()
            gh.runs[OWN][field] = invalid
            out = r.execute_published()
            self.assertTrue(out["result"].startswith("NO_DECISION(evaluated_unproven:own_run"), out)
            self.assertEqual(gh.writes, [])
        r, gh, _n, _b, _d = setup()
        gh.exec_total = 2  # a short page with a native count mismatch cannot prove absence
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:runs_page)")
        r, gh, _n, _b, _d = setup()
        gh.exec_runs.append(copy.deepcopy(gh.runs[OWN]))
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:runs_duplicate)")

    def test_fa_p1_03_job_and_health_identity_is_bound(self):
        for line in (health("555", run="99"), health("555").replace("__ATTEMPT__", "9"), health("555", v=2)):
            out, gh, _n, _r = published(exec_runs=[earlier(4321)], logs={4321: line})
            self.assertEqual((out["result"], gh.writes), ("NO_DECISION(evaluated_unproven:health_binding=4321.1)", []))
        for job in ({"run_id": 99}, {"run_attempt": 9}):
            r, gh, _n, _b, _d = setup(exec_runs=[earlier(4321)])
            gh.exec_jobs[(4321, 1)] = dict(status="completed", conclusion="success", **job)
            self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:job=4321.1)")
        # A completed successful run with no execute job is not proof that it never evaluated.
        r, gh, _n, _b, _d = setup(exec_runs=[earlier(4321)])
        self.assertEqual(r.execute_published()["result"], "NO_DECISION(evaluated_unproven:jobs=4321.1)")
        # A latest skipped attempt cannot erase an earlier evaluation.
        out, gh, _n, _r = published(exec_runs=[earlier(4321, run_attempt=2, conclusion="skipped")],
                                    logs={(4321, 1): health("555")})
        self.assertEqual((out["result"], gh.writes), ("NO_DECISION(already_evaluated=4321.1)", []))

    def test_a_run_created_just_after_the_clock_read_is_not_a_census_failure(self):
        """A newer executor run created between this run's clock read and its list read (or a small clock skew) waits
        for the group and is no reason to fail closed; a row far in the future still is."""
        for seconds, want in ((30, "WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)"), (B.RUN_POST_SLACK_SECONDS + 60, "NO_DECISION(evaluated_unproven:run_row_clock)")):
            r, gh, _n, _b, _d = setup(exec_runs=[TE.executor_run(9100, created=NOW + timedelta(minutes=2, seconds=seconds), status="queued", event="workflow_dispatch")])
            gh.exec_jobs[(9100, 1)] = {"status": "queued", "conclusion": None, "steps": []}
            self.assertEqual((r.execute_published()["result"], gh.writes), (want, []), seconds)

    def test_started_then_cancelled_attempt_is_not_assumed_unevaluated(self):
        # A cancelled attempt can have executed before cancellation. Its own log is required.
        for log, expected in ((None, "NO_DECISION(evaluated_unproven:health=4321.1)"),
                              (health("555"), "NO_DECISION(already_evaluated=4321.1)")):
            r, gh, _n, _b, _d = setup(exec_runs=[earlier(4321, conclusion="cancelled")], logs={4321: log})
            gh.exec_jobs[(4321, 1)] = {"status": "completed", "conclusion": "cancelled", "started_at": B.iso(NOW - timedelta(minutes=1)),
                                       "steps": [{"status": "completed", "conclusion": "success"}]}
            out = r.execute_published()
            self.assertEqual((out["result"], gh.writes), (expected, []))
            self.assertIn(("TEXT", "actions/jobs/1004321/logs"), gh.calls)

    def test_native_pull_request_brief_cannot_reach_evaluation(self):
        # previous_anchor and execute() both enforce the permitted event set, even when the brief
        # and its native run agree on the prohibited event.
        for event in ("workflow_dispatch", "workflow_run"):
            env = {"GITHUB_EVENT_NAME": event}
            if event == "workflow_run":
                env.update(S1_BRIEF_RUN_ID="555", S1_BRIEF_RUN_ATTEMPT="1", S1_BRIEF_MAIN=MAIN, S1_BRIEF_EVENT="pull_request")
            out, gh, _n, _r = published(env=env, mutate=lambda w: w["run"].update(event="pull_request"))
            self.assertIn(out["result"], ("NO_DECISION(brief_run=555:run_binding)", "BRIEF_UNVERIFIED(run_binding)"))
            self.assertEqual(gh.writes, [])
            self.assertEqual(reads(gh, "actions/workflows/s1-executor.yml/runs"), [])

    def test_two_runs_for_one_brief_evaluate_it_once(self):
        """End to end: the first run evaluates and prints its health line; the second reads that line from the first run's
        job log and stops."""
        out1, gh1, _n, _r = published()
        self.assertTrue(out1["result"].startswith("WOULD_MERGE("))
        log = "\n".join(out1["lines"]) + "\n"
        out2, gh2, _n, _r = published(env={"GITHUB_RUN_ID": "9500"}, exec_runs=[earlier(OWN, event="workflow_dispatch")], logs={OWN: log})
        self.assertEqual((out2["result"], gh2.writes), (f"NO_DECISION(already_evaluated={OWN}.1)", []))
        # and the other way round (FA-P1-01): the lower id runs second and still sees the higher id's evaluation
        out3, gh3, _n, _r = published(env={"GITHUB_RUN_ID": "8000"}, exec_runs=[earlier(OWN, event="workflow_dispatch")], logs={OWN: log})
        self.assertEqual((out3["result"], gh3.writes), (f"NO_DECISION(already_evaluated={OWN}.1)", []))


class ShadowNeverWrites(unittest.TestCase):
    def test_a_shadow_switch_never_writes_from_a_dispatched_run(self):
        beat = lambda w: w["issue_comments"].append(TE.TB.comment(71, "S1_HEARTBEAT_v1 main=a contract=44444444", TE.TB.BOT, 5))
        for name, kw in {"merge decided": {}, "merge decided, heartbeat due": {"mutate": None},
                         "nothing actionable": {"mutate": lambda w: (beat(w), w.update(pulls=[], pr={}))},
                         "a bot-dispatched brief": {"mutate": lambda w: w["run"].update(event="workflow_dispatch")},
                         "a push fallback brief": {"mutate": lambda w: w["run"].update(event="push")}}.items():
            with self.subTest(name):
                out, gh, _n, _r = published(mode="SHADOW", **kw)
                self.assertEqual((out["mode"], gh.writes, out["writes"]), ("SHADOW", [], []))
                self.assertFalse([c for c in gh.calls if c[0] in ("POST", "PUT", "PATCH", "DELETE")])
        # LIVE v1 enable: the switch on main reads LIVE with the narrow merge scope, the fallback route OFF; the write scopes
        # are the execute job's only (a SHADOW world above still writes nothing)
        switch = json.loads((ROOT / B.SWITCH).read_text(encoding="utf-8"))
        self.assertEqual((switch["executor"], switch["live_scope"], switch["fallback_route"]), ("LIVE", "MERGE_LOW_NORMAL_ONLY", "OFF"))
        self.assertEqual(EXEC_WORKFLOW["jobs"]["execute"]["permissions"], {"contents": "write", "actions": "read", "pull-requests": "write", "issues": "write"})
        self.assertEqual(EXEC_WORKFLOW["permissions"], {})

    def test_the_dispatch_trigger_takes_no_input_and_no_event_text_reaches_a_run_line(self):
        self.assertIsNone(EXEC_WORKFLOW[True]["workflow_dispatch"])                     # no inputs: nothing a dispatcher can pass
        self.assertNotIn("schedule", EXEC_WORKFLOW[True])
        text = (ROOT / B.EXECUTOR_WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("secrets.", text)
        self.assertEqual(EXEC_WORKFLOW["jobs"]["execute"]["concurrency"], {"group": "s1-executor", "cancel-in-progress": False})
        for step in EXEC_WORKFLOW["jobs"]["execute"]["steps"]:
            self.assertNotIn("${{", step.get("run", ""), step.get("name"))
        # the S1_BRIEF_* come only from github.event.workflow_run, which a dispatched run does not have (empty)
        env = EXEC_WORKFLOW["jobs"]["execute"]["steps"][-1]["env"]
        for key in E.BRIEF_ENV:
            self.assertTrue(env[key].startswith("${{ github.event.workflow_run."), key)


# ----------------------------------------------------------------------------------------------- the metronome
T0 = dt.datetime(2026, 11, 26, 14, 0, tzinfo=dt.timezone.utc)


def brun(created_min, event="workflow_dispatch", status="completed", conclusion="success", took=4, rid=1):
    created = T0 + dt.timedelta(minutes=created_min)
    return {"id": rid, "event": event, "status": status, "conclusion": conclusion if status == "completed" else None, "head_branch": "main",
            "created_at": M.iso(created), "updated_at": M.iso(created + dt.timedelta(minutes=took))}


def erun(created_min, event="workflow_dispatch", status="completed", rid=2):
    created = T0 + dt.timedelta(minutes=created_min)
    return {"id": rid, "event": event, "status": status, "conclusion": "success" if status == "completed" else None, "head_branch": "main",
            "created_at": M.iso(created), "updated_at": M.iso(created + dt.timedelta(minutes=1))}


class Reader:
    """The metronome's S1EXEC reads (jobs of a run or of one attempt, and job logs) over a fixed world. `pubs` maps a
    brief run id to WRITTEN, NONE (a fallback run that built nothing) or None (unreadable); `attempts` maps
    (executor run, attempt) to {"job": overrides, "log": text} or None (unreadable). An executor attempt that is not
    listed has an execute job whose health line evaluated brief run 1."""

    def __init__(self, pubs=None, attempts=None):
        self.pubs, self.attempts, self.logs, self.calls = dict(pubs or {}), dict(attempts or {}), {}, []

    def jobs(self, run_id, attempt):
        self.calls.append(("jobs", run_id, attempt))
        if attempt is None:                                                          # a brief run: its build and publish jobs
            state = self.pubs.get(run_id, "WRITTEN")
            if state is None:
                return None
            if state == "NONE":
                return [{"name": "build", "status": "completed", "conclusion": "success"}, {"name": "publish", "status": "completed", "conclusion": "skipped"}]
            jid = 500000 + run_id
            self.logs[jid] = f"S1_TICK_BRIEF_PUBLISHED issue=3 run={run_id} result=WRITTEN reason=created\n"
            return [{"name": "build", "status": "completed", "conclusion": "success"}, {"id": jid, "name": "publish", "status": "completed", "conclusion": "success"}]
        spec = self.attempts.get((run_id, attempt), {"log": hline(run_id, attempt, "1")})
        if spec is None:
            return None
        if spec == "nojob":
            return []
        jid = 700000 + 10 * run_id + attempt
        self.logs[jid] = spec.get("log")
        return [dict({"id": jid, "name": "execute", "status": "completed", "conclusion": "success", "run_id": run_id, "run_attempt": attempt,
                      "steps": [{"name": M.EXECUTE_STEP, "status": "completed", "conclusion": "success"}]}, **(spec.get("job") or {}))]

    def log(self, job_id):
        self.calls.append(("log", job_id))
        return self.logs.get(job_id)


def hline(run_id, attempt, brief_run, result="WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)", brief_attempt="1"):
    doc = {"v": 1, "run": str(run_id), "attempt": str(attempt), "brief_run": brief_run, "brief_attempt": brief_attempt, "result": result, "mode": "SHADOW"}
    return "2026-11-26T14:30:00Z S1_EXECUTOR_HEALTH " + json.dumps(doc, sort_keys=True) + "\n"


class MetronomeDispatchesTheExecutor(unittest.TestCase):
    def test_due_once_after_a_completed_successful_brief_run_of_any_event(self):
        now, R = T0 + dt.timedelta(minutes=31), Reader
        self.assertEqual(M.s1exec_due(now, [brun(21)], [], R()), (True, "DUE"))          # completed at :25, 6 minutes ago
        for event in ("schedule", "push", "workflow_run"):                               # F2 closed: a fallback build publishes too
            self.assertEqual(M.s1exec_due(now, [brun(21, event=event)], [], R()), (True, "DUE"), event)
        # liveness round (L1): an executor attempt that EVALUATED the publication stops it, whatever started it
        self.assertEqual(M.s1exec_due(now, [brun(21)], [erun(26)], R()), (False, "ALREADY_EVALUATED"))
        self.assertEqual(M.s1exec_due(now, [brun(21)], [erun(25, event="workflow_run")], R()), (False, "ALREADY_EVALUATED"))
        self.assertEqual(M.s1exec_due(now, [brun(21)], [erun(10)], R()), (True, "DUE"))  # an executor run for the previous brief
        self.assertEqual(M.s1exec_due(now, [brun(21)], [erun(30, status="in_progress")], R()), (False, "TARGET_ACTIVE"))
        for concl in ("skipped", "cancelled"):                                           # FA-P2-02: evaluated nothing, does not suppress
            self.assertEqual(M.s1exec_due(now, [brun(21)], [dict(erun(26), conclusion=concl)], R(attempts={(2, 1): "nojob"})), (True, "DUE"), concl)
        self.assertEqual(M.s1exec_due(now, [brun(29, status="in_progress")], [], R()), (False, "NO_BRIEF_RUN"))
        self.assertEqual(M.s1exec_due(now, [brun(21, conclusion="failure")], [], R()), (False, "NO_BRIEF_RUN"))
        self.assertEqual(M.s1exec_due(now, [brun(21, conclusion="cancelled")], [], R()), (False, "NO_BRIEF_RUN"))   # replaced by the concurrency group
        self.assertEqual(M.s1exec_due(now, [], [], R()), (False, "NO_BRIEF_RUN"))
        self.assertEqual(M.s1exec_due(T0 + dt.timedelta(minutes=46), [brun(21)], [], R()), (False, "BRIEF_TOO_OLD"))   # completed 21 min ago
        # the newest COMPLETED successful run decides: a run in progress or cancelled after it does not hide it
        self.assertEqual(M.s1exec_due(now, [brun(21), brun(28, event="push", status="in_progress", rid=3)], [], R()), (True, "DUE"))
        self.assertEqual(M.s1exec_due(now, [brun(21), brun(26, conclusion="cancelled", rid=3)], [], R()), (True, "DUE"))
        self.assertEqual(M.s1exec_due(now, [dict(brun(21), updated_at=None)], [], R()), (False, "RUN_ROW_UNREADABLE"))
        self.assertEqual(M.s1exec_due(now, [brun(21)], []), (False, "EVALUATION_UNREAD"))  # no reader: never a blind dispatch

    def test_the_tick_dispatches_the_executor_with_its_own_token_and_mechanism(self):
        now = T0 + dt.timedelta(minutes=31)

        class Fake:
            def __init__(self, exec_rows):
                self.exec_rows, self.sent, self.read, self.reader = exec_rows, [], [], Reader()

            def environment(self):
                return {"protection_rules": [{"type": "wait_timer", "wait_timer": 10}]}

            def mode(self):
                return {"mode": "ACTIVE_DATA"}

            def runs(self, wf):
                self.read.append(wf)
                return {M.S1BRIEF["workflow"]: [brun(21)], M.S1EXEC["workflow"]: self.exec_rows}.get(wf, [])

            def jobs(self, run_id, attempt):
                return self.reader.jobs(run_id, attempt)

            def log(self, job_id):
                return self.reader.log(job_id)

            def dispatch(self, wf, inputs):
                self.sent.append((wf, inputs))

        gh = Fake([])
        plan = M.run(gh, now, self_run_id=1)
        self.assertIn("s1-executor.yml", gh.read)
        self.assertEqual(plan["targets"]["S1EXEC"], "DUE")
        self.assertIn(("s1-executor.yml", {}), gh.sent)                                  # no inputs
        self.assertEqual(gh.sent[-1], (M.SELF_WORKFLOW, {}))                             # the loop still continues last
        gh = Fake([erun(26)])
        plan = M.run(gh, now, self_run_id=1)
        self.assertNotIn("s1-executor.yml", [w for w, _i in gh.sent])
        self.assertEqual(plan["targets"]["S1EXEC"], "ALREADY_EVALUATED")
        # SHADOW mode: logged only
        p = M.decide(now, mode="SHADOW", hourly_runs=[], monday_runs=[], self_runs=[], self_run_id=None,
                     environment={"protection_rules": [{"type": "wait_timer", "wait_timer": 10}]}, s1brief_runs=[brun(21)], s1exec_runs=[],
                     s1exec_reader=Reader())
        self.assertIn({"workflow": "s1-executor.yml", "inputs": {}}, p["would_dispatch"])
        self.assertNotIn({"workflow": "s1-executor.yml", "inputs": {}}, p["dispatch"])
        # an unreadable executor census fails every target closed (as every other read)
        class Broken(Fake):
            def runs(self, wf):
                if wf == M.S1EXEC["workflow"]:
                    raise ValueError("WORKFLOW_RUNS_INVALID_SHAPE")
                return super().runs(wf)
        gh = Broken([])
        plan = M.run(gh, now, self_run_id=1)
        self.assertEqual((plan["dispatch"], plan["read_status"]), ([], "DEGRADED"))
        self.assertIn("S1EXEC", plan["failed_reads"])
        # but an unreadable job or log is UNKNOWN for S1EXEC only: the other targets and the loop go on
        class NoJobs(Fake):
            def jobs(self, run_id, attempt):
                raise TimeoutError("READ_BUDGET_EXCEEDED")
        gh = NoJobs([])
        plan = M.run(gh, now, self_run_id=1)
        self.assertEqual((plan["targets"]["S1EXEC"], plan["read_status"], plan["next_tick"]), ("PUBLICATION_UNKNOWN", "PASS", True))
        self.assertNotIn("s1-executor.yml", [w for w, _i in gh.sent])

    def test_no_new_route_token_or_permission(self):
        self.assertIn("s1-executor.yml", M.DISPATCH_ALLOWLIST)
        self.assertIn("S1EXEC", M.DATA_TARGET_KEYS)
        gh, sent = M.Github("x"), []

        class Answer:                                                                    # no network: the allowed request is captured
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return b""

        with mock.patch.object(M.urllib.request, "urlopen", lambda req, timeout=None: sent.append((req.get_method(), req.full_url)) or Answer()):
            gh._req("POST", f"/repos/{M.REPO}/actions/workflows/s1-executor.yml/dispatches", {"ref": "main", "inputs": {}})
            gh._req("GET", f"/repos/{M.REPO}/actions/workflows/s1-executor.yml/runs?per_page=30&branch=main")
        self.assertEqual(sent, [("POST", f"https://api.github.com/repos/{M.REPO}/actions/workflows/s1-executor.yml/dispatches"),
                                ("GET", f"https://api.github.com/repos/{M.REPO}/actions/workflows/s1-executor.yml/runs?per_page=30&branch=main")])
        with self.assertRaises(ValueError):
            gh._req("POST", f"/repos/{M.REPO}/actions/workflows/s1-tick-brief.yml/runs")
        self.assertEqual(METRO_WORKFLOW["permissions"], {"actions": "write", "contents": "read", "deployments": "read"})
        self.assertEqual(METRO_WORKFLOW["jobs"]["tick"]["steps"][-1]["env"], {"GITHUB_TOKEN": "${{ github.token }}"})
        self.assertNotIn("secrets.", (ROOT / ".github/workflows/framework-metronome.yml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
