from __future__ import annotations

import unittest

from backtest_engine.graphs import latest_upstream_knowledge, temporal_dependency_violations, topological_order, validate_provenance_graph
from backtest_engine.ledgers import CounterfactualDeploymentRow, DecisionLineageRepairRow, DecisionLineageRow, validate_decision_lineage, validate_repair_ledger
from backtest_engine.rotation import RotationEvidence, classify_rotation
from backtest_engine.sensors import SensorDefinition, cluster_aware_evidence_count, validate_sensor_registry
from backtest_engine.statistics import benjamini_hochberg, cluster_bootstrap_mean_ci, connected_interval_clusters, empirical_coverage, entropy_effective_rank, interval_score, leave_one_out_means, mean_interval_width, moving_block_bootstrap_indices, participation_ratio, pinball_loss, purged_expanding_walk_forward, stationary_bootstrap_indices


class StatisticalFoundationTests(unittest.TestCase):
    def test_interval_and_pinball_scores(self) -> None:
        self.assertEqual(interval_score(5.0, 4.0, 6.0, 0.1), 2.0)
        self.assertEqual(interval_score(7.0, 4.0, 6.0, 0.1), 22.0)
        self.assertAlmostEqual(pinball_loss(7.0, 6.0, 0.9), 0.9)
        self.assertAlmostEqual(pinball_loss(5.0, 6.0, 0.9), 0.1)

    def test_coverage_and_width(self) -> None:
        observed = [1.0, 2.0, 4.0]
        lower = [0.0, 1.5, 2.0]
        upper = [2.0, 2.5, 3.0]
        self.assertAlmostEqual(empirical_coverage(observed, lower, upper), 2 / 3)
        self.assertAlmostEqual(mean_interval_width(lower, upper), 4 / 3)

    def test_effective_rank_definitions(self) -> None:
        self.assertAlmostEqual(participation_ratio([1.0, 1.0, 1.0, 1.0]), 4.0)
        self.assertAlmostEqual(entropy_effective_rank([1.0, 1.0, 1.0, 1.0]), 4.0)
        self.assertAlmostEqual(participation_ratio([4.0, 0.0, 0.0, 0.0]), 1.0)
        self.assertAlmostEqual(entropy_effective_rank([4.0, 0.0, 0.0, 0.0]), 1.0)

    def test_bootstraps_are_deterministic(self) -> None:
        self.assertEqual(moving_block_bootstrap_indices(12, 3, 4, 17), moving_block_bootstrap_indices(12, 3, 4, 17))
        self.assertEqual(stationary_bootstrap_indices(12, 4.0, 3, 23), stationary_bootstrap_indices(12, 4.0, 3, 23))

    def test_purged_walk_forward(self) -> None:
        splits = purged_expanding_walk_forward(30, 10, 5, purge=2, embargo=3)
        self.assertGreaterEqual(len(splits), 2)
        for split in splits:
            self.assertLess(max(split.train_indices), min(split.purged_indices))
            self.assertLess(max(split.purged_indices), min(split.test_indices))

    def test_benjamini_hochberg(self) -> None:
        result = benjamini_hochberg({"a": 0.001, "b": 0.01, "c": 0.2, "d": 0.8}, 0.05)
        self.assertTrue(result["a"]["rejected"])
        self.assertTrue(result["b"]["rejected"])
        self.assertFalse(result["c"]["rejected"])

    def test_leave_one_out_means(self) -> None:
        self.assertEqual(leave_one_out_means([1.0, 2.0, 3.0]), (2.5, 2.0, 1.5))

    def test_connected_interval_clusters(self) -> None:
        clusters = connected_interval_clusters([
            ("2026-01-01T00:00:00Z", "2026-01-10T00:00:00Z"),
            ("2026-01-05T00:00:00Z", "2026-01-15T00:00:00Z"),
            ("2026-02-01T00:00:00Z", "2026-02-05T00:00:00Z"),
        ])
        self.assertEqual(clusters, (1, 1, 2))

    def test_cluster_bootstrap(self) -> None:
        point, low, high = cluster_bootstrap_mean_ci({"a": [1.0, 3.0], "b": [5.0]}, 1000, 1)
        self.assertAlmostEqual(point, 3.5)
        self.assertLessEqual(low, point)
        self.assertGreaterEqual(high, point)


class GraphFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.nodes = {
            "source": {"node_type": "SOURCE", "authority_role": "OWNER", "knowledge_at_utc": "2026-07-27T10:00:00Z"},
            "feature": {"node_type": "FEATURE", "method_id": "FEATURE_V1"},
            "decision": {"node_type": "TEST", "method_id": "TEST_V1", "decision_at_utc": "2026-07-27T10:05:00Z"},
            "result": {"node_type": "RESULT", "method_id": "RESULT_V1"},
        }
        self.edges = [("source", "feature"), ("feature", "decision"), ("decision", "result")]

    def test_valid_provenance_graph(self) -> None:
        self.assertEqual(validate_provenance_graph(self.nodes, self.edges)["status"], "PASS")

    def test_cycle_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            topological_order(self.nodes, self.edges + [("result", "source")])

    def test_latest_knowledge_propagates(self) -> None:
        self.assertEqual(latest_upstream_knowledge(self.nodes, self.edges)["decision"], "2026-07-27T10:00:00Z")

    def test_post_decision_input_is_detected(self) -> None:
        nodes = dict(self.nodes)
        nodes["source"] = dict(nodes["source"])
        nodes["source"]["knowledge_at_utc"] = "2026-07-27T10:06:00Z"
        self.assertEqual(len(temporal_dependency_violations(nodes, self.edges)), 1)


