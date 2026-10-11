from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.daily_capture.build_weekly_cfgi_summary import cfgi_from_capture, target_week_window


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

    def test_actual_workflow_passes_resolved_preclose_or_final_mode(self):
        workflow = Path(".github/workflows/sunday-market-close-and-cfgi.yml").read_text()
        self.assertIn('--mode "${{ steps.mode.outputs.mode }}"', workflow)
        self.assertIn('cron: \'5 2 * * 1\'', workflow)
        self.assertIn("build_weekly_cfgi_summary.py", workflow)


if __name__ == "__main__":
    unittest.main()
