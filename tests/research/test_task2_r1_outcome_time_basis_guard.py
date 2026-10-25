"""Task2 R1: outcomes cannot silently change their declared measurement window.

Research-only regressions.  They never upgrade original outcome labels, infer
first-knowledge timing or authorize a forecast/model/portfolio action.
"""
import unittest
from pathlib import Path

from scripts.research import task2_official_r1_original_evidence_gate_v1 as m

FORECAST_PATH = (
    "04_MARKET_LEARNING/handlekompas/official/daily/2026/10/19/"
    "CMP-20261019-test-time-window.json"
)
START = "2026-10-19T21:00:00Z"
ISSUE = "2026-10-19T22:28:05Z"
TARGET = "2026-10-20T09:00:00Z"


def original():
    return {
        "compass_id": "CMP-20261019-test-time-window",
        "compass_sha256": "a" * 64,
        "issued_at_utc": ISSUE,
        "scoring_contract": m.V3,
    }


def measured_outcome():
    return {
        "contract": m.EXPECTED_OUTCOME,
        "horizon": "12h",
        "compass_id": original()["compass_id"],
        "compass_sha256": original()["compass_sha256"],
        "forecast_path": FORECAST_PATH,
        "scoring_contract": m.V3,
        "issued_at_utc": ISSUE,
        "target_at_utc": TARGET,
        "target_observation_at_utc": TARGET,
        "matured_at_utc": "2026-10-20T10:00:00Z",
        "direction_accuracy": {
            "btc": {"result": "CORRECT"},
            "eth": {"result": "ABSTAINED"},
        },
        "time_basis": {
            "nominal_horizon_hours": 12,
            "effective_window_hours": 12,
            "start_reference_at_utc": START,
            "endpoint_semantics": "HOURLY_CLOSE_TIME_NEAREST_TO_REFERENCE_PLUS_HORIZON",
        },
    }


def assess(outcome):
    return m.original_outcome_assessment(
        original(), FORECAST_PATH, outcome, Path("frozen-outcome.json"), "12h"
    )[0]


class OriginalOutcomeTimeBasisTests(unittest.TestCase):
    def test_valid_frozen_12h_basis_passes(self):
        self.assertEqual(assess(measured_outcome()), [])

    def test_valid_72h_and_168h_original_windows(self):
        for horizon, hours, target, matured in (
            ("72h", 72, "2026-10-15T05:00:00Z", "2026-10-15T06:00:00Z"),
            ("168h", 168, "2026-10-19T05:00:00Z", "2026-10-19T06:00:00Z"),
        ):
            with self.subTest(horizon=horizon):
                forecast = original()
                forecast["issued_at_utc"] = "2026-10-12T06:00:00Z"
                outcome = measured_outcome()
                outcome["issued_at_utc"] = forecast["issued_at_utc"]
                outcome["horizon"] = horizon
                outcome["target_at_utc"] = target
                outcome["target_observation_at_utc"] = target
                outcome["matured_at_utc"] = matured
                outcome["time_basis"].update({
                    "start_reference_at_utc": "2026-10-12T05:00:00Z",
                    "nominal_horizon_hours": hours,
                    "effective_window_hours": hours,
                })
                reasons, labels = m.original_outcome_assessment(
                    forecast, FORECAST_PATH, outcome, Path("outcome.json"), horizon
                )
                self.assertEqual(reasons, [])
                self.assertEqual(labels, {"CORRECT": 1, "ABSTAINED": 1})

    def test_wrong_horizon_claim_is_quarantined_even_if_file_name_matches(self):
        altered = measured_outcome()
        altered["time_basis"]["nominal_horizon_hours"] = 72
        self.assertIn("ORIGINAL_TIME_BASIS_HORIZON_MISMATCH", assess(altered))

    def test_wrong_target_reference_window_is_quarantined(self):
        altered = measured_outcome()
        altered["target_at_utc"] = "2026-10-20T10:00:00Z"
        altered["target_observation_at_utc"] = altered["target_at_utc"]
        altered["matured_at_utc"] = "2026-10-20T11:00:00Z"
        self.assertIn("ORIGINAL_TARGET_REFERENCE_WINDOW_MISMATCH", assess(altered))

    def test_effective_window_claim_must_match_declared_horizon(self):
        altered = measured_outcome()
        altered["time_basis"]["effective_window_hours"] = 72
        self.assertIn("ORIGINAL_TIME_BASIS_EFFECTIVE_WINDOW_MISMATCH", assess(altered))

    def test_malformed_present_basis_is_not_accepted_as_absent(self):
        altered = measured_outcome()
        altered["time_basis"] = "PASS"
        self.assertIn("ORIGINAL_TIME_BASIS_MALFORMED", assess(altered))

    def test_invalid_reference_clock_is_quarantined(self):
        altered = measured_outcome()
        altered["time_basis"]["start_reference_at_utc"] = "2026-10-19T23:00:00+02:00"
        self.assertIn("ORIGINAL_REFERENCE_CLOCK_INVALID", assess(altered))

    def test_v3_missing_required_time_basis_is_quarantined(self):
        altered = measured_outcome()
        altered.pop("time_basis")
        self.assertIn("ORIGINAL_V3_TIME_BASIS_MISSING", assess(altered))

    def test_reference_only_mutation_quarantines_valid_target_observation(self):
        altered = measured_outcome()
        altered["time_basis"]["start_reference_at_utc"] = "2026-10-19T20:00:00Z"
        self.assertEqual(altered["target_at_utc"], altered["target_observation_at_utc"])
        self.assertIn("ORIGINAL_TARGET_REFERENCE_WINDOW_MISMATCH", assess(altered))

    def test_historical_outcome_without_optional_basis_remains_unmodified(self):
        legacy = measured_outcome()
        legacy.pop("time_basis")
        legacy["scoring_contract"] = "OFFICIAL_DAILY_COMPASS_SCORING_v2"
        earlier = original()
        earlier["scoring_contract"] = "OFFICIAL_DAILY_COMPASS_SCORING_v2"
        reasons, labels = m.original_outcome_assessment(
            earlier, FORECAST_PATH, legacy, Path("legacy-outcome.json"), "12h"
        )
        self.assertEqual(reasons, [])
        self.assertEqual(labels, {"CORRECT": 1, "ABSTAINED": 1})


if __name__ == "__main__":
    unittest.main()
