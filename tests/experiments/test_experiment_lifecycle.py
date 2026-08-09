import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parents[2]
SCRIPT = REPO_ROOT / "scripts" / "experiments" / "experiment_lifecycle.py"
OUTCOME_SCRIPT = REPO_ROOT / "scripts" / "learning" / "outcome_maturation_engine.py"


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


def candidate(**values):
    base = {
        "metric_path": "spot.BTCUSDT.close",
        "direction": "UP",
        "target_unit": "PERCENT_MOVE",
        "target_value": None,
        "threshold_pct": 2.0,
        "range_low": None,
        "range_high": None,
        "range_lower_pct": None,
        "range_upper_pct": None,
        "horizon_days": 7,
        "rationale": "Prospective test",
    }
    base.update(values)
    return base


class ExperimentLifecycleTest(unittest.TestCase):
    def _one_frozen(self, repo: Path) -> dict:
        return json.loads(next((repo / "research/framework_memory/forecast_memory").rglob("*.json")).read_text())

    def test_percentage_btc_target_is_frozen_as_v2(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            summary = run_engine(repo, {"forecast_candidates": [candidate()], "experiment_candidates": []}, context("2026-08-05T10:00:00Z"))
            self.assertEqual(summary["new_forecasts"], 1)
            frozen = self._one_frozen(repo)
            self.assertEqual(frozen["contract"], "FROZEN_FORECAST_v2")
            self.assertEqual(frozen["unit_contract"], "FORECAST_TARGET_UNIT_CONTRACT_v2")
            self.assertEqual(frozen["target_unit"], "PERCENT_MOVE")
            self.assertEqual(frozen["threshold_pct"], 2.0)
            self.assertTrue(frozen["experimental_only"])
            self.assertFalse(frozen["authority"]["portfolio_action"])

    def test_absolute_btc_target_normalizes_without_unit_confusion(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            c = candidate(direction="DOWN", target_unit="ABSOLUTE_VALUE", target_value=63000.0, threshold_pct=None)
            summary = run_engine(repo, {"forecast_candidates": [c], "experiment_candidates": []}, context("2026-08-05T10:00:00Z"))
            self.assertEqual(summary["new_forecasts"], 1)
            frozen = self._one_frozen(repo)
            self.assertEqual(frozen["target_unit"], "ABSOLUTE_VALUE")
            self.assertEqual(frozen["target_value"], 63000.0)
            self.assertAlmostEqual(frozen["threshold_pct"], 1.5625, places=8)

    def test_absolute_breadth_target_normalizes(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            c = candidate(
                metric_path="breadth.decliners", direction="UP", target_unit="ABSOLUTE_VALUE",
                target_value=58.0, threshold_pct=None, horizon_days=1,
            )
            summary = run_engine(repo, {"forecast_candidates": [c], "experiment_candidates": []}, context("2026-08-05T10:00:00Z"))
            self.assertEqual(summary["new_forecasts"], 1)
            frozen = self._one_frozen(repo)
            self.assertEqual(frozen["start_value"], 30.0)
            self.assertEqual(frozen["target_value"], 58.0)
            self.assertAlmostEqual(frozen["threshold_pct"], (58 / 30 - 1) * 100, places=8)

    def test_absolute_range_target_is_explicit_and_normalized(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            c = candidate(
                direction="RANGE", target_unit="ABSOLUTE_RANGE", target_value=None, threshold_pct=None,
                range_low=62000.0, range_high=66000.0,
            )
            summary = run_engine(repo, {"forecast_candidates": [c], "experiment_candidates": []}, context("2026-08-05T10:00:00Z"))
            self.assertEqual(summary["new_forecasts"], 1)
            frozen = self._one_frozen(repo)
            self.assertEqual(frozen["target_unit"], "ABSOLUTE_RANGE")
            self.assertEqual(frozen["range_low"], 62000.0)
            self.assertEqual(frozen["range_high"], 66000.0)
            self.assertAlmostEqual(frozen["range_lower_pct"], -3.125, places=8)
            self.assertAlmostEqual(frozen["range_upper_pct"], 3.125, places=8)

    def test_ambiguous_legacy_threshold_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            legacy = {
                "metric_path": "spot.BTCUSDT.close", "direction": "DOWN", "threshold": 63000.0,
                "range_low": None, "range_high": None, "horizon_days": 7, "rationale": "ambiguous",
            }
            summary = run_engine(repo, {"forecast_candidates": [legacy], "experiment_candidates": []}, context("2026-08-05T10:00:00Z"))
            self.assertEqual(summary["new_forecasts"], 0)
            self.assertEqual(len(list((repo / "research/framework_memory/forecast_memory").rglob("*.json"))), 0)

    def test_absolute_target_direction_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            c = candidate(direction="DOWN", target_unit="ABSOLUTE_VALUE", target_value=65000.0, threshold_pct=None)
            summary = run_engine(repo, {"forecast_candidates": [c], "experiment_candidates": []}, context("2026-08-05T10:00:00Z"))
            self.assertEqual(summary["new_forecasts"], 0)

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
            candidate_row = json.loads(next((repo / "research/experiment_lifecycle/candidates").rglob("*.json")).read_text())
            self.assertFalse(candidate_row["dormancy_policy"]["automatic_age_expiry"])

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
            run_engine(repo, {"forecast_candidates": [], "experiment_candidates": [dict(base, evidence_basis=["first numeric print"])]}, context("2026-08-05T10:00:00Z", "run-1"))
            run_engine(repo, {"forecast_candidates": [], "experiment_candidates": [dict(base, evidence_basis=["later numeric print"])]}, context("2026-08-05T14:00:00Z", "run-2"))
            self.assertEqual(len(list((repo / "research/experiment_lifecycle/candidates").rglob("*.json"))), 1)
            self.assertEqual(len(list((repo / "research/experiment_lifecycle/observations").rglob("*.json"))), 2)

    def test_same_capture_forecasts_share_event_window_and_frozen_controls(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {
                "forecast_candidates": [
                    candidate(metric_path="spot.BTCUSDT.close", threshold_pct=1.0, rationale="BTC candidate"),
                    candidate(metric_path="spot.ETHUSDT.close", threshold_pct=1.5, rationale="ETH candidate"),
                ],
                "experiment_candidates": [],
            }
            run_engine(repo, output, context("2026-08-05T10:00:00Z", "run-shared"))
            forecasts = [json.loads(path.read_text()) for path in (repo / "research/framework_memory/forecast_memory").rglob("*.json")]
            self.assertEqual(len(forecasts), 2)
            self.assertEqual(len({row["causal_event_window_id"] for row in forecasts}), 1)
            self.assertEqual(len({row["controls"]["deterministic_placebo_direction"] for row in forecasts}), 1)


class OutcomeQuarantineTest(unittest.TestCase):
    def test_quarantined_v1_is_not_rescored_or_rewritten(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            forecast_root = repo / "research/framework_memory/forecast_memory/2026/08"
            outcome_root = repo / "research/framework_memory/outcome_memory"
            evidence_root = repo / "evidence"
            remediation = repo / "research/framework_memory/remediation"
            forecast_root.mkdir(parents=True)
            outcome_root.mkdir(parents=True)
            evidence_root.mkdir(parents=True)
            remediation.mkdir(parents=True)

            frozen = {
                "contract": "FROZEN_FORECAST_v1", "forecast_id": "legacy-bad", "frozen_at_utc": "2026-08-01T00:00:00Z",
                "outcome_due_utc": "2026-08-02T00:00:00Z", "metric_path": "spot.BTCUSDT.close", "direction": "DOWN",
                "start_value": 65000.0, "threshold_pct": 64699.1,
            }
            (forecast_root / "legacy-bad.json").write_text(json.dumps(frozen))
            quarantine = {
                "contract": "R0_DIRECTIONAL_UNIT_QUARANTINE_v1",
                "affected_forecasts": [{"forecast_id": "legacy-bad"}],
            }
            (remediation / "R0_DIRECTIONAL_UNIT_QUARANTINE_v1.json").write_text(json.dumps(quarantine))
            ev = {"captured_at_utc": "2026-08-02T00:00:00Z", "spot": {"BTCUSDT": {"close": 60000.0}}}
            (evidence_root / "ev.json").write_text(json.dumps(ev))

            cmd = [
                sys.executable, str(OUTCOME_SCRIPT), "--forecast-root", str(repo / "research/framework_memory/forecast_memory"),
                "--evidence-root", str(evidence_root), "--output-root", str(outcome_root), "--now-utc", "2026-08-03T00:00:00Z",
            ]
            summary = json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)
            self.assertEqual(summary["quarantined"], 1)
            self.assertFalse((outcome_root / "legacy-bad.json").exists())


if __name__ == "__main__":
    unittest.main()
