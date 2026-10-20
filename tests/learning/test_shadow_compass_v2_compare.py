from __future__ import annotations

import copy
import unittest

from scripts.learning.shadow_compass_v2_compare import pair_outcomes


def outcome(
    *,
    shadow: bool,
    ident: str,
    issued: str,
    result: str,
    predicted: str = "UP",
    start: str = "2026-10-01T05:00:00Z",
) -> dict:
    row = {
        "scoring_contract": "SHADOW_COMPASS_V2_SCORING_v3" if shadow else "OFFICIAL_DAILY_COMPASS_SCORING_v3",
        "horizon": "12h",
        "issued_at_utc": issued,
        "target_at_utc": "2026-10-01T17:00:00Z",
        "target_observation_at_utc": "2026-10-01T16:00:00Z",
        "target_observation_open_at_utc": "2026-10-01T15:00:00Z",
        "target_source_window_end_utc": "2026-10-01T17:00:00Z",
        "matured_at_utc": "2026-10-01T17:30:00Z",
        "time_basis": {
            "status": "PASS",
            "start_reference_at_utc": start,
            "nominal_horizon_hours": 12,
            "effective_window_hours": 11,
            "window_deviation_hours": 1,
            "endpoint_semantics": "HOURLY_CLOSE_TIME_NEAREST_TO_REFERENCE_PLUS_HORIZON",
            "source_window_end_semantics": "COLLECTION_BOUNDARY_NOT_CANDLE_CLOSE",
            "source_first_knowledge_status": "UNKNOWN_NOT_PROVEN_BY_BATCH_END",
        },
        "realized": {
            "btc_return_pct": -0.2,
            "eth_return_pct": -0.3,
            "ethbtc_return_pct": -0.1,
            "btc_mfe_pct": 0.2,
            "btc_mae_pct": -0.8,
            "eth_mfe_pct": 0.4,
            "eth_mae_pct": -1.1,
        },
        "direction_accuracy": {
            "btc": {"result": result, "predicted": predicted},
            "eth": {"result": result, "predicted": predicted},
        },
        "baselines": {"persistence": {"status": "SCORED", "correct": False}},
        "source_path": f"outcomes/{ident}.json",
        "forecast_path": f"forecasts/{ident}.json",
        "outcome_sha256": ident * 2,
    }
    if shadow:
        row["forecast_id"] = ident
        row["comparison_metadata"] = {"official_comparison_eligible": True}
    else:
        row["compass_id"] = ident
    return row


