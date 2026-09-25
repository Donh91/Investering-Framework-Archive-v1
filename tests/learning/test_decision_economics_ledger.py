"""Decision Economics Ledger v1.1 regression tests."""
from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from scripts.learning import decision_economics_ledger as del_


def write_returns(path: Path, start: date, days: int, fn) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", *del_.SEGMENTS])
        for index in range(days):
            day = start + timedelta(days=index)
            writer.writerow([
                day.isoformat(),
                *[("" if fn(day, segment) is None else fn(day, segment)) for segment in del_.SEGMENTS],
            ])


def compass(compass_id: str, issued: str, statuses) -> dict:
    return {
        "contract": "OFFICIAL_DAILY_COMPASS_v1",
        "compass_id": compass_id,
        "compass_sha256": compass_id * 4,
        "issued_at_utc": issued,
        "data_status": "OK",
        "capitalization_ladder": [
            {"segment": segment, "status": status}
            for segment, status in zip(del_.SEGMENTS, statuses)
        ],
    }


class DecisionEconomicsLedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.csv = Path(self.tmp.name) / "returns.csv"
        write_returns(self.csv, date(2026, 4, 1), 260, lambda day, segment: 0.01)
        self.returns = del_.load_returns(self.csv)
        self.as_of = del_.parse_utc("2026-12-31T00:00:00Z")

    def test_fresh_capital_does_not_buy_on_prepare_wait_or_hold(self):
        compasses = [
            compass("A", "2026-09-07T06:00:00Z", ("HOLD", "PREPARE", "WAIT", "HARD_WAIT", "WAIT", "HOLD")),
            compass("B", "2026-09-14T06:00:00Z", ("HOLD", "PREPARE", "WAIT", "HARD_WAIT", "WAIT", "HOLD")),
        ]
        rows = del_.score_compasses(compasses, self.returns, self.as_of)
        fresh = [row for row in rows if row["interpretation"] == "FRESH_CAPITAL"]
        self.assertTrue(fresh)
        self.assertTrue(all(row["compass_exposure"] == 0.0 for row in fresh))
        self.assertTrue(all(row["compass_turnover"] == 0.0 for row in fresh))

    def test_deploy_enters_once_and_later_hold_has_zero_turnover(self):
        statuses_enter = ("DEPLOY", "HOLD", "WAIT", "WAIT", "HARD_WAIT", "HARD_WAIT")
        statuses_hold = ("HOLD", "HOLD", "WAIT", "WAIT", "HARD_WAIT", "HARD_WAIT")
        rows = del_.score_compasses(
            [
                compass("A", "2026-09-07T06:00:00Z", statuses_enter),
                compass("B", "2026-09-14T06:00:00Z", statuses_hold),
            ],
            self.returns,
            self.as_of,
        )
        btc = [
            row for row in rows
            if row["segment"] == "BTC"
            and row["interpretation"] == "FRESH_CAPITAL"
            and row["challenger"] == "CASH"
            and row["horizon_days"] == 7
        ]
        self.assertEqual([row["compass_exposure"] for row in btc], [1.0, 1.0])
        # Initialization is deliberately cost-neutral; persistent HOLD must not
        # be charged again on the second freeze.
        self.assertEqual([row["compass_turnover"] for row in btc], [0.0, 0.0])

    def test_turnover_cost_only_applies_on_actual_exit_transition(self):
        enter = compass("A", "2026-09-07T06:00:00Z", ("DEPLOY", "HOLD", "WAIT", "WAIT", "WAIT", "WAIT"))
        exit_ = compass("B", "2026-09-14T06:00:00Z", ("EXIT", "HOLD", "WAIT", "WAIT", "WAIT", "WAIT"))
        rows = del_.score_compasses([enter, exit_], self.returns, self.as_of)
        row = next(
            row for row in rows
            if row["compass_id"] == "B"
            and row["segment"] == "BTC"
            and row["interpretation"] == "FRESH_CAPITAL"
            and row["challenger"] == "CASH"
            and row["horizon_days"] == 7
        )
        self.assertEqual(row["compass_exposure"], 0.0)
        self.assertEqual(row["compass_turnover"], 1.0)
        self.assertAlmostEqual(row["compass_pnl"], -del_.ONE_WAY_COST["BTC"])

    def test_incumbent_holder_exposes_absence_of_derisk_action(self):
        rows = del_.score_compasses(
            [compass("A", "2026-09-07T06:00:00Z", ("HOLD", "HOLD", "WAIT", "WAIT", "HARD_WAIT", "HARD_WAIT"))],
            self.returns,
            self.as_of,
        )
        current_states = {"HOLD", "PREPARE", "WAIT", "HARD_WAIT"}
        incumbent = [row for row in rows if row["interpretation"] == "INCUMBENT_HOLDER" and row["ladder_state"] in current_states]
        self.assertTrue(incumbent)
        self.assertTrue(all(row["compass_exposure"] == 1.0 for row in incumbent))

    def test_missing_return_is_data_missing_not_zero(self):
        write_returns(
            self.csv,
            date(2026, 4, 1),
            260,
            lambda day, segment: None if segment == "ETH" and day == date(2026, 9, 9) else 0.01,
        )
        returns = del_.load_returns(self.csv)
        rows = del_.score_compasses(
            [compass("A", "2026-09-07T06:00:00Z", ("HOLD",) * 6)],
            returns,
            self.as_of,
        )
        eth3 = [row for row in rows if row["segment"] == "ETH" and row["horizon_days"] == 3]
        self.assertTrue(all(row["status"] == "DATA_MISSING" for row in eth3))
        self.assertTrue(all(row["paired_delta"] is None for row in eth3))

    def test_core_state_is_point_in_time(self):
        before = del_.challenger_target("CORE_STATE_BTC100_5PCT", self.returns, date(2026, 9, 10))
        write_returns(
            self.csv,
            date(2026, 4, 1),
            260,
            lambda day, segment: -0.20 if day >= date(2026, 9, 10) else 0.01,
        )
        changed_future = del_.load_returns(self.csv)
        after = del_.challenger_target("CORE_STATE_BTC100_5PCT", changed_future, date(2026, 9, 10))
        self.assertEqual(before, after)

    def test_row_identity_includes_interpretation_and_authority_is_zero(self):
        rows = del_.score_compasses(
            [compass("A", "2026-09-07T06:00:00Z", ("HOLD",) * 6)],
            self.returns,
            self.as_of,
        )
        candidates = [
            row for row in rows
            if row["segment"] == "BTC" and row["horizon_days"] == 7 and row["challenger"] == "CASH"
        ]
        self.assertEqual(len(candidates), 2)
        self.assertNotEqual(candidates[0]["row_id"], candidates[1]["row_id"])
        self.assertTrue(all(row["authority"] == del_.AUTHORITY for row in candidates))

    def test_first_ok_freeze_per_iso_week_is_the_only_inference_unit(self):
        rows = del_.score_compasses(
            [
                compass("A", "2026-09-07T06:00:00Z", ("HOLD",) * 6),
                compass("B", "2026-09-07T18:00:00Z", ("HOLD",) * 6),
                compass("C", "2026-09-14T06:00:00Z", ("HOLD",) * 6),
            ],
            self.returns,
            self.as_of,
        )
        flags = {row["compass_id"]: row["weekly_inference_unit"] for row in rows}
        self.assertTrue(flags["A"])
        self.assertFalse(flags["B"])
        self.assertTrue(flags["C"])

    def test_unavailable_action_fails_closed_without_guessing(self):
        rows = del_.score_compasses(
            [compass("A", "2026-09-07T06:00:00Z", ("UNAVAILABLE", "HOLD", "WAIT", "WAIT", "WAIT", "WAIT"))],
            self.returns,
            self.as_of,
        )
        btc = [row for row in rows if row["segment"] == "BTC"]
        self.assertTrue(all(row["status"] == "COMPASS_ACTION_UNSCORABLE" for row in btc))


if __name__ == "__main__":
    unittest.main()
