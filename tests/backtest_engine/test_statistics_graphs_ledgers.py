from __future__ import annotations

import unittest

from backtest_engine.graphs import (
    latest_upstream_knowledge,
    temporal_dependency_violations,
    topological_order,
    validate_provenance_graph,
)
from backtest_engine.ledgers import (
    CounterfactualDeploymentRow,
    DecisionLineageRow,
    validate_decision_lineage,
)
from backtest_engine.statistics import (
    benjamini_hochberg,
    empirical_coverage,
    entropy_effective_rank,
    interval_score,
    leave_one_out_means,
    mean_interval_width,
    moving_block_bootstrap_indices,
    participation_ratio,
    pinball_loss,
    purged_expanding_walk_forward,
    stationary_bootstrap_indices,
)


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
        eigenvalues = [1.0, 1.0, 1.0, 1.0]
        self.assertAlmostEqual(participation_ratio(eigenvalues), 4.0)
        self.assertAlmostEqual(entropy_effective_rank(eigenvalues), 4.0)
        concentrated = [4.0, 0.0, 0.0, 0.0]
        self.assertAlmostEqual(participation_ratio(concentrated), 1.0)
        self.assertAlmostEqual(entropy_effective_rank(concentrated), 1.0)

    def test_bootstraps_are_deterministic_and_in_range(self) -> None:
        first = moving_block_bootstrap_indices(12, 3, 4, seed=17)
        second = moving_block_bootstrap_indices(12, 3, 4, seed=17)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 4)
        self.assertTrue(all(len(replication) == 12 for replication in first))
        self.assertTrue(all(0 <= index < 12 for replication in first for index in replication))

        stationary_a = stationary_bootstrap_indices(12, 4.0, 3, seed=23)
        stationary_b = stationary_bootstrap_indices(12, 4.0, 3, seed=23)
        self.assertEqual(stationary_a, stationary_b)

    def test_purged_walk_forward(self) -> None:
        splits = purged_expanding_walk_forward(
            sample_size=30,
            minimum_train_size=10,
            test_size=5,
            purge=2,
            embargo=3,
        )
        self.assertGreaterEqual(len(splits), 2)
        for split in splits:
            self.assertLess(max(split.train_indices), min(split.purged_indices))
            self.assertLess(max(split.purged_indices), min(split.test_indices))
            if split.embargo_indices:
                self.assertLess(max(split.test_indices), min(split.embargo_indices))

    def test_benjamini_hochberg(self) -> None:
        result = benjamini_hochberg({"a": 0.001, "b": 0.01, "c": 0.2, "d": 0.8}, alpha=0.05)
        self.assertTrue(result["a"]["rejected"])
        self.assertTrue(result["b"]["rejected"])
        self.assertFalse(result["c"]["rejected"])
        self.assertLessEqual(result["a"]["adjusted_p_value"], result["b"]["adjusted_p_value"])

    def test_leave_one_out_means(self) -> None:
        self.assertEqual(leave_one_out_means([1.0, 2.0, 3.0]), (2.5, 2.0, 1.5))


class GraphFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.nodes = {
            "source": {
                "node_type": "SOURCE",
                "authority_role": "OWNER",
                "knowledge_at_utc": "2026-07-27T10:00:00Z",
            },
            "feature": {
                "node_type": "FEATURE",
                "method_id": "FEATURE_V1",
            },
            "decision": {
                "node_type": "TEST",
                "method_id": "TEST_V1",
                "decision_at_utc": "2026-07-27T10:05:00Z",
            },
            "result": {
                "node_type": "RESULT",
                "method_id": "RESULT_V1",
            },
        }
        self.edges = [("source", "feature"), ("feature", "decision"), ("decision", "result")]

    def test_valid_provenance_graph(self) -> None:
        result = validate_provenance_graph(self.nodes, self.edges)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("source", result["owner_nodes"])

    def test_cycle_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            topological_order(self.nodes, self.edges + [("result", "source")])

    def test_latest_knowledge_propagates(self) -> None:
        latest = latest_upstream_knowledge(self.nodes, self.edges)
        self.assertEqual(latest["decision"], "2026-07-27T10:00:00Z")

    def test_post_decision_input_is_detected(self) -> None:
        nodes = dict(self.nodes)
        nodes["source"] = dict(nodes["source"])
        nodes["source"]["knowledge_at_utc"] = "2026-07-27T10:06:00Z"
        violations = temporal_dependency_violations(nodes, self.edges)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["node_id"], "decision")

    def test_conclusion_without_owner_path_fails(self) -> None:
        nodes = dict(self.nodes)
        nodes["source"] = dict(nodes["source"])
        nodes["source"]["authority_role"] = "SHADOW"
        result = validate_provenance_graph(nodes, self.edges)
        self.assertEqual(result["status"], "FAIL")


class LedgerContractTests(unittest.TestCase):
    def test_full_point_in_time_row_passes(self) -> None:
        row = DecisionLineageRow(
            record_id="event-1",
            record_type="STATE_CHANGE",
            event_time_utc="2026-07-27T10:00:00Z",
            knowledge_at_utc="2026-07-27T10:01:00Z",
            decision_at_utc="2026-07-27T10:02:00Z",
            rule_version="RULE_V1",
            input_artifact_ids=("artifact-1",),
            input_hashes=("abc123",),
            state_before="NO_ROTATION",
            state_after="NO_ROTATION",
            action_permission="NONE",
            lineage_class="FULL_POINT_IN_TIME",
        )
        self.assertEqual(row.validate(), [])
        report = validate_decision_lineage([row])
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["bt10_eligible_rows"], 1)

    def test_full_point_in_time_missing_timestamp_fails(self) -> None:
        row = DecisionLineageRow(
            record_id="event-2",
            record_type="STATE_CHANGE",
            event_time_utc="2026-07-27T10:00:00Z",
            knowledge_at_utc=None,
            decision_at_utc="2026-07-27T10:02:00Z",
            rule_version="RULE_V1",
            input_artifact_ids=("artifact-1",),
            input_hashes=("abc123",),
            state_before=None,
            state_after=None,
            action_permission=None,
            lineage_class="FULL_POINT_IN_TIME",
        )
        self.assertTrue(row.validate())

    def test_counterfactual_row_temporal_contract(self) -> None:
        row = CounterfactualDeploymentRow(
            event_id="flush-1",
            policy_id="DELAY_2D",
            event_knowledge_at_utc="2026-07-27T10:00:00Z",
            decision_at_utc="2026-07-27T10:05:00Z",
            execution_at_utc="2026-07-29T10:05:00Z",
            label_end_utc="2026-08-27T10:05:00Z",
            entry_price=62000.0,
            horizon_price=65000.0,
            realized_delta=3000.0,
            foregone_delta=500.0,
            maximum_adverse_excursion=-0.04,
            maximum_favorable_excursion=0.09,
            drawdown_avoided=0.02,
            opportunity_cost=0.01,
            regret_sign="NEGATIVE",
            source_hashes=("hash1",),
        )
        self.assertEqual(row.validate(), [])


if __name__ == "__main__":
    unittest.main()
