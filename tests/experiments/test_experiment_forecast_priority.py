import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "experiments" / "experiment_lifecycle.py"


class ExperimentForecastPriorityTest(unittest.TestCase):
    def test_daily_director_forecast_is_not_crowded_out_by_discovery_candidates(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            daily = root / "daily"
            daily.mkdir()
            experiments = []
            for index in range(6):
                experiments.append({
                    "kind": "SENSOR_COMBINATION",
                    "title": f"Discovery pair {index}",
                    "hypothesis": "The pair may contain forward information.",
                    "falsifier": "The fixed target is not satisfied at the horizon.",
                    "horizon_days": 7,
                    "components": [
                        {"metric_path": "breadth.advancers", "operator": "GT", "threshold": 50},
                        {"metric_path": "spot.ETHBTC.close", "operator": "GT", "threshold": 0.029},
                    ],
                    "target_metric_path": "spot.BTCUSDT.close",
                    "target_direction": "UP",
                    "target_threshold_pct": 1.0 + index / 10,
                    "regime_dependency": "DISCOVERY",
                    "novelty_reason": f"candidate-{index}",
                    "evidence_basis": ["prospective"],
                })
            output = {
                "experiment_candidates": experiments,
                "forecast_candidates": [{
                    "metric_path": "spot.ETHUSDT.close",
                    "direction": "UP",
                    "target_mode": "PCT_MOVE",
                    "threshold_pct": 2.0,
                    "target_value": None,
                    "range_low": None,
                    "range_high": None,
                    "horizon_days": 7,
                    "rationale": "Daily Director priority forecast",
                }],
            }
            context = {
                "latest_capture": {
                    "captured_at_utc": "2026-08-05T10:00:00Z",
                    "run_id": "run-priority",
                    "market_metrics": {
                        "spot": {"BTCUSDT": {"close": 64000.0}, "ETHUSDT": {"close": 1870.0}, "ETHBTC": {"close": 0.0292}},
                        "breadth": {"advancers": 55},
                    },
                },
                "previous_capture": {
                    "captured_at_utc": "2026-08-05T06:00:00Z",
                    "market_metrics": {
                        "spot": {"BTCUSDT": {"close": 63000.0}, "ETHUSDT": {"close": 1830.0}, "ETHBTC": {"close": 0.0290}},
                        "breadth": {"advancers": 45},
                    },
                },
                "metric_deltas": [],
            }
            (daily / "output.json").write_text(json.dumps(output))
            (daily / "context.json").write_text(json.dumps(context))
            (daily / "receipt.json").write_text(json.dumps({"contract": "API_AGENT_RECEIPT_v3"}))
            subprocess.run([
                sys.executable, str(SCRIPT),
                "--repo-root", str(root),
                "--daily-output", str(daily / "output.json"),
                "--daily-context", str(daily / "context.json"),
                "--daily-receipt", str(daily / "receipt.json"),
                "--candidate-root", str(root / "research/experiment_lifecycle/candidates"),
                "--observation-root", str(root / "research/experiment_lifecycle/observations"),
                "--dispatch-root", str(root / "research/experiment_lifecycle/dispatch"),
                "--forecast-root", str(root / "research/framework_memory/forecast_memory"),
                "--outcome-root", str(root / "research/framework_memory/outcome_memory"),
                "--receipt-root", str(root / "research/experiment_lifecycle/receipts"),
                "--registry-output", str(root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"),
                "--manifest-output", str(root / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json"),
                "--max-new-forecasts", "5",
            ], check=True)
            forecasts = [json.loads(path.read_text()) for path in (root / "research/framework_memory/forecast_memory").rglob("*.json")]
            self.assertEqual(len(forecasts), 5)
            # Frozen forecasts store the canonical document-rooted metric path so that
            # the maturation resolver dereferences the same metric that was read at
            # freeze time (TASK3 R3-04). The Director candidate is still supplied in
            # market-metrics-relative form; only the stored path is canonicalised.
            self.assertIn("market_metrics.spot.ETHUSDT.close", {row["metric_path"] for row in forecasts})
            self.assertEqual({row["metric_path_root"] for row in forecasts}, {"CAPTURE_DOCUMENT_ROOT"})
            self.assertTrue(all(row["unit_contract_version"] == "FORECAST_TARGET_UNITS_v2" for row in forecasts))


if __name__ == "__main__":
    unittest.main()
