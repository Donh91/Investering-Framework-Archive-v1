from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.api_agent.forward_evidence_observer import mature as mature_t2
from scripts.api_agent.forward_evidence_observer import observe as observe_t2
from scripts.learning.fnp_cumulative_forward import (
    ATTACHMENT_CONTRACT,
    AUTHORITY,
    SOURCE_CONTRACT,
    attach_maturity,
    freeze_receipt,
    scan,
    source_row_from_t2,
    validate_source_row,
)


def base_check(**overrides):
    value = {
        "test_id": "GATE_BTC_PARTIAL_FT_1",
        "check_id": "CHECK-T5-001",
        "timestamp_utc": "2026-09-24T00:00:00Z",
        "source_run_id": "natural-owner-run-1",
        "source_hash": "a" * 64,
        "eligible_check": True,
        "missing_fields": [],
        "framework_state": "OWNER_FROZEN_STATE",
        "asset_tier": "BTC",
        "benchmark_action_WAIT": "WAIT",
        "experimental_action_BTC_PARTIAL": "BTC_PARTIAL",
        "experimental_action_GRADUATED": "DATA_BLOCKED_UNLESS_OWNER_FIELDS_COMPLETE",
        "actual_decision_divergence": True,
        "permission_reason": "EXISTING_OWNER_PERMISSION",
        "blocking_reason": "EXISTING_OWNER_LOCK",
        "required_data_complete": True,
        "entry_reference_price": 64000.0,
        "position_fraction_assumed": 0.25,
    }
    value.update(overrides)
    return value


def t2_divergence(**overrides):
    return observe_t2(base_check(**overrides))


def maturity_receipt(receipt):
    observations = [
        {
            "horizon": "24H",
            "observed_at_utc": "2026-09-25T00:00:00Z",
            "return_pct": 2.0,
            "max_favorable_excursion_pct": 3.0,
            "max_adverse_excursion_pct": -1.0,
            "benchmark_return_pct": 0.0,
            "source_hash": "b" * 64,
            "source_provider": "OWNER_MARKET_DATA",
            "data_quality": "VERIFIED",
        },
        {
            "horizon": "72H",
            "observed_at_utc": "2026-09-27T00:00:00Z",
            "return_pct": 4.0,
            "max_favorable_excursion_pct": 5.0,
            "max_adverse_excursion_pct": -1.5,
            "benchmark_return_pct": 0.0,
            "source_hash": "c" * 64,
            "source_provider": "OWNER_MARKET_DATA",
            "data_quality": "VERIFIED",
        },
        {
            "horizon": "7D",
            "observed_at_utc": "2026-10-01T00:00:00Z",
            "return_pct": 6.0,
            "max_favorable_excursion_pct": 8.0,
            "max_adverse_excursion_pct": -2.0,
            "benchmark_return_pct": 0.0,
            "source_hash": "d" * 64,
            "source_provider": "OWNER_MARKET_DATA",
            "data_quality": "VERIFIED",
        },
    ]
    return mature_t2(receipt, observations, "2026-10-01T00:00:00Z")


