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
        tape = scenario([100, 90, 80, 70])
        tape[2] = replace(tape[2], bid=79, ask=79)
        with self.assertRaisesRegex(ValueError, 'UNREGISTERED_STATIC_TOY_FIXTURE_BLOCKED'):
            simulate_synthetic(tape, signal(), policy())

    def test_shifted_historical_clock_cannot_masquerade_as_toy_scenario(self):
        tape = scenario([100, 90, 80, 70])
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

if __name__=='__main__': unittest.main(verbosity=2)

