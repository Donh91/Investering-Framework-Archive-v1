"""Portable SHADOW logic checks; does not execute Bend or verify Python producer.

Run: python -m unittest test_shadow_model.py -v (from this directory)
"""
import unittest
from itertools import product

CONTRACTS = ("MATURED_OUTCOME_v2", "MATURED_OUTCOME_v3", "OTHER")
STATUSES = ("MATURED", "CENSORED", "UNKNOWN")
RESULTS = ("HIT", "MISS", "UNKNOWN")
FLAGS = (True, False, None)
BINDINGS = (True, False)


def classified_scoreable(contract, status, result, eligible, binding):
    """Reduced abstract model of PR #1675 eligibility, not actual receipt validation."""
    return (contract in CONTRACTS[:2]
            and status == "MATURED"
            and eligible is True
            and result in ("HIT", "MISS")
            and binding is True)


def baseline_validation_from_counts(_candidate):
    # Reflects current prospective_row's absence of independent admission.
    return False


class TestShadowModel(unittest.TestCase):
    def test_exhaustive_abstract_input_cross_product(self):
        cases = list(product(CONTRACTS, STATUSES, RESULTS, FLAGS, BINDINGS))
        self.assertEqual(len(cases), 162)
        for contract, status, result, flag, binding in cases:
            actual = classified_scoreable(contract, status, result, flag, binding)
            # Independent, declarative oracle for the abstract state space.
            expected = (contract in ("MATURED_OUTCOME_v2", "MATURED_OUTCOME_v3")
                        and status == "MATURED" and result in ("HIT", "MISS")
                        and type(flag) is bool and flag and binding)
            self.assertEqual(actual, expected, (contract, status, result, flag, binding))
            if status != "MATURED":
                self.assertFalse(actual)
            if actual:
                self.assertFalse(baseline_validation_from_counts({"matured_outcome_count": 1}))

    def test_counter_cannot_self_authorize(self):
        for counter in (None, -1, 0, 1, 99, True, "99"):
            self.assertFalse(baseline_validation_from_counts({"matured_outcome_count": counter}))

    def test_known_regression_is_caught_by_negative_oracle(self):
        # A deliberately wrong status shortcut, used ONLY as a mutant fixture.
        mutant = lambda status: status in ("MATURED", "CENSORED")
        self.assertTrue(mutant("CENSORED"))
        self.assertFalse(classified_scoreable("MATURED_OUTCOME_v3", "CENSORED", "HIT", True, True))

    def test_unbound_or_unqualified_hit_is_not_scoreable(self):
        for flag, binding in ((False, True), (None, True), (True, False)):
            self.assertFalse(classified_scoreable("MATURED_OUTCOME_v3", "MATURED", "HIT", flag, binding))


if __name__ == "__main__":
    unittest.main()
