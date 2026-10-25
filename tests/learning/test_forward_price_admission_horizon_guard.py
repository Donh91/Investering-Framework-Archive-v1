"""Synthetic-only diagnostic checks. No provider reads, issuance or scoring."""
from __future__ import annotations

import copy
import unittest

from scripts.learning.forward_price_admission_horizon_guard import (
    CONTRACT, HORIZONS, diagnose_captured_source,
)


def capture():
    return {
        "contract": "FORWARD_PRICE_SOURCE_CUSTODY_PUBLIC_BINDING_v1",
        "asset": "BTC", "quote": "USD", "provider": "KRAKEN",
        "instrument_id": "XXBTZUSD", "private_repository": "Donh91/secrets",
        "status": "CAPTURED_NOT_ADMITTED", "source_admitted": False,
        "forecast_issued": False, "historical_replay_allowed": False,
        "outcome_scoring_allowed": False,
        "original_historical_provider_first_known_verified": False,
        "collector_commit_sha": None, "admission_blockers": ["UNKNOWN_FIRST_KNOWN"],
    }


class ForwardPriceAdmissionHorizonGuardTests(unittest.TestCase):
    def test_all_requested_horizons_are_diagnostic_only(self):
        for horizon in HORIZONS:
            with self.subTest(horizon=horizon):
                result = diagnose_captured_source(capture(), horizon)
                self.assertEqual(result["contract"], CONTRACT)
                self.assertEqual(result["status"], "UNAVAILABLE")
                self.assertEqual(result["reason_codes"][0], "SOURCE_NOT_ADMITTED")
                self.assertIs(result["source_admitted"], False)
                self.assertIs(result["forecast_issued"], False)
                self.assertIs(result["eligible_for_public_price"], False)
                self.assertIs(result["eligible_for_canonical_score"], False)
                for field in ("low_usd", "high_usd", "expected_close_usd", "coverage_probability"):
                    self.assertIsNone(result[field])

    def test_hourly_horizons_refuse_daily_only_builder(self):
        for horizon in ("12h", "72h"):
            result = diagnose_captured_source(capture(), horizon)
            self.assertEqual(result["required_family"], "HOURLY_REQUIRED")
            self.assertIn("PRICE_MODEL_NOT_IMPLEMENTED", result["reason_codes"])

    def test_daily_builder_horizons_do_not_imply_issuance(self):
        for horizon in ("24h", "7d", "14d", "21d"):
            result = diagnose_captured_source(capture(), horizon)
            self.assertIn("RESEARCH_ONLY_NOT_ISSUED", result["reason_codes"])
            self.assertFalse(result["eligible_for_public_price"])

    def test_4_to_8w_has_no_invented_model_or_confidence(self):
        for horizon in ("30d", "56d"):
            result = diagnose_captured_source(capture(), horizon)
            self.assertEqual(result["required_family"], "LONG_HORIZON_SHADOW")
            self.assertIsNone(result["coverage_probability"])

    def test_reject_unregistered_horizon_or_boolean(self):
        for value in ("1h", "3d", "8w", "168h", "", None, 72, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                diagnose_captured_source(capture(), value)

    def test_reject_binding_non_object(self):
        for value in (None, [], "BTC", 123):
            with self.subTest(value=value), self.assertRaises(ValueError):
                diagnose_captured_source(value, "24h")

    def test_capture_self_promotion_is_diagnosed_not_admitted(self):
        for key, value in (
            ("source_admitted", True), ("forecast_issued", True),
            ("status", "ISSUED"), ("historical_replay_allowed", True),
            ("outcome_scoring_allowed", True),
            ("original_historical_provider_first_known_verified", True),
            ("collector_commit_sha", "a" * 40),
            ("provider_first_known_proven", True), ("public_issuance", True),
        ):
            with self.subTest(key=key):
                source = capture(); source[key] = value
                result = diagnose_captured_source(source, "7d")
                self.assertEqual(result["reason_codes"][0], "SOURCE_BINDING_INVALID_OR_AUTHORITY_CONFLICT")
                self.assertIs(result["source_admitted"], False)
                self.assertIsNone(result["low_usd"])

    def test_wrong_usdt_provider_or_identity_never_admits(self):
        for key, value in (
            ("quote", "USDT"), ("instrument_id", "XBTUSDT"),
            ("provider", "OTHER"), ("asset", "ETH"),
            ("private_repository", "Donh91/Investering-Framework-Archive-v1"),
            ("contract", "UNKNOWN"),
        ):
            with self.subTest(key=key):
                source = capture(); source[key] = value
                self.assertEqual(diagnose_captured_source(source, "24h")["reason_codes"][0],
                                 "SOURCE_BINDING_INVALID_OR_AUTHORITY_CONFLICT")

    def test_missing_authority_never_defaults_to_true(self):
        for key in ("source_admitted", "status", "forecast_issued", "collector_commit_sha"):
            with self.subTest(key=key):
                source = capture(); del source[key]
                self.assertEqual(diagnose_captured_source(source, "14d")["reason_codes"][0],
                                 "SOURCE_BINDING_INVALID_OR_AUTHORITY_CONFLICT")

    def test_pseudo_positive_number_and_payload_are_not_echoed(self):
        source = capture()
        source.update(low_usd=50000, high_usd=200000,
                      expected_close_usd=150000, coverage_probability=.99)
        result = diagnose_captured_source(source, "7d")
        self.assertNotIn("150000", str(result))
        self.assertIsNone(result["coverage_probability"])

    def test_input_not_modified(self):
        source = capture(); frozen = copy.deepcopy(source)
        diagnose_captured_source(source, "56d")
        self.assertEqual(source, frozen)

    def test_no_portfolio_action_from_any_diagnostic(self):
        for horizon in HORIZONS:
            self.assertIs(diagnose_captured_source(capture(), horizon)["portfolio_action"], False)


if __name__ == "__main__":
    unittest.main()
