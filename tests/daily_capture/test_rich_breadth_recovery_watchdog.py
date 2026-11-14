import datetime as dt
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
