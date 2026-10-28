"""Prospective status means the forecast existed by each original UTC window start."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.cycle_navigator.build_weekly_cycle_navigator import append_forward_ranges

LEDGER = Path("05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl")
FREEZE = {
    "btc_range_low": 79000, "btc_range_high": 90000,
    "eth_range_low": 2200, "eth_range_high": 2900,
    "intraday_map": {
        "day_1_2": "BTC $79000–$87000, ETH $2200–$2600",
        "day_3_4": "BTC $78000–$89000, ETH $2100–$2800",
        "day_5_7": "BTC $77000–$90000, ETH $2000–$2900",
    },
}


class ForwardRangeWindowClockTests(unittest.TestCase):
    def make_rows(self, generated):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            append_forward_ranges(
                root, public_issue_number=31, machine_issue_number=32,
                year=2026, week=44,
                generated_unix=int(datetime.fromisoformat(generated.replace("Z", "+00:00")).timestamp()),
                freeze=FREEZE)
            return [json.loads(x) for x in (root / LEDGER).read_text().splitlines()]

    def test_exact_monday_utc_boundary_is_prospective(self):
        rows = self.make_rows("2026-10-26T00:00:00Z")
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(x["status"] == "FROZEN_PROSPECTIVE" for x in rows))

    def test_monday_morning_is_not_prospective_for_full_week_or_day_1_2(self):
        rows = self.make_rows("2026-10-26T06:00:00Z")
        by_window = {}
        for x in rows:
            by_window.setdefault(x["window"], []).append(x["status"])
        self.assertEqual(set(by_window), {"weekly", "day_1_2", "day_3_4", "day_5_7"})
        self.assertTrue(all(s == "ISSUED_AFTER_WINDOW_START" for s in
                            by_window["weekly"] + by_window["day_1_2"]))
        self.assertTrue(all(s == "FROZEN_PROSPECTIVE" for s in
                            by_window["day_3_4"] + by_window["day_5_7"]))

    def test_wednesday_after_window_start_is_not_retroactively_promoted(self):
        rows = self.make_rows("2026-10-28T12:00:00Z")
        for x in rows:
            expect = ("FROZEN_PROSPECTIVE" if x["window"] == "day_5_7"
                      else "ISSUED_AFTER_WINDOW_START")
            self.assertEqual(x["status"], expect)

    def test_append_only_does_not_rewrite_first_frozen_release(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def issue(stamp):
                append_forward_ranges(
                    root, public_issue_number=31, machine_issue_number=32,
                    year=2026, week=44,
                    generated_unix=int(datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()),
                    freeze=FREEZE)
            issue("2026-10-26T00:00:00Z")
            original = (root / LEDGER).read_bytes()
            issue("2026-10-28T12:00:00Z")
            self.assertEqual((root / LEDGER).read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
