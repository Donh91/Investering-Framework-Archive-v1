from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "scripts" / "health" / "hourly_sequence_watchdog.py"
spec = importlib.util.spec_from_file_location("hourly_sequence_watchdog", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class HourlySequenceWatchdogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 31, 17, 42, tzinfo=timezone.utc)

    def latest(self, *, end: str = "2026-08-31T17:00:00Z", status: str = "COMPLETE"):
        return {
            "contract": "HOURLY_SEQUENCE_LATEST_POINTER_v2_2",
            "status": status,
            "run_id": "HOURLY_SEQUENCE_fixture",
            "window_end_utc": end,
        }

    def test_fresh_owner_is_noop(self):
        receipt = module.build_receipt(self.latest(), self.now, 90, 12, [])
        self.assertEqual(receipt["decision"], "NOOP_FRESH")
        self.assertFalse(receipt["owner"]["is_stale"])

    def test_stale_owner_requires_dispatch_without_guard(self):
        receipt = module.build_receipt(
            self.latest(end="2026-08-31T16:00:00Z"), self.now, 90, 12, []
        )
        self.assertEqual(receipt["decision"], "DISPATCH_REQUIRED")
        self.assertEqual(receipt["owner"]["reason"], "WINDOW_END_STALE")
        self.assertFalse(receipt["guard"]["blocked"])

    def test_non_complete_owner_is_stale_even_when_recent(self):
        receipt = module.build_receipt(
            self.latest(status="PARTIAL"), self.now, 90, 12, []
        )
        self.assertEqual(receipt["decision"], "DISPATCH_REQUIRED")
        self.assertEqual(receipt["owner"]["reason"], "LATEST_NOT_COMPLETE")

    def test_active_equivalent_run_suppresses_duplicate_dispatch(self):
        runs = [
            {
                "id": 123,
                "status": "in_progress",
                "event": "schedule",
                "created_at": "2026-08-31T17:39:00Z",
            }
        ]
        receipt = module.build_receipt(
            self.latest(end="2026-08-31T16:00:00Z"), self.now, 90, 12, runs
        )
        self.assertEqual(receipt["decision"], "NOOP_ACTIVE_OR_RECENT_RUN")
        self.assertEqual(receipt["guard"]["reason"], "ACTIVE_EQUIVALENT_RUN")
        self.assertEqual(receipt["guard"]["run_id"], 123)

    def test_recent_completed_run_suppresses_eventual_consistency_race(self):
        runs = [
            {
                "id": 124,
                "status": "completed",
                "conclusion": "success",
                "event": "workflow_dispatch",
                "created_at": "2026-08-31T17:35:00Z",
            }
        ]
        receipt = module.build_receipt(
            self.latest(end="2026-08-31T16:00:00Z"), self.now, 90, 12, runs
        )
        self.assertEqual(receipt["decision"], "NOOP_ACTIVE_OR_RECENT_RUN")
        self.assertEqual(receipt["guard"]["reason"], "RECENT_EQUIVALENT_RUN_RACE_GUARD")

    def test_old_completed_run_does_not_suppress_recovery(self):
        runs = [
            {
                "id": 125,
                "status": "completed",
                "conclusion": "success",
                "event": "schedule",
                "created_at": "2026-08-31T17:00:00Z",
            }
        ]
        receipt = module.build_receipt(
            self.latest(end="2026-08-31T16:00:00Z"), self.now, 90, 12, runs
        )
        self.assertEqual(receipt["decision"], "DISPATCH_REQUIRED")

    def test_missing_window_end_fails_stale(self):
        latest = self.latest()
        latest.pop("window_end_utc")
        receipt = module.build_receipt(latest, self.now, 90, 12, [])
        self.assertEqual(receipt["decision"], "DISPATCH_REQUIRED")
        self.assertEqual(receipt["owner"]["reason"], "WINDOW_END_MISSING")

    def test_authority_firewall_is_explicit(self):
        receipt = module.build_receipt(self.latest(), self.now, 90, 12, [])
        authority = receipt["authority"]
        self.assertFalse(authority["canonical_market_state"])
        self.assertFalse(authority["portfolio_execution"])
        self.assertFalse(authority["automatic_rule_changes"])
        self.assertTrue(authority["dispatch_existing_owner_only"])


if __name__ == "__main__":
    unittest.main()
