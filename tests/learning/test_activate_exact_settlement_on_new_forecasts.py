from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "learning" / "activate_exact_settlement_on_new_forecasts.py"


class ProspectiveSettlementActivationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=self.repo, check=True)
        self.root = self.repo / "research/framework_memory/forecast_memory/2026/09"
        self.root.mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)

    def forecast(self, forecast_id: str, metric: str, **overrides):
        value = {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": forecast_id,
            "scientific_admission_status": "QUALIFIED_FOR_FORWARD_TEST",
            "metric_path": metric,
            "frozen_at_utc": "2026-09-02T10:00:00Z",
            "outcome_due_utc": "2026-09-03T10:00:00Z",
        }
        value.update(overrides)
        return value

    def write(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, sort_keys=True) + "\n")
        return path

    def run_script(self):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(self.repo), "--forecast-root", str(self.repo / "research/framework_memory/forecast_memory")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_supported_untracked_forecast_is_activated_before_first_persistence(self):
        path = self.write("new.json", self.forecast("new", "market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price"))
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(path.read_text())
        self.assertEqual(value["settlement_contract_version"], "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1")
        self.assertEqual(value["settlement_activation_semantics"], "PRE_FIRST_CANONICAL_PERSISTENCE_UNTRACKED_FORECAST_ONLY")
        summary = json.loads(result.stdout)
        self.assertEqual(summary["counts"]["ACTIVATED_EXACT_SETTLEMENT"], 1)
        self.assertEqual(summary["historical_tracked_forecasts_modified"], 0)

    def test_historical_tracked_forecast_is_byte_identical(self):
        path = self.write("historical.json", self.forecast("historical", "market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price"))
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.repo, check=True)
        before = path.read_bytes()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assertNotIn("settlement_contract_version", json.loads(path.read_text()))
        self.assertEqual(json.loads(result.stdout)["untracked_forecast_files_scanned"], 0)

    def test_untracked_unsupported_metric_is_left_untouched(self):
        path = self.write("macro.json", self.forecast("macro", "market_metrics.macro.VIXCLS.value"))
        before = path.read_bytes()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(json.loads(result.stdout)["counts"]["SKIPPED_UNSUPPORTED_METRIC"], 1)

    def test_unadmitted_price_forecast_is_left_untouched(self):
        path = self.write(
            "blocked.json",
            self.forecast(
                "blocked",
                "market_metrics.derivatives.ETH-USDT-SWAP.mark_price.mark_price",
                scientific_admission_status="SCIENTIFIC_ADMISSION_BLOCKED",
            ),
        )
        before = path.read_bytes()
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(json.loads(result.stdout)["counts"]["SKIPPED_NOT_SCIENTIFICALLY_ADMITTED"], 1)

    def test_conflicting_untracked_settlement_contract_fails_closed(self):
        self.write(
            "conflict.json",
            self.forecast(
                "conflict",
                "spot.BTCUSDT.close",
                settlement_contract_version="SOME_OTHER_SETTLEMENT_CONTRACT",
            ),
        )
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SETTLEMENT_CONTRACT_CONFLICT", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
