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
        "horizon": "12h",
        "issued_at_utc": issued,
        "target_at_utc": "2026-10-01T17:00:00Z",
        "target_observation_at_utc": "2026-10-01T16:00:00Z",
        "time_basis": {"start_reference_at_utc": start},
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
        pair = report["pairs"][0]
        self.assertEqual(pair["integrity"]["status"], "FAIL")
        self.assertEqual(
            pair["asset_comparisons"]["btc"]["comparison_state"],
            "PAIR_INTEGRITY_FAIL",
        )


if __name__ == "__main__":
    unittest.main()
