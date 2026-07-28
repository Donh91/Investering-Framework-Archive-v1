from __future__ import annotations

import math
import unittest

from backtest_engine.liquidity_research import (
    ResearchContractViolation,
    benjamini_hochberg_adjust,
    block_permutation_family_max,
    first_differences,
    holm_adjust,
    lagged_correlation,
    pearson_correlation,
    purged_expanding_walk_forward,
    rolling_beta,
    scan_lags,
    validate_dag,
)


class LiquidityResearchStatisticsTests(unittest.TestCase):
    def test_shared_trend_can_create_high_level_correlation_without_change_correlation(self) -> None:
        x = [float(index) + math.sin(index) for index in range(1, 200)]
        y = [3.0 * index + math.cos(index * 1.7) * 20.0 for index in range(1, 200)]
        self.assertGreater(pearson_correlation(x, y), 0.97)
        self.assertLess(abs(pearson_correlation(first_differences(x), first_differences(y))), 0.20)

    def test_true_positive_lag_is_recovered(self) -> None:
        predictor = [math.sin(index / 7.0) + 0.2 * math.sin(index / 2.0) for index in range(300)]
        outcome = [0.0, 0.0, 0.0] + predictor[:-3]
        results = scan_lags(predictor, outcome, range(0, 9))
        best = max(results, key=lambda row: abs(row.correlation))
        self.assertEqual(best.lag, 3)
        self.assertGreater(best.correlation, 0.99)

    def test_negative_lag_is_rejected(self) -> None:
        with self.assertRaises(ResearchContractViolation):
            lagged_correlation([1, 2, 3, 4], [1, 2, 3, 4], -1)

    def test_multiple_testing_adjustments_are_bounded_and_ordered(self) -> None:
        p_values = [0.001, 0.01, 0.04, 0.20]
        holm = holm_adjust(p_values)
        bh = benjamini_hochberg_adjust(p_values)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in holm + bh))
        self.assertGreaterEqual(holm[0], p_values[0])
        self.assertGreaterEqual(bh[0], p_values[0])

    def test_block_permutation_is_deterministic(self) -> None:
        x = [math.sin(index / 5.0) for index in range(100)]
        y = [math.cos(index / 8.0) for index in range(100)]
        a = block_permutation_family_max(x, y, [0, 1, 2, 3], block_size=8, permutations=20, seed=20260728)
        b = block_permutation_family_max(x, y, [0, 1, 2, 3], block_size=8, permutations=20, seed=20260728)
        self.assertEqual(a, b)

    def test_walk_forward_respects_purge_embargo_and_holdout(self) -> None:
        splits = purged_expanding_walk_forward(
            120, min_train=40, test_size=10, purge=3, embargo=2, final_holdout=20
        )
        for split in splits:
            self.assertGreaterEqual(split.test_start - split.train_end_exclusive, 3)
            self.assertLessEqual(split.test_end_exclusive, 100)
        self.assertGreaterEqual(splits[1].train_end_exclusive - splits[0].test_end_exclusive, 2)

    def test_rolling_beta_recovers_linear_exposure(self) -> None:
        x = [float(index) for index in range(30)]
        y = [2.5 * value + 7.0 for value in x]
        beta = rolling_beta(x, y, 10)
        self.assertAlmostEqual(beta[-1], 2.5, places=12)

    def test_dag_cycle_is_rejected(self) -> None:
        with self.assertRaises(ResearchContractViolation):
            validate_dag(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])
        self.assertEqual(validate_dag(["a", "b", "c"], [("a", "b"), ("b", "c")]), ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
