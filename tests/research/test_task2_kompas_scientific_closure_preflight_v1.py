"""Adversarial public-only Task2 / Kompas W46 source and score checks."""
import copy
import unittest

from scripts.research.task2_kompas_scientific_closure_preflight_v1 import examine, utc


def fixture():
    cn = {
        "schema": "CN_PUBLIC_SNAPSHOT_V2",
        "public_live_precision": {
            "contract": "CN_PUBLIC_LIVE_PRICE_PRECISION_v1",
            "forecast_week": "2026-W46",
            "public_issue_number": 33,
            "frozen_at_utc": "2026-11-09T10:52:34Z",
            "live_as_of_utc": "2026-11-10T12:00:00Z",
            "price_quote_labels": {
                "actual_native_spot": {"BTC": "USDT", "ETH": "USDT"},
                "forecast_model_declared": {"BTC": "USDT", "ETH": "USDT"},
                "comparison_precision_eligible": False,
            },
            "daily_price_path": {
                asset: {"points": [
                    {"day": 1, "low": 95, "high": 105, "expected_close": 100},
                    {"day": 2, "low": 90, "high": 100, "expected_close": 95},
                ]} for asset in ("BTC", "ETH")
            },
            "daily_observations": {
                asset: [
                    {"day": 1, "date": "2026-11-09", "status": "COMPLETE",
                     "low": 96, "high": 106, "close": 104,
                     "observed_hours": 24, "as_of_utc": "2026-11-10T00:00:00Z"},
                    {"day": 2, "date": "2026-11-10", "status": "LIVE",
                     "low": 88, "high": 101, "close": 89,
                     "observed_hours": 12, "as_of_utc": "2026-11-10T12:00:00Z"},
                ] for asset in ("BTC", "ETH")
            },
        },
        "public_scorecard": {
            "price_range_precision": {"score": 81.81},
            "frozen_claim_precision": {
                "score": 100, "scored_parameter_count": 2,
                "parameter_coverage_pct": 16.666667,
            },
        },
    }
    compass = {
        "contract": "PUBLIC_COMPASS_PROJECTION_v1",
        "compass_id": "SYNTHETIC_COMPASS",
        "issued_at_utc": "2026-11-12T15:57:36Z",
        "public_data_health": {"native_data_health": "DEGRADED"},
        "full_stack": {"official_freshness": {
            "valid_until_utc": "2026-11-12T16:00:00Z",
        }},
        "original_source_age_at_issue": {
            "provider_first_published_at_utc": None,
            "first_investor_delivery_at_utc": None,
        },
    }
    return cn, compass


class ScientificClosurePreflightTests(unittest.TestCase):
    def test_issuance_remaining_life_and_opaque_first_known(self):
        cn, compass = fixture()
        result = examine(cn, compass)
        self.assertEqual(result["official"]["remaining_validity_at_issue_seconds"], 144)
        self.assertEqual(result["official"]["clock_status"], "SHORT_REMAINING_VALIDITY_UNDER_15M")
        self.assertIsNone(result["official"]["first_provider_published_at"])
        self.assertIsNone(result["official"]["first_user_delivered_at"])
        self.assertFalse(result["edge_proven"])

    def test_preissue_monday_and_live_tuesday_not_scientific_results(self):
        cn, compass = fixture()
        rows = examine(cn, compass)["daily_diagnostics"]
        monday = next(x for x in rows if x["asset"] == "BTC" and x["day"] == 1)
        tuesday = next(x for x in rows if x["asset"] == "BTC" and x["day"] == 2)
        self.assertTrue(monday["contains_preissue_hours_possible"])
        self.assertFalse(tuesday["contains_preissue_hours_possible"])
        self.assertEqual(tuesday["interpretation"], "PROVISIONAL_INTRADAY")
        self.assertEqual(tuesday["low_breach_pct"], round(100 * (90 - 88) / 90, 4))
        self.assertEqual(tuesday["close_error_pct"], round(100 * (89 - 95) / 95, 4))
        self.assertFalse(all(x["scientific_score_admitted"] for x in rows))

    def test_score_family_no_false_100pct_total_accuracy(self):
        cn, compass = fixture()
        scores = examine(cn, compass)["score_families_kept_separate"]
        self.assertEqual(scores["range_score"], 81.81)
        self.assertEqual(scores["frozen_claim_score"], 100)
        self.assertEqual(scores["frozen_claim_scored_parameters"], 2)
        self.assertLess(scores["frozen_claim_coverage_pct"], 20)
        self.assertIsNone(scores["combined_accuracy"])

    def test_upstream_unqualified_quote_remains_unqualified(self):
        cn, compass = fixture()
        x = examine(cn, compass)["source_comparison"]
        self.assertTrue(x["same_native_and_declared_usdt"])
        self.assertFalse(x["upstream_comparison_precision_eligible"])
        self.assertFalse(x["scientific_pit_admitted"])
        cn["public_live_precision"]["price_quote_labels"]["forecast_model_declared"]["ETH"] = "USD"
        x = examine(cn, compass)["source_comparison"]
        self.assertFalse(x["same_native_and_declared_usdt"])

    def test_missing_day_returns_abstention_not_zero_score(self):
        cn, compass = fixture()
        obs = cn["public_live_precision"]["daily_observations"]["BTC"][1]
        obs.update(status="NOT_STARTED", low=None, high=None, close=None)
        day = next(x for x in examine(cn, compass)["daily_diagnostics"]
                   if x["asset"] == "BTC" and x["day"] == 2)
        self.assertIsNone(day["low_breach_pct"])
        self.assertIsNone(day["close_error_pct"])
        self.assertEqual(day["interpretation"], "ABSTAIN")

    def test_invalid_contracts_and_missing_issued_day_fail_closed(self):
        cn, compass = fixture()
        cn["schema"] = "WRONG"
        with self.assertRaisesRegex(ValueError, "CN_PUBLIC_CONTRACT_MISMATCH"):
            examine(cn, compass)
        cn, compass = fixture()
        cn["public_live_precision"]["daily_price_path"]["ETH"]["points"].pop()
        with self.assertRaisesRegex(ValueError, "ISSUED_DAILY_POINT_MISSING"):
            examine(cn, compass)

    def test_expired_on_issuance_not_repaired_by_ui(self):
        cn, compass = fixture()
        compass["full_stack"]["official_freshness"]["valid_until_utc"] = "2026-11-12T15:40:00Z"
        self.assertEqual(examine(cn, compass)["official"]["clock_status"], "ISSUED_AT_OR_AFTER_EXPIRY")

    def test_utc_rejects_naive_and_non_z(self):
        for stamp in ("2026-11-12T18:00:00", "2026-11-12T18:00:00+00:00"):
            with self.assertRaisesRegex(ValueError, "UTC_Z_TIMESTAMP_REQUIRED"):
                utc(stamp)


if __name__ == "__main__":
    unittest.main()
