from __future__ import annotations

import unittest

from scripts.api_agent.meme_alpha_lifecycle_v1 import (
    attach_lifecycle_observation,
    classify_phoenix_state,
    derive_phoenix_signal_families,
    phoenix_eligibility,
)


def eligible_snapshot() -> dict:
    return {
        "identity_ok": True,
        "age_hours": 72,
        "prior_demand_state": "REAL_PRIOR_DEMAND",
        "prior_peak_market_cap_usd": 300_000,
        "current_market_cap_usd": 45_000,
        "prior_peak_liquidity_usd": 30_000,
        "current_liquidity_usd": 18_000,
        "sellability_pass": True,
        "buyer_velocity": 9,
        "dormant_buyer_velocity": 3,
        "seller_velocity": 3,
        "dormant_seller_velocity": 5,
        "volume_velocity": 12_000,
        "dormant_volume_velocity": 5_000,
        "independent_quality_wallet_reentries": 1,
        "social_saturation": 0.20,
        "onchain_wakeup_lead_minutes_vs_social": 90,
        "holder_breadth_delta_pct": 8,
        "top10_concentration_delta_pct": -4,
    }


class MemeAlphaLifecycleV1Tests(unittest.TestCase):
    def test_static_low_cap_filter_is_not_enough(self) -> None:
        row = eligible_snapshot()
        row.update({
            "prior_demand_state": "ARTIFACT_OR_UNPROVEN",
            "buyer_velocity": 0,
            "volume_velocity": 0,
            "independent_quality_wallet_reentries": 0,
        })
        result = classify_phoenix_state(row)
        self.assertEqual(result["state"], "INELIGIBLE")
        self.assertIn("PRIOR_DEMAND_UNPROVEN", result["reasons"])

    def test_price_reclaim_alone_cannot_wakeup_or_alert(self) -> None:
        row = eligible_snapshot()
        row.update({
            "buyer_velocity": 0,
            "seller_velocity": 0,
            "volume_velocity": 0,
            "independent_quality_wallet_reentries": 0,
            "social_saturation": 1.0,
            "onchain_wakeup_lead_minutes_vs_social": -1,
            "holder_breadth_delta_pct": 0,
            "top10_concentration_delta_pct": 0,
            "reclaim_confirmed": True,
        })
        families = derive_phoenix_signal_families(row)
        self.assertEqual(families, {"L", "P"})
        result = classify_phoenix_state(row)
        self.assertEqual(result["state"], "CRASHED_SURVIVOR")

    def test_microstructure_wallet_liquidity_pre_social_convergence_is_pre_reclaim(self) -> None:
        row = eligible_snapshot()
        result = classify_phoenix_state(row)
        self.assertEqual(result["state"], "PHOENIX_PRE_RECLAIM_CONVERGENCE")
        self.assertTrue({"M", "L", "W", "S"}.issubset(set(result["signal_families"])))

    def test_reclaim_must_wait_for_pullback_retest(self) -> None:
        row = eligible_snapshot()
        row["reclaim_confirmed"] = True
        reclaim = classify_phoenix_state(row)
        self.assertEqual(reclaim["state"], "PHOENIX_RECLAIM")

        row["pullback_active"] = True
        pending = classify_phoenix_state(row, previous_state="PHOENIX_RECLAIM")
        self.assertEqual(pending["state"], "PHOENIX_RETEST_PENDING")
        self.assertNotEqual(pending["state"], "PHOENIX_GAMBLE_CANDIDATE")

    def test_retest_failure_is_retained_as_negative_example(self) -> None:
        row = eligible_snapshot()
        row.update({
            "retest_completed": True,
            "retest_liquidity_deterioration_pct": 35,
            "buyer_breadth_above_dormant_baseline": True,
        })
        result = classify_phoenix_state(row, previous_state="PHOENIX_RETEST_PENDING")
        self.assertEqual(result["state"], "FAILED_RECLAIM")

    def test_retest_pass_requires_explicit_deep_research_before_gamble_candidate(self) -> None:
        row = eligible_snapshot()
        row.update({
            "retest_completed": True,
            "retest_liquidity_deterioration_pct": 10,
            "buyer_breadth_above_dormant_baseline": True,
            "quality_wallet_distribution": False,
            "price_structure_invalidated": False,
            "sell_pressure_reaccelerated": False,
        })
        passed = classify_phoenix_state(row, previous_state="PHOENIX_RETEST_PENDING")
        self.assertEqual(passed["state"], "PHOENIX_RETEST_PASSED")

        still_wait = classify_phoenix_state(row, previous_state="PHOENIX_RETEST_PASSED")
        self.assertEqual(still_wait["state"], "PHOENIX_RETEST_PASSED")

        row["deep_research_pass"] = True
        gamble = classify_phoenix_state(row, previous_state="PHOENIX_RETEST_PASSED")
        self.assertEqual(gamble["state"], "PHOENIX_GAMBLE_CANDIDATE")

    def test_hard_fail_invalidates_even_strong_convergence(self) -> None:
        row = eligible_snapshot()
        row["critical_liquidity_withdrawal"] = True
        result = classify_phoenix_state(row)
        self.assertEqual(result["state"], "INVALIDATED")
        self.assertIn("CRITICAL_LIQUIDITY_WITHDRAWAL", result["hard_fail_reasons"])

    def test_append_only_history_preserves_state_transition(self) -> None:
        row = eligible_snapshot()
        state = attach_lifecycle_observation({}, row, "2026-09-15T05:00:00Z")
        self.assertEqual(state["phoenix_state"], "PHOENIX_PRE_RECLAIM_CONVERGENCE")
        self.assertEqual(len(state["phoenix_history"]), 1)

    def test_eligibility_records_drawdown_and_liquidity_survival(self) -> None:
        result = phoenix_eligibility(eligible_snapshot())
        self.assertTrue(result["eligible"])
        self.assertEqual(result["drawdown_from_verified_peak_pct"], 85.0)
        self.assertEqual(result["liquidity_survival_ratio"], 0.6)


if __name__ == "__main__":
    unittest.main()
