from __future__ import annotations

import unittest

from scripts.experiments.sensor_relationship_compression import (
    RELATIONSHIP_CLASSES,
    build_readout,
    prospective_row,
)


AUDIT = """
Historical overlap:
- 2,886 aligned daily rows
- 124 relative-strength sequence episodes
ETH/BTC 20-day momentum versus ETH/BTC 14-day volatility
Spearman correlation: approximately 0.10
Distance correlation: approximately 0.41
estimate stable across eight subsamples
BTC 20-day momentum
ETH relative participation proxy
achieved temporal cross-validation AUC around 0.72 for seven-day sequence survival.
However, performance weakened in the 2022-2024 subperiod.
"""


class SensorRelationshipCompressionTests(unittest.TestCase):
    def test_semantic_duplicate_is_redundant_audit_only(self) -> None:
        row = prospective_row({
            "candidate_id": "EC-dup",
            "title": "Legacy sensor pair P01",
            "kind": "SENSOR_COMBINATION",
            "state": "WAITING_FOR_MAPPING",
            "scientific_admission_status": "SEMANTIC_DUPLICATE_KEEP_SHADOW",
            "observation_count": 2,
            "matured_outcome_count": 0,
            "semantic_fingerprint": "abc",
        })
        self.assertEqual(row["relationship_classes"], ["REDUNDANT"])
        self.assertEqual(row["presentation_role"], "AUDIT_ONLY")
        self.assertFalse(row["current_prospective_validation"])

    def test_data_waiting_pair_fails_closed(self) -> None:
        row = prospective_row({
            "candidate_id": "EC-wait",
            "title": "Emergent pair",
            "kind": "SENSOR_COMBINATION",
            "state": "WAITING_FOR_DATA",
            "scientific_admission_status": "QUALIFIED_FOR_FORWARD_TEST",
            "observation_count": 100,
            "matured_outcome_count": 0,
        })
        self.assertEqual(row["relationship_classes"], ["DATA_BLOCKED"])
        self.assertEqual(row["presentation_role"], "DATA_BLOCKED")

    def test_unmapped_prospective_pair_is_not_inferred_unique(self) -> None:
        row = prospective_row({
            "candidate_id": "EC-low-linear-correlation",
            "title": "Low Pearson pair",
            "kind": "SENSOR_COMBINATION",
            "state": "MATURED_INCONCLUSIVE",
            "scientific_admission_status": "QUALIFIED_FOR_FORWARD_TEST",
            "observation_count": 146,
            "matured_outcome_count": 1,
            "pearson": 0.01,
            "spearman": 0.02,
        })
        self.assertEqual(row["relationship_classes"], [])
        self.assertEqual(row["presentation_role"], "UNRESOLVED")
        self.assertNotIn("UNIQUE", row["relationship_classes"])

    def test_historical_proxy_is_not_current_prospective_validation(self) -> None:
        readout = build_readout({"generated_at_utc": "2026-09-23T00:00:00Z", "candidates": []}, AUDIT)
        self.assertEqual(len(readout["historical_rows"]), 2)
        nonlinear = next(row for row in readout["historical_rows"] if row["relationship_id"] == "HIST_ETHBTC_MOMENTUM_VOLATILITY")
        self.assertEqual(nonlinear["relationship_classes"], ["NONLINEARLY_DEPENDENT"])
        self.assertFalse(nonlinear["current_prospective_validation"])
        self.assertEqual(nonlinear["presentation_role"], "AUDIT_ONLY")

    def test_semantic_fingerprint_duplicates_are_count_once_flags_only(self) -> None:
        registry = {
            "generated_at_utc": "2026-09-23T00:00:00Z",
            "candidates": [
                {"candidate_id": "EC-a", "title": "A", "kind": "SENSOR_COMBINATION", "state": "WAITING_FOR_MAPPING", "scientific_admission_status": "SEMANTIC_DUPLICATE_KEEP_SHADOW", "semantic_fingerprint": "same"},
                {"candidate_id": "EC-b", "title": "B", "kind": "SENSOR_COMBINATION", "state": "WAITING_FOR_MAPPING", "scientific_admission_status": "SEMANTIC_DUPLICATE_KEEP_SHADOW", "semantic_fingerprint": "same"},
            ],
        }
        readout = build_readout(registry, AUDIT)
        self.assertEqual(readout["semantic_duplicate_groups"], [{
            "semantic_fingerprint": "same",
            "candidate_ids": ["EC-a", "EC-b"],
            "presentation_rule": "COUNT_ONCE_MAXIMUM",
        }])
        self.assertFalse(readout["rules"]["aligned_sensor_count_adds_conviction"])

    def test_readout_changes_no_authority_or_weights(self) -> None:
        registry = {"generated_at_utc": "2026-09-23T00:00:00Z", "candidates": []}
        readout = build_readout(registry, AUDIT)
        authority = readout["authority"]
        self.assertTrue(authority["research_only"])
        for key in (
            "binding",
            "canonical_market_state",
            "market_gate_change",
            "model_weight_change",
            "portfolio_action",
            "automatic_sensor_promotion",
            "automatic_sensor_retirement",
        ):
            self.assertFalse(authority[key])
        self.assertFalse(readout["rules"]["presentation_roles_are_weights"])
        for row in readout["historical_rows"] + readout["prospective_rows"]:
            self.assertTrue(set(row["relationship_classes"]).issubset(RELATIONSHIP_CLASSES))
            self.assertNotIn("weight", row)
            self.assertNotIn("score", row)


if __name__ == "__main__":
    unittest.main()
