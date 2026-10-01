from __future__ import annotations

import unittest

from scripts.learning.strategic_compass_outcomes import asset_direction_scores, direction_score


class StrategicCompassOutcomeTests(unittest.TestCase):
    def test_up_and_down_direction_scoring(self):
        self.assertTrue(direction_score("UP", 5.0)["correct"])
        self.assertTrue(direction_score("DOWN", -5.0)["correct"])
        self.assertFalse(direction_score("UP", -1.0)["correct"])

    def test_sideways_fails_closed_without_preregistered_tolerance(self):
        row = direction_score("SIDEWAYS", 0.2)
        self.assertIsNone(row["correct"])
        self.assertEqual(row["result"], "UNAVAILABLE_NO_REGISTERED_SIDEWAYS_TOLERANCE")

    def test_month_lane_scores_asset_specific_directions(self):
        forecast = {"btc_direction": "UP", "eth_direction": "DOWN", "ethbtc_direction": "DOWN"}
        out = asset_direction_scores(forecast, "21_30d", 5.0, -2.0, -3.0)
        self.assertTrue(out["btc"]["correct"])
        self.assertTrue(out["eth"]["correct"])
        self.assertTrue(out["ethbtc"]["correct"])

    def test_4_8w_structural_direction_is_not_proxy_scored_as_btc_or_eth(self):
        forecast = {"direction": "UP"}
        out = asset_direction_scores(forecast, "4_8w", 8.0, 10.0, 2.0)
        self.assertEqual(out["btc"]["result"], "UNAVAILABLE_NO_ASSET_SPECIFIC_FORECAST")
        self.assertEqual(out["eth"]["result"], "UNAVAILABLE_NO_ASSET_SPECIFIC_FORECAST")
        self.assertEqual(out["ethbtc"]["result"], "UNAVAILABLE_NO_ASSET_SPECIFIC_FORECAST")
        self.assertIsNone(out["btc"]["correct"])

    def test_no_edge_and_unavailable_abstain(self):
        self.assertEqual(direction_score("NO_EDGE", 8.0)["result"], "ABSTAINED")
        self.assertEqual(direction_score("UNAVAILABLE", -8.0)["result"], "ABSTAINED")


if __name__ == "__main__":
    unittest.main()
