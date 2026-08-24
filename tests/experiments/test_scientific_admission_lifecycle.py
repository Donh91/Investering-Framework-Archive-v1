import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "experiments" / "experiment_lifecycle_scientific_admission.py"


def context(captured="2026-08-23T20:00:00Z"):
    return {
        "latest_capture": {
            "captured_at_utc": captured,
            "run_id": "admission-test-run",
            "market_metrics": {
                "spot": {"BTCUSDT": {"close": 64000.0}, "ETHBTC": {"close": 0.0302}},
                "breadth": {"advancers": 60},
            },
        },
        "previous_capture": {
            "captured_at_utc": "2026-08-23T16:00:00Z",
            "market_metrics": {
                "spot": {"BTCUSDT": {"close": 63000.0}, "ETHBTC": {"close": 0.0298}},
                "breadth": {"advancers": 52},
            },
        },
        "metric_deltas": [],
    }


def pair(title, first_path="breadth.advancers"):
    return {
        "kind": "SENSOR_COMBINATION",
        "title": title,
        "hypothesis": "The pair may add forward information beyond either component alone.",
        "falsifier": "It fails to beat the strongest single component on prospective independent windows.",
        "horizon_days": 7,
        "components": [
            {"metric_path": first_path, "operator": "GT", "threshold": 55},
            {"metric_path": "spot.ETHBTC.close", "operator": "GT", "threshold": 0.03},
        ],
        "target_metric_path": "spot.BTCUSDT.close",
        "target_direction": "UP",
        "target_threshold_pct": 1.0,
        "target_unit_contract_version": "FORECAST_TARGET_UNITS_v2",
        "regime_dependency": "ROTATION_WATCH",
        "novelty_reason": "ADMISSION_TEST",
        "revisit_conditions": [],
        "evidence_basis": [],
    }


def run(repo: Path, output: dict):
    daily = repo / "daily"
    daily.mkdir(parents=True, exist_ok=True)
    (daily / "output.json").write_text(json.dumps(output))
    (daily / "context.json").write_text(json.dumps(context()))
    (daily / "receipt.json").write_text(json.dumps({"contract": "API_AGENT_RECEIPT_v3"}))
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
        "--admission-root", str(repo / "research/experiment_lifecycle/admission"),
        "--admission-registry-output", str(repo / "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"),
    ]
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


class ScientificAdmissionLifecycleTest(unittest.TestCase):
    def test_semantic_duplicate_is_kept_shadow_and_does_not_receive_forward_execution(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            summary = run(repo, {"forecast_candidates": [], "experiment_candidates": [pair("Pair A"), pair("Pair B")]})
            self.assertEqual(summary["new_candidate_count"], 2)
            self.assertEqual(summary["new_forecasts"], 1)
            admissions = json.loads((repo / "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json").read_text())
            self.assertEqual(admissions["status_counts"]["QUALIFIED_FOR_FORWARD_TEST"], 1)
            self.assertEqual(admissions["status_counts"]["SEMANTIC_DUPLICATE_KEEP_SHADOW"], 1)
            manifest = json.loads((repo / "research/experiment_lifecycle/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json").read_text())
            self.assertEqual(manifest["contract"], "EXPERIMENT_DISPATCH_MANIFEST_v2_SCIENTIFIC_ADMISSION")
            self.assertTrue(all(row["candidate_id"] for row in manifest["requests"]))

    def test_historical_candidate_requalification_is_non_retroactive(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, {"forecast_candidates": [], "experiment_candidates": [pair("Original")]})
            admission_path = next((repo / "research/experiment_lifecycle/admission").rglob("*.json"))
            admission = json.loads(admission_path.read_text())
            self.assertFalse(admission["historical_candidate_requalification"])
            self.assertTrue(admission["no_retroactive_rescore"])
            self.assertFalse(admission["authority"]["canonical_effect"])


if __name__ == "__main__":
    unittest.main()
