import sys
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2] / "scripts" / "research"))
from task2_protection_synthetic_v1 import (Quote, Warning, Policy, simulate_synthetic,
    price_only_lead_synthetic, validate, registered_toy_case_names, registered_toy_definition)

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)

def raw_scenario(prices, spread=0, capacities=None, step_h=1):
    capacities = capacities or [1e9] * len(prices)
    return [Quote(BASE + timedelta(hours=i*step_h), BASE + timedelta(hours=i*step_h),
                  p*(1-spread/2), p*(1+spread/2), capacities[i])
            for i,p in enumerate(prices)]

def scenario(prices, spread=0, capacities=None, step_h=1):
    """Select CODE-OWNED fixture bytes by exact immutable toy definition."""
    if spread != 0 or step_h != 1:
        raise ValueError("NO_DYNAMIC_FIXTURE_PARAMS")
    key=(tuple(prices),tuple(capacities) if capacities is not None else None)
    ids=[id for id in registered_toy_case_names() if registered_toy_definition(id)==key]
    if len(ids)!=1:
        raise ValueError("UNREGISTERED_STATIC_TOY_FIXTURE_BLOCKED")
    return ids[0]

def signal(delivered_h=0, issued_h=0, source_h=0, proof='SYNTHETIC_FIXTURE_ONLY'):
    return Warning(BASE+timedelta(hours=source_h), BASE+timedelta(hours=issued_h),
                   BASE+timedelta(hours=delivered_h), 'HIGH', proof)

def policy(trim=0.5, delay=0, reentry=2, fee=0.001, slip=0.001, gas=0):
    return Policy(trim,delay,reentry,fee,slip,gas)

