import sys
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2] / "scripts" / "research"))
from task2_protection_synthetic_v1 import Quote, Warning, Policy, simulate_synthetic

BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)

def scenario(prices, spread=0, capacities=None, step_h=1):
    capacities = capacities or [1e9] * len(prices)
    return [Quote(BASE + timedelta(hours=i*step_h), BASE + timedelta(hours=i*step_h),
                  p*(1-spread/2), p*(1+spread/2), capacities[i])
            for i,p in enumerate(prices)]

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
        self.assertEqual(out['sale_at'],(BASE+timedelta(hours=3)).isoformat())
        self.assertEqual(out['reentry_status'],'HORIZON_ENDED_BEFORE_REENTRY')
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
        self.assertEqual(out['sale_at'],(BASE+timedelta(hours=1)).isoformat())
        self.assertEqual(out['reentry_at'],(BASE+timedelta(hours=2)).isoformat())
    def test_btc_low_loss_not_altcoin_fill_proxy(self):
        # Illiquid altcoin never borrows a synthetic liquid BTC fill.
        out=simulate_synthetic(scenario([100,80,50,30], capacities=[1e9,10,10,10]),signal(),policy())
        self.assertEqual(out['sale_status'],'BLOCKED_BY_LIQUIDITY')
    def test_historical_proof_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'HISTORICAL_OR_UNAUTHORIZED_WARNING_BLOCKED'):
            simulate_synthetic(scenario([100,90]),signal(proof='PIT_VERIFIED'),policy())
    def test_future_source_forbidden(self):
        with self.assertRaisesRegex(ValueError,'LOOKAHEAD'):
            simulate_synthetic(scenario([100,90]),signal(source_h=2),policy())
    def test_delivered_before_issue_forbidden(self):
        with self.assertRaisesRegex(ValueError,'LOOKAHEAD'):
            simulate_synthetic(scenario([100,90]),signal(issued_h=2,delivered_h=1),policy())
    def test_duplicate_quotes_forbidden(self):
        tape=scenario([100,90,80]);tape[2]=replace(tape[2],at=tape[1].at,known_at=tape[1].at)
        with self.assertRaisesRegex(ValueError,'OUT_OF_ORDER'):
            simulate_synthetic(tape,signal(),policy())
    def test_future_quote_capture_forbidden(self):
        tape=scenario([100,90]);tape[1]=replace(tape[1],known_at=tape[1].at+timedelta(hours=2))
        with self.assertRaisesRegex(ValueError,'QUOTE_CAPTURE'):
            simulate_synthetic(tape,signal(),policy())
    def test_no_negative_spread_or_nan(self):
        tape=scenario([100,90]);tape[1]=replace(tape[1],bid=float('nan'))
        with self.assertRaisesRegex(ValueError,'NONFINITE'):
            simulate_synthetic(tape,signal(),policy())
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

if __name__=='__main__': unittest.main(verbosity=2)

