import unittest
from scripts.cycle_navigator.precision_evidence_coverage_v1 import evidence_coverage, valid_score


class PrecisionCoverage(unittest.TestCase):
    def test_regression_three_missing_weeks(self):
        result = evidence_coverage([100, None, None, None], 3)
        self.assertEqual(result['coverage_status'], 'INSUFFICIENT_EVIDENCE')
        self.assertEqual(result['scoreable_observations'], 1)
        self.assertEqual(result['unscored_observations'], 3)
        self.assertFalse(result['latest_observation_scoreable'])

    def test_zero_is_real_outcome(self):
        self.assertEqual(evidence_coverage([100, 100, 0, 0], 3)['coverage_status'], 'COMPLETE')
        self.assertTrue(valid_score(0))

    def test_missing_is_not_zero(self):
        self.assertEqual(evidence_coverage([None] * 4, 3)['scoreable_observations'], 0)
        self.assertEqual(evidence_coverage([None] * 4, 3)['coverage_status'], 'INSUFFICIENT_EVIDENCE')

    def test_partial_minimum(self):
        self.assertEqual(evidence_coverage([0, 50, 100, None], 3)['coverage_status'], 'PARTIAL')
        self.assertFalse(evidence_coverage([0, 50, 100, None], 3)['latest_observation_scoreable'])

    def test_invalid_values_never_count(self):
        for value in (True, False, float('nan'), float('inf'), -1, 101, '100'):
            with self.subTest(value=value):
                self.assertFalse(valid_score(value))
        result = evidence_coverage([True, float('nan'), 101, 0], 3)
        self.assertEqual(result['invalid_observations'], 3)
        self.assertEqual(result['scoreable_observations'], 1)

    def test_invalid_window(self):
        for n in (0, 5, True):
            with self.assertRaises(ValueError):
                evidence_coverage([], n)
        with self.assertRaises(ValueError):
            evidence_coverage([100] * 5, 3)
