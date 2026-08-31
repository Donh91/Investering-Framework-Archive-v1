"""Synthetic source-shape controls. No provider calls or production evidence."""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import unittest
import tempfile


ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts/daily_capture' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


weekly = load('build_weekly_market_close_package')
hourly = load('build_hourly_sequence')
capture = load('build_capture_index')
START = datetime(2026, 8, 24, tzinfo=timezone.utc)
HOUR = 3_600_000


def klines(count=168, start_time=START):
    start = int(start_time.timestamp() * 1000)
    return [[start + i * HOUR, str(100 + i), str(102 + i), str(99 + i),
             str(101 + i), '10', start + (i + 1) * HOUR - 1,
             '1000', 10, '5', '500', '0'] for i in range(count)]


def run_weekly(root, rows, *, mode='final', now='2026-08-31T00:10:00Z'):
    args = ['weekly', '--output-root', str(root), '--mode', mode, '--now-utc', now]
    with patch.object(weekly, 'fetch_klines', return_value=rows), patch('sys.argv', args), contextlib.redirect_stdout(io.StringIO()):
        weekly.main()


def read_package(root):
    return json.loads(next(root.rglob('WEEKLY_MARKET_CLOSE_PACKAGE.json')).read_text())


def candle(open_, close):
    return dict(open=open_, close=close, high=max(open_, close)+1, low=min(open_, close)-1,
                volume=10, quote_volume=100, trade_count=1, taker_buy_base_volume=5,
                taker_buy_quote_volume=50, taker_sell_quote_volume=50, taker_buy_quote_share=.5)


class HourlyIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_complete_week_remains_eligible_and_shadow_only(self):
        run_weekly(self.root, klines())
        p = read_package(self.root)
        self.assertEqual(p['completeness'], 'COMPLETE')
        self.assertTrue(all(p[k] is False for k in ('canonical_data_ping', 'framework_state_change', 'portfolio_action')))
        self.assertEqual(p['symbols']['BTCUSDT']['hour_count'], 168)
        self.assertEqual(p['symbols']['BTCUSDT']['weekly_open'], 100)
        self.assertEqual(p['symbols']['BTCUSDT']['weekly_close'], 268)

    def check_week_boundary(self, start_time):
        now = (start_time+timedelta(days=7, minutes=10)).isoformat()
        run_weekly(self.root, klines(start_time=start_time), now=now)
        p = read_package(self.root)
        self.assertEqual(p['symbols']['BTCUSDT']['hour_count'], 168)
        self.assertEqual(p['symbols']['BTCUSDT']['expected_hour_count'], 168)
        self.assertEqual((p['iso_year'], p['iso_week']), tuple(start_time.isocalendar()[:2]))

    def check_invalid_week(self, mutation):
        rows = klines()
        if mutation == 'duplicate_and_gap': rows[42] = copy.deepcopy(rows[41])
        elif mutation == 'gap': rows.pop(42)
        elif mutation == 'outside_window':
            rows[0][0] -= HOUR; rows[0][6] -= HOUR
        elif mutation == 'off_grid':
            rows[42][0] += 1; rows[42][6] += 1
        elif mutation == 'wrong_close': rows[42][6] -= 1
        elif mutation == 'nan': rows[42][4] = 'NaN'
        elif mutation == 'infinity': rows[42][2] = 'Infinity'
        elif mutation == 'boolean': rows[42][1:5] = ['1', '2', '0.5', True]
        elif mutation == 'negative_volume': rows[42][5] = '-1'
        elif mutation == 'invalid_ohlc': rows[42][2] = '1'
        elif mutation == 'short_row': rows[42] = rows[42][:3]
        old = self.root / 'previous' / 'WEEKLY_MARKET_CLOSE_PACKAGE.json'
        old.parent.mkdir(); old.write_bytes(b'previous archived package\n')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with self.assertRaises((ValueError, SystemExit)):
            run_weekly(self.root, rows)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(after, before)

    def test_provider_order_cannot_change_weekly_open_or_close(self):
        run_weekly(self.root, list(reversed(klines())))
        p = read_package(self.root)
        self.assertEqual(p['symbols']['BTCUSDT']['weekly_open'], 100)
        self.assertEqual(p['symbols']['BTCUSDT']['weekly_close'], 268)
        self.assertEqual(p['symbols']['BTCUSDT']['daily_ranges'][0]['open'], 100)

    def test_preclose_excludes_open_candle_and_reports_gap(self):
        rows = klines(3); rows.pop(0)
        run_weekly(self.root, rows, mode='preclose', now='2026-08-24T02:30:00Z')
        p = read_package(self.root)
        self.assertIs(p['final'], False)
        self.assertEqual(p['completeness'], 'PARTIAL')
        self.assertEqual(p['symbols']['BTCUSDT']['hour_count'], 1)
        self.assertEqual(p['symbols']['BTCUSDT']['expected_hour_count'], 2)
        self.assertEqual(p['symbols']['BTCUSDT']['completeness'], 'DEGRADED')

    def test_gap_does_not_turn_multi_hour_price_or_oi_change_into_one_hour(self):
        stamp = int(START.timestamp()*1000)
        spot = {'BTCUSDT': {stamp: candle(100, 105), stamp+2*HOUR: candle(120, 126), stamp+3*HOUR: candle(126, 132.3)}}
        oi = {'BTCUSDT': {stamp: {'oi': 100}, stamp+2*HOUR: {'oi': 130}, stamp+3*HOUR: {'oi': 143}}}
        rows = hourly.build_rows(START, START+timedelta(hours=3), spot, oi, {}, {}, 'PASS', 'PASS')
        # Existing open-to-close boundary convention remains; no new return definition.
        self.assertAlmostEqual(rows[0]['btc_return_1h_pct'], 5)
        self.assertAlmostEqual(rows[2]['btc_return_1h_pct'], 5)
        self.assertIsNone(rows[2]['btc_oi_change_1h_pct'])
        self.assertEqual(rows[2]['btc_price_oi_state'], 'UNAVAILABLE')
        self.assertAlmostEqual(rows[3]['btc_return_1h_pct'], 5)
        self.assertAlmostEqual(rows[3]['btc_oi_change_1h_pct'], 10)

    def check_invalid_spot(self, mutation):
        rows = klines(3)
        if mutation == 'duplicate': rows.append(copy.deepcopy(rows[0]))
        elif mutation == 'off_grid': rows[1][0] += 1
        elif mutation == 'wrong_close': rows[1][6] -= 1
        elif mutation == 'nan': rows[1][4] = 'NaN'
        elif mutation == 'boolean': rows[1][1:5] = ['1', '2', '0.5', True]
        with self.assertRaises(hourly.SourceError):
            hourly.parse_spot(json.dumps(rows).encode(), 'BTCUSDT')

    def test_spot_parser_preserves_legitimate_zero_volume_and_price_decline(self):
        rows = klines(2)
        rows[1][4] = '100'; rows[1][5] = '0'; rows[1][7] = '0'; rows[1][9] = '0'; rows[1][10] = '0'
        parsed = hourly.parse_spot(json.dumps(rows).encode(), 'BTCUSDT')
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[rows[1][0]]['close'], 100)
        self.assertIsNone(parsed[rows[1][0]]['taker_buy_quote_share'])

    def check_owner_inventory(self, sequence_disabled):
        for name in capture.OWNER_DIRS.values():
            d = self.root / name; d.mkdir(); (d/'receipt.json').write_text('{"status":"PASS"}')
        codes = {owner: 0 for owner in capture.OWNER_DIRS}
        if sequence_disabled: codes['binance_spot'] = 78
        status = self.root/'status.json'; status.write_text(json.dumps(codes))
        output = self.root/'captures'
        args = ['capture', '--root', str(self.root), '--status-file', str(status), '--output-root', str(output), '--run-id', 'synthetic-audit', '--trigger', 'test']
        with patch('sys.argv', args), patch.object(capture, 'extract_metrics', return_value={}), contextlib.redirect_stdout(io.StringIO()):
            capture.main()
        p = json.loads(next(p for p in output.rglob('*.json') if p.name != 'LATEST.json').read_text())
        self.assertEqual(p['owners_passed'], sum(o['status']=='PASS' for o in p['owners']))
        self.assertEqual(p['owners_planned'], len(p['owners']))
        self.assertEqual(p['owners_disabled'], int(sequence_disabled))
        self.assertEqual(p['owners_active_planned'], len(p['owners'])-int(sequence_disabled))
        self.assertEqual(p['anchor_core_passed'], 3)
        self.assertEqual(p['status'], 'COMPLETE')
        self.assertIs(p['portfolio_action'], False)
        self.assertIs(p['framework_state_change'], False)


def add_case(name, method, value):
    def run(self):
        getattr(self, method)(value)
    run.__name__ = name
    setattr(HourlyIntegrityTests, name, run)


for case in ('duplicate_and_gap', 'gap', 'outside_window', 'off_grid', 'wrong_close',
             'nan', 'infinity', 'boolean', 'negative_volume', 'invalid_ohlc', 'short_row'):
    add_case('test_invalid_week_' + case, 'check_invalid_week', case)
for case in ('duplicate', 'off_grid', 'wrong_close', 'nan', 'boolean'):
    add_case('test_invalid_spot_' + case, 'check_invalid_spot', case)
add_case('test_owner_inventory_all_pass', 'check_owner_inventory', False)
add_case('test_owner_inventory_sequence_disabled', 'check_owner_inventory', True)
add_case('test_utc_week_at_dst', 'check_week_boundary', datetime(2026, 3, 23, tzinfo=timezone.utc))
add_case('test_utc_week_at_iso_year_boundary', 'check_week_boundary', datetime(2025, 12, 29, tzinfo=timezone.utc))
