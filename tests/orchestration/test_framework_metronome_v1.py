"""Tests for the framework metronome (pure decision + allowlists + loop safety)."""
import datetime as dt
import pathlib
import unittest

from scripts.orchestration import framework_metronome_v1 as M

UTC = dt.timezone.utc
ROOT = pathlib.Path(__file__).resolve().parents[2]
ENV_OK = {"protection_rules": [{"type": "wait_timer", "wait_timer": 10}]}


def run(created, status="completed", rid=1):
    return {"id": rid, "status": status, "created_at": created.strftime("%Y-%m-%dT%H:%M:%SZ")}


def plan(now, mode="ACTIVE", hourly=(), monday=(), self_runs=(), env=ENV_OK, self_id=99):
    return M.decide(now, mode=mode, hourly_runs=list(hourly), monday_runs=list(monday),
                    self_runs=list(self_runs), self_run_id=self_id, environment=env)


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
        self.assertEqual(plan(summer)["targets"]["MONDAY"], "DUE")
        self.assertEqual(plan(winter + dt.timedelta(days=1))["targets"]["MONDAY"], "NOT_MONDAY_CPH")
        ran = run(dt.datetime(2026, 11, 15, 23, 30, tzinfo=UTC))  # 00:30 CET Monday counts
        self.assertEqual(plan(winter, monday=[ran])["targets"]["MONDAY"], "ALREADY_RAN_THIS_MONDAY")
        last_week = run(dt.datetime(2026, 11, 9, 8, 37, tzinfo=UTC))
        self.assertEqual(plan(winter, monday=[last_week])["targets"]["MONDAY"], "DUE")

    def test_shadow_mode_dispatches_nothing_but_the_loop(self):
        now = dt.datetime(2026, 11, 16, 1, 45, tzinfo=UTC)
        p = plan(now, mode="SHADOW")
        self.assertEqual(p["dispatch"], [])
        self.assertEqual(len(p["would_dispatch"]), 2)
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
                return []

            def environment(self):
                return ENV_OK

            def dispatch(self, wf, inputs):
                if wf in self.fail:
                    raise RuntimeError("boom")
                self.calls.append(wf)

        now = dt.datetime(2026, 11, 16, 1, 45, tzinfo=UTC)
        gh = Fake()
        p = M.run(gh, now, 99)
        self.assertEqual(gh.calls, ["hourly-sequence-capture.yml", "weekly-api-calibration-shadow.yml", "framework-metronome.yml"])
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
