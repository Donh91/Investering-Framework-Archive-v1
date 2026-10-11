from __future__ import annotations

import unittest
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from scripts.daily_capture.build_weekly_cfgi_summary import cfgi_from_capture, resolve_close_mode, target_week_window


class WeeklyCfgiFinalWeekBindingTests(unittest.TestCase):
    def test_sunday_preclose_uses_current_completed_to_date_iso_week(self):
        monday, end = target_week_window(datetime(2026, 10, 11, 21, 35, tzinfo=timezone.utc), "preclose")
        self.assertEqual(monday.isoformat(), "2026-10-05T00:00:00+00:00")
        self.assertEqual(end.isoformat(), "2026-10-12T00:00:00+00:00")

    def test_monday_final_targets_preceding_completed_week_not_empty_new_week(self):
        monday, end = target_week_window(datetime(2026, 10, 12, 0, 5, tzinfo=timezone.utc), "final")
        self.assertEqual(monday.isoformat(), "2026-10-05T00:00:00+00:00")
        self.assertEqual(end.isoformat(), "2026-10-12T00:00:00+00:00")
        self.assertTrue(monday <= datetime(2026, 10, 11, 23, 59, tzinfo=timezone.utc) < end)
        self.assertFalse(monday <= datetime(2026, 10, 12, 0, 1, tzinfo=timezone.utc) < end)

    def test_cross_year_iso_week(self):
        monday, end = target_week_window(datetime(2027, 1, 4, 0, 5, tzinfo=timezone.utc), "final")
        self.assertEqual((monday.isocalendar().year, monday.isocalendar().week), (2026, 53))
        self.assertEqual(end.isoformat(), "2027-01-04T00:00:00+00:00")

    def test_bad_mode_fails_closed(self):
        with self.assertRaises(ValueError):
            target_week_window(datetime.now(timezone.utc), "typo")

    def test_current_capture_nested_cfgi_is_consumed_without_new_calls(self):
        packet = {"owners": [], "market_metrics": {"sentiment": {"cfgi": {
            "symbols": {"BTC": {"score": 43, "owner_status": "PASS"},
                        "ETH": {"score": 40, "owner_status": "PASS"},
                        "MARKET": {"score": 41, "owner_status": "PASS"}}
        }}}}
        rows, billing = cfgi_from_capture(packet)
        self.assertEqual(len(rows), 3)
        self.assertEqual({row["symbol"] for row in rows}, {"BTC", "ETH", "MARKET"})
        self.assertEqual(billing, {})

    def test_existing_workflow_untouched_and_resolves_preclose_final(self):
        workflow = Path(".github/workflows/sunday-market-close-and-cfgi.yml").read_text()
        self.assertIn("cron: '35 23 * * 0'", workflow)
        self.assertIn("cron: '5 2 * * 1'", workflow)
        self.assertIn("python scripts/daily_capture/build_weekly_cfgi_summary.py", workflow)
        self.assertNotIn('--mode "${{ steps.mode.outputs.mode }}"', workflow.partition("Build zero-cost weekly CFGI summary from daily owner captures")[2].partition("Build preliminary weekly forensics")[0])

    def test_auto_mode_uses_schedule_payload_not_execution_date(self):
        for trigger, expected in (("35 23 * * 0", "preclose"), ("5 2 * * 1", "final")):
            with self.subTest(trigger=trigger), tempfile.TemporaryDirectory() as d:
                path = Path(d) / "event.json"
                path.write_text(json.dumps({"schedule": trigger}))
                self.assertEqual(resolve_close_mode("auto", event_name="schedule", event_path=str(path)), expected)

    def test_auto_mode_supports_dispatch_payload(self):
        for mode in ("preclose", "final"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                path = Path(d) / "event.json"
                path.write_text(json.dumps({"inputs": {"mode": mode}}))
                self.assertEqual(resolve_close_mode("auto", event_name="workflow_dispatch", event_path=str(path)), mode)

    def test_unknown_triggers_fail_closed_without_wrong_week_write(self):
        with self.assertRaises(ValueError):
            resolve_close_mode("auto", event_name="", event_path="")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "event.json"
            path.write_text(json.dumps({"schedule": "10 10 * * 3"}))
            with self.assertRaises(ValueError):
                resolve_close_mode("auto", event_name="schedule", event_path=str(path))
            path.write_text(json.dumps({"inputs": {"mode": "unknown"}}))
            with self.assertRaises(ValueError):
                resolve_close_mode("auto", event_name="workflow_dispatch", event_path=str(path))
        self.assertEqual(resolve_close_mode("final", event_name="", event_path=""), "final")


if __name__ == "__main__":
    unittest.main()
