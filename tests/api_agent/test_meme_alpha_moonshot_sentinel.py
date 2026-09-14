from __future__ import annotations

import copy
import unittest

from scripts.api_agent import meme_alpha_moonshot_sentinel as s


CONFIG = {
    "scanner": {"absolute_minimum_liquidity_usd": 5000, "minimum_liquidity_usd_for_deep_dive": 12000, "max_candidates_per_scan": 5},
    "birth_cohort_percentile_thresholds": {"buyer_velocity": 97.5, "transaction_velocity": 97.5, "volume_to_liquidity": 95, "liquidity_resilience": 80},
    "microstructure": {"minimum_successful_sells": 3, "maximum_one_hour_price_expansion_pct_for_fresh_alert": 500, "maximum_six_hour_price_expansion_pct_for_fresh_alert": 1500},
    "convergence": {"minimum_signal_families_for_deep_dive": 2, "minimum_signal_families_for_gamble_alert": 3, "accepted_gamble_family_sets": [["M", "S", "P"], ["M", "S", "W"]]},
    "convexity": {"minimum_remaining_convexity_multiple_for_gamble_alert": 10},
    "alert": {"daily_cap": 3, "default_expiry_minutes": 45, "max_entry_market_cap_expansion_from_alert": 2, "max_liquidity_deterioration_pct": 25},
    "risk": {"position_size_output_allowed": False, "automatic_execution": False, "average_down": False, "leverage": False},
    "evolution": {"mutation_budget": 2},
    "version": "1.0.0",
}


class SentinelTests(unittest.TestCase):
    def test_extreme_microstructure_can_reach_deep_dive(self) -> None:
        events = []
        for i in range(100):
            events.append({
                "token_ca": "0x" + f"{i:040x}", "pool_address": str(i), "liquidity_usd": 15000 + i * 10,
                "buys_h1": i, "sells_h1": 5, "buyer_velocity_per_minute": i / 60,
                "transaction_velocity_per_minute": (i + 5) / 60, "volume_to_liquidity_h1": i / 10,
                "market_cap_usd": 100000, "price_change_h1_pct": 10, "price_change_h6_pct": 20,
            })
        ranked = s.add_birth_cohort_percentiles(events)
        triage = s.initial_triage(ranked[-1], CONFIG)
        self.assertEqual(triage["alert_state"], "DEEP_DIVE")
        self.assertTrue(triage["exceptional_microstructure_override"])
        self.assertTrue(triage["families"]["M"])

    def test_failed_sell_evidence_blocks_deep_dive(self) -> None:
        event = {
            "token_ca": "0x" + "1" * 40, "liquidity_usd": 50000, "sells_h1": 0,
            "price_change_h1_pct": 0, "price_change_h6_pct": 0,
            "birth_cohort_percentiles": {"buyer_velocity": 100, "transaction_velocity": 100, "volume_to_liquidity": 100},
        }
        triage = s.initial_triage(event, CONFIG, {"families": {"S": True, "P": True}})
        self.assertEqual(triage["alert_state"], "SILENT")
        self.assertIn("INSUFFICIENT_SUCCESSFUL_SELL_EVIDENCE", triage["execution_gate_reasons"])

    def test_gamble_alert_requires_convergence_no_fatal_and_convexity(self) -> None:
        triage = {"execution_gate_pass": True, "candidate_id": "eth:0x1", "event": {"token_ca": "0x1", "symbol": "X"}}
        assessment = {
            "archetype": "PRODUCT_STEALTH", "M": {"state": "PASS"}, "S": {"state": "PASS"}, "P": {"state": "PASS"},
            "W": {"state": "UNKNOWN"}, "N": {"state": "UNKNOWN"}, "fatal_risks": [], "remaining_convexity_multiple": 25,
            "hundred_x_feasibility": "REMOTE", "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "x",
        }
        self.assertEqual(s.final_alert_decision(triage, assessment, CONFIG)["state"], "MOONSHOT_GAMBLE_ALERT")
        assessment["fatal_risks"] = ["sellability conflict"]
        self.assertEqual(s.final_alert_decision(triage, assessment, CONFIG)["state"], "MOONSHOT_WATCH")

    def test_daily_cap_blocks_gamble_alert(self) -> None:
        triage = {"execution_gate_pass": True, "candidate_id": "eth:0x1", "event": {"token_ca": "0x1", "symbol": "X"}}
        assessment = {
            "archetype": "PRODUCT_STEALTH", "M": {"state": "PASS"}, "S": {"state": "PASS"}, "P": {"state": "PASS"},
            "W": {"state": "UNKNOWN"}, "N": {"state": "UNKNOWN"}, "fatal_risks": [], "remaining_convexity_multiple": 25,
            "hundred_x_feasibility": "REMOTE", "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "x",
        }
        self.assertNotEqual(s.final_alert_decision(triage, assessment, CONFIG, alerts_last_24h=3)["state"], "MOONSHOT_GAMBLE_ALERT")

    def test_challenger_mutations_are_bounded_and_preserve_risk(self) -> None:
        champion = copy.deepcopy(CONFIG)
        challengers = s.propose_challengers(champion, {"missed_winners": 5, "false_positives": 1, "late_alerts": 0})
        self.assertEqual(len(challengers), 1)
        challenger = challengers[0]
        self.assertLessEqual(len(challenger["autonomous_mutations"]), 2)
        self.assertEqual(challenger["risk"], champion["risk"])
        self.assertGreaterEqual(challenger["birth_cohort_percentile_thresholds"]["buyer_velocity"], 90)

    def test_promotion_requires_all_guardrails(self) -> None:
        champion = copy.deepcopy(CONFIG)
        challenger = copy.deepcopy(CONFIG)
        challenger["version"] = "1.0.0-g1"
        challenger["autonomous_mutations"] = [{"path": "a"}, {"path": "b"}]
        contract = {"adaptive_evolution": {"auto_promotion": {
            "minimum_matured_observations": 50, "minimum_distinct_calendar_days": 14,
            "minimum_alerted_or_control_events": 10, "requires_validation_utility_improvement_pct": 5,
            "requires_two_consecutive_validation_windows": True,
        }}}
        windows = []
        for i in range(14):
            windows.append({
                "date": f"2026-09-{i + 1:02d}", "matured_observations": 4, "alerted_or_control_events": 1,
                "champion": {"precision": .3, "recall": .3, "sellability_rate": .8, "false_positive_rate": .7, "lead_time_score": .5},
                "challenger": {"precision": .4, "recall": .35, "sellability_rate": .85, "false_positive_rate": .6, "lead_time_score": .6},
            })
        decision = s.promotion_decision(champion, challenger, windows, contract)
        self.assertEqual(decision["decision"], "AUTO_PROMOTE_RESEARCH_CHAMPION")
        self.assertFalse(decision["production_execution_authority_created"])


if __name__ == "__main__":
    unittest.main()