class CounterfactualTests(unittest.TestCase):
    def test_crash_protection_mechanical_synthetic(self):
        out=simulate_synthetic(scenario([100,95,60,50,55,58]),signal(),policy(reentry=4))
        self.assertGreater(out['net_delta_vs_hold_usd'],0)
        self.assertEqual(out['evidence_class'],'SYNTHETIC_ONLY_NOT_HISTORICAL_EDGE')
    def test_v_recovery_false_exit_regret(self):
        out=simulate_synthetic(scenario([100,95,98,110,130,160]),signal(),policy(reentry=3))
        self.assertLess(out['net_delta_vs_hold_usd'],0)
    def test_parabolic_bull_false_alarm(self):
        out=simulate_synthetic(scenario([100,110,120,145,170]),signal(),policy(reentry=3))
        self.assertLess(out['net_delta_vs_hold_usd'],0)
    def test_stale_delivery_blocks_early_sale(self):
        out=simulate_synthetic(scenario([100,95,70,60,63]),signal(delivered_h=3),policy(reentry=2))
        self.assertEqual(out['sale_at'],(BASE+timedelta(hours=4)).isoformat())
        self.assertEqual(out['reentry_status'],'HORIZON_ENDED_BEFORE_REENTRY')
    def test_cost_accounting_and_time_out_are_visible(self):
        out=simulate_synthetic(scenario([100,95,85,90,100]),signal(),policy(reentry=2,fee=.01,slip=.02,gas=1))
        self.assertGreater(out['trade_notional_turnover_usd'],0)
        self.assertGreater(out['intermediate_trading_fees_usd'],0)
        self.assertGreater(out['intermediate_slippage_usd'],0)
        self.assertEqual(out['gas_cost_usd'],2)
        self.assertEqual(out['time_partially_out_of_market_hours'],2)
        self.assertTrue(out['spread_included_in_bid_ask'])
    def test_blocked_sale_incurs_no_fictional_trade_cost(self):
        out=simulate_synthetic(scenario([100,95,80],capacities=[1e9,100,100]),signal(),policy(gas=10))
        self.assertEqual(out['intermediate_trading_fees_usd'],0)
        self.assertEqual(out['trade_notional_turnover_usd'],0)
        self.assertEqual(out['gas_cost_usd'],0)
        self.assertEqual(out['time_partially_out_of_market_hours'],0)
    def test_liquidity_blocks_not_fantasy_fill(self):
        out=simulate_synthetic(scenario([100,95,70,60],capacities=[1e9,100,1e9,1e9]),signal(),policy())
        self.assertEqual(out['sale_status'],'BLOCKED_BY_LIQUIDITY')
        self.assertEqual(out['net_delta_vs_hold_usd'],0)
    def test_reentry_blocked_carries_cash(self):
        out=simulate_synthetic(scenario([100,95,90,130,160],capacities=[1e9,1e9,1e9,100,1e9]),signal(),policy(reentry=2))
        self.assertEqual(out['reentry_status'],'BLOCKED_BY_LIQUIDITY')
        self.assertLess(out['net_delta_vs_hold_usd'],0)
    def test_fee_makes_flat_roundtrip_worse(self):
        out=simulate_synthetic(scenario([100,100,100,100,100]),signal(),policy(reentry=1,fee=.01,slip=.01))
        self.assertLess(out['net_delta_vs_hold_usd'],0)
    def test_zero_fee_spread_flat_equals_hold(self):
        out=simulate_synthetic(scenario([100,100,100,100]),signal(),policy(reentry=1,fee=0,slip=0))
        self.assertAlmostEqual(out['net_delta_vs_hold_usd'],0)
    def test_next_quote_no_same_signal_bar(self):
        out=simulate_synthetic(scenario([100,90,80,70]),signal(delivered_h=1),policy(reentry=0))
        self.assertEqual(out['sale_at'],(BASE+timedelta(hours=2)).isoformat())
        self.assertEqual(out['reentry_at'],(BASE+timedelta(hours=3)).isoformat())
    def test_warning_before_first_quote_fills_first_quote(self):
        # Issued and delivered before the synthetic tape starts; the first
        # quote is the first time a tradable quote is actually available.
        out=simulate_synthetic(scenario([100,95,90,92]),
            signal(source_h=-1,issued_h=-1,delivered_h=-1),policy(reentry=2))
        self.assertEqual(out['sale_at'],BASE.isoformat())
        self.assertEqual(out['reentry_at'],(BASE+timedelta(hours=2)).isoformat())
        self.assertEqual(out['evidence_class'],'SYNTHETIC_ONLY_NOT_HISTORICAL_EDGE')

    def test_warning_delivered_on_first_quote_waits_until_next(self):
        # No execution on a quote published simultaneously with delivery.
        out=simulate_synthetic(scenario([100,95,90]),signal(),policy())
        self.assertEqual(out['sale_at'],(BASE+timedelta(hours=1)).isoformat())

    def test_btc_low_loss_not_altcoin_fill_proxy(self):
        # Illiquid altcoin never borrows a synthetic liquid BTC fill.
        out=simulate_synthetic(scenario([100,80,50,30], capacities=[1e9,10,10,10]),signal(),policy())
        self.assertEqual(out['sale_status'],'BLOCKED_BY_LIQUIDITY')
    def test_historical_proof_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'HISTORICAL_OR_UNAUTHORIZED_WARNING_BLOCKED'):
            simulate_synthetic(scenario([100,90]),signal(proof='PIT_VERIFIED'),policy())
    def test_forged_label_cannot_admit_unregistered_historical_tape(self):
        # Unrecognized caller-supplied observations must not be accepted even
        # if every timestamp, execution clock, and warning label looks valid.
        historical_like = raw_scenario([101, 99, 82, 75])
        with self.assertRaisesRegex(ValueError, 'UNREGISTERED_STATIC_TOY_FIXTURE_BLOCKED'):
            simulate_synthetic(historical_like, signal(proof='SYNTHETIC_FIXTURE_ONLY'), policy())

    def test_mutated_valid_toy_tape_is_not_in_admission_roster(self):
        tape=raw_scenario([100, 90, 80, 70])
        tape[2] = replace(tape[2], bid=79, ask=79)
        with self.assertRaisesRegex(ValueError, 'UNREGISTERED_STATIC_TOY_FIXTURE_BLOCKED'):
            simulate_synthetic(tape, signal(), policy())

    def test_shifted_historical_clock_cannot_masquerade_as_toy_scenario(self):
        tape=raw_scenario([100, 90, 80, 70])
        tape = [replace(q, at=q.at + timedelta(days=180),
                        known_at=q.known_at + timedelta(days=180)) for q in tape]
        with self.assertRaisesRegex(ValueError, 'UNREGISTERED_STATIC_TOY_FIXTURE_BLOCKED'):
            simulate_synthetic(tape, signal(), policy())

    def test_reproduced_frozen_toy_only_has_no_scientific_authority(self):
        out = simulate_synthetic(scenario([100, 95, 60, 50, 55, 58]), signal(), policy())
        self.assertEqual(out['evidence_class'], 'SYNTHETIC_ONLY_NOT_HISTORICAL_EDGE')
        self.assertFalse(out['historical_result_admissible'])
        self.assertFalse(out['statistical_significance_admissible'])
        self.assertFalse(out['portfolio_action_authorized'])

    def test_future_source_forbidden(self):
        with self.assertRaisesRegex(ValueError,'LOOKAHEAD'):
            simulate_synthetic(scenario([100,90]),signal(source_h=2),policy())
    def test_delivered_before_issue_forbidden(self):
        with self.assertRaisesRegex(ValueError,'LOOKAHEAD'):
            simulate_synthetic(scenario([100,90]),signal(issued_h=2,delivered_h=1),policy())
    def test_duplicate_quotes_forbidden(self):
        tape=raw_scenario([100,90,80]);tape[2]=replace(tape[2],at=tape[1].at,known_at=tape[1].at)
        with self.assertRaisesRegex(ValueError,'OUT_OF_ORDER'):
            validate(tape,signal(),policy(),10000)
    def test_future_quote_capture_forbidden(self):
        tape=raw_scenario([100,90]);tape[1]=replace(tape[1],known_at=tape[1].at+timedelta(hours=2))
        with self.assertRaisesRegex(ValueError,'QUOTE_CAPTURE'):
            validate(tape,signal(),policy(),10000)
    def test_no_negative_spread_or_nan(self):
        tape=raw_scenario([100,90]);tape[1]=replace(tape[1],bid=float('nan'))
        with self.assertRaisesRegex(ValueError,'NONFINITE'):
            validate(tape,signal(),policy(),10000)
    def test_negative_cost_forbidden(self):
        with self.assertRaisesRegex(ValueError,'POLICY_COST'):
            simulate_synthetic(scenario([100,90]),signal(),policy(fee=-1))
    def test_bad_trade_fraction_forbidden(self):
        with self.assertRaisesRegex(ValueError,'POLICY_RANGE'):
            simulate_synthetic(scenario([100,90]),signal(),policy(trim=1.1))
    def test_no_live_action_authority(self):
        out=simulate_synthetic(scenario([100,90]),signal(),policy())
        self.assertFalse(out['portfolio_action_authorized'])
        self.assertEqual(out['live_sell_rule'],'NONE')
    def test_hold_and_policy_capital_matched(self):
        out=simulate_synthetic(scenario([100,80,85,90]),signal(),policy(trim=.5,reentry=1,fee=0,slip=0))
        self.assertGreater(out['terminal_hold_usd'],0)
        self.assertGreater(out['terminal_policy_usd'],0)
    def test_unknown_warning_state_forbidden(self):
        with self.assertRaisesRegex(ValueError,'HISTORICAL_OR_UNAUTHORIZED'):
            simulate_synthetic(scenario([100,90]),replace(signal(),state='BUILDING'),policy())

    def test_every_registered_toy_case_is_in_exact_same_validation_roster(self):
        for case_id in registered_toy_case_names():
            with self.subTest(case_id=case_id):
                out = simulate_synthetic(case_id, signal(), policy())
                self.assertEqual(out["evidence_class"], "SYNTHETIC_ONLY_NOT_HISTORICAL_EDGE")
                self.assertFalse(out["historical_result_admissible"])
                self.assertFalse(out["portfolio_action_authorized"])

    def test_caller_supplied_literal_proof_not_admitted_as_case_id(self):
        with self.assertRaisesRegex(ValueError,'UNREGISTERED_STATIC_TOY_FIXTURE_BLOCKED'):
            simulate_synthetic('SYNTHETIC_FIXTURE_ONLY',signal(),policy())

    def test_price_baseline_rejects_historical_tape_exact_like_toy(self):
        with self.assertRaisesRegex(ValueError,'UNREGISTERED_STATIC_TOY_FIXTURE_BLOCKED'):
            price_only_lead_synthetic(raw_scenario([100,98,96,94]),signal())

