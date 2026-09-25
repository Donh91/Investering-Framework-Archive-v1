"""Regression tests for bounded slow-macro recovery scheduling."""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.daily_capture.slow_macro_recovery import decide, latest_valid_macro_capture

NOW = datetime(2026, 9, 25, 8, 0, tzinfo=timezone.utc)


def write_capture(root: Path, stamp: str, *, macro: dict | None, name: str) -> Path:
    path = root / "2026/09/25" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    packet = {
        "contract": "DAILY_LIVE_ANCHOR_INDEX_v3",
        "captured_at_utc": stamp,
        "market_metrics": {"macro": macro or {}},
    }
    path.write_text(json.dumps(packet), encoding="utf-8")
    return path


class SlowMacroRecoveryGuardTest(unittest.TestCase):
    def test_fresh_macro_does_not_duplicate_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_capture(root, "2026-09-25T00:00:00Z", macro={"DGS10": {"value": 4.2}}, name="fresh.json")
            out = decide(root, NOW, threshold_hours=24)
            self.assertFalse(out["run_slow_lane"])
            self.assertEqual(out["reason"], "MACRO_CAPTURE_FRESH_ENOUGH")
            self.assertEqual(out["age_seconds"], 8 * 3600)

    def test_stale_macro_makes_next_successful_anchor_a_recovery_slot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_capture(root, "2026-09-24T07:00:00Z", macro={"DGS10": {"value": 4.2}}, name="stale.json")
            out = decide(root, NOW, threshold_hours=24)
            self.assertTrue(out["run_slow_lane"])
            self.assertEqual(out["reason"], "MACRO_RECOVERY_DUE")
            self.assertEqual(out["age_seconds"], 25 * 3600)
            self.assertFalse(out["authority"]["source_substitution"])
            self.assertFalse(out["authority"]["forward_fill"])

    def test_empty_later_tactical_capture_does_not_hide_last_valid_macro(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = write_capture(root, "2026-09-24T07:00:00Z", macro={"DGS10": {"value": 4.2}}, name="old-valid.json")
            write_capture(root, "2026-09-25T07:00:00Z", macro={}, name="new-tactical.json")
            latest, path = latest_valid_macro_capture(root)
            self.assertEqual(latest, datetime(2026, 9, 24, 7, 0, tzinfo=timezone.utc))
            self.assertTrue(path.endswith(old.name))
            self.assertTrue(decide(root, NOW, threshold_hours=24)["run_slow_lane"])

    def test_no_valid_macro_fails_toward_capture_not_false_freshness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_capture(root, "2026-09-25T07:00:00Z", macro={}, name="empty.json")
            out = decide(root, NOW, threshold_hours=24)
            self.assertTrue(out["run_slow_lane"])
            self.assertEqual(out["reason"], "NO_VALID_MACRO_CAPTURE")
            self.assertIsNone(out["age_seconds"])

    def test_future_timestamp_cannot_suppress_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_capture(root, "2026-09-25T09:00:00Z", macro={"DGS10": {"value": 4.2}}, name="future.json")
            out = decide(root, NOW, threshold_hours=24)
            self.assertTrue(out["run_slow_lane"])
            self.assertEqual(out["reason"], "LATEST_MACRO_CAPTURE_FROM_FUTURE")


if __name__ == "__main__":
    unittest.main()
