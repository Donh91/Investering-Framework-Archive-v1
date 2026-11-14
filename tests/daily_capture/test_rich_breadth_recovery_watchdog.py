import datetime as dt
import importlib.util
import json
from unittest.mock import patch
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("watch", ROOT / "scripts/daily_capture/rich_breadth_recovery_watchdog.py")
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


class BreadthWatchdogTest(unittest.TestCase):
    def test_decisions(self):
        now = dt.datetime(2026, 11, 14, 13, tzinfo=dt.timezone.utc)
        self.assertEqual(watch.decision("2026-11-14T08:00:00Z", now, []), "FRESH")
        self.assertEqual(watch.decision("2026-11-14T07:59:59Z", now, []), "DISPATCH")
        for active in ("queued", "pending", "in_progress", "waiting", "requested"):
            self.assertEqual(watch.decision("2026-11-14T07:00:00Z", now, [active]), "ACTIVE")
        for invalid in (None, "bad", "2026-11-14T14:00:00Z", "2026-11-14T07:00:00"):
            with self.assertRaises(ValueError):
                watch.decision(invalid, now, [])

    def test_workflow_binds_nonblocking_bounded_step_and_tests(self):
        wf = (ROOT / ".github/workflows/hourly-sequence-capture.yml").read_text()
        self.assertIn("actions: write", wf)
        self.assertIn("timeout-minutes: 3", wf)
        self.assertIn("continue-on-error: true", wf)
        self.assertIn("scripts/daily_capture/rich_breadth_recovery_watchdog.py", wf)
        gate = (ROOT / ".github/workflows/cn-site-v2-gate.yml").read_text()
        self.assertIn("test_rich_breadth_recovery_watchdog.py", gate)

    def test_actual_daily_owner_timestamp_and_fail_closed_shapes(self):
        now = dt.datetime(2026, 11, 14, 13, tzinfo=dt.timezone.utc)
        stamp = "2026-11-14T07:00:00Z"
        for payload in (
            {"retrieval_timestamp": stamp},
            {"observation": {"retrieval_timestamp_utc": stamp}},
            {"retrieved_at_utc": stamp},
        ):
            with self.subTest(payload=payload):
                self.assertEqual(watch.extract_timestamp(payload), stamp)
                self.assertEqual(watch.decision(watch.extract_timestamp(payload), now, []), "DISPATCH")
        for payload in ([], {"observation": "untrusted"}, {"retrieved_at_utc": 10}):
            with self.subTest(invalid_payload=payload):
                with self.assertRaises(ValueError):
                    watch.decision(watch.extract_timestamp(payload), now, [])

    def test_main_fresh_daily_owner_makes_no_gh_calls(self):
        stamp = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=15)).isoformat()
        calls = []

        def fake_run(args):
            calls.append(args)
            if args[:2] == ["git", "fetch"]:
                return ""
            if args[:2] == ["git", "show"]:
                return json.dumps({"retrieval_timestamp": stamp})
            raise AssertionError(f"unexpected subprocess: {args}")

        with patch.object(watch, "run", side_effect=fake_run):
            watch.main()
        self.assertEqual([args[:2] for args in calls], [["git", "fetch"], ["git", "show"]])

    def test_main_stale_daily_owner_dispatches_once_without_inputs(self):
        stamp = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=6)).isoformat()
        calls = []

        def fake_run(args):
            calls.append(args)
            if args[:2] == ["git", "fetch"]:
                return ""
            if args[:2] == ["git", "show"]:
                return json.dumps({"retrieval_timestamp": stamp})
            if args[:3] == ["gh", "run", "list"]:
                return "[]"
            if args[:3] == ["gh", "workflow", "run"]:
                return ""
            raise AssertionError(f"unexpected subprocess: {args}")

        with patch.object(watch, "run", side_effect=fake_run):
            watch.main()
        dispatches = [args for args in calls if args[:3] == ["gh", "workflow", "run"]]
        self.assertEqual(dispatches, [["gh", "workflow", "run", "rich-breadth-checkpoint.yml", "--ref", "main"]])


if __name__ == "__main__":
    unittest.main()
