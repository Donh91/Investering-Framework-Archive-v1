import contextlib
import hashlib
import importlib.util
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


def load_owner(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


weekly = load_owner('scripts/daily_capture/build_weekly_market_close_package.py', 'weekly_owner_contract')
cfgi = load_owner('scripts/data_terminal/cfgi_owner_collector.py', 'cfgi_owner_contract')


class Response:
    def __init__(self, rows):
        self.rows = rows
        self.headers = {'X-Credits-Used': '3', 'X-Credits-Remaining': '97'}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({'data': self.rows}).encode()


class WeeklyCloseArchitectureTests(unittest.TestCase):
    def assert_non_binding(self, packet, authority):
        self.assertEqual(packet['authority'], authority)
        for key in ('canonical_data_ping', 'framework_state_change', 'portfolio_action'):
            self.assertIs(packet[key], False)

    def run_weekly(self, root, mode='final', omit_last=False):
        def fetch(symbol, start_ms, end_ms, base_url):
            rows = [[stamp, '10', '12', '9', '11', '5', stamp + 3_599_999]
                    for stamp in range(start_ms, end_ms, 3_600_000)]
            return rows[:-1] if omit_last else rows

        argv = ['weekly', '--output-root', str(root), '--mode', mode,
                '--now-utc', '2026-08-31T02:00:00Z']
        with patch('sys.argv', argv), patch.object(weekly, 'fetch_klines', side_effect=fetch), contextlib.redirect_stdout(io.StringIO()):
            weekly.main()

    def test_weekly_close_script_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            self.run_weekly(root)
            body = (root / '2026/W35/WEEKLY_MARKET_CLOSE_PACKAGE.json').read_bytes()
            packet = json.loads(body)
            receipt = json.loads((root / '2026/W35/WEEKLY_MARKET_CLOSE_RECEIPT.json').read_text())
            pointer = json.loads((root / 'LATEST_WEEKLY_MARKET_CLOSE.json').read_text())
            self.assertEqual(packet['contract'], 'WEEKLY_MARKET_CLOSE_PACKAGE_v3')
            self.assertEqual(receipt['contract'], 'WEEKLY_MARKET_CLOSE_RECEIPT_v3')
            self.assertEqual(pointer['contract'], 'WEEKLY_MARKET_CLOSE_POINTER_v3')
            self.assert_non_binding(packet, 'SHADOW_CALIBRATION_INPUT')
            self.assertIs(packet['final'], True)
            self.assertEqual(packet['completeness'], 'COMPLETE')
            self.assertEqual(set(packet['symbols']), {'BTCUSDT', 'ETHUSDT', 'ETHBTC'})
            for symbol in packet['symbols'].values():
                self.assertEqual(symbol['hour_count'], 168)
                self.assertEqual(len(symbol['daily_ranges']), 7)
            self.assertEqual(receipt['sha256'], hashlib.sha256(body).hexdigest())
            self.assertEqual(pointer['sha256'], receipt['sha256'])
            self.assertEqual((root.parent / pointer['path']).read_bytes(), body)
            self.assertIn('MASTER_MONDAY', receipt['handoff_targets'])

    def test_incomplete_final_week_does_not_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            with self.assertRaisesRegex(SystemExit, 'FINAL_WEEK_INCOMPLETE'):
                self.run_weekly(root, omit_last=True)
            self.assertFalse(root.exists())

    def test_delayed_sunday_preclose_fails_before_network_or_wrong_week_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            event = Path(tmp) / 'event.json'
            event.write_text(json.dumps({'schedule': '35 23 * * 0'}))
            argv = ['weekly', '--output-root', str(root), '--mode', 'preclose',
                    '--now-utc', '2026-10-12T00:41:00Z']
            env = {'GITHUB_EVENT_NAME': 'schedule', 'GITHUB_EVENT_PATH': str(event),
                   'GITHUB_RUN_ATTEMPT': '1'}
            with patch('sys.argv', argv), patch.dict(weekly.os.environ, env), patch.object(weekly, 'fetch_klines') as fetch:
                with self.assertRaisesRegex(ValueError, 'SCHEDULED_WEEK_ROLLOVER_UNBOUND'):
                    weekly.main()
            fetch.assert_not_called()
            self.assertFalse(root.exists())

    def test_monday_final_after_delay_still_closes_previous_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            event = Path(tmp) / 'event.json'
            event.write_text(json.dumps({'schedule': '5 2 * * 1'}))
            argv = ['weekly', '--output-root', str(root), '--mode', 'final',
                    '--now-utc', '2026-10-12T05:39:00Z']
            def fetch(symbol, start_ms, end_ms, base_url):
                return [[stamp, '10', '12', '9', '11', '5', stamp + 3_599_999]
                        for stamp in range(start_ms, end_ms, 3_600_000)]
            env = {'GITHUB_EVENT_NAME': 'schedule', 'GITHUB_EVENT_PATH': str(event),
                   'GITHUB_RUN_ATTEMPT': '1'}
            with patch('sys.argv', argv), patch.dict(weekly.os.environ, env), patch.object(weekly, 'fetch_klines', side_effect=fetch), contextlib.redirect_stdout(io.StringIO()):
                weekly.main()
            packet = json.loads((root / '2026/W41/WEEKLY_MARKET_CLOSE_PACKAGE.json').read_text())
            self.assertEqual(packet['close_mode'], 'FINAL_COMPLETED_ISO_WEEK')
            self.assertEqual(packet['iso_week'], 41)
            self.assertEqual(packet['symbols']['BTCUSDT']['hour_count'], 168)
            self.assertFalse((root / '2026/W42').exists())

    def test_scheduled_week_binding_rejects_rerun_dispatch_and_wrong_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            event = Path(tmp) / 'event.json'
            event.write_text(json.dumps({'schedule': '35 23 * * 0'}))
            sunday = datetime(2026, 10, 11, 21, 35, tzinfo=timezone.utc)
            weekly.validate_actions_week_binding(sunday, 'preclose', event_name='schedule',
                                                  event_path=str(event), run_attempt='1')
            with self.assertRaisesRegex(ValueError, 'RERUN_ORIGINAL_WEEK'):
                weekly.validate_actions_week_binding(sunday, 'preclose', event_name='schedule',
                                                      event_path=str(event), run_attempt='2')
            with self.assertRaisesRegex(ValueError, 'DISPATCH_ORIGINAL_WEEK'):
                weekly.validate_actions_week_binding(sunday, 'preclose', event_name='workflow_dispatch',
                                                      event_path=str(event), run_attempt='1')
            with self.assertRaisesRegex(ValueError, 'SCHEDULE_MODE_MISMATCH'):
                weekly.validate_actions_week_binding(sunday, 'final', event_name='schedule',
                                                      event_path=str(event), run_attempt='1')
            with self.assertRaisesRegex(ValueError, 'SCHEDULE_EVENT_UNAVAILABLE'):
                weekly.validate_actions_week_binding(sunday, 'preclose', event_name='schedule',
                                                      event_path=str(event) + '.missing', run_attempt='1')
            # ISO-year rollover: same fail-closed rule without guessing a week.
            jan_sunday = datetime(2027, 1, 3, 21, 35, tzinfo=timezone.utc)
            weekly.validate_actions_week_binding(jan_sunday, 'preclose', event_name='schedule',
                                                  event_path=str(event), run_attempt='1')
            with self.assertRaisesRegex(ValueError, 'SCHEDULED_WEEK_ROLLOVER_UNBOUND'):
                weekly.validate_actions_week_binding(datetime(2027, 1, 4, 0, 30, tzinfo=timezone.utc),
                                                      'preclose', event_name='schedule',
                                                      event_path=str(event), run_attempt='1')

    def test_master_monday_reuses_final_source_without_mutation_or_api_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            self.run_weekly(root, mode='final')
            paths = sorted(root.rglob('*.json'))
            before = {str(p): p.read_bytes() for p in paths}
            argv = ['weekly', '--output-root', str(root), '--mode', 'final',
                    '--now-utc', '2026-08-31T06:27:00Z', '--require-existing-final']
            event = Path(tmp) / 'master-monday-event.json'
            event.write_text(json.dumps({'schedule': '40 2 * * 1'}))
            env = {'GITHUB_EVENT_NAME': 'schedule', 'GITHUB_EVENT_PATH': str(event),
                   'GITHUB_RUN_ATTEMPT': '1'}
            with patch('sys.argv', argv), patch.dict(weekly.os.environ, env), patch.object(weekly, 'fetch_klines') as fetch, contextlib.redirect_stdout(io.StringIO()) as output:
                weekly.main()
            fetch.assert_not_called()
            receipt = json.loads(output.getvalue())
            self.assertEqual(receipt['status'], 'PASS')
            self.assertEqual(receipt['mode'], 'REUSE_VERIFIED_FINAL_NO_SOURCE_MUTATION')
            self.assertEqual(before, {str(p): p.read_bytes() for p in paths})
            self.assertIn('--require-existing-final', Path('.github/workflows/weekly-api-calibration-shadow.yml').read_text())
            with self.assertRaisesRegex(ValueError, 'SCHEDULE_MODE_MISMATCH'):
                weekly.validate_actions_week_binding(datetime(2026, 8, 31, 6, 27, tzinfo=timezone.utc),
                                                      'final', event_name='schedule', event_path=str(event),
                                                      run_attempt='1', consumer=False)

    def test_master_monday_missing_or_corrupt_final_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            with self.assertRaisesRegex(SystemExit, 'EXISTING_FINAL_MARKET_CLOSE_INTEGRITY_FAIL_CLOSED'):
                weekly.verify_existing_final(datetime(2026, 8, 31, 6, 27, tzinfo=timezone.utc), root)
            self.assertFalse(root.exists())
            self.run_weekly(root, mode='final')
            receipt_path = root / '2026/W35/WEEKLY_MARKET_CLOSE_RECEIPT.json'
            original = receipt_path.read_bytes()
            bad = json.loads(original)
            bad['sha256'] = '0' * 64
            receipt_path.write_text(json.dumps(bad))
            with patch.object(weekly, 'fetch_klines') as fetch:
                with self.assertRaisesRegex(SystemExit, 'EXISTING_FINAL_MARKET_CLOSE_INTEGRITY_FAIL_CLOSED'):
                    weekly.verify_existing_final(datetime(2026, 8, 31, 6, 27, tzinfo=timezone.utc), root)
                fetch.assert_not_called()
            self.assertEqual(json.loads(receipt_path.read_text())['sha256'], '0' * 64)
            receipt_path.write_bytes(original)
            with self.assertRaisesRegex(SystemExit, 'EXISTING_FINAL_MARKET_CLOSE_INTEGRITY_FAIL_CLOSED'):
                weekly.verify_existing_final(datetime(2026, 9, 7, 6, 27, tzinfo=timezone.utc), root)

    def test_preclose_is_partial_and_non_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            self.run_weekly(root, mode='preclose')
            packet = json.loads((root / '2026/W36/WEEKLY_MARKET_CLOSE_PACKAGE.json').read_text())
            self.assertIs(packet['final'], False)
            self.assertEqual(packet['completeness'], 'PARTIAL')
            self.assert_non_binding(packet, 'SHADOW_CALIBRATION_INPUT')

    def run_cfgi(self, root, rows, key='synthetic-test-key'):
        environment = {'CFGI_API_KEY': key} if key else {}
        with patch('sys.argv', ['cfgi', '--output-dir', str(root)]), patch.dict(cfgi.os.environ, environment, clear=True), patch.object(cfgi.urllib.request, 'urlopen', return_value=Response(rows)) as request, contextlib.redirect_stdout(io.StringIO()):
            cfgi.main()
        request.assert_called_once()

    def test_cfgi_owner_is_shadow_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'cfgi'
            self.run_cfgi(root, [{'symbol': symbol, 'score': 50, 'stale': False}
                                 for symbol in ('MARKET', 'BTC', 'ETH')])
            body = (root / 'owner_snapshot.json').read_bytes()
            packet = json.loads(body)
            receipt = json.loads((root / 'receipt.json').read_text())
            self.assertEqual(packet['contract'], 'CFGI_OWNER_SNAPSHOT_v3')
            self.assertEqual(receipt['contract'], 'CFGI_OWNER_RECEIPT_v3')
            self.assert_non_binding(packet, 'SHADOW_OBSERVATION_ONLY')
            self.assertEqual(packet['symbols'], ['MARKET', 'BTC', 'ETH'])
            self.assertEqual(packet['timeframe'], '4h')
            self.assertEqual(packet['fields'], ['score'])
            self.assertEqual(packet['billing']['expected_credits'], 3)
            self.assertEqual(packet['billing']['credits_used'], 3)
            self.assertEqual(receipt['sha256'], hashlib.sha256(body).hexdigest())
            self.assertEqual(receipt['row_count'], 3)
            self.assertEqual(receipt['status'], 'PASS')

    def test_stale_cfgi_row_is_degraded_without_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'cfgi'
            self.run_cfgi(root, [{'symbol': 'BTC', 'score': 50, 'stale': True}])
            packet = json.loads((root / 'owner_snapshot.json').read_text())
            receipt = json.loads((root / 'receipt.json').read_text())
            self.assert_non_binding(packet, 'SHADOW_OBSERVATION_ONLY')
            self.assertEqual(packet['rows'][0]['owner_status'], 'STALE')
            self.assertEqual(receipt['status'], 'DEGRADED')

    def test_empty_cfgi_response_does_not_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'cfgi'
            with self.assertRaisesRegex(SystemExit, 'cfgi_empty'):
                self.run_cfgi(root, [])
            self.assertFalse(root.exists())

    def test_missing_cfgi_key_does_not_request_or_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'cfgi'
            with patch('sys.argv', ['cfgi', '--output-dir', str(root)]), patch.dict(cfgi.os.environ, {}, clear=True), patch.object(cfgi.urllib.request, 'urlopen') as request:
                with self.assertRaisesRegex(SystemExit, 'CFGI_API_KEY_missing'):
                    cfgi.main()
            request.assert_not_called()
            self.assertFalse(root.exists())

    def test_schedule_precedes_weekly_bridge(self):
        text = Path('.github/workflows/sunday-market-close-and-cfgi.yml').read_text()
        self.assertIn("cron: '35 23 * * 0'", text)
        self.assertIn("timezone: 'Europe/Copenhagen'", text)
        self.assertIn('LATEST_WEEKLY_MARKET_CLOSE', Path('scripts/daily_capture/build_weekly_market_close_package.py').read_text())


if __name__ == '__main__':
    unittest.main()
