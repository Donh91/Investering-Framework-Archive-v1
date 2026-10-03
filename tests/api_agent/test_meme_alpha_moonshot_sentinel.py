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

    def test_material_visibility_gap_routes_to_existing_deep_dive_without_score(self) -> None:
        event = {
            "token_ca": "0x" + "a" * 40, "liquidity_usd": 50000, "sells_h1": 5,
            "price_change_h1_pct": 10, "price_change_h6_pct": 20,
            "birth_cohort_percentiles": {
                "buyer_velocity": 98, "transaction_velocity": 98,
                "volume_to_liquidity": 20,
            },
        }
        triage = s.initial_triage(event, CONFIG)
        self.assertTrue(triage["families"]["M"])
        self.assertFalse(triage["exceptional_microstructure_override"])
        self.assertEqual(triage["family_count"], 1)
        self.assertEqual(triage["alert_state"], "DEEP_DIVE")
        self.assertTrue(triage["visibility_gap"]["escalate_existing_deep_dive"])
        self.assertIsNone(triage["visibility_gap"]["predictive_score"])

    def test_visibility_gap_never_bypasses_execution_gate(self) -> None:
        event = {
            "token_ca": "0x" + "b" * 40, "liquidity_usd": 50000, "sells_h1": 0,
            "price_change_h1_pct": 10, "price_change_h6_pct": 20,
            "birth_cohort_percentiles": {
                "buyer_velocity": 98, "transaction_velocity": 98,
                "volume_to_liquidity": 20,
            },
        }
        triage = s.initial_triage(event, CONFIG)
        self.assertTrue(triage["visibility_gap"]["escalate_existing_deep_dive"])
        self.assertFalse(triage["execution_gate_pass"])
        self.assertEqual(triage["alert_state"], "SILENT")

    def test_failed_sell_evidence_blocks_deep_dive(self) -> None:
        event = {
            "token_ca": "0x" + "1" * 40, "liquidity_usd": 50000, "sells_h1": 0,
            "price_change_h1_pct": 0, "price_change_h6_pct": 0,
            "birth_cohort_percentiles": {"buyer_velocity": 100, "transaction_velocity": 100, "volume_to_liquidity": 100},
        }
        triage = s.initial_triage(event, CONFIG, {"families": {"S": True, "P": True}})
        self.assertEqual(triage["alert_state"], "SILENT")
        self.assertIn("INSUFFICIENT_SUCCESSFUL_SELL_EVIDENCE", triage["execution_gate_reasons"])

    def test_gamble_alert_requires_convergence_no_fatal_convexity_and_deterministic_non_m_evidence(self) -> None:
        token = "0x" + "1" * 40
        triage = {"execution_gate_pass": True, "candidate_id": f"eth:{token}", "event": {"token_ca": token, "symbol": "X"}}
        assessment = {
            "archetype": "PRODUCT_STEALTH", "M": {"state": "PASS"}, "S": {"state": "PASS"}, "P": {"state": "PASS"},
            "W": {"state": "UNKNOWN"}, "N": {"state": "UNKNOWN"}, "fatal_risks": [], "remaining_convexity_multiple": 25,
            "hundred_x_feasibility": "REMOTE", "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "x",
        }
        without = s.final_alert_decision(triage, assessment, CONFIG)
        self.assertEqual(without["state"], "MOONSHOT_WATCH")
        self.assertFalse(without["deterministic_evidence_gate_pass"])
        self.assertIn("DETERMINISTIC_NON_M_EVIDENCE_MISSING", without["deterministic_evidence_reasons"])
        evidence = {
            "contract": "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1",
            "status": "PASS",
            "candidate_id": f"eth:{token}",
            "token_ca": token,
            "llm_generated": False,
            "receipts": [{
                "family": "P",
                "state": "PASS",
                "deterministic": True,
                "llm_generated": False,
                "source_contract": "MEME_ALPHA_ETH_BLOCKSCOUT_EXACT_CA_PROVENANCE_v1",
                "evidence_refs": ["receipt:product:fixture"],
            }],
        }
        allowed = s.final_alert_decision(triage, assessment, CONFIG, deterministic_evidence=evidence)
        self.assertEqual(allowed["state"], "MOONSHOT_GAMBLE_ALERT")
        self.assertEqual(allowed["llm_judged_families"], ["M", "P", "S"])
        self.assertEqual(allowed["deterministic_verified_families"], ["P"])
        self.assertEqual(allowed["deterministic_confirmed_families"], ["P"])
        assessment["fatal_risks"] = ["sellability conflict"]
        self.assertEqual(s.final_alert_decision(triage, assessment, CONFIG, deterministic_evidence=evidence)["state"], "MOONSHOT_WATCH")

    def test_daily_cap_blocks_gamble_alert(self) -> None:
        token = "0x" + "2" * 40
        triage = {"execution_gate_pass": True, "candidate_id": f"eth:{token}", "event": {"token_ca": token, "symbol": "X"}}
        assessment = {
            "archetype": "PRODUCT_STEALTH", "M": {"state": "PASS"}, "S": {"state": "PASS"}, "P": {"state": "PASS"},
            "W": {"state": "UNKNOWN"}, "N": {"state": "UNKNOWN"}, "fatal_risks": [], "remaining_convexity_multiple": 25,
            "hundred_x_feasibility": "REMOTE", "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "x",
        }
        evidence = {
            "contract": "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1", "status": "PASS",
            "candidate_id": f"eth:{token}", "token_ca": token, "llm_generated": False,
            "receipts": [{"family": "S", "state": "PASS", "deterministic": True, "llm_generated": False,
                          "source_contract": "INDEPENDENT_SOCIAL_ROOT_RECEIPT_v1", "evidence_refs": ["fixture:social"]}],
        }
        self.assertNotEqual(s.final_alert_decision(triage, assessment, CONFIG, alerts_last_24h=3, deterministic_evidence=evidence)["state"], "MOONSHOT_GAMBLE_ALERT")


    def test_fabricated_llm_families_cannot_create_gamble_alert(self) -> None:
        token = "0x" + "3" * 40
        triage = {"execution_gate_pass": True, "candidate_id": f"eth:{token}", "event": {"token_ca": token, "symbol": "X"}}
        assessment = {
            "archetype": "CABAL_WALLET_PROPAGATION",
            "M": {"state": "PASS"}, "W": {"state": "PASS"}, "S": {"state": "PASS"}, "P": {"state": "PASS"}, "N": {"state": "PASS"},
            "fatal_risks": [], "remaining_convexity_multiple": 50, "hundred_x_feasibility": "PLAUSIBLE",
            "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "model says all families pass",
        }
        result = s.final_alert_decision(triage, assessment, CONFIG)
        self.assertEqual(result["state"], "MOONSHOT_WATCH")
        self.assertFalse(result["deterministic_evidence_gate_pass"])
        self.assertNotIn("passed_families", result)
        self.assertEqual(result["llm_judged_families"], ["M", "N", "P", "S", "W"])

    def test_deterministic_evidence_must_match_candidate_and_be_non_llm_non_m(self) -> None:
        token = "0x" + "4" * 40
        triage = {"execution_gate_pass": True, "candidate_id": f"eth:{token}", "event": {"token_ca": token, "symbol": "X"}}
        assessment = {
            "archetype": "PRODUCT_STEALTH", "M": {"state": "PASS"}, "W": {"state": "PASS"}, "S": {"state": "PASS"},
            "P": {"state": "PASS"}, "N": {"state": "UNKNOWN"}, "fatal_risks": [], "remaining_convexity_multiple": 20,
            "hundred_x_feasibility": "REMOTE", "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "x",
        }
        cases = [
            {
                "contract": "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1", "status": "PASS",
                "candidate_id": "eth:wrong", "token_ca": token, "llm_generated": False,
                "receipts": [{"family": "W", "state": "PASS", "deterministic": True, "llm_generated": False, "source_contract": "WALLET_v1", "evidence_refs": ["x"]}],
            },
            {
                "contract": "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1", "status": "PASS",
                "candidate_id": f"eth:{token}", "token_ca": token, "llm_generated": True,
                "receipts": [{"family": "W", "state": "PASS", "deterministic": True, "llm_generated": False, "source_contract": "WALLET_v1", "evidence_refs": ["x"]}],
            },
            {
                "contract": "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1", "status": "PASS",
                "candidate_id": f"eth:{token}", "token_ca": token, "llm_generated": False,
                "receipts": [{"family": "M", "state": "PASS", "deterministic": True, "llm_generated": False, "source_contract": "MICRO_v1", "evidence_refs": ["x"]}],
            },
        ]
        for evidence in cases:
            with self.subTest(evidence=evidence):
                result = s.final_alert_decision(triage, assessment, CONFIG, deterministic_evidence=evidence)
                self.assertNotEqual(result["state"], "MOONSHOT_GAMBLE_ALERT")
                self.assertFalse(result["deterministic_evidence_gate_pass"])

    def test_deterministic_family_cannot_upgrade_llm_failed_family(self) -> None:
        token = "0x" + "5" * 40
        triage = {"execution_gate_pass": True, "candidate_id": f"eth:{token}", "event": {"token_ca": token, "symbol": "X"}}
        assessment = {
            "archetype": "PRODUCT_STEALTH", "M": {"state": "PASS"}, "W": {"state": "FAIL"}, "S": {"state": "PASS"},
            "P": {"state": "PASS"}, "N": {"state": "UNKNOWN"}, "fatal_risks": [], "remaining_convexity_multiple": 20,
            "hundred_x_feasibility": "REMOTE", "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "x",
        }
        evidence = {
            "contract": "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1", "status": "PASS",
            "candidate_id": f"eth:{token}", "token_ca": token, "llm_generated": False,
            "receipts": [{"family": "W", "state": "PASS", "deterministic": True, "llm_generated": False,
                          "source_contract": "WALLET_v1", "evidence_refs": ["fixture:wallet"]}],
        }
        result = s.final_alert_decision(triage, assessment, CONFIG, deterministic_evidence=evidence)
        self.assertEqual(result["state"], "MOONSHOT_WATCH")
        self.assertEqual(result["deterministic_verified_families"], ["W"])
        self.assertEqual(result["deterministic_confirmed_families"], [])
        self.assertFalse(result["deterministic_evidence_gate_pass"])

    def test_eth_p_rejects_robinhood_source_contract(self) -> None:
        token = "0x" + "6" * 40
        triage = {"execution_gate_pass": True, "candidate_id": f"eth:{token}", "event": {"token_ca": token, "symbol": "X"}}
        assessment = {
            "archetype": "PRODUCT_STEALTH", "M": {"state": "PASS"}, "S": {"state": "PASS"},
            "P": {"state": "PASS"}, "W": {"state": "UNKNOWN"}, "N": {"state": "UNKNOWN"},
            "fatal_risks": [], "remaining_convexity_multiple": 25,
            "hundred_x_feasibility": "REMOTE", "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "x",
        }
        evidence = {
            "contract": "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1", "status": "PASS",
            "candidate_id": f"eth:{token}", "token_ca": token, "llm_generated": False,
            "receipts": [{"family": "P", "state": "PASS", "deterministic": True, "llm_generated": False,
                          "source_contract": "MEME_ALPHA_BLOCKSCOUT_EXACT_CA_ENRICHMENT_v1", "evidence_refs": ["fixture:robinhood"]}],
        }
        result = s.final_alert_decision(triage, assessment, CONFIG, deterministic_evidence=evidence)
        self.assertEqual(result["state"], "MOONSHOT_WATCH")
        self.assertFalse(result["deterministic_evidence_gate_pass"])
        self.assertIn("DETERMINISTIC_SOURCE_CONTRACT_CHAIN_MISMATCH:P", result["deterministic_evidence_reasons"])

    def test_deterministic_eth_p_cannot_upgrade_llm_p_unknown(self) -> None:
        token = "0x" + "7" * 40
        triage = {"execution_gate_pass": True, "candidate_id": f"eth:{token}", "event": {"token_ca": token, "symbol": "X"}}
        assessment = {
            "archetype": "PRODUCT_STEALTH", "M": {"state": "PASS"}, "S": {"state": "PASS"},
            "P": {"state": "UNKNOWN"}, "W": {"state": "UNKNOWN"}, "N": {"state": "UNKNOWN"},
            "fatal_risks": [], "remaining_convexity_multiple": 25,
            "hundred_x_feasibility": "REMOTE", "recommendation": "GAMBLE_CANDIDATE", "invalidate_if": [], "summary": "x",
        }
        evidence = {
            "contract": "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1", "status": "PASS",
            "candidate_id": f"eth:{token}", "token_ca": token, "llm_generated": False,
            "receipts": [{"family": "P", "state": "PASS", "deterministic": True, "llm_generated": False,
                          "source_contract": "MEME_ALPHA_ETH_BLOCKSCOUT_EXACT_CA_PROVENANCE_v1", "evidence_refs": ["fixture:eth"]}],
        }
        result = s.final_alert_decision(triage, assessment, CONFIG, deterministic_evidence=evidence)
        self.assertEqual(result["state"], "MOONSHOT_WATCH")
        self.assertEqual(result["deterministic_verified_families"], ["P"])
        self.assertEqual(result["deterministic_confirmed_families"], [])
        self.assertFalse(result["deterministic_evidence_gate_pass"])

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