class PriceOnlyLeadTests(unittest.TestCase):
    def test_early_warning_beats_frozen_price_triggers(self):
        out=price_only_lead_synthetic(scenario([100,98,96,94]),signal())
        self.assertEqual(out['lead_vs_p2_hours'],2)
        self.assertEqual(out['lead_vs_p1_hours'],3)
    def test_late_warning_cannot_get_early_lead_credit(self):
        out=price_only_lead_synthetic(scenario([100,98,96,94]),signal(delivered_h=3))
        self.assertEqual(out['lead_vs_p2_hours'],-1)
        self.assertEqual(out['lead_vs_p1_hours'],0)
    def test_false_positive_warning_on_pump(self):
        out=price_only_lead_synthetic(scenario([100,110,120,140]),signal())
        self.assertTrue(out['no_price_trigger_in_window'])
        self.assertIsNone(out['lead_vs_p1_hours'])
    def test_delivery_after_horizon_cannot_earn_credit(self):
        with self.assertRaisesRegex(ValueError,'DELIVERY_OUTSIDE'):
            price_only_lead_synthetic(scenario([100,90]),signal(delivered_h=3))
    def test_future_known_source_cannot_lead(self):
        with self.assertRaisesRegex(ValueError,'LOOKAHEAD'):
            price_only_lead_synthetic(scenario([100,90]),signal(source_h=3))
    def test_quote_capture_futurity_cannot_lead(self):
        q=raw_scenario([100,90]);q[1]=replace(q[1],known_at=q[1].at+timedelta(minutes=1))
        with self.assertRaisesRegex(ValueError,'QUOTE_CAPTURE'):
            validate(q,signal(),policy(),10000)


