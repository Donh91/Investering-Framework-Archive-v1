"""Synthetic fixtures only. No market observations or Task2 outcome scoring."""
from __future__ import annotations
import copy
import unittest
from forecast_path_consistency_v1 import validate_bundle


def example():
    return {
        "contract": "RESEARCH_PRICE_PATH_CONSISTENCY_INPUT_v1",
        "authority": "RESEARCH_ONLY",
        "forecast_id": "SYNTHETIC-0001",
        "issued_at_utc": "2026-10-24T10:00:00Z",
        "asset": "BTC", "quote": "USD", "venue": "SYNTHETIC",
        "model_id": "synthetic-v1", "source_binding_sha256": "a" * 64,
        "anchor_price": 100.0,
        "paths": [
            {"target": "WINDOW_EXTREMA", "window_start_utc": "2026-10-24T11:00:00Z",
             "window_end_utc": "2026-10-25T11:00:00Z", "low_q10": 90.0,
             "high_q90": 110.0, "joint_coverage_probability": None},
            {"target": "WINDOW_EXTREMA", "window_start_utc": "2026-10-24T11:00:00Z",
             "window_end_utc": "2026-10-31T11:00:00Z", "low_q10": 80.0,
             "high_q90": 120.0, "joint_coverage_probability": None},
            {"target": "TERMINAL_CLOSE", "window_start_utc": "2026-10-24T11:00:00Z",
             "window_end_utc": "2026-10-25T11:00:00Z", "q10": 92.0, "q50": 101.0, "q90": 108.0},
            {"target": "TERMINAL_CLOSE", "window_start_utc": "2026-10-24T11:00:00Z",
             "window_end_utc": "2026-10-31T11:00:00Z", "q10": 87.0, "q50": 99.0, "q90": 115.0},
        ],
    }


class PathConsistencyTests(unittest.TestCase):
    def fail(self, payload, expected):
        result = validate_bundle(payload)
        self.assertEqual(result["status"], "FAIL", result)
        self.assertIn(expected, result["findings"])
        self.assertFalse(result["forecast_issued"])

    def test_valid_bundle_is_never_science_or_prod_admission(self):
        r = validate_bundle(example())
        self.assertEqual(r["status"], "PASS_LOGICAL_CHECKS_ONLY")
        self.assertEqual(r["nested_extrema_comparisons"], 1)
        self.assertFalse(r["source_admitted"])
        self.assertFalse(r["joint_coverage_calibrated"])
        self.assertFalse(r["production_or_portfolio_authority"])

    def test_nested_low_must_not_increase(self):
        p = example(); p["paths"][1]["low_q10"] = 95.0
        self.fail(p, "NESTED_LOW_QUANTILE_INCREASED")

    def test_nested_high_must_not_decrease(self):
        p = example(); p["paths"][1]["high_q90"] = 105.0
        self.fail(p, "NESTED_HIGH_QUANTILE_DECREASED")

    def test_terminal_close_medians_can_reverse_over_time(self):
        p = example(); p["paths"][3]["q50"] = 90.0
        self.assertEqual(validate_bundle(p)["status"], "PASS_LOGICAL_CHECKS_ONLY")

    def test_terminal_close_quantile_crossing_rejected(self):
        p = example(); p["paths"][2]["q50"] = 111.0
        self.fail(p, "CLOSE_QUANTILES_INVALID")

    def test_marginal_low_high_cannot_claim_joint_80pct(self):
        p = example(); p["paths"][0]["joint_coverage_probability"] = 0.8
        self.fail(p, "JOINT_COVERAGE_NOT_ESTABLISHED")

    def test_bad_or_late_issue_time_rejected(self):
        p = example(); p["issued_at_utc"] = "2026-10-24T11:00:00Z"
        self.fail(p, "WINDOW_OR_ISSUE_TIME_INVALID")

    def test_non_utc_time_rejected(self):
        p = example(); p["paths"][0]["window_start_utc"] = "2026-10-24T13:00:00+02:00"
        self.fail(p, "WINDOW_OR_ISSUE_TIME_INVALID")

    def test_backwards_window_rejected(self):
        p = example(); p["paths"][0]["window_end_utc"] = "2026-10-23T11:00:00Z"
        self.fail(p, "WINDOW_OR_ISSUE_TIME_INVALID")

    def test_duplicate_target_horizon_rejected(self):
        p = example(); p["paths"].append(copy.deepcopy(p["paths"][0]))
        self.fail(p, "DUPLICATE_TARGET_WINDOW")

    def test_usdt_masquerading_as_usd_rejected(self):
        p = example(); p["quote"] = "USDT"
        self.fail(p, "ASSET_QUOTE_INVALID")

    def test_bad_source_digest_rejected(self):
        p = example(); p["source_binding_sha256"] = "b" * 63
        self.fail(p, "SOURCE_DIGEST_INVALID")

    def test_boolean_anchor_rejected(self):
        p = example(); p["anchor_price"] = True
        self.fail(p, "ANCHOR_INVALID")

    def test_infinite_price_rejected(self):
        p = example(); p["paths"][0]["high_q90"] = float("inf")
        self.fail(p, "EXTREMA_QUANTILES_INVALID")

    def test_huge_integer_price_fails_closed(self):
        p = example(); p["paths"][0]["low_q10"] = 10 ** 1000
        self.fail(p, "EXTREMA_QUANTILES_INVALID")

    def test_low_above_high_rejected(self):
        p = example(); p["paths"][0]["low_q10"] = 111.0
        self.fail(p, "EXTREMA_QUANTILES_INVALID")

    def test_malformed_or_extra_fields_rejected(self):
        p = example(); p["paths"][0]["implied_coverage"] = 0.8
        self.fail(p, "PATH_SCHEMA_INVALID")

    def test_absent_paths_fail_closed(self):
        p = example(); p["paths"] = []
        self.fail(p, "PATH_COLLECTION_INVALID")

    def test_invalid_root_fail_closed(self):
        self.fail({"random": True}, "ROOT_SCHEMA_INVALID")

    def test_no_cross_horizon_assertions_for_different_start_times(self):
        p = example()
        p["paths"][1]["window_start_utc"] = "2026-10-25T11:00:00Z"
        p["paths"][1]["low_q10"] = 95
        p["paths"][1]["high_q90"] = 105
        r = validate_bundle(p)
        self.assertEqual(r["status"], "PASS_LOGICAL_CHECKS_ONLY")
        self.assertEqual(r["nested_extrema_comparisons"], 0)

    def test_empty_joint_coverage_is_explicit(self):
        p = example(); p["paths"][0].pop("joint_coverage_probability")
        self.fail(p, "PATH_SCHEMA_INVALID")


if __name__ == "__main__":
    unittest.main()
