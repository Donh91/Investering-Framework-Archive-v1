"""Adversarial future-cohort tests. No source/PIT admission is ever granted."""
import unittest

from prospective_gate import ensure_study_not_started_late, preflight, first_daily_candidate_preflight


def freeze(**changes):
    record = {
        "contract": "OFFICIAL_DAILY_COMPASS_v1",
        "compass_id": "CMP-20261102-aaaaaaaaaaaa",
        "scoring_contract": "OFFICIAL_DAILY_COMPASS_SCORING_v3",
        "issued_at_utc": "2026-11-02T07:17:00Z",
        "market_reference": {"observation_open_utc": "2026-11-02T06:00:00Z", "btc_usdt": 77777.0},
        "market_now": {"btc_delta_pct": -0.5,
                       "market_observation_open_utc": "2026-11-02T06:00:00Z",
                       "predecessor_market_observation_open_utc": "2026-11-02T04:00:00Z"},
        "horizons": {"NEXT_12H": {"expected_direction": "DOWN"}},
    }
    record.update(changes)
    return record


def public(**changes):
    result = {
        "server_created_at_utc": "2026-11-02T07:20:00Z",
        "first_git_commit_sha40": "a" * 40,
        "original_file_sha256": "b" * 64,
        "original_path": "04_MARKET_LEARNING/handlekompas/official/daily/2026/11/02/CMP-20261102-aaaaaaaaaaaa.json",
    }
    result.update(changes)
    return result


def source(**changes):
    result = {
        "market_first_known_at_utc": "2026-11-02T07:05:00Z",
        "baseline_first_known_at_utc": "2026-11-02T07:05:00Z",
    }
    result.update(changes)
    return result


