from __future__ import annotations

import unittest

from backtest_engine.authority import validate_direct_challenger, validate_owner_registry
from backtest_engine.lineage_recovery import retrospective_policy_quarantine, validate_prospective_receipt

CONTRACT = {
    "minimum_overlap_sessions": 30,
    "median_abs_close_dev_bps_max": 5.0,
    "p95_abs_close_dev_bps_max": 20.0,
    "max_abs_close_dev_bps_max": 75.0,
    "gate_agreement_rate_min": 0.99,
}


class AuthorityTests(unittest.TestCase):
    def test_coinbase_passes(self) -> None:
        metrics = {
            "overlap_rows": 90,
            "median_abs_close_dev_bps": 1.954168,
            "p95_abs_close_dev_bps": 8.509676,
            "max_abs_close_dev_bps": 12.671977,
            "gate_agreement_rate_0_0275": 1.0,
            "gate_agreement_rate_0_0300": 1.0,
        }
        self.assertEqual(validate_direct_challenger(metrics, CONTRACT)["status"], "PASS")

    def test_kraken_fails_one_gate(self) -> None:
        metrics = {
            "overlap_rows": 90,
            "median_abs_close_dev_bps": 2.592025,
            "p95_abs_close_dev_bps": 8.301702,
            "max_abs_close_dev_bps": 11.228070,
            "gate_agreement_rate_0_0275": 0.988889,
            "gate_agreement_rate_0_0300": 1.0,
        }
        result = validate_direct_challenger(metrics, CONTRACT)
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["checks"]["gate_0_0275"])

    def test_registry_requires_derived_diagnostic(self) -> None:
        registry = {
            "rules": {"missing_is_not_zero": True, "derived_cannot_score_direct_gate": True},
            "families": {"ETHBTC_DIRECT": {"owner": "BINANCE", "diagnostic_only": []}},
        }
        self.assertTrue(validate_owner_registry(registry))


class LineageTests(unittest.TestCase):
    def test_fnp_is_retrospective(self) -> None:
        self.assertTrue(
            retrospective_policy_quarantine(
                "2026-05-25T23:59:59Z",
                "2026-06-13T11:03:08Z",
            )
        )

    def test_valid_no_action_receipt(self) -> None:
        row = {
            "event_id": "X",
            "policy_family": "REBUY",
            "rule_version": "V1",
            "knowledge_at_utc": "2026-01-01T00:00:00Z",
            "decision_at_utc": "2026-01-01T00:01:00Z",
            "execution_at_utc": "2026-01-01T00:01:00Z",
            "label_end_utc": "2026-01-02T00:00:00Z",
            "action_permission": "NONE",
            "no_action_reason": "gate unmet",
            "source_hashes": ["abc"],
            "transaction_cost_contract": "ZERO_NO_TRADE",
        }
        self.assertEqual(validate_prospective_receipt(row), [])

    def test_no_action_requires_reason(self) -> None:
        row = {
            "event_id": "X",
            "policy_family": "REBUY",
            "rule_version": "V1",
            "knowledge_at_utc": "2026-01-01T00:00:00Z",
            "decision_at_utc": "2026-01-01T00:01:00Z",
            "execution_at_utc": "2026-01-01T00:01:00Z",
            "label_end_utc": "2026-01-02T00:00:00Z",
            "action_permission": "NONE",
            "source_hashes": ["abc"],
            "transaction_cost_contract": "ZERO_NO_TRADE",
        }
        self.assertTrue(validate_prospective_receipt(row))


if __name__ == "__main__":
    unittest.main()