class LedgerContractTests(unittest.TestCase):
    def test_legacy_full_point_in_time_row_passes(self) -> None:
        row = DecisionLineageRow("event-1", "STATE_CHANGE", "2026-07-27T10:00:00Z", "2026-07-27T10:01:00Z", "2026-07-27T10:02:00Z", "RULE_V1", ("artifact-1",), ("abc123",), "NO_ROTATION", "NO_ROTATION", "NONE", "FULL_POINT_IN_TIME")
        self.assertEqual(row.validate(), [])
        self.assertEqual(validate_decision_lineage([row])["bt10_eligible_rows"], 1)

    def test_repair_class_a_passes(self) -> None:
        row = DecisionLineageRepairRow("A-1", "POLICY_DECISION", "A_FULLY_REPLAYABLE", "2026-07-27T10:00:00Z", "EXACT", "2026-07-27T10:01:00Z", "EXACT", "2026-07-27T10:02:00Z", "2026-07-27T10:03:00Z", "2026-08-27T10:03:00Z", "POLICY_V1", "LOCKED", "OPEN", "PARTIAL", "10BP_ROUND_TRIP", ("artifact-1",), ("abc",), ())
        self.assertEqual(row.validate(), [])
        self.assertTrue(validate_repair_ledger([row])["actual_policy_replay_unlocked"])

    def test_partial_requires_missing_fields(self) -> None:
        row = DecisionLineageRepairRow("B-1", "POLICY_DECISION", "B_PARTIALLY_RECONSTRUCTABLE", None, "UNKNOWN", None, "UNKNOWN", None, None, None, None, None, None, None, None, ("artifact",), ("hash",), ("knowledge_at_utc",))
        self.assertEqual(row.validate(), [])

    def test_counterfactual_temporal_contract(self) -> None:
        row = CounterfactualDeploymentRow("flush-1", "DELAY_2D", "2026-07-27T10:00:00Z", "2026-07-27T10:05:00Z", "2026-07-29T10:05:00Z", "2026-08-27T10:05:00Z", 62000.0, 65000.0, 3000.0, 500.0, -0.04, 0.09, 0.02, 0.01, "NEGATIVE", ("hash1",))
        self.assertEqual(row.validate(), [])


class SensorRegistryTests(unittest.TestCase):
    def test_registry_and_cluster_count(self) -> None:
        rows = [
            SensorDefinition("ETHBTC_DIRECT", "RELATIVE_STRENGTH", "CORE_TRANSITION_SIGNAL", "PERMIT_AND_VETO", "CORE", True, "BINANCE_ETHBTC_SPOT", "FAIL_CLOSED", ("ETH_RELATIVE_STRENGTH",)),
            SensorDefinition("ETHBTC_DERIVED", "RELATIVE_STRENGTH", "DESCRIPTIVE_CONTEXT", "CONTEXT_ONLY", "RETAINED", False, None, "DIAGNOSTIC_ONLY", ("DIAGNOSTIC",)),
            SensorDefinition("BREADTH", "PARTICIPATION", "CONFIRMATION_VETO", "VETO_ONLY", "CORE", False, "BREADTH_V2", "FAIL_CLOSED_FOR_ROTATION", ("BROAD_ROTATION",)),
        ]
        report = validate_sensor_registry(rows)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["dependency_cluster_count"], 2)
        count = cluster_aware_evidence_count(["ETHBTC_DIRECT", "ETHBTC_DERIVED", "BREADTH"], {row.sensor_id: row for row in rows})
        self.assertEqual(count["raw_sensor_count"], 3)
        self.assertEqual(count["independent_cluster_count"], 2)


class RotationArchitectureTests(unittest.TestCase):
    def test_derived_ratio_cannot_score_gate(self) -> None:
        result = classify_rotation(RotationEvidence(False, "DERIVED_DIAGNOSTIC", 0.031, 5, 5, 0.8, 0.8, 0.1, -1.0, True, True))
        self.assertEqual(result["label"], "NO_SIGNAL")
        self.assertFalse(result["can_score_direct_gate"])

    def test_eth_strength_does_not_equal_broad_rotation(self) -> None:
        result = classify_rotation(RotationEvidence(True, "DIRECT_OWNER", 0.0305, 4, 3, 0.42, 0.30, -0.05, -0.2, False, True))
        self.assertEqual(result["label"], "ETH_RELATIVE_STRENGTH_CONFIRMED")
        self.assertFalse(result["canonical_rotation_permission"])

    def test_broad_rotation_requires_all_layers(self) -> None:
        result = classify_rotation(RotationEvidence(True, "DIRECT_CHALLENGER_APPROVED", 0.031, 5, 4, 0.60, 0.60, 0.03, -0.4, True, True))
        self.assertEqual(result["label"], "BROAD_ALT_ROTATION_CONFIRMED")
        self.assertTrue(result["canonical_rotation_permission"])


if __name__ == "__main__":
    unittest.main()
