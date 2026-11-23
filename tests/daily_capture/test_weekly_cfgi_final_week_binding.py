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

    def test_sunday_workflow_passes_one_source_bound_mode_to_both_collectors(self):
        workflow = Path(".github/workflows/sunday-market-close-and-cfgi.yml").read_text()
        self.assertIn("cron: '35 23 * * 0'", workflow)
        self.assertIn("cron: '5 2 * * 1'", workflow)
        for marker in ("Build verified weekly price ranges", "Build zero-cost weekly CFGI summary"):
            step = workflow.split("- name: " + marker, 1)[1].split("- name:", 1)[0]
            self.assertIn('--mode "${{ steps.mode.outputs.mode }}"', step)
        self.assertNotIn("continue-on-error: true", workflow.split("- name: Build verified weekly price ranges")[1].split("- name:",1)[0])

    def test_source_and_cfgi_share_exact_event_dispatch_matrix(self):
        from scripts.daily_capture.build_weekly_market_close_package import validate_actions_week_binding
        valid = (
            ("2026-11-29T22:35:00Z", "preclose", False),
            ("2026-11-30T01:05:00Z", "final", False),
            ("2026-06-28T21:35:00Z", "preclose", False),
            ("2026-06-29T00:05:00Z", "final", False),
        )
        with tempfile.TemporaryDirectory() as d:
            event = Path(d) / "event.json"
            for at, mode, _ in valid:
                event.write_text(json.dumps({"ref": "refs/heads/main", "inputs": {"mode": mode}}))
                now = datetime.fromisoformat(at.replace("Z", "+00:00"))
                self.assertEqual(resolve_close_mode(mode, event_name="workflow_dispatch",
                    event_path=str(event), run_attempt="1", now=now), mode)
                validate_actions_week_binding(now, mode, event_name="workflow_dispatch",
                    event_path=str(event), run_attempt="1")
            for bad_time, mode, ref, attempt in (
                ("2026-11-29T22:30:00Z", "preclose", "refs/heads/main", "1"),
                ("2026-11-30T00:30:00Z", "final", "refs/heads/main", "1"),
                ("2026-11-30T01:05:00Z", "final", "refs/heads/feature", "1"),
                ("2026-11-30T01:05:00Z", "final", "refs/heads/main", "2"),
                ("2026-12-01T01:05:00Z", "final", "refs/heads/main", "1"),
                ("2026-06-28T22:35:00Z", "preclose", "refs/heads/main", "1"),
            ):
                event.write_text(json.dumps({"ref": ref, "inputs": {"mode": mode}}))
                now = datetime.fromisoformat(bad_time.replace("Z", "+00:00"))
                with self.assertRaises(ValueError):
                    resolve_close_mode(mode, event_name="workflow_dispatch",
                        event_path=str(event), run_attempt=attempt, now=now)
                with self.assertRaises(ValueError):
                    validate_actions_week_binding(now, mode, event_name="workflow_dispatch",
                        event_path=str(event), run_attempt=attempt)
            event.write_text(json.dumps({"ref": "refs/heads/main", "inputs": {"mode": "preclose"}}))
            with self.assertRaises(ValueError):
                resolve_close_mode("final", event_name="workflow_dispatch",
                    event_path=str(event), run_attempt="1",
                    now=datetime(2026, 11, 30, 1, 5, tzinfo=timezone.utc))

    def test_valid_scheduled_and_wrong_week_runs_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            event = Path(d) / "event.json"
            event.write_text(json.dumps({"schedule": "5 2 * * 1"}))
            valid = datetime(2026, 11, 30, 1, 5, tzinfo=timezone.utc)
            self.assertEqual(resolve_close_mode("auto", event_name="schedule",
                event_path=str(event), run_attempt="1", now=valid), "final")
            for now in (datetime(2026, 12, 1, 1, 5, tzinfo=timezone.utc),
                        datetime(2026, 11, 29, 1, 5, tzinfo=timezone.utc)):
                with self.assertRaises(ValueError):
                    resolve_close_mode("auto", event_name="schedule", event_path=str(event),
                        run_attempt="1", now=now)
            with self.assertRaisesRegex(ValueError, "RERUN_ORIGINAL_WEEK"):
                resolve_close_mode("final", event_name="schedule", event_path=str(event),
                    run_attempt="2", now=valid)
            with self.assertRaises(ValueError):
                resolve_close_mode("preclose", event_name="schedule", event_path=str(event),
                    run_attempt="1", now=valid)
            event.write_text(json.dumps({"schedule":"10 10 * * 3"}))
            with self.assertRaises(ValueError):
                resolve_close_mode("auto", event_name="schedule", event_path=str(event),
                    run_attempt="1", now=valid)

    def test_offline_explicit_mode_and_unknown_triggers(self):
        self.assertEqual(resolve_close_mode("final",event_name="",event_path=""),"final")
        self.assertEqual(resolve_close_mode("preclose",event_name="",event_path=""),"preclose")
        with self.assertRaises(ValueError):
            resolve_close_mode("auto",event_name="",event_path="")
        with self.assertRaises(ValueError):
            resolve_close_mode("final",event_name="push",event_path="")


if __name__ == "__main__":
    unittest.main()