class ShadowOfficialPairingTests(unittest.TestCase):
    def test_pairs_identical_window_by_nearest_issue_time_without_using_outcome(self):
        shadow = outcome(
            shadow=True,
            ident="S1",
            issued="2026-10-01T06:12:00Z",
            result="CORRECT",
        )
        far = outcome(
            shadow=False,
            ident="O1",
            issued="2026-10-01T07:52:00Z",
            result="CORRECT",
        )
        near = outcome(
            shadow=False,
            ident="O2",
            issued="2026-10-01T05:42:00Z",
            result="ABSTAINED",
        )
        report = pair_outcomes([far, near], [shadow])
        self.assertEqual(report["pair_count"], 1)
        pair = report["pairs"][0]
        self.assertEqual(pair["official_compass_id"], "O2")
        self.assertEqual(pair["integrity"]["status"], "PASS")
        self.assertFalse(pair["integrity"]["selection_used_outcome_correctness"])
        self.assertEqual(
            pair["asset_comparisons"]["btc"]["comparison_state"],
            "SHADOW_CORRECT_OFFICIAL_ABSTAINED",
        )

    def test_changing_correctness_does_not_change_selected_pair(self):
        shadow = outcome(
            shadow=True,
            ident="S1",
            issued="2026-10-01T06:12:00Z",
            result="CORRECT",
        )
        a = outcome(
            shadow=False,
            ident="O1",
            issued="2026-10-01T05:42:00Z",
            result="CORRECT",
        )
        b = outcome(
            shadow=False,
            ident="O2",
            issued="2026-10-01T07:52:00Z",
            result="INCORRECT",
        )
        first = pair_outcomes([a, b], [shadow])["pairs"][0]["official_compass_id"]
        a2, b2 = copy.deepcopy(a), copy.deepcopy(b)
        a2["direction_accuracy"]["btc"]["result"] = "INCORRECT"
        b2["direction_accuracy"]["btc"]["result"] = "CORRECT"
        second = pair_outcomes([a2, b2], [shadow])["pairs"][0]["official_compass_id"]
        self.assertEqual(first, second)

    def test_same_horizon_but_different_frozen_window_is_not_paired(self):
        shadow = outcome(
            shadow=True,
            ident="S1",
            issued="2026-10-01T06:12:00Z",
            result="CORRECT",
        )
        official = outcome(
            shadow=False,
            ident="O1",
            issued="2026-10-01T05:42:00Z",
            result="CORRECT",
            start="2026-10-01T04:00:00Z",
        )
        report = pair_outcomes([official], [shadow])
        self.assertEqual(report["pair_count"], 0)
        self.assertEqual(report["unpaired_shadow_count"], 1)

    def test_cross_version_pair_is_excluded_before_selection(self):
        shadow = outcome(shadow=True, ident="S1", issued="2026-10-01T06:12:00Z", result="CORRECT")
        near_legacy = outcome(shadow=False, ident="O1", issued="2026-10-01T06:10:00Z", result="CORRECT")
        near_legacy["scoring_contract"] = "OFFICIAL_DAILY_COMPASS_SCORING_v2"
        valid_v3 = outcome(shadow=False, ident="O2", issued="2026-10-01T07:00:00Z", result="ABSTAINED")
        report = pair_outcomes([near_legacy, valid_v3], [shadow])
        self.assertEqual(report["pair_count"], 1)
        self.assertEqual(report["pairs"][0]["official_compass_id"], "O2")
        self.assertEqual(report["pairs"][0]["integrity"]["status"], "PASS")
        missing = outcome(shadow=False, ident="O3", issued="2026-10-01T06:11:00Z", result="CORRECT")
        missing.pop("scoring_contract")
        self.assertEqual(pair_outcomes([missing], [shadow])["pair_count"], 0)

    def test_legacy_v2_pair_cannot_report_verified_time_basis(self):
        shadow = outcome(shadow=True, ident="S1", issued="2026-10-01T06:12:00Z", result="CORRECT")
        official = outcome(shadow=False, ident="O1", issued="2026-10-01T06:10:00Z", result="CORRECT")
        shadow["scoring_contract"] = "SHADOW_COMPASS_V2_SCORING_v2"
        official["scoring_contract"] = "OFFICIAL_DAILY_COMPASS_SCORING_v2"
        report = pair_outcomes([official], [shadow])
        self.assertEqual(report["pair_count"], 0)
        self.assertEqual(report["quarantined_pair_count"], 1)
        pair = report["quarantined_pairs"][0]
        self.assertEqual(pair["integrity"]["status"], "LEGACY_TIME_BASIS_UNVERIFIED")
        self.assertEqual(pair["asset_comparisons"]["btc"]["comparison_state"], "PAIR_TIME_BASIS_UNVERIFIED")

    def test_foreign_v3_suffix_never_admitted(self):
        shadow = outcome(shadow=True, ident="S1", issued="2026-10-01T06:12:00Z", result="CORRECT")
        official = outcome(shadow=False, ident="O1", issued="2026-10-01T06:10:00Z", result="CORRECT")
        shadow["scoring_contract"] = "FOREIGN_SCORING_v3"
        report = pair_outcomes([official], [shadow])
        self.assertEqual(report["pair_count"], 0)
        self.assertEqual(report["quarantined_pair_count"], 0)

    def test_v3_time_basis_missing_or_malformed_is_quarantined(self):
        for defect in ("missing_open", "wrong_close", "missing_batch", "future_batch", "missing_matured", "early_matured", "bad_status", "wrong_semantics", "bad_effective", "foreign_official"):
            with self.subTest(defect=defect):
                shadow = outcome(shadow=True, ident="S1", issued="2026-10-01T06:12:00Z", result="CORRECT")
                official = outcome(shadow=False, ident="O1", issued="2026-10-01T06:10:00Z", result="CORRECT")
                if defect == "missing_open":
                    shadow.pop("target_observation_open_at_utc")
                elif defect == "wrong_close":
                    shadow["target_observation_open_at_utc"] = "2026-10-01T14:00:00Z"
                elif defect == "missing_batch":
                    shadow["target_source_window_end_utc"] = None
                elif defect == "future_batch":
                    shadow["target_source_window_end_utc"] = "2099-01-01T00:00:00Z"
                elif defect == "missing_matured":
                    shadow.pop("matured_at_utc")
                elif defect == "early_matured":
                    shadow["matured_at_utc"] = "2026-10-01T16:30:00Z"
                elif defect == "bad_status":
                    shadow["time_basis"]["status"] = "FAIL"
                elif defect == "wrong_semantics":
                    shadow["time_basis"]["source_window_end_semantics"] = "BATCH_IS_CANDLE"
                elif defect == "bad_effective":
                    shadow["time_basis"]["effective_window_hours"] = 12
                else:
                    official["scoring_contract"] = "OTHER_OFFICIAL_SCORING_v3"
                report = pair_outcomes([official], [shadow])
                self.assertEqual(report["pair_count"], 0)
                if defect != "foreign_official":
                    self.assertEqual(report["quarantined_pair_count"], 0)
                    self.assertEqual(report["quarantined_candidate_count"], 1)
                    self.assertEqual(report["quarantined_candidates"][0]["reason"], "V3_TIME_BASIS_INVALID_PRE_SELECTION")

    def test_future_batch_cannot_steal_valid_pair_slot(self):
        closer = outcome(shadow=True, ident="Sfuture", issued="2026-10-01T06:01:00Z", result="CORRECT")
        closer["target_source_window_end_utc"] = "2099-01-01T00:00:00Z"
        eligible = outcome(shadow=True, ident="Svalid", issued="2026-10-01T06:30:00Z", result="INCORRECT")
        official = outcome(shadow=False, ident="O1", issued="2026-10-01T06:00:00Z", result="CORRECT")
        result = pair_outcomes([official], [closer, eligible])
        self.assertEqual(result["pair_count"], 1)
        self.assertEqual(result["pairs"][0]["shadow_forecast_id"], "Svalid")
        self.assertEqual(result["quarantined_candidate_count"], 1)

    def test_malformed_nearest_v3_cannot_steal_valid_pair_slot(self):
        near_invalid = outcome(shadow=True, ident="Sbad", issued="2026-10-01T06:01:00Z", result="CORRECT")
        near_invalid.pop("target_observation_open_at_utc")
        farther_valid = outcome(shadow=True, ident="Sgood", issued="2026-10-01T07:00:00Z", result="INCORRECT")
        official = outcome(shadow=False, ident="O1", issued="2026-10-01T06:00:00Z", result="CORRECT")
        report = pair_outcomes([official], [near_invalid, farther_valid])
        self.assertEqual(report["pair_count"], 1)
        self.assertEqual(report["pairs"][0]["shadow_forecast_id"], "Sgood")
        self.assertEqual(report["pairs"][0]["integrity"]["status"], "PASS")
        self.assertEqual(report["quarantined_candidate_count"], 1)
        self.assertEqual(report["quarantined_candidates"][0]["shadow_forecast_id"], "Sbad")
        self.assertEqual(report["unpaired_shadow_count"], 1)
        # Outcome-blind selection: changing correctness cannot promote Sbad.
        near_invalid["direction_accuracy"]["btc"]["result"] = "INCORRECT"
        farther_valid["direction_accuracy"]["btc"]["result"] = "CORRECT"
        repeat = pair_outcomes([official], [near_invalid, farther_valid])
        self.assertEqual(repeat["pairs"][0]["shadow_forecast_id"], "Sgood")

    def test_one_to_one_pairing_prevents_reusing_same_official(self):
        s1 = outcome(
            shadow=True,
            ident="S1",
            issued="2026-10-01T06:10:00Z",
            result="CORRECT",
        )
        s2 = outcome(
            shadow=True,
            ident="S2",
            issued="2026-10-01T06:20:00Z",
            result="INCORRECT",
        )
        official = outcome(
            shadow=False,
            ident="O1",
            issued="2026-10-01T06:12:00Z",
            result="ABSTAINED",
        )
        report = pair_outcomes([official], [s1, s2])
        self.assertEqual(report["pair_count"], 1)
        self.assertEqual(report["unpaired_shadow_count"], 1)

    def test_realized_mismatch_fails_integrity_instead_of_rematching(self):
        shadow = outcome(
            shadow=True,
            ident="S1",
            issued="2026-10-01T06:12:00Z",
            result="CORRECT",
        )
        official = outcome(
            shadow=False,
            ident="O1",
            issued="2026-10-01T05:42:00Z",
            result="ABSTAINED",
        )
        official["realized"]["btc_return_pct"] = 9.0
        report = pair_outcomes([official], [shadow])
        self.assertEqual(report["pair_count"], 0)
        self.assertEqual(report["quarantined_pair_count"], 1)
        pair = report["quarantined_pairs"][0]
        self.assertEqual(pair["integrity"]["status"], "FAIL")
        self.assertEqual(
            pair["asset_comparisons"]["btc"]["comparison_state"],
            "PAIR_INTEGRITY_FAIL",
        )


if __name__ == "__main__":
    unittest.main()