# EDGE-001 Mission 1/2/3 structural shadow ledger; no historical observations.
from edge001_two_sleeve_shadow_contract_v1 import (
    validate_two_sleeve_shadow_row, audit_two_sleeve_shadow_batch,
)

class TwoSleeveContractTests(unittest.TestCase):
    def toy(self, role="PRE_IGNITION_MICRO"):
        # All numeric fields here are fabricated UNIT TEST fixtures.
        row = {
            "record_id": "TOY-" + role, "source_commit": "a" * 40,
            "source_receipt_id": "SYNTHETIC-UNVERIFIED-RECEIPT",
            "source_contract_id": "SYNTHETIC-ONLY",
            "first_known_at": "2026-01-01T00:00:00Z",
            "asof_at": "2026-01-01T01:00:00Z",
            "issued_at": "2026-01-01T02:00:00Z",
            "delivered_at": "2026-01-01T03:00:00Z",
            "sleeve_role": role,
            "original_consensus_or_abstention": "ABSTAIN",
            "market_regime_frozen": "UNKNOWN",
            "asset_universe_vintage": "TOY-UNIVERSE",
            "event_family_id": "TOY-FAMILY-1", "currency": "USD",
            "initial_capital": 1000.0, "notional": 100.0,
            "execution_at": "2026-01-01T05:00:00Z",
            "quote_at": "2026-01-01T04:00:00Z",
            "quote_first_known_at": "2026-01-01T04:00:00Z",
            "capacity_at_execution": 200.0,
            "bid_ask": {"bid": 10.0, "ask": 11.0},
            "fees_slippage_gas": {"fees": 1.0, "slippage": 2.0, "gas": 3.0},
            "filled_fraction": 0.5, "missed_fill": False,
            "opportunity_cost": 0.0, "drawdown": 0.25,
            "terminal_net_liquidatable_wealth": 900.0,
            "hold_baseline_wealth": 950.0,
            "tax_assumption_or_unknown": "UNKNOWN",
            "status": "SHADOW_ACCOUNTING_CANDIDATE",
        }
        if role == "CASH":
            row.update(notional=0, filled_fraction=0, execution_at=None,
                       quote_at=None, quote_first_known_at=None,
                       capacity_at_execution=None, bid_ask=None,
                       fees_slippage_gas={"fees": 0, "slippage": 0, "gas": 0},
                       opportunity_cost=0, drawdown=0,
                       terminal_net_liquidatable_wealth=1000,
                       hold_baseline_wealth=1000)
        return row

    def test_valid_row_is_never_admitted_to_edge_or_actions(self):
        out = validate_two_sleeve_shadow_row(self.toy())
        self.assertEqual(out["structural_status"],
                         "STRUCTURAL_ONLY_UNVERIFIED_PROVENANCE")
        self.assertFalse(out["provider_first_known_verified"])
        self.assertFalse(out["actual_fill_verified"])
        self.assertFalse(out["historical_pit_admitted"])
        self.assertFalse(out["portfolio_economic_edge_admitted"])
        self.assertFalse(out["live_portfolio_action_authorized"])
        self.assertNotIn("900", str(out))
        self.assertNotIn("SYNTHETIC-UNVERIFIED-RECEIPT", str(out))

    def test_same_clock_three_roles_but_not_scientific_edge(self):
        out = audit_two_sleeve_shadow_batch([
            self.toy("PRE_IGNITION_MICRO"),
            self.toy("LATE_LIQUID_LARGE"),
            self.toy("CASH"),
        ])
        self.assertTrue(out["complete_three_role_cohort"])
        self.assertFalse(out["valid_for_historical_scoring"])
        self.assertIsNone(out["independent_event_family_n"])

    def test_incomplete_cohort_not_hallucinated_complete(self):
        out = audit_two_sleeve_shadow_batch([self.toy()])
        self.assertFalse(out["complete_three_role_cohort"])

    def test_forged_pit_or_live_label_rejected(self):
        row = self.toy()
        row["status"] = "PIT_VERIFIED_LIVE"
        with self.assertRaisesRegex(ValueError, "RESEARCH_ONLY_ENUM"):
            validate_two_sleeve_shadow_row(row)

    def test_source_clock_future_to_issue_rejected(self):
        row = self.toy()
        row["first_known_at"] = "2026-01-01T06:00:00Z"
        with self.assertRaisesRegex(ValueError, "CAUSAL_SOURCE_CLOCK"):
            validate_two_sleeve_shadow_row(row)

    def test_non_utc_clock_rejected(self):
        row = self.toy()
        row["issued_at"] = "2026-01-01T03:00:00+01:00"
        with self.assertRaisesRegex(ValueError, "CLOCK_INVALID"):
            validate_two_sleeve_shadow_row(row)

    def test_fill_on_delivery_quote_rejected(self):
        row = self.toy()
        row["quote_at"] = row["delivered_at"]
        with self.assertRaisesRegex(ValueError, "QUOTE_AFTER_DELIVERY"):
            validate_two_sleeve_shadow_row(row)

    def test_positive_fill_exceeding_capacity_rejected(self):
        row = self.toy()
        row["capacity_at_execution"] = 49.0
        with self.assertRaisesRegex(ValueError, "EXCEEDS_CAPACITY"):
            validate_two_sleeve_shadow_row(row)

    def test_missed_fill_cannot_create_profit(self):
        row = self.toy()
        row.update(filled_fraction=0, missed_fill=True, execution_at=None,
                   terminal_net_liquidatable_wealth=12345)
        with self.assertRaisesRegex(ValueError, "UNFILLED_TERMINAL_WEALTH"):
            validate_two_sleeve_shadow_row(row)

    def test_missed_fill_and_filled_are_incompatible(self):
        row = self.toy()
        row["missed_fill"] = True
        with self.assertRaisesRegex(ValueError, "MISSED_FILL_CANNOT_BE_FILLED"):
            validate_two_sleeve_shadow_row(row)

    def test_nan_or_boolean_money_rejected(self):
        row = self.toy()
        row["notional"] = float("nan")
        with self.assertRaisesRegex(ValueError, "FINITE_REQUIRED"):
            validate_two_sleeve_shadow_row(row)
        row["notional"] = True
        with self.assertRaisesRegex(ValueError, "FINITE_REQUIRED"):
            validate_two_sleeve_shadow_row(row)

    def test_bad_sha_and_unknown_extra_fields_rejected(self):
        row = self.toy()
        row["source_commit"] = "main"
        with self.assertRaisesRegex(ValueError, "SHA40"):
            validate_two_sleeve_shadow_row(row)
        row = self.toy()
        row["private_secret"] = "must-not-escape"
        with self.assertRaisesRegex(ValueError, "FIELDS_EXACT_SET"):
            validate_two_sleeve_shadow_row(row)

    def test_cash_cannot_have_filled_trade_or_costs(self):
        row = self.toy("CASH")
        row["filled_fraction"] = 0.5
        with self.assertRaisesRegex(ValueError, "CASH_NO_TRADE"):
            validate_two_sleeve_shadow_row(row)
        row = self.toy("CASH")
        row["fees_slippage_gas"]["fees"] = 1
        with self.assertRaisesRegex(ValueError, "CASH_NO_TRADE_COST"):
            validate_two_sleeve_shadow_row(row)

    def test_invalid_enum_type_rejected_consistently(self):
        row = self.toy()
        row["status"] = []
        with self.assertRaisesRegex(ValueError, "RESEARCH_ONLY_ENUM"):
            validate_two_sleeve_shadow_row(row)

    def test_unmatched_cohort_clock_or_wealth_blocked(self):
        a = self.toy("PRE_IGNITION_MICRO")
        b = self.toy("LATE_LIQUID_LARGE")
        b["initial_capital"] = 1100
        with self.assertRaisesRegex(ValueError, "UNMATCHED_STARTING_WEALTH"):
            audit_two_sleeve_shadow_batch([a, b])
        b = self.toy("LATE_LIQUID_LARGE")
        b["asof_at"] = "2026-01-01T01:30:00Z"
        with self.assertRaisesRegex(ValueError, "UNMATCHED_DECISION_CLOCK"):
            audit_two_sleeve_shadow_batch([a, b])

    def test_duplicate_role_rejected(self):
        a = self.toy()
        b = self.toy()
        b["record_id"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "DUPLICATE_ROLE"):
            audit_two_sleeve_shadow_batch([a, b])