class TemporalGateTests(unittest.TestCase):
    def test_apparently_good_candidate_is_not_scientifically_admitted(self):
        row = preflight(freeze(), public(), source())
        self.assertTrue(row["temporal_preflight_pass"])
        self.assertFalse(row["scientifically_admitted"])
        self.assertFalse(row["independent_publication_verified"])
        self.assertFalse(row["independent_source_first_known_verified"])
        self.assertFalse(row["external_full_day_census_verified"])
        self.assertEqual(row["evidence_state"], "CLOCK_PREFLIGHT_ONLY_EXTERNAL_AUTHENTICATION_REQUIRED")

    def test_new_v41_momentum_is_not_a_forward_forecast_for_locked_study(self):
        f = freeze(decision_policy_version="2026-10-31_OBSERVED_MOMENTUM_SOURCE_SEPARATION_V4_1",
                   horizons={"NEXT_12H": {
                       "expected_direction": "DOWN",
                       "semantics": "OBSERVED_MOMENTUM_NOT_FORECAST",
                       "predictive_edge_status": "NOT_PROVEN",
                   }})
        row = preflight(f, public(), source())
        self.assertIn("NOWCAST_NOT_FORWARD_FORECAST_FOR_LOCKED_STUDY", row["quarantine_reasons"])
        self.assertFalse(row["temporal_preflight_pass"])
        self.assertFalse(row["scientifically_admitted"])

    def test_missing_or_forged_semantics_do_not_bypass_v41_policy(self):
        for value in (None, "PROVEN_FUTURE_FORECAST", ""):
            with self.subTest(marker=value):
                h = {"expected_direction": "UP"}
                if value is not None:
                    h["semantics"] = value
                f = freeze(decision_policy_version="2026-10-31_OBSERVED_MOMENTUM_SOURCE_SEPARATION_V4_1",
                           horizons={"NEXT_12H": h})
                result = preflight(f, public(), source())
                self.assertIn("NOWCAST_NOT_FORWARD_FORECAST_FOR_LOCKED_STUDY", result["quarantine_reasons"])
                self.assertFalse(result["scientifically_admitted"])

    def test_observed_momentum_marker_fails_even_without_policy_id(self):
        f = freeze(horizons={"NEXT_12H": {
            "expected_direction": "UP", "semantics": "OBSERVED_MOMENTUM_NOT_FORECAST",
        }})
        row = preflight(f, public(), source())
        self.assertIn("NOWCAST_NOT_FORWARD_FORECAST_FOR_LOCKED_STUDY", row["quarantine_reasons"])
        self.assertFalse(row["temporal_preflight_pass"])

    def test_forged_pit_bit_is_not_a_valid_admission(self):
        row = preflight(freeze(pit_verified=True), public(scientific_approved=True), source())
        self.assertIn("UNTRUSTED_SELF_ATTESTATION_IGNORED", row["quarantine_reasons"])
        self.assertFalse(row["scientifically_admitted"])

    def test_missing_anchor_fails_closed(self):
        row = preflight(freeze(), None, None)
        self.assertIn("NO_INDEPENDENT_PUBLICATION_TIME_INPUT", row["quarantine_reasons"])
        self.assertIn("SOURCE_FIRST_KNOWN_CLOCKS_MISSING", row["quarantine_reasons"])

    def test_post_outcome_publication_fails(self):
        row = preflight(freeze(), public(server_created_at_utc="2026-11-02T20:00:00Z"), source())
        self.assertIn("PUBLICATION_NOT_BEFORE_TARGET", row["quarantine_reasons"])

    def test_too_short_forward_lead_fails(self):
        row = preflight(freeze(), public(server_created_at_utc="2026-11-02T10:01:00Z"), source())
        self.assertIn("LESS_THAN_TEN_EFFECTIVE_FORECAST_HOURS", row["quarantine_reasons"])

    def test_reference_future_candle_fails(self):
        row = preflight(freeze(market_reference={"observation_open_utc": "2026-11-02T07:00:00Z", "btc_usdt": 77777.0}), public(), source())
        self.assertIn("REFERENCE_CANDLE_FROM_FUTURE", row["quarantine_reasons"])

    def test_unknown_source_clock_fails(self):
        row = preflight(freeze(), public(), source(market_first_known_at_utc=None))
        self.assertIn("SOURCE_FIRST_KNOWN_CLOCKS_MISSING", row["quarantine_reasons"])

    def test_source_known_after_issue_fails(self):
        row = preflight(freeze(), public(), source(baseline_first_known_at_utc="2026-11-02T07:19:00Z"))
        self.assertIn("SOURCE_KNOWN_AFTER_ISSUANCE", row["quarantine_reasons"])

    def test_no_recompute_future_momentum(self):
        for momentum in (None, 0, "0.5", float("nan"), True):
            with self.subTest(momentum=momentum):
                row = preflight(freeze(market_now={"btc_delta_pct": momentum, "market_observation_open_utc": "2026-11-02T06:00:00Z", "predecessor_market_observation_open_utc": "2026-11-02T04:00:00Z"}), public(), source())
                self.assertFalse(row["temporal_preflight_pass"])

    def test_price_momentum_reference_mismatch_is_not_eligible(self):
        good = freeze()
        good["market_now"]["market_observation_open_utc"] = "2026-11-02T05:00:00Z"
        row = preflight(good, public(), source())
        self.assertIn("MOMENTUM_OBSERVATION_NOT_REFERENCE_BOUND", row["quarantine_reasons"])

    def test_predecessor_must_be_from_earlier_market_observation(self):
        good = freeze()
        good["market_now"]["predecessor_market_observation_open_utc"] = "2026-11-02T06:00:00Z"
        row = preflight(good, public(), source())
        self.assertIn("MOMENTUM_PREDECESSOR_NOT_PREVIOUS_OBSERVATION", row["quarantine_reasons"])

    def test_swapped_forecast_identity_is_rejected(self):
        row = preflight(freeze(compass_id="CMP-20261102-bbbbbbbbbbbb"), public(), source())
        self.assertIn("FORECAST_ID_PATH_ISSUANCE_MISMATCH", row["quarantine_reasons"])

    def test_abstention_not_cherrypicked(self):
        row = preflight(freeze(horizons={"NEXT_12H": {"expected_direction": "NO_EDGE"}}), public(), source())
        self.assertIn("NO_DIRECTIONAL_CALL_OR_ABSTAIN", row["quarantine_reasons"])

    def test_outside_primary_window(self):
        row = preflight(freeze(issued_at_utc="2026-11-02T20:17:00Z"), public(server_created_at_utc="2026-11-02T20:20:00Z"), source())
        self.assertIn("OUTSIDE_DAILY_UTC_SELECTION_WINDOW", row["quarantine_reasons"])

    def test_old_history_cannot_be_reenrolled(self):
        row = preflight(freeze(issued_at_utc="2026-10-31T07:17:00Z", compass_id="CMP-20261031-aaaaaaaaaaaa"), public(server_created_at_utc="2026-10-31T07:20:00Z", original_path="04_MARKET_LEARNING/handlekompas/official/daily/2026/10/31/CMP-20261031-aaaaaaaaaaaa.json"), source())
        self.assertIn("OUTSIDE_FROZEN_COHORT", row["quarantine_reasons"])

    def test_legacy_scoring_quarantined(self):
        row = preflight(freeze(scoring_contract="OFFICIAL_DAILY_COMPASS_SCORING_v2"), public(), source())
        self.assertIn("SCORING_VERSION_NOT_REGISTERED", row["quarantine_reasons"])

    def test_provenance_blob_identity_not_supplied(self):
        row = preflight(freeze(), public(first_git_commit_sha40="fake", original_file_sha256="z" * 64), source())
        self.assertIn("PUBLIC_BLOB_IDENTITY_UNBOUND", row["quarantine_reasons"])

    def test_missing_timezone_rejected(self):
        row = preflight(freeze(issued_at_utc="2026-11-02T07:17:00"), public(), source())
        self.assertIn("ISSUE_CLOCK_MISSING_OR_INVALID", row["quarantine_reasons"])

    def test_first_original_abstention_cannot_be_replaced_by_later_winner(self):
        rows = [
            {"forecast": freeze(issued_at_utc="2026-11-02T07:10:00Z",
                                 horizons={"NEXT_12H": {"expected_direction": "NO_EDGE"}}),
             "public_witness": public(server_created_at_utc="2026-11-02T07:12:00Z"),
             "source_witness": source()},
            {"forecast": freeze(issued_at_utc="2026-11-02T07:20:00Z"),
             "public_witness": public(server_created_at_utc="2026-11-02T07:23:00Z"),
             "source_witness": source()},
        ]
        result = first_daily_candidate_preflight("2026-11-02", rows)
        self.assertEqual(result["selection_state"], "FIRST_REPORTED_PUBLICATION_CLOCK_ONLY")
        self.assertIn("NO_DIRECTIONAL_CALL_OR_ABSTAIN", result["quarantine_reasons"])
        self.assertEqual(result["reported_window_candidates"], 2)
        self.assertFalse(result["scientifically_admitted"])

    def test_missing_earlier_publication_blocks_entire_day(self):
        rows = [
            {"forecast": freeze(issued_at_utc="2026-11-02T07:10:00Z"),
             "public_witness": public(server_created_at_utc=None), "source_witness": source()},
            {"forecast": freeze(issued_at_utc="2026-11-02T07:20:00Z"),
             "public_witness": public(server_created_at_utc="2026-11-02T07:23:00Z"),
             "source_witness": source()},
        ]
        result = first_daily_candidate_preflight("2026-11-02", rows)
        self.assertEqual(result["selection_state"], "AMBIGUOUS_FIRST_PUBLICATION_BLOCK_DAY")
        self.assertFalse(result["scientifically_admitted"])

    def test_study_requires_protocol_merge_before_start(self):
        self.assertTrue(ensure_study_not_started_late("2026-11-01T23:59:59Z"))
        self.assertFalse(ensure_study_not_started_late("2026-11-02T00:00:00Z"))
        self.assertFalse(ensure_study_not_started_late(None))


if __name__ == "__main__":
    unittest.main()
