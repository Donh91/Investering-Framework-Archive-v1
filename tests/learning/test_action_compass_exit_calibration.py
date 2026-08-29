from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "learning" / "action_compass_exit_calibration.py"
SPEC = importlib.util.spec_from_file_location("action_compass_exit_calibration", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ExitCalibrationTests(unittest.TestCase):
    def test_groups_matured_warning_rows_without_creating_exit_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outcome_root = root / "outcomes"
            output = root / "LATEST.json"
            outcome_root.mkdir(parents=True)
            sidecar = {
                "contract": "ACTION_COMPASS_OUTCOME_SIDECAR_v1_1",
                "horizon": "7D",
                "status": "MATURED",
                "decision_snapshot": {
                    "lane_3_state": "PARABOLIC_ALTSEASON",
                    "lane_3_action": "HOLD",
                    "lane_3_warning": "DISTRIBUTION_WARNING",
                },
                "series_outcomes": [
                    {
                        "series_id": "BTC_USDT_MARK_PRICE",
                        "status": "MATURED",
                        "terminal_return_pct": 8.0,
                        "max_upside_from_start_pct": 19.0,
                        "max_drawdown_from_start_pct": -6.0,
                        "time_to_trough_hours": 72.0,
                        "normalized_full_exit_counterfactual": {
                            "capital_preserved_pct": 0.0,
                            "upside_foregone_pct": 8.0,
                        },
                    },
                    {
                        "series_id": "ETH_USDT_MARK_PRICE",
                        "status": "MATURED",
                        "terminal_return_pct": -12.0,
                        "max_upside_from_start_pct": 11.0,
                        "max_drawdown_from_start_pct": -24.0,
                        "time_to_trough_hours": 120.0,
                        "normalized_full_exit_counterfactual": {
                            "capital_preserved_pct": 12.0,
                            "upside_foregone_pct": 0.0,
                        },
                    },
                ],
            }
            (outcome_root / "sample.json").write_text(json.dumps(sidecar), encoding="utf-8")
            report = MODULE.build_report(outcome_root, "2026-08-29T16:00:00Z")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["warning_series_row_count"], 2)
            self.assertEqual(len(report["cohorts"]), 2)
            btc = next(row for row in report["cohorts"] if row["series_id"] == "BTC_USDT_MARK_PRICE")
            self.assertEqual(btc["lane_3_state"], "PARABOLIC_ALTSEASON")
            self.assertEqual(btc["lane_3_warning"], "DISTRIBUTION_WARNING")
            self.assertEqual(btc["median_max_upside_after_signal_pct"], 19.0)
            self.assertEqual(btc["median_full_exit_terminal_upside_foregone_reference_pct"], 8.0)
            self.assertTrue(report["interpretation_boundary"]["descriptive_only"])
            self.assertFalse(report["interpretation_boundary"]["market_rule_change"])
            self.assertFalse(report["interpretation_boundary"]["portfolio_action"])

    def test_empty_repository_is_explicit_not_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = MODULE.build_report(root / "missing", "2026-08-29T16:00:00Z")
            self.assertEqual(report["status"], "NO_MATURED_ROWS")
            self.assertEqual(report["source_sidecar_count"], 0)
            self.assertEqual(report["cohorts"], [])


if __name__ == "__main__":
    unittest.main()
