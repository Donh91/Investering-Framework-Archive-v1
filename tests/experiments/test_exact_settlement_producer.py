from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / "scripts" / "experiments"
if str(EXPERIMENTS) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS))

import experiment_lifecycle_scientific_admission as module  # noqa: E402


class ExactSettlementProducerTests(unittest.TestCase):
    def forecast(self, metric: str, **overrides):
        value = {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": "ff-test",
            "metric_path": metric,
            "scientific_admission": {
                "contract": "EXPERIMENT_SCIENTIFIC_ADMISSION_v1",
                "status": "QUALIFIED_FOR_FORWARD_TEST",
                "record_sha256": "a" * 64,
            },
        }
        value.update(overrides)
        return value

    def test_supported_document_root_price_metric_is_frozen_exact(self):
        frozen = self.forecast("market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price")
        result = module.apply_exact_settlement_contract(frozen)
        self.assertIs(result, frozen)
        self.assertEqual(
            frozen["settlement_contract_version"],
            "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
        )
        self.assertEqual(
            frozen["settlement_activation_semantics"],
            "FROZEN_AT_CREATION_PROSPECTIVE_ONLY",
        )

    def test_supported_spot_metric_is_frozen_exact(self):
        frozen = self.forecast("market_metrics.spot.ETHBTC.close")
        module.apply_exact_settlement_contract(frozen)
        self.assertEqual(
            frozen["settlement_contract_version"],
            "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
        )

    def test_unsupported_metric_is_unchanged(self):
        frozen = self.forecast("market_metrics.macro.VIXCLS.value")
        before = dict(frozen)
        module.apply_exact_settlement_contract(frozen)
        self.assertEqual(frozen, before)
        self.assertNotIn("settlement_contract_version", frozen)

    def test_conflicting_contract_fails_closed(self):
        frozen = self.forecast(
            "market_metrics.derivatives.ETH-USDT-SWAP.mark_price.mark_price",
            settlement_contract_version="SOME_OTHER_CONTRACT",
        )
        with self.assertRaisesRegex(ValueError, "SETTLEMENT_CONTRACT_CONFLICT"):
            module.apply_exact_settlement_contract(frozen)

    def test_production_freeze_path_calls_helper(self):
        source = (ROOT / "scripts/experiments/experiment_lifecycle_scientific_admission.py").read_text()
        self.assertIn("apply_exact_settlement_contract(frozen)", source)
        self.assertLess(
            source.index("apply_exact_settlement_contract(frozen)"),
            source.index("base.write_new(args.forecast_root"),
        )


if __name__ == "__main__":
    unittest.main()
