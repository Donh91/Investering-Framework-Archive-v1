"""Deterministic negative/positive source-age census research fixtures."""
import unittest
from scripts.research.official_compass_source_age_census import age, summarize


def official(src: int, packet: int, status: str = "OK", health: str = "PASS"):
    return {
        "data_status": status,
        "source_bindings": {
            "auto_market_state": {
                "freshness": {
                    "status": health,
                    "checks": [
                        {"lane": "source_observation_freshness", "age_seconds": src},
                        {"lane": "auto_market_state_packet", "age_seconds": packet},
                    ],
                }
            }
        },
    }


class OfficialCompassSourceAgeCensusTest(unittest.TestCase):
    def test_exact_threshold_boundary_is_age_eligible(self):
        result = summarize([official(1800, 50)])
        self.assertEqual(result["older_than_30m"], 0)
        self.assertEqual(result["packet_within_30m_source_older_30m"], 0)
        self.assertEqual(result["official_OK"], 1)

    def test_integral_float_seconds_from_pinned_official_producer_are_lossless(self):
        # The original immutable October Official JSON encodes 10356.0
        # rather than 10356. These values must produce the same census.
        self.assertEqual(summarize([official(1800.0, 30.0)]),
                         summarize([official(1800, 30)]))
        result = summarize([official(1801.0, 40.0)])
        self.assertEqual(result["older_than_30m"], 1)
        self.assertEqual(result["packet_within_30m_source_older_30m"], 1)

    def test_nonintegral_packet_seconds_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "missing_or_invalid_age:auto_market_state_packet"):
            summarize([official(100, 1.5)])

    def test_aged_market_observation_in_fresh_wrapper_detected(self):
        result = summarize([official(1801, 40)])
        self.assertEqual(result["older_than_30m"], 1)
        self.assertEqual(result["packet_within_30m_source_older_30m"], 1)
        self.assertEqual(result["official_OK_source_older_30m"], 1)

    def test_60_120_180m_strict_age_boundaries(self):
        result = summarize([official(3601, 90), official(7201, 70), official(10801, 60)])
        self.assertEqual(result["older_than_30m"], 3)
        self.assertEqual(result["older_than_60m"], 3)
        self.assertEqual(result["older_than_120m"], 2)
        self.assertEqual(result["older_than_180m"], 1)

    def test_degraded_source_not_inflated_into_ok(self):
        result = summarize([official(16487, 13745, "DEGRADED", "STALE_OR_UNAVAILABLE")])
        self.assertEqual(result["official_OK"], 0)
        self.assertEqual(result["official_DEGRADED"], 1)
        self.assertEqual(result["freshness_PASS"], 0)

    def test_old_wrapper_not_mistaken_for_fresh(self):
        result = summarize([official(3000, 1801)])
        self.assertEqual(result["packet_within_30m_source_older_30m"], 0)

    def test_missing_required_observation_age_fails_closed(self):
        x = official(100, 50)
        del x["source_bindings"]["auto_market_state"]["freshness"]["checks"][0]["age_seconds"]
        with self.assertRaisesRegex(ValueError, "missing_or_invalid_age"):
            summarize([x])

    def test_duplicate_required_lane_fails_closed(self):
        x = official(100, 50)
        x["source_bindings"]["auto_market_state"]["freshness"]["checks"].append(
            {"lane": "source_observation_freshness", "age_seconds": 101})
        with self.assertRaisesRegex(ValueError, "missing_or_invalid_age"):
            summarize([x])

    def test_null_and_negative_age_fail_closed(self):
        for invalid in (None, -1, True, False, 1.5, -0.5, float("nan"), float("inf"), "1800"):
            x = official(invalid, 50)
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "missing_or_invalid_age"):
                    summarize([x])

    def test_unknown_official_status_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unexpected_official_status"):
            summarize([official(2000, 20, "UNKNOWN")])

    def test_freshness_pass_is_not_identical_to_official_ok(self):
        r = summarize([official(1000, 20, "DEGRADED", "PASS")])
        self.assertEqual(r["official_DEGRADED"], 1)
        self.assertEqual(r["freshness_PASS"], 1)


if __name__ == "__main__":
    unittest.main()
