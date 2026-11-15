"""Explicit governed CN NO_EDGE must remain typed, not silently become unavailable."""
import unittest
from scripts.data_ping.native_handlekompas import horizon_map

HEALTHY = {"validation_status": "PASS", "decision_context_status": "PASS", "blockers": []}
ACTION = {"NOW": "HOLD_WAIT"}
CONTRACT = "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1"


def projection(direction):
    return {"decision_projection": {"contract": CONTRACT, "next_2_3w": {
        "direction": direction, "summary": "A source-qualified no-edge finding."}}}


class NativeNoEdge2to3WeeksTests(unittest.TestCase):
    def test_explicit_no_edge_is_not_unavailable_or_trading_permission(self):
        h = horizon_map(HEALTHY, ACTION, projection("NO_EDGE"))["NEXT_2_3W"]
        self.assertEqual(h["expected_direction"], "NO_EDGE")
        self.assertEqual(h["label"], "NO_EDGE")
        self.assertEqual(h["action_posture"], "WAIT")
        self.assertIn("Ingen klar fordel", h["expected_path"])
        self.assertIsNone(h["confidence"])
        self.assertIsNone(h["eta"])

    def test_absent_invalid_or_unqualified_projection_remains_unavailable(self):
        for doc in (None, {}, {"decision_projection": {"next_2_3w": {"direction": "NO_EDGE"}}},
                    projection("UNAVAILABLE"), projection("FORGED_UP")):
            with self.subTest(doc=doc):
                h = horizon_map(HEALTHY, ACTION, doc)["NEXT_2_3W"]
                self.assertEqual(h["expected_direction"], "UNAVAILABLE")
                self.assertNotIn("Ingen klar fordel", h["expected_path"])

    def test_degraded_market_health_still_fails_closed(self):
        degraded = {**HEALTHY, "decision_context_status": "FAIL"}
        h = horizon_map(degraded, ACTION, projection("NO_EDGE"))["NEXT_2_3W"]
        self.assertEqual(h["expected_direction"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
