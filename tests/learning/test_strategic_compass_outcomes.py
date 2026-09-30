from __future__ import annotations

import unittest

from scripts.learning.strategic_compass_outcomes import direction_score


class StrategicCompassOutcomeTests(unittest.TestCase):
    def test_up_and_down_direction_scoring(self):
        self.assertTrue(direction_score("UP", 5.0)["correct"])
        self.assertTrue(direction_score("DOWN", -5.0)["correct"])
        self.assertFalse(direction_score("UP", -1.0)["correct"])

    def test_sideways_fails_closed_without_preregistered_tolerance(self):
        row = direction_score("SIDEWAYS", 0.2)
        self.assertIsNone(row["correct"])
        self.assertEqual(row["result"], "UNAVAILABLE_NO_REGISTERED_SIDEWAYS_TOLERANCE")

    def test_no_edge_and_unavailable_abstain(self):
        self.assertEqual(direction_score("NO_EDGE", 8.0)["result"], "ABSTAINED")
        self.assertEqual(direction_score("UNAVAILABLE", -8.0)["result"], "ABSTAINED")


if __name__ == "__main__":
    unittest.main()
