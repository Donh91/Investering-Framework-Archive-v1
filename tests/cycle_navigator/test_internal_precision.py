from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/cycle_navigator/build_internal_precision.py"
spec = importlib.util.spec_from_file_location("internal_precision", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class InternalPrecisionTests(unittest.TestCase):
    def test_w37_bounded_migration_is_explicit_and_complete(self) -> None:
        score = json.loads((ROOT / "05_CYCLE_NAVIGATOR/weekly/2026/W38/CYCLE_NAVIGATOR_SCORECARD.json").read_text())
        rows, source = mod.score_rows_from_public(score)
        self.assertEqual(source, "BOUNDED_W37_MIGRATION_FROM_EXISTING_FROZEN_CLAIMS")
        self.assertEqual(len(rows), 7)
        by_id = {row["parameter_id"]: row for row in rows}
        self.assertEqual(by_id["structural_call_4"]["score"], 50.0)
        self.assertEqual(by_id["structural_call_1"]["score"], 100.0)
        accounted, mature, coverage = mod.internal_coverage(rows)
        self.assertEqual((accounted, mature, coverage), (7, 7, 100.0))

    def test_current_cn_does_not_invent_intraday_or_ranges(self) -> None:
        machine = json.loads((ROOT / "05_CYCLE_NAVIGATOR/weekly/2026/W38/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").read_text())
        freeze = json.loads((ROOT / "05_CYCLE_NAVIGATOR/weekly/2026/W38/CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_text())
        claims, unavailable = mod.build_claims(26, 2026, 38, machine, freeze)
        pids = {row["source_parameter_id"] for row in claims}
        self.assertNotIn("intraday_day_1_2", pids)
        self.assertNotIn("btc_range", pids)
        self.assertNotIn("eth_range", pids)
        self.assertIn("intraday_day_1_2", unavailable)
        self.assertIn("btc_range", unavailable)
        self.assertIn("eth_range", unavailable)

    def test_future_intraday_claims_are_frozen_only_when_available(self) -> None:
        freeze = {
            "btc_range_low": 1,
            "btc_range_high": 2,
            "eth_range_low": None,
            "eth_range_high": None,
            "ethbtc_condition": "flat or higher",
            "breadth_condition": "weak",
            "structural_calls": ["regime", "ethbtc", "leadership", "rotation", "altseason"],
            "intraday_map": {"day_1_2": "down then stabilize", "day_3_4": "UNAVAILABLE", "day_5_7": "recovery attempt"},
        }
        machine = {"base_case_2_3_weeks": "selective rotation", "base_case_4_8_weeks": "UNAVAILABLE"}
        claims, unavailable = mod.build_claims(27, 2026, 39, machine, freeze)
        pids = {row["source_parameter_id"] for row in claims}
        self.assertIn("intraday_day_1_2", pids)
        self.assertIn("intraday_day_5_7", pids)
        self.assertNotIn("intraday_day_3_4", pids)
        self.assertIn("intraday_day_3_4", unavailable)
        self.assertIn("base_case_4_8_weeks", unavailable)

    def test_ledger_is_idempotent_but_conflict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.jsonl"
            row = {"score_key": "Y2026-W37-CN25", "value": 1}
            mod.append_ledger(path, row)
            mod.append_ledger(path, row)
            self.assertEqual(len(path.read_text().splitlines()), 1)
            with self.assertRaises(SystemExit):
                mod.append_ledger(path, {"score_key": "Y2026-W37-CN25", "value": 2})

    def test_box_has_compact_required_dimensions(self) -> None:
        rows = [
            {"parameter_id": "structural_call_1", "family": "regime", "status": "SUPPORTED", "score": 100.0},
            {"parameter_id": "ethbtc_condition", "family": "ethbtc", "status": "SUPPORTED", "score": 100.0},
            {"parameter_id": "breadth_condition", "family": "breadth", "status": "SUPPORTED", "score": 100.0},
            {"parameter_id": "structural_call_4", "family": "rotation", "status": "MIXED", "score": 50.0},
            {"parameter_id": "intraday_day_1_2", "family": "intraday", "status": "SUPPORTED", "score": 100.0},
        ]
        box = mod.render_box(issue_scored=25, completed_week=37, public_structural=90.0, rows=rows, unavailable=["btc_range"], pending_long=2, self_critique="under-called drawdown")
        self.assertIn("Weekly structural 90%", box)
        self.assertIn("Intraday 100%", box)
        self.assertIn("Regime 100%", box)
        self.assertIn("Rotation 50%", box)
        self.assertIn("Self-critique:", box)
        self.assertLessEqual(len(box.splitlines()), 8)


if __name__ == "__main__":
    unittest.main()
