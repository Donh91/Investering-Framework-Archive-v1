import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "experiments" / "experiment_lifecycle.py"


def run_engine(repo: Path, output: dict, context: dict, catalog: Path | None = None) -> dict:
    daily = repo / "daily"
    daily.mkdir(parents=True, exist_ok=True)
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


def context(captured_at: str, run_id: str = "run-1") -> dict:
    return {
        "latest_capture": {
            "captured_at_utc": captured_at,
            "run_id": run_id,
            "market_metrics": {
                "spot": {
                    "BTCUSDT": {"close": 64000.0},
                    "ETHUSDT": {"close": 1870.0},
                    "ETHBTC": {"close": 0.0292},
                },
                "breadth": {"advancers": 55, "decliners": 30},
            },
        },
        "previous_capture": {
            "captured_at_utc": "2026-08-05T06:00:00Z",
            "market_metrics": {
                "spot": {
                    "BTCUSDT": {"close": 63000.0},
                    "ETHUSDT": {"close": 1830.0},
                    "ETHBTC": {"close": 0.0290},
                },
                "breadth": {"advancers": 45, "decliners": 35},
            },
        },
        "metric_deltas": [],
    }


class ExperimentLifecycleTest(unittest.TestCase):
    def test_forecast_candidate_is_frozen_and_matures_later(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {
                "forecast_candidates": [{
                    "metric_path": "spot.BTCUSDT.close",
                    "direction": "UP",
                    "threshold": 2.0,
                    "range_low": None,
                    "range_high": None,
                    "horizon_days": 7,
                    "rationale": "Prospective test",
                }],
                "experiment_candidates": [],
            }
            summary = run_engine(repo, output, context("2026-08-05T10:00:00Z"))
            self.assertEqual(summary["new_forecasts"], 1)
            registry = json.loads((repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text())
            self.assertEqual(registry["state_counts"]["WAITING_FOR_MATURITY"], 1)
            frozen = json.loads(next((repo / "research/framework_memory/forecast_memory").rglob("*.json")).read_text())
            self.assertTrue(frozen["experimental_only"])
            self.assertFalse(frozen["authority"]["portfolio_action"])
            self.assertEqual(frozen["controls"]["always_wait"], "ALWAYS_WAIT")
            self.assertIn(frozen["controls"]["deterministic_placebo_direction"], {"UP", "DOWN", "RANGE"})

    def test_legacy_pair_waits_for_mapping_without_expiry(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            catalog = repo / "catalog.json"
            catalog.write_text(json.dumps({
                "test_id": "SENSOR_PAIR_DISCOVERY_LAB_V0_1",
                "pairs": [{"pair_id": "P99", "sensor_a": "ODD_A", "sensor_b": "ODD_B"}],
            }))
            run_engine(repo, {"forecast_candidates": [], "experiment_candidates": []}, context("2026-08-05T10:00:00Z"), catalog)
            registry = json.loads((repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json").read_text())
            self.assertEqual(registry["state_counts"]["WAITING_FOR_MAPPING"], 1)
            candidate = json.loads(next((repo / "research/experiment_lifecycle/candidates").rglob("*.json")).read_text())
            self.assertFalse(candidate["dormancy_policy"]["automatic_age_expiry"])
            self.assertEqual(len(list((repo / "research/framework_memory/forecast_memory").rglob("*.json"))), 0)

    def test_semantic_candidate_dedup_ignores_changing_evidence_text(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            base = {
                "kind": "SENSOR_COMBINATION",
                "title": "Breadth plus ETH relative strength",
                "hypothesis": "The conjunction may improve rotation discrimination.",
                "falsifier": "It fails to beat the strongest single component after sufficient independent windows.",
                "horizon_days": 7,
                "components": [
                    {"metric_path": "breadth.advancers", "operator": "GT", "threshold": 50},
                    {"metric_path": "spot.ETHBTC.close", "operator": "GT", "threshold": 0.029},
                ],
                "target_metric_path": "spot.BTCUSDT.close",
                "target_direction": "UP",
                "target_threshold_pct": 1.0,
                "regime_dependency": "ROTATION_WATCH",
                "novelty_reason": "PAIR_DISCOVERY",
                "revisit_conditions": ["Both metrics available"],
            }
            first = dict(base, evidence_basis=["first numeric print"])
            second = dict(base, evidence_basis=["later numeric print"])
            run_engine(repo, {"forecast_candidates": [], "experiment_candidates": [first]}, context("2026-08-05T10:00:00Z", "run-1"))
            run_engine(repo, {"forecast_candidates": [], "experiment_candidates": [second]}, context("2026-08-05T14:00:00Z", "run-2"))
            candidates = list((repo / "research/experiment_lifecycle/candidates").rglob("*.json"))
            self.assertEqual(len(candidates), 1)
            observations = list((repo / "research/experiment_lifecycle/observations").rglob("*.json"))
            self.assertEqual(len(observations), 2)

    def test_same_capture_forecasts_share_event_window_and_frozen_controls(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {
                "forecast_candidates": [
                    {
                        "metric_path": "spot.BTCUSDT.close", "direction": "UP", "threshold": 1.0,
                        "range_low": None, "range_high": None, "horizon_days": 7, "rationale": "BTC candidate",
                    },
                    {
                        "metric_path": "spot.ETHUSDT.close", "direction": "UP", "threshold": 1.5,
                        "range_low": None, "range_high": None, "horizon_days": 7, "rationale": "ETH candidate",
                    },
                ],
                "experiment_candidates": [],
            }
            run_engine(repo, output, context("2026-08-05T10:00:00Z", "run-shared"))
            forecasts = [json.loads(path.read_text()) for path in (repo / "research/framework_memory/forecast_memory").rglob("*.json")]
            self.assertEqual(len(forecasts), 2)
            self.assertEqual(len({row["causal_event_window_id"] for row in forecasts}), 1)
            self.assertEqual(len({row["controls"]["deterministic_placebo_direction"] for row in forecasts}), 1)
            for row in forecasts:
                self.assertEqual(row["controls"]["control_freeze_time_utc"], "2026-08-05T10:00:00Z")
                self.assertEqual(row["controls"]["always_wait"], "ALWAYS_WAIT")


if __name__ == "__main__":
    unittest.main()