class FnpCumulativeForwardTests(unittest.TestCase):
    def test_eligible_t2_divergence_freezes_exactly_one_t5_source_row(self):
        receipt = t2_divergence()
        row = source_row_from_t2(receipt)
        self.assertEqual(row["contract"], SOURCE_CONTRACT)
        self.assertEqual(row["test_id"], "FNP_CUMULATIVE")
        self.assertEqual(row["asset_tier"], "BTC")
        self.assertEqual(row["blocked_action"], "BTC_PARTIAL")
        self.assertEqual(row["benchmark_action"], "WAIT")
        self.assertEqual(row["frozen_horizons"]["24H"], "2026-09-25T00:00:00Z")
        self.assertEqual(row["frozen_horizons"]["72H"], "2026-09-27T00:00:00Z")
        self.assertEqual(row["frozen_horizons"]["7D"], "2026-10-01T00:00:00Z")
        self.assertTrue(all(value is None for value in row["outcome_fields"].values()))
        self.assertEqual(row["outcome_evaluator_status"], "BLOCKED_AUTHORITATIVE_FNP_EVALUATOR_MISSING")
        self.assertEqual(row["authority"], AUTHORITY)
        validate_source_row(row)

    def test_replay_of_same_frozen_decision_is_duplicate_noop(self):
        receipt = t2_divergence()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = freeze_receipt(receipt, root)
            second = freeze_receipt(receipt, root)
            self.assertEqual(first["status"], "CREATED")
            self.assertEqual(second["status"], "DUPLICATE_NOOP")
            self.assertEqual(first["row_id"], second["row_id"])
            self.assertEqual(len(list((root / "source_rows").rglob("*.json"))), 1)

    def test_no_divergence_cannot_create_t5_row(self):
        receipt = observe_t2(base_check(experimental_action_BTC_PARTIAL="WAIT", actual_decision_divergence=False))
        with self.assertRaisesRegex(ValueError, "t2_divergence_captured_required"):
            source_row_from_t2(receipt)

    def test_missing_asset_tier_fails_closed(self):
        receipt = t2_divergence()
        receipt["divergence_source_row"]["asset_tier"] = ""
        with self.assertRaisesRegex(ValueError, "asset_tier_required"):
            source_row_from_t2(receipt)

    def test_mutated_t2_frozen_input_fails_closed(self):
        receipt = t2_divergence()
        receipt["divergence_source_row"]["entry_reference_price"] = 1.0
        with self.assertRaisesRegex(ValueError, "t2_frozen_input_hash_invalid"):
            source_row_from_t2(receipt)

    def test_pre_activation_t2_divergence_is_not_backfilled(self):
        old = observe_t2(base_check(timestamp_utc="2026-09-23T23:51:00Z"))
        with self.assertRaisesRegex(ValueError, "retrospective_row_backfill_forbidden"):
            source_row_from_t2(old)

    def test_maturity_attachment_binds_frozen_horizons_but_does_not_invent_fnp_metrics(self):
        receipt = t2_divergence()
        t2_maturity = maturity_receipt(receipt)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_result = freeze_receipt(receipt, root)
            source = json.loads(Path(source_result["path"]).read_text())
            result = attach_maturity(source, t2_maturity, root)
            attachment = json.loads(Path(result["path"]).read_text())
        self.assertEqual(attachment["contract"], ATTACHMENT_CONTRACT)
        self.assertTrue(attachment["maturity_complete"])
        self.assertEqual(set(attachment["raw_evaluator_inputs_by_frozen_horizon"]), {"24H", "72H", "7D"})
        self.assertTrue(all(value is None for value in attachment["derived_fnp_metrics"].values()))
        self.assertEqual(attachment["evaluation_status"], "BLOCKED_AUTHORITATIVE_FNP_EVALUATOR_MISSING")
        self.assertFalse(attachment["counts_as_valid_outcome_row"])
        self.assertFalse(attachment["retrospective_horizon_selection"])
        self.assertEqual(attachment["authority"], AUTHORITY)

    def test_wrong_maturity_lineage_fails_closed(self):
        receipt = t2_divergence()
        t2_maturity = maturity_receipt(receipt)
        t2_maturity["frozen_input_sha256"] = "e" * 64
        row = source_row_from_t2(receipt)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "maturity_frozen_input_mismatch"):
                attach_maturity(row, t2_maturity, Path(tmp))

    def test_scan_with_missing_upstream_roots_creates_only_run_receipt_and_no_source_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = scan(
                root / "missing-coverage",
                root / "missing-maturity",
                root / "t5",
                "natural-run-1",
                "2026-09-24T01:00:00Z",
            )
            self.assertEqual(result["status"], "PASS_NO_ELIGIBLE_INPUT")
            self.assertEqual(result["source_rows_created"], 0)
            self.assertEqual(result["current_source_row_count"], 0)
            self.assertEqual(result["invalid_input_count"], 0)
            self.assertFalse(result["derived_fnp_metrics_emitted"])
            self.assertFalse(result["retrospective_backfill_performed"])
            self.assertEqual(len(list((root / "t5" / "source_rows").rglob("*.json"))), 0)
            self.assertEqual(len(list((root / "t5" / "runs").glob("*.json"))), 1)

    def test_source_and_attachment_builders_do_not_mutate_inputs(self):
        receipt = t2_divergence()
        receipt_before = copy.deepcopy(receipt)
        row = source_row_from_t2(receipt)
        self.assertEqual(receipt, receipt_before)
        t2_maturity = maturity_receipt(receipt)
        maturity_before = copy.deepcopy(t2_maturity)
        with tempfile.TemporaryDirectory() as tmp:
            attach_maturity(row, t2_maturity, Path(tmp))
        self.assertEqual(t2_maturity, maturity_before)


if __name__ == "__main__":
    unittest.main()
