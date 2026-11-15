"""Tests for the framework metronome (pure decision + allowlists + loop safety)."""
import datetime as dt
import pathlib
import unittest

from scripts.orchestration import framework_metronome_v1 as M

UTC = dt.timezone.utc
ROOT = pathlib.Path(__file__).resolve().parents[2]
ENV_OK = {"protection_rules": [{"type": "wait_timer", "wait_timer": 10}]}


def run(created, status="completed", rid=1, conclusion="success"):
    return {"id": rid, "status": status, "conclusion": conclusion if status == "completed" else None,
            "created_at": created.strftime("%Y-%m-%dT%H:%M:%SZ")}


FINAL_OK_W47 = run(dt.datetime(2026, 11, 16, 1, 7, tzinfo=UTC))  # 02:07 CET Monday, succeeded


def plan(now, mode="ACTIVE", hourly=(), monday=(), self_runs=(), env=ENV_OK, self_id=99, recovery=(), close=None):
    if close is None:
        close = [FINAL_OK_W47]
    return M.decide(now, mode=mode, hourly_runs=list(hourly), monday_runs=list(monday),
                    self_runs=list(self_runs), self_run_id=self_id, environment=env,
                    recovery_runs=list(recovery), close_runs=list(close))


class MetronomeTest(unittest.TestCase):
    def test_hourly_due_from_minute_5_once_per_hour(self):
        now = dt.datetime(2026, 11, 15, 10, 7, tzinfo=UTC)
        p = plan(now, hourly=[run(now - dt.timedelta(minutes=70))])
        self.assertEqual([d["workflow"] for d in p["dispatch"]], ["hourly-sequence-capture.yml"])
        self.assertEqual(p["dispatch"][0]["inputs"], {"chain_entry_signal": "true"})
        self.assertEqual(plan(now.replace(minute=4))["targets"]["HOURLY"], "BEFORE_MINUTE_05")
        self.assertEqual(plan(now, hourly=[run(now.replace(minute=3))])["targets"]["HOURLY"], "ALREADY_RAN_THIS_HOUR")
        self.assertEqual(plan(now, hourly=[run(now.replace(minute=2))])["targets"]["HOURLY"], "DUE")  # :02 is last hour's straggler
        self.assertEqual(plan(now, hourly=[run(now - dt.timedelta(hours=2), "in_progress")])["targets"]["HOURLY"], "TARGET_ACTIVE")

    def test_monday_slot_in_copenhagen_time_both_dst_states(self):
        winter = dt.datetime(2026, 11, 16, 1, 41, tzinfo=UTC)  # 02:41 CET
        self.assertEqual(plan(winter)["targets"]["MONDAY"], "DUE")
        self.assertEqual(plan(winter - dt.timedelta(minutes=2))["targets"]["MONDAY"], "BEFORE_MONDAY_SLOT")
        summer = dt.datetime(2026, 6, 1, 0, 41, tzinfo=UTC)  # 02:41 CEST
        final_summer = run(dt.datetime(2026, 6, 1, 0, 10, tzinfo=UTC))  # 02:10 CEST
        self.assertEqual(plan(summer, close=[final_summer])["targets"]["MONDAY"], "DUE")
        self.assertEqual(plan(winter + dt.timedelta(days=1))["targets"]["MONDAY"], "NOT_MONDAY_CPH")
        ran = run(dt.datetime(2026, 11, 15, 23, 30, tzinfo=UTC))  # 00:30 CET Monday counts
        self.assertEqual(plan(winter, monday=[ran])["targets"]["MONDAY"], "ALREADY_RAN_THIS_MONDAY")
        last_week = run(dt.datetime(2026, 11, 9, 8, 37, tzinfo=UTC))
        self.assertEqual(plan(winter, monday=[last_week])["targets"]["MONDAY"], "DUE")

    def test_recovery_hourly_from_minute_35(self):
        now = dt.datetime(2026, 11, 15, 10, 36, tzinfo=UTC)
        self.assertEqual(plan(now)["targets"]["RECOVERY"], "DUE")
        self.assertEqual(plan(now.replace(minute=30))["targets"]["RECOVERY"], "BEFORE_MINUTE_35")
        self.assertEqual(plan(now, recovery=[run(now.replace(minute=33))])["targets"]["RECOVERY"], "ALREADY_RAN_THIS_HOUR")

    def test_sunday_preclose_window_before_midnight_only(self):
        sun = dt.datetime(2026, 11, 15, 22, 36, tzinfo=UTC)  # 23:36 CET Sunday
        p = plan(sun, close=[])
        self.assertEqual(p["targets"]["PRECLOSE"], "DUE")
        self.assertIn({"workflow": M.CLOSE_WORKFLOW, "inputs": {"mode": "preclose"}}, p["dispatch"])
        self.assertEqual(plan(sun.replace(minute=20), close=[])["targets"]["PRECLOSE"], "BEFORE_PRECLOSE_SLOT")
        self.assertEqual(plan(sun.replace(minute=59), close=[])["targets"]["PRECLOSE"], "TOO_CLOSE_TO_MIDNIGHT")
        self.assertEqual(plan(sun, close=[run(sun.replace(minute=35))])["targets"]["PRECLOSE"], "ALREADY_RAN_THIS_SLOT")
        self.assertEqual(plan(sun - dt.timedelta(days=1), close=[])["targets"]["PRECLOSE"], "NOT_SUNDAY_CPH")

    def test_final_close_then_master_monday_strictly_in_order(self):
        t0205 = dt.datetime(2026, 11, 16, 1, 6, tzinfo=UTC)  # 02:06 CET Monday
        p = plan(t0205, close=[])
        self.assertEqual(p["targets"]["FINAL"], "DUE")
        self.assertIn({"workflow": M.CLOSE_WORKFLOW, "inputs": {"mode": "final"}}, p["dispatch"])
        self.assertEqual(plan(t0205.replace(minute=0), close=[])["targets"]["FINAL"], "BEFORE_FINAL_SLOT")
        t0241 = t0205.replace(minute=41)
        # Master Monday waits until FINAL has SUCCEEDED this Monday.
        self.assertEqual(plan(t0241, close=[])["targets"]["MONDAY"], "WAITING_FOR_SUNDAY_FINAL")
        running = run(t0205, "in_progress")
        self.assertEqual(plan(t0241, close=[running])["targets"]["MONDAY"], "WAITING_FOR_SUNDAY_FINAL")
        self.assertEqual(plan(t0241, close=[running])["targets"]["FINAL"], "TARGET_ACTIVE")
        self.assertEqual(plan(t0241)["targets"]["FINAL"], "FINAL_SUCCEEDED_THIS_MONDAY")
        self.assertEqual(plan(t0241)["targets"]["MONDAY"], "DUE")

    def test_late_preclose_cron_on_monday_never_counts_as_final(self):
        """GitHub fires the Sunday 23:35 preclose cron ~7 h late; on Monday it fails (rollover unbound)."""
        t = dt.datetime(2026, 11, 16, 6, 0, tzinfo=UTC)  # 07:00 CET Monday
        late_preclose_failed = run(dt.datetime(2026, 11, 16, 5, 50, tzinfo=UTC), conclusion="failure")
        p = plan(t, close=[late_preclose_failed])
        self.assertEqual(p["targets"]["FINAL"], "DUE")
        self.assertEqual(p["targets"]["MONDAY"], "WAITING_FOR_SUNDAY_FINAL")
        sunday_preclose_ok = run(dt.datetime(2026, 11, 15, 22, 40, tzinfo=UTC))  # Sunday's own preclose
        self.assertEqual(plan(t, close=[sunday_preclose_ok])["targets"]["MONDAY"], "WAITING_FOR_SUNDAY_FINAL")
        # A success between Monday 00:00 and 02:00 CET is not the final close either.
        early_ok = run(dt.datetime(2026, 11, 16, 0, 30, tzinfo=UTC))  # 01:30 CET Monday
        self.assertEqual(plan(t, close=[early_ok])["targets"]["FINAL"], "DUE")

    def test_shadow_mode_dispatches_nothing_but_the_loop(self):
        now = dt.datetime(2026, 11, 16, 1, 45, tzinfo=UTC)
        p = plan(now, mode="SHADOW")
        self.assertEqual(p["dispatch"], [])
        self.assertEqual([d["workflow"] for d in p["would_dispatch"]],
                         ["hourly-sequence-capture.yml", "native-market-recovery.yml", "weekly-api-calibration-shadow.yml"])
        self.assertTrue(p["next_tick"])
        self.assertEqual(M.read_mode({"mode": "ACTIVE"}), "ACTIVE")
        for doc in (None, {}, {"mode": "active"}, {"mode": "ON"}, "ACTIVE"):
            self.assertEqual(M.read_mode(doc), "SHADOW")

    def test_never_spins_without_a_valid_wait_timer(self):
        now = dt.datetime(2026, 11, 15, 10, 7, tzinfo=UTC)
        for env in (None, {}, {"protection_rules": []}, {"protection_rules": [{"type": "wait_timer", "wait_timer": 0}]},
                    {"protection_rules": [{"type": "wait_timer", "wait_timer": 4}]},
                    {"protection_rules": [{"type": "wait_timer", "wait_timer": 31}]},
                    {"protection_rules": [{"type": "wait_timer", "wait_timer": True}]}):
            p = plan(now, env=env)
            self.assertFalse(p["next_tick"])
            self.assertEqual(p["next_tick_reason"], "WAIT_TIMER_MISSING_OR_OUT_OF_RANGE")

    def test_exactly_one_loop(self):
        now = dt.datetime(2026, 11, 15, 10, 7, tzinfo=UTC)
        mine = run(now, "in_progress", rid=99)
        self.assertTrue(plan(now, self_runs=[mine])["next_tick"])
        other = run(now, "queued", rid=100)
        p = plan(now, self_runs=[mine, other])
        self.assertFalse(p["next_tick"])
        self.assertEqual(p["next_tick_reason"], "ANOTHER_METRONOME_RUN_ACTIVE")
        self.assertTrue(plan(now, self_runs=[mine, run(now, "completed", rid=100)])["next_tick"])

    def test_client_route_and_dispatch_allowlists(self):
        gh = M.Github("t")
        for method, route in (("POST", "/repos/Donh91/Investering-Framework-Vault/actions/workflows/x.yml/dispatches"),
                              ("POST", f"/repos/{M.REPO}/actions/workflows/daily-compass.yml/dispatches"),
                              ("DELETE", f"/repos/{M.REPO}/actions/runs/1"),
                              ("POST", f"/repos/{M.REPO}/issues/1156/comments"),
                              ("GET", f"/repos/{M.REPO}/contents/README.md?ref=main")):
            with self.assertRaises(ValueError):
                gh._req(method, route)

    def test_run_dispatches_targets_then_next_tick_and_reports_errors(self):
        class Fake:
            def __init__(self, fail=()):
                self.calls, self.fail = [], set(fail)

            def mode(self):
                return {"mode": "ACTIVE"}

            def runs(self, wf):
                return [FINAL_OK_W47] if wf == M.CLOSE_WORKFLOW else []

            def environment(self):
                return ENV_OK

            def dispatch(self, wf, inputs):
                if wf in self.fail:
                    raise RuntimeError("boom")
                self.calls.append(wf)

        now = dt.datetime(2026, 11, 16, 1, 45, tzinfo=UTC)
        gh = Fake()
        p = M.run(gh, now, 99)
        self.assertEqual(gh.calls, ["hourly-sequence-capture.yml", "native-market-recovery.yml",
                                    "weekly-api-calibration-shadow.yml", "framework-metronome.yml"])
        self.assertEqual(p["errors"], [])
        gh = Fake(fail={"hourly-sequence-capture.yml"})
        p = M.run(gh, now, 99)
        self.assertEqual(p["errors"], ["hourly-sequence-capture.yml:RuntimeError"])
        self.assertIn("framework-metronome.yml", gh.calls)  # one failed target never kills the loop
        gh = Fake(fail={"framework-metronome.yml"})
        p = M.run(gh, now, 99)
        self.assertFalse(p["next_tick"])  # a failed self-dispatch is reported, never hidden
        self.assertEqual(p["next_tick_reason"], "SELF_DISPATCH_FAILED")
        self.assertEqual(p["errors"], ["framework-metronome.yml:RuntimeError"])

    def test_only_main_non_pr_runs_serve_or_occupy_a_slot(self):  # Codex P2 on #2146
        now = dt.datetime(2026, 11, 16, 1, 45, tzinfo=UTC)
        recent = now - dt.timedelta(minutes=5)
        pr_run = dict(run(recent, status="in_progress", rid=7), head_branch="fix-x", event="pull_request")
        branch_run = dict(run(recent, rid=8), head_branch="fix-x", event="workflow_dispatch")
        main_run = dict(run(recent, rid=9), head_branch="main", event="schedule")
        self.assertEqual(M.production_runs([pr_run, branch_run, main_run, "junk"]), [main_run])

        class Fake:
            calls: list = []

            def mode(self):
                return {"mode": "ACTIVE"}

            def runs(self, wf):
                if wf == M.SELF_WORKFLOW:
                    return []  # the loop's own runs stay unfiltered: exactly one loop, conservatively
                return [FINAL_OK_W47] if wf == M.CLOSE_WORKFLOW else [pr_run, branch_run]

            def environment(self):
                return ENV_OK

            def dispatch(self, wf, inputs):
                self.calls.append(wf)

        gh = Fake()
        M.run(gh, now, 99)
        self.assertEqual(gh.calls, ["hourly-sequence-capture.yml", "native-market-recovery.yml",
                                    "weekly-api-calibration-shadow.yml", "framework-metronome.yml"])
        routes = []
        client = M.Github("t")
        client._req = lambda method, route, payload=None: routes.append(route) or {"workflow_runs": []}
        client.runs(M.RECOVERY["workflow"])
        self.assertTrue(routes[0].endswith("/runs?per_page=30&branch=main"))

    def test_transient_target_read_fails_closed_but_preserves_single_loop(self):
        class Fake:
            calls = []

            def mode(self):
                return {"mode": "ACTIVE"}

            def runs(self, wf):
                if wf == M.HOURLY["workflow"]:
                    raise TimeoutError("temporary failure")
                return [FINAL_OK_W47] if wf == M.CLOSE_WORKFLOW else []

            def environment(self):
                return ENV_OK

            def dispatch(self, wf, inputs):
                self.calls.append(wf)

        fake = Fake()
        result = M.run(fake, dt.datetime(2026, 11, 16, 1, 45, tzinfo=UTC), 99)
        self.assertEqual(fake.calls, [M.SELF_WORKFLOW])
        self.assertEqual(result["dispatch"], [])
        self.assertEqual(result["read_status"], "DEGRADED")
        self.assertIn("HOURLY", result["failed_reads"])
        self.assertTrue(result["next_tick"])
        self.assertIn("READ_HOURLY:TimeoutError", result["errors"])

    def test_missing_self_census_or_wait_timer_never_restarts_unverified(self):
        class Fake:
            calls = []

            def mode(self):
                return {"mode": "ACTIVE"}

            def runs(self, wf):
                if wf == M.SELF_WORKFLOW:
                    raise ConnectionError("self census unavailable")
                return []

            def environment(self):
                return ENV_OK

            def dispatch(self, wf, inputs):
                self.calls.append(wf)

        fake = Fake()
        result = M.run(fake, dt.datetime(2026, 11, 15, 10, 10, tzinfo=UTC), 99)
        self.assertEqual(fake.calls, [])
        self.assertFalse(result["next_tick"])
        self.assertEqual(result["next_tick_reason"], "LOOP_SAFETY_READ_UNVERIFIED")

        class BadEnv(Fake):
            def runs(self, wf):
                return []

            def environment(self):
                raise TimeoutError("wait timer unavailable")

        fake2 = BadEnv()
        result2 = M.run(fake2, dt.datetime(2026, 11, 15, 10, 10, tzinfo=UTC), 99)
        self.assertFalse(result2["next_tick"])
        self.assertEqual(fake2.calls, [])

    def test_unreadable_active_mode_degrades_to_shadow_and_next_tick(self):
        class Fake:
            calls = []

            def mode(self):
                raise TimeoutError("mode read unavailable")

            def runs(self, wf):
                return []

            def environment(self):
                return ENV_OK

            def dispatch(self, wf, inputs):
                self.calls.append(wf)

        fake = Fake()
        result = M.run(fake, dt.datetime(2026, 11, 15, 10, 10, tzinfo=UTC), 99)
        self.assertEqual(result["mode"], "SHADOW")
        self.assertEqual(result["dispatch"], [])
        self.assertEqual(fake.calls, [M.SELF_WORKFLOW])

    def test_retry_get_only_never_post(self):
        from unittest import mock
        import io
        import urllib.error

        route = f"/repos/{M.REPO}/actions/workflows/{M.HOURLY['workflow']}/runs?per_page=30&branch=main"
        class Resp:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'{"workflow_runs": []}'

        gh = M.Github("placeholder")
        calls = []
        def fake_urlopen(req, timeout):
            calls.append(req.get_method())
            if len(calls) < 3:
                raise urllib.error.HTTPError(req.full_url, 503, "retry", {}, io.BytesIO())
            return Resp()
        with mock.patch.object(M.urllib.request, "urlopen", side_effect=fake_urlopen), mock.patch.object(M.time, "sleep") as sleep:
            self.assertEqual(gh._req("GET", route), {"workflow_runs": []})
        self.assertEqual(calls, ["GET", "GET", "GET"])
        self.assertEqual(sleep.call_count, 2)

        calls.clear()
        def fail_post(req, timeout):
            calls.append(req.get_method())
            raise urllib.error.HTTPError(req.full_url, 503, "ambiguous", {}, io.BytesIO())
        with mock.patch.object(M.urllib.request, "urlopen", side_effect=fail_post), mock.patch.object(M.time, "sleep") as sleep:
            with self.assertRaises(urllib.error.HTTPError):
                gh._req("POST", f"/repos/{M.REPO}/actions/workflows/{M.SELF_WORKFLOW}/dispatches", {"ref": "main", "inputs": {}})
        self.assertEqual(calls, ["POST"])
        sleep.assert_not_called()

    def test_malformed_200_run_census_fails_closed(self):
        gh = M.Github("t")
        for invalid in (
            None, [], {"total_count": 1}, {"workflow_runs": None},
            {"workflow_runs": {}, "total_count": 0},
            {"workflow_runs": [1]}, {"workflow_runs": [], "total_count": 1},
            {"workflow_runs": [{"id": 1}], "total_count": 0},
        ):
            with self.subTest(invalid=invalid):
                gh._req = lambda method, route, payload=None, body=invalid: body
                with self.assertRaises(ValueError):
                    gh.runs(M.HOURLY["workflow"])
        gh._req = lambda method, route, payload=None: {"workflow_runs": [], "total_count": 0}
        self.assertEqual(gh.runs(M.SELF_WORKFLOW), [])

    def test_post_ambiguous_network_errors_are_never_retried(self):
        import urllib.error
        from unittest import mock

        gh = M.Github("t")
        route = f"/repos/{M.REPO}/actions/workflows/{M.SELF_WORKFLOW}/dispatches"
        for err in (urllib.error.URLError("unknown POST result"), TimeoutError("ambiguous")):
            with self.subTest(error=type(err).__name__):
                with mock.patch.object(M.urllib.request, "urlopen", side_effect=err) as request:
                    with mock.patch.object(M.time, "sleep") as sleep:
                        with self.assertRaises(type(err)):
                            gh._req("POST", route, {"ref": "main", "inputs": {}})
                    self.assertEqual(request.call_count, 1)
                    sleep.assert_not_called()

    def test_native_main_shadow_end_to_end_and_ci_runner_contract(self):
        import io
        from contextlib import redirect_stdout
        from unittest import mock

        class Fake:
            calls = []

            def mode(self):
                return {"mode": "SHADOW"}

            def runs(self, wf):
                return []

            def environment(self):
                return ENV_OK

            def dispatch(self, wf, inputs):
                if wf != M.SELF_WORKFLOW:
                    raise AssertionError("SHADOW_MUST_NOT_DISPATCH_TARGET")
                self.calls.append(wf)

        fake = Fake()
        output = io.StringIO()
        # Pin the Sunday -> Monday timeline, rather than accidentally
        # passing a 'would_dispatch' mutant based on the runner's wall clock.
        fixed = dt.datetime(2026, 11, 16, 1, 45, tzinfo=UTC)
        class FrozenDatetime(dt.datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed.astimezone(tz) if tz is not None else fixed
        with mock.patch.object(M.dt, "datetime", FrozenDatetime):
            with mock.patch.object(M, "Github", return_value=fake):
                with mock.patch.dict(M.os.environ, {"GITHUB_TOKEN": "synthetic-token"}):
                    with redirect_stdout(output):
                        code = M.main([])
        self.assertEqual(code, 0, output.getvalue())
        self.assertEqual(fake.calls, [M.SELF_WORKFLOW])
        self.assertIn('"mode": "SHADOW"', output.getvalue())
        plan = M.json.loads(output.getvalue().split(" ", 1)[1])
        self.assertEqual(plan["dispatch"], [])
        self.assertEqual([item["workflow"] for item in plan["would_dispatch"]],
                         [M.HOURLY["workflow"], M.RECOVERY["workflow"], M.CLOSE_WORKFLOW])
        self.assertNotIn("synthetic-token", output.getvalue())

        wf = (ROOT / ".github/workflows/master-monday-preflight-gate.yml").read_text(encoding="utf-8")
        self.assertIn("python -m unittest -v tests.orchestration.test_framework_metronome_v1", wf)
        self.assertNotIn("python -m unittest --collect-only -v tests.orchestration.test_framework_metronome_v1", wf)

    def test_workflow_is_bounded_and_minimal(self):
        wf = (ROOT / ".github/workflows/framework-metronome.yml").read_text(encoding="utf-8")
        self.assertIn("environment: framework-metronome", wf)
        self.assertIn("group: framework-metronome", wf)
        self.assertIn("cancel-in-progress: false", wf)
        self.assertIn("actions: write", wf)
        self.assertNotIn("contents: write", wf)
        self.assertNotIn("secrets.", wf)
        self.assertNotIn("framework-market-owner-writer", wf)  # never holds the data writer lock
        self.assertIn("timeout-minutes: 5", wf)


if __name__ == "__main__":
    unittest.main()
