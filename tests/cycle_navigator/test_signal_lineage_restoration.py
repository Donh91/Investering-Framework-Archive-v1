"""Pin actual W48 behavior and distinguish context presence from consumption."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from dataclasses import replace
from scripts.cycle_navigator.weekly_offline_issuer import build_offline_value
from scripts.cycle_navigator.signal_snapshot_shadow_v1 import Signal, snapshot

ROOT = Path(__file__).resolve().parents[2]
def read(path):
    return json.loads((ROOT / path).read_text())
def w48():
    raw = read('03_DAILY_CAPTURE_LOGS/weekly/2026/W47.json')
    baseline = read('05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W48.json')
    prior = read('05_CYCLE_NAVIGATOR/weekly/2026/W47/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json')
    context = {'completed_week_hourly_capture': raw, 'master_monday_pointer': {'iso_year': 2026, 'iso_week': 47}}
    return context, baseline, prior

def issue(c, b, p):
    return build_offline_value(c, b, p, 2026, 48, 36, 35)

class Lineage(unittest.TestCase):
    def test_w48_all_fourteen_original_daily_closes(self):
        v = issue(*w48())['forecast_freeze']['daily_price_path']
        original = read('05_CYCLE_NAVIGATOR/weekly/2026/W48/CYCLE_NAVIGATOR_FORECAST_FREEZE.json')['daily_price_path']
        for asset in ('BTC', 'ETH'):
            self.assertEqual([x['expected_close'] for x in v[asset]['points']],
                             [x['expected_close'] for x in original[asset]['points']])

    def test_unconsumed_signal_families_do_not_change_any_issuer_output(self):
        c, b, p = w48()
        original = issue(c, b, p)
        # Mutations apply directly to the context passed to the real issuer.
        for family in ('ethbtc', 'breadth', 'open_interest', 'etf_flow', 'btc_dominance', 'taker_flow', 'master_monday_context'):
            altered = copy.deepcopy(c)
            altered[family] = {'value': -987654321, 'status': 'CONTRADICTORY'}
            self.assertEqual(original, issue(altered, b, p), family)
        # Replace actual source fields one family at a time, holding prices fixed.
        for group, field in [('hourly_sequence', 'ethbtc'), ('hourly_sequence', 'spot_flow_readback'),
                             ('hourly_sequence', 'derivatives_oi_complete_hours'), ('hourly_sequence', 'market_interpretation')]:
            altered = copy.deepcopy(c)
            altered['completed_week_hourly_capture'][group][field] = {'contradictory': 999999}
            self.assertEqual(original, issue(altered, b, p), field)
        for field in ('settled_etf', 'rotation_context'):
            altered = copy.deepcopy(c)
            altered['completed_week_hourly_capture'][field] = {'contradictory': 999999}
            self.assertEqual(original, issue(altered, b, p), field)

    def test_price_mutation_changes_daily_path(self):
        c, b, p = w48()
        old = issue(c, b, p)['forecast_freeze']['daily_price_path']['BTC']
        c['completed_week_hourly_capture']['hourly_sequence']['btc']['week_range']['open'] *= 1.1
        self.assertNotEqual(old, issue(c, b, p)['forecast_freeze']['daily_price_path']['BTC'])

    def test_source_gate_does_not_accept_missing_hours(self):
        c, b, p = w48(); c['completed_week_hourly_capture']['hourly_gap_diagnostics']['observed_hours'] = 167
        with self.assertRaisesRegex(ValueError, 'CN_OFFLINE_SOURCE_UNQUALIFIED'): issue(c, b, p)

class PIT(unittest.TestCase):
    def setUp(self):
        self.s = Signal('source', hashlib.sha256(b'fixture').hexdigest(), 'ethbtc', 'venue-a', 1.0, 'ratio',
                        '2026-11-23T09:00:00Z', '2026-11-23T09:10:00Z', 'VALID', 3600, 'ADVISORY')
        self.freeze = '2026-11-23T09:30:00Z'
    def test_pit_and_unknown(self):
        self.assertEqual(snapshot([self.s], self.freeze)['signals'][0]['admission'], 'ADMITTED')
        for s in (replace(self.s, available_at_utc='2026-11-23T10:00:00Z'), replace(self.s, value=None),
                  replace(self.s, max_age_seconds=1), replace(self.s, quality='CONTRADICTORY')):
            self.assertEqual(snapshot([s], self.freeze)['signals'][0]['admission'], 'UNKNOWN')
    def test_bad_authority_hash_and_duplicates_rejected(self):
        for s in (replace(self.s, authority='PRODUCTION'), replace(self.s, source_sha256='fake')):
            with self.assertRaises(ValueError): snapshot([s], self.freeze)
        with self.assertRaises(ValueError): snapshot([self.s, self.s], self.freeze)

class CapabilityGuard(unittest.TestCase):
    def test_removal_and_rewire_are_detected(self):
        from scripts.cycle_navigator.capability_guard_v1 import compare
        old = read('scripts/cycle_navigator/CN_MM_CAPABILITY_CONTRACT_v1.json')
        new = copy.deepcopy(old)
        del new['capabilities']['etf_flow']
        new['capabilities']['ethbtc_leadership']['authority'] = 'PRODUCTION'
        with self.assertRaisesRegex(ValueError, 'MISSING_REQUIRED_DOMAINS'):
            compare(old, new)
        new['capabilities']['etf_flow'] = old['capabilities']['etf_flow']
        failures = compare(old, new)
        self.assertIn('ethbtc_leadership:CHANGED:authority', failures)
        self.assertEqual(compare(old, old), [])
