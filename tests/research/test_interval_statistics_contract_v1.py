import unittest
from backtest_engine.statistics import interval_score, empirical_coverage, mean_interval_width


class IntervalStatisticsContractTests(unittest.TestCase):
    def test_interval_score(self):
        self.assertEqual(interval_score(5, 0, 10, 0.1), 10)
        self.assertEqual(interval_score(-2, 0, 10, 0.1), 50)

    def test_coverage_and_width(self):
        self.assertEqual(empirical_coverage([0, 5, 11], [0, 0, 0], [10, 10, 10]), 2 / 3)
        self.assertEqual(mean_interval_width([0, 1], [10, 5]), 7)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            interval_score(1, 3, 2, 0.1)
        with self.assertRaises(ValueError):
            empirical_coverage([], [], [])
        with self.assertRaises(ValueError):
            mean_interval_width([2], [1])


if __name__ == '__main__':
    unittest.main()
