from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "tools/backtest_readiness"
sys.path.insert(0, str(MODULE_DIR))

import validate_contracts as validator  # noqa: E402


class BacktestContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = validator.load_json(validator.OWNER_PATH)
        cls.gate = validator.load_json(validator.GATE_PATH)
        cls.matrix = validator.load_json(validator.MATRIX_PATH)
        cls.fixtures = validator.load_json(validator.FIXTURE_PATH)

    def test_frozen_contracts_pass(self) -> None:
        result = validator.run_validation()
        self.assertTrue(result.ok, result.errors)

    def test_duplicate_dataset_id_fails(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["datasets"].append(copy.deepcopy(registry["datasets"][0]))
        result = validator.validate_owner_registry(registry)
        self.assertFalse(result.ok)
        self.assertTrue(any("dataset_ids contains duplicates" in error for error in result.errors))

    def test_derived_dataset_cannot_score_direct_gate(self) -> None:
        registry = copy.deepcopy(self.registry)
        target = next(row for row in registry["datasets"] if row["dataset_id"] == "ETHBTC_OKX_DERIVED_DAILY")
        target["allowed_tests"].append("BT04_DIRECT_GATE")
        result = validator.validate_owner_registry(registry)
        self.assertFalse(result.ok)
        self.assertTrue(any("derived dataset allowed in direct gate" in error for error in result.errors))

    def test_unknown_package_reference_fails(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["datasets"][0]["source_package"] = "NON_EXISTENT_PACKAGE"
        result = validator.validate_owner_registry(registry)
        self.assertFalse(result.ok)
        self.assertTrue(any("unknown source_package" in error for error in result.errors))

    def test_economic_execution_lock_is_required(self) -> None:
        gate = copy.deepcopy(self.gate)
        gate["execution_policy"]["economic_backtest_allowed"] = True
        result = validator.validate_gate(gate)
        self.assertFalse(result.ok)
        self.assertIn("economic_backtest_allowed must remain false", result.errors)

    def test_g20_must_remain_no(self) -> None:
        gate = copy.deepcopy(self.gate)
        row = next(item for item in gate["mandatory_gates"] if item["gate"].startswith("G20_"))
        row["status"] = "YES"
        result = validator.validate_gate(gate)
        self.assertFalse(result.ok)
        self.assertIn("G20 must remain NO until artifact-backed approval", result.errors)

    def test_primary_endpoint_is_mandatory(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["families"]["ENGINEERING"][0].pop("primary_endpoint")
        result = validator.validate_matrix(matrix)
        self.assertFalse(result.ok)
        self.assertTrue(any("missing primary_endpoint" in error for error in result.errors))

    def test_temporal_fixture_expectations_pass(self) -> None:
        result = validator.validate_temporal_fixtures(self.fixtures)
        self.assertTrue(result.ok, result.errors)

    def test_invalid_temporal_expectation_is_detected(self) -> None:
        fixtures = copy.deepcopy(self.fixtures)
        case = next(item for item in fixtures["cases"] if item["case_id"] == "INVALID_ETF_USED_BEFORE_PUBLICATION")
        case["expected_valid"] = True
        result = validator.validate_temporal_fixtures(fixtures)
        self.assertFalse(result.ok)
        self.assertTrue(any("INVALID_ETF_USED_BEFORE_PUBLICATION" in error for error in result.errors))

    def test_all_test_ids_are_unique(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["families"]["ENGINEERING"].append(copy.deepcopy(matrix["families"]["ENGINEERING"][0]))
        result = validator.validate_matrix(matrix)
        self.assertFalse(result.ok)
        self.assertTrue(any("test_ids contains duplicates" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