class TwoSleeveManifestConsistencyTests(unittest.TestCase):
    def test_machine_contract_matches_exact_code_fields_and_flags(self):
        import json
        from edge001_two_sleeve_shadow_contract_v1 import (
            CONTRACT, REQUIRED_FIELDS, ROLES, STATES
        )
        root = Path(__file__).resolve().parents[2]
        p = root / "06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/TWO_SLEEVE_SHADOW_ROW_CONTRACT_v1.json"
        spec = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(spec["contract"], CONTRACT)
        self.assertEqual(set(spec["required_fields"]), REQUIRED_FIELDS)
        self.assertEqual(set(spec["allowed_sleeve_roles"]), ROLES)
        self.assertEqual(set(spec["allowed_statuses"]), STATES)
        self.assertEqual(len(spec["required_fields"]), len(REQUIRED_FIELDS))
        self.assertTrue(all(value is False for value in spec["evidence_claims"].values()))
        self.assertFalse(spec["private_values_in_public_repository"])
        self.assertEqual(spec["live_actions"], "NONE")


# Altseason M1/M2/M3 P0-B source feasibility, PUBLIC METADATA only.
from edge001_altseason_source_feasibility_v1 import (
    validate_source_feasibility_registry, CONTRACT as FEASIBILITY_CONTRACT,
)

