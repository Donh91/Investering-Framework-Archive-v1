import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "experiments" / "experiment_lifecycle.py"


def run_engine(repo: Path, output: dict, context: dict, catalog: Path | None = None) -> dict:
    daily = repo / "daily"
    daily.mkdir(parents=True)
    files = {
        "output.json": output,
        "context.json": context,
        "receipt.json": {"contract": "API_AGENT_RECEIPT_v3"},
    }
    for name, value in files.items():
        (daily / name).write_text(json.dumps(value))
    cmd = [
        sys.executable, str(SCRIPT),
        "--repo-root", str(repo),
        "--daily-output", str(daily / "output.json"),
        "--daily-context", str(daily / "context.json"),
        "--daily-receipt", str(daily / "receipt.json"),
        "--candidate-root", str(repo / "research/experiment_lifecycle/candidates"),
        "--observation-root", str(repo / "research/experiment_lifecycle/observations"),
        "--dispatch-root", str(repo / "research/experiment_lifecycle/dispatch"),
        "--forecast-root", str(repo / "research/framework_memory/forecast_memory"),
        "--outcome-root", str(repo / "research/framework_memory/outcome_memory"),
        "--receipt-root", str(repo / "research/experiment_lifecycle/receipts"),
        "--registry-output", str(repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"),
        "--manifest-output", str(repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json"),
    ]
    if catalog:
        cmd += ["--legacy-sensor-catalog", str(catalog)]
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


class ExperimentLifecycleTest(unittest.TestCase):
    def test_forecast_candidate_is_frozen_and_matures_later(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            context = {
                "latest_capture": {"captured_at_utc": "2026-08-05T10:00:00Z", "run_id": "run-1", "market_metrics": {"spot": {"BTCUSDT": {"close": 64000.0}}}},
                "previous_capture": {"captured_at_utc": "2026-08-05T06:00:00Z", "market_metrics": {"spot": {"BTCUSDT": {"close": 63000.0}}}},
                "metric_deltas": [],
            }
            output = {
                "forecast_candidates": [{"metric_path": "spot.BTCUSDT.close", "direction": "UP", "threshold": 2.0, "range_low": None, "range_high": None, "horizon_days": 7, "rationale": "Prospective test"}],
                "experiment_candidates": [],
            }
            summary = run_engine(repo, output, context)
            self.assertEqual(summary["new_forecasts"], 1)
            registry = json.loads((repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text())
            self.assertEqual(registry["state_counts"]["WAITING_FOR_MATURITY"], 1)
            frozen = json.loads(next((repo / "research/framework_memory/forecast_memory").rglob("*.json")).read_text())
            self.assertTrue(frozen["experimental_only"])
            self.assertFalse(frozen["authority"]["portfolio_action"])

    def test_legacy_pair_waits_for_mapping_without_expiry(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            catalog = repo / "catalog.json"
            catalog.write_text(json.dumps({"test_id": "SENSOR_PAIR_DISCOVERY_LAB_V0_1", "pairs": [{"pair_id": "P99", "sensor_a": "ODD_A", "sensor_b": "ODD_B"}]}))
            context = {"latest_capture": {"captured_at_utc": "2026-08-05T10:00:00Z", "run_id": "run-1", "market_metrics": {}}, "previous_capture": None, "metric_deltas": []}
            run_engine(repo, {"forecast_candidates": [], "experiment_candidates": []}, context, catalog)
            registry = json.loads((repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text())
            self.assertEqual(registry["state_counts"]["WAITING_FOR_MAPPING"], 1)
            candidate = json.loads(next((repo / "research/experiment_lifecycle/candidates").rglob("*.json")).read_text())
            self.assertFalse(candidate["dormancy_policy"]["automatic_age_expiry"])
            self.assertEqual(len(list((repo / "research/framework_memory/forecast_memory").rglob("*.json"))), 0)


if __name__ == "__main__":
    unittest.main()