class AltseasonP0BFeasibilityTests(unittest.TestCase):
    @staticmethod
    def manifest():
        import json
        root = Path(__file__).resolve().parents[2]
        p = root / (
            "06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/"
            "ALTSEASON_SOURCE_FEASIBILITY_V1.json"
        )
        return json.loads(p.read_text(encoding="utf-8"))

    def clone(self):
        from copy import deepcopy
        return deepcopy(self.manifest())

    def test_actual_public_catalog_has_no_fictitious_admission(self):
        out = validate_source_feasibility_registry(self.manifest())
        self.assertEqual(out["contract"], FEASIBILITY_CONTRACT)
        self.assertEqual(out["rows_n"], 18)
        self.assertEqual(out["counts"], {
            "AVAILABLE_NOT_PIT": 11, "AVAILABLE_VERIFIED": 0,
            "MISSING": 6, "UNSAFE": 1,
        })
        self.assertFalse(out["historical_pit_admitted"])
        self.assertFalse(out["historical_portfolio_tournament_authorized"])
        self.assertFalse(out["research_claim_of_edge_allowed"])
        self.assertFalse(out["live_portfolio_action_authorized"])
        self.assertFalse(out["exact_source_bytes_independently_verified"])
        self.assertFalse(out["private_values_echoed"])

    def test_18_unique_source_inputs_and_reactivation_triggers(self):
        rows = self.manifest()["rows"]
        self.assertEqual(len(set(r["id"] for r in rows)), 18)
        self.assertTrue(all(r["next_reactivation_trigger"].strip() for r in rows))
        self.assertTrue(all(r["blocking_reasons"] for r in rows))

    def test_private_alpha_contract_only_metadata_and_no_values(self):
        rows = self.manifest()["rows"]
        private = [r for r in rows if r["source_repo"] == "Donh91/Meme-Alpha-Lab"]
        self.assertEqual(len(private), 1)
        self.assertEqual(private[0]["access_class"], "PRIVATE_METADATA_ONLY")
        self.assertTrue(all(r["private_values_in_public"] is False for r in rows))
        out = str(validate_source_feasibility_registry(self.manifest()))
        self.assertNotIn("token_address", out)
        self.assertNotIn("capacity_usd", out)

    def test_provider_self_proof_without_receipt_fails(self):
        x = self.clone()
        x["rows"][0]["capability_proof"]["provider_first_publication"] = True
        with self.assertRaisesRegex(ValueError, "CLAIMED_PROOF_WITHOUT_RECEIPT"):
            validate_source_feasibility_registry(x)

    def test_verified_status_requires_all_5_proof_receipts(self):
        x = self.clone()
        x["rows"][0]["status"] = "AVAILABLE_VERIFIED"
        with self.assertRaisesRegex(ValueError, "AVAILABLE_VERIFIED_LAUNDERED"):
            validate_source_feasibility_registry(x)

    def test_fake_receipt_format_is_rejected(self):
        x = self.clone()
        x["rows"][0]["binding_receipts"]["provider_first_publication"] = "LOOK_VERIFIED"
        with self.assertRaisesRegex(ValueError, "BOUND_RECEIPT_SHA256"):
            validate_source_feasibility_registry(x)

    def test_labeled_verified_document_cannot_be_promoted(self):
        x = self.clone()
        source = x["rows"][0]
        source["status"] = "AVAILABLE_VERIFIED"
        source["capability_proof"] = {k: True for k in source["capability_proof"]}
        source["binding_receipts"] = {k: "a" * 64 for k in source["binding_receipts"]}
        with self.assertRaisesRegex(ValueError, "DOCUMENTARY_OR_PRIVATE_NOT_VERIFIED"):
            validate_source_feasibility_registry(x)

    def test_private_alpha_mislabelled_public_rejected(self):
        x = self.clone()
        private = next(r for r in x["rows"] if r["source_repo"] == "Donh91/Meme-Alpha-Lab")
        private["access_class"] = "PUBLIC_METADATA"
        with self.assertRaisesRegex(ValueError, "PRIVATE_REPO_MUST_REMAIN_METADATA_ONLY"):
            validate_source_feasibility_registry(x)

    def test_private_data_or_round3_analysis_cannot_be_activated(self):
        x = self.clone()
        x["public_values_copied"] = True
        with self.assertRaisesRegex(ValueError, "PRIVATE_VALUE_EXPORT"):
            validate_source_feasibility_registry(x)
        x = self.clone()
        x["explicit_authority"]["round3_analysis_authorized"] = True
        with self.assertRaisesRegex(ValueError, "AUTHORITY_MUST_REMAIN_FALSE"):
            validate_source_feasibility_registry(x)

    def test_round3_firewall_cannot_be_relabeled(self):
        x = self.clone()
        restricted = next(r for r in x["rows"] if r["status"] == "UNSAFE")
        restricted["status"] = "AVAILABLE_NOT_PIT"
        with self.assertRaisesRegex(ValueError, "RESTRICTED_MUST_BE_UNSAFE"):
            validate_source_feasibility_registry(x)

    def test_unsafe_status_needs_explicit_analysis_firewall(self):
        x = self.clone()
        restricted = next(r for r in x["rows"] if r["status"] == "UNSAFE")
        restricted["blocking_reasons"] = ["LICENSED_ACCESS"]
        with self.assertRaisesRegex(ValueError, "UNSAFE_FIREWALL_REQUIRED"):
            validate_source_feasibility_registry(x)

    def test_no_traversal_or_secrets_source_pointer(self):
        x = self.clone()
        x["rows"][0]["source_path"] = "../secrets/token.json"
        with self.assertRaisesRegex(ValueError, "SOURCE_LOCATOR_UNSAFE"):
            validate_source_feasibility_registry(x)
        x = self.clone()
        x["rows"][0]["source_repo"] = "Donh91/secrets"
        with self.assertRaisesRegex(ValueError, "SOURCE_LOCATOR_UNSAFE"):
            validate_source_feasibility_registry(x)

    def test_source_blob_sha_must_be_exact_40_hex(self):
        x = self.clone()
        x["rows"][0]["source_blob_sha"] = "main"
        with self.assertRaisesRegex(ValueError, "SOURCE_BLOB_SHA40"):
            validate_source_feasibility_registry(x)

    def test_duplicate_source_id_rejected(self):
        x = self.clone()
        x["rows"][1]["id"] = x["rows"][0]["id"]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_OR_INVALID_SOURCE_ID"):
            validate_source_feasibility_registry(x)

    def test_arbitrary_private_field_rejected(self):
        x = self.clone()
        x["rows"][0]["user_wallet"] = "DO_NOT_LOG"
        with self.assertRaisesRegex(ValueError, "SOURCE_FIELD_SET"):
            validate_source_feasibility_registry(x)

    def test_unrecognized_state_or_wrong_boolean_rejected(self):
        x = self.clone()
        x["rows"][0]["status"] = ["AVAILABLE_VERIFIED"]
        with self.assertRaisesRegex(ValueError, "UNRECOGNIZED_STATE"):
            validate_source_feasibility_registry(x)
        x = self.clone()
        x["rows"][0]["capability_proof"]["full_position_sellability"] = 1
        with self.assertRaisesRegex(ValueError, "PROOF_FIELDS_REQUIRED"):
            validate_source_feasibility_registry(x)

    def test_regime_lag_and_sellability_cannot_get_trade_edge(self):
        out = validate_source_feasibility_registry(self.manifest())
        self.assertIn("INDEPENDENT_EVENT_FAMILY_N", out["blocked_source_ids"])
        self.assertIn("HISTORIC_MICRO_EXECUTABLE_DEPTH", out["blocked_source_ids"])
        self.assertIn("MICRO_PAIRED_SELLABILITY", out["blocked_source_ids"])
        self.assertFalse(out["research_claim_of_edge_allowed"])


if __name__=='__main__': unittest.main(verbosity=2)

