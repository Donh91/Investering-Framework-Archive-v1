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


    def test_metronome_dispatch_reuses_only_current_valid_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            event = Path(tmp) / 'event.json'
            def bind(inputs, ref='refs/heads/main'):
                event.write_text(json.dumps({'ref': ref, 'inputs': inputs}))
            def validate(when, mode='final', consumer=False, attempt='1'):
                weekly.validate_actions_week_binding(datetime.fromisoformat(when.replace('Z', '+00:00')),
                    mode, event_name='workflow_dispatch', event_path=str(event),
                    run_attempt=attempt, consumer=consumer)
            # Monday 2026-11-30 is ISO W49; FINAL is for the completed W48.
            bind({'mode': 'final'})
            validate('2026-11-30T01:05:00Z')
            for timestamp in ('2026-11-30T00:30:00Z', '2026-12-01T02:00:00Z'):
                with self.assertRaisesRegex(ValueError, 'DISPATCH_ORIGINAL_WEEK_UNBOUND'):
                    validate(timestamp)
            bind({'mode': 'preclose'})
            with self.assertRaisesRegex(ValueError, 'DISPATCH_ORIGINAL_WEEK_UNBOUND'):
                validate('2026-11-30T01:10:00Z')
            validate('2026-11-29T22:35:00Z', mode='preclose')
            with self.assertRaisesRegex(ValueError, 'DISPATCH_ORIGINAL_WEEK_UNBOUND'):
                validate('2026-11-30T01:10:00Z', mode='preclose')
            bind({'mode': 'final'}, ref='refs/heads/feature')
            with self.assertRaisesRegex(ValueError, 'DISPATCH_ORIGINAL_WEEK_UNBOUND'):
                validate('2026-11-30T01:10:00Z')
            bind({'mode': 'final'})
            with self.assertRaisesRegex(ValueError, 'RERUN_ORIGINAL_WEEK_UNBOUND'):
                validate('2026-11-30T01:10:00Z', attempt='2')
            # Weekly consumer has a DIFFERENT workflow input schema and
            # remains impossible before 02:40 Copenhagen.
            bind({'force_reissue': 'false'})
            validate('2026-11-30T01:40:00Z', consumer=True)
            with self.assertRaisesRegex(ValueError, 'DISPATCH_ORIGINAL_WEEK_UNBOUND'):
                validate('2026-11-30T01:30:00Z', consumer=True)
            with self.assertRaisesRegex(ValueError, 'DISPATCH_ORIGINAL_WEEK_UNBOUND'):
                validate('2026-12-01T01:40:00Z', consumer=True)
            with self.assertRaisesRegex(ValueError, 'DISPATCH_ORIGINAL_WEEK_UNBOUND'):
                validate('2026-11-30T01:40:00Z', consumer=False)

    def test_metronome_dispatch_produces_and_consumes_final_without_reissue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            event = Path(tmp) / 'event.json'
            event.write_text(json.dumps({'ref': 'refs/heads/main', 'inputs': {'mode': 'final'}}))
            env = {'GITHUB_EVENT_NAME': 'workflow_dispatch',
                   'GITHUB_EVENT_PATH': str(event), 'GITHUB_RUN_ATTEMPT': '1'}
            def fetch(symbol, start_ms, end_ms, base_url):
                return [[stamp, '10', '12', '9', '11', '5', stamp + 3_599_999]
                        for stamp in range(start_ms, end_ms, 3_600_000)]
            argv = ['weekly', '--output-root', str(root), '--mode', 'final',
                    '--now-utc', '2026-11-30T02:00:00Z']
            with patch('sys.argv', argv), patch.dict(weekly.os.environ, env, clear=True), \
                 patch.object(weekly, 'fetch_klines', side_effect=fetch):
                with contextlib.redirect_stdout(io.StringIO()):
                    weekly.main()
            pointer = json.loads((root / 'LATEST_WEEKLY_MARKET_CLOSE.json').read_text())
            self.assertTrue(pointer['final'])
            self.assertEqual((pointer['iso_year'], pointer['iso_week']), (2026, 48))
            originals = {str(p): p.read_bytes() for p in root.rglob('*.json')}
            event.write_text(json.dumps({'ref': 'refs/heads/main', 'inputs': {'force_reissue': 'false'}}))
            argv.append('--require-existing-final')
            with patch('sys.argv', argv), patch.dict(weekly.os.environ, env, clear=True), \
                 patch.object(weekly, 'fetch_klines') as request, \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                weekly.main()
            request.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())['status'], 'PASS')
            self.assertEqual(originals, {str(p): p.read_bytes() for p in root.rglob('*.json')})

    def test_late_native_final_cron_reuses_source_bytes_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            self.run_weekly(root, mode='final')
            original = {str(p): p.read_bytes() for p in root.rglob('*.json')}
            argv = ['weekly', '--output-root', str(root), '--mode', 'final',
                    '--now-utc', '2026-08-31T10:00:00Z']
            # A delayed scheduled producer is valid on local Monday, but
            # cannot overwrite its earlier successful source issuance.
            ev = Path(tmp) / 'event.json'
            ev.write_text(json.dumps({'schedule': '5 2 * * 1'}))
            env = {'GITHUB_EVENT_NAME': 'schedule', 'GITHUB_EVENT_PATH': str(ev),
                   'GITHUB_RUN_ATTEMPT': '1'}
            with patch('sys.argv', argv), patch.dict(weekly.os.environ, env, clear=True), \
                 patch.object(weekly, 'fetch_klines') as fetch, \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                weekly.main()
            fetch.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())['mode'],
                             'REUSE_VERIFIED_FINAL_NO_SOURCE_MUTATION')
            self.assertEqual(original, {str(p): p.read_bytes() for p in root.rglob('*.json')})
            # A corrupted original may NOT be silently repaired by a later
            # native run: frozen first-source provenance takes priority.
            ptr = root / 'LATEST_WEEKLY_MARKET_CLOSE.json'
            ptr.write_text(json.dumps({'status': 'PASS'}))
            with patch('sys.argv', argv), patch.dict(weekly.os.environ, env, clear=True), \
                 patch.object(weekly, 'fetch_klines') as fetch:
                with self.assertRaisesRegex(SystemExit,
                                             'EXISTING_FINAL_MARKET_CLOSE_INTEGRITY_FAIL_CLOSED'):
                    weekly.main()
            fetch.assert_not_called()

    def test_first_final_replaces_same_week_preclose_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'weekly_close'
            def fetch(symbol, start_ms, end_ms, base_url):
                return [[stamp, '10', '12', '9', '11', '5', stamp + 3_599_999]
                        for stamp in range(start_ms, end_ms, 3_600_000)]
            with patch('sys.argv', ['weekly', '--output-root', str(root),
                 '--mode', 'preclose', '--now-utc', '2026-08-30T20:40:00Z']), \
                 patch.object(weekly, 'fetch_klines', side_effect=fetch), \
                 contextlib.redirect_stdout(io.StringIO()):
                weekly.main()
            pre = json.loads((root / '2026/W35/WEEKLY_MARKET_CLOSE_PACKAGE.json').read_text())
            self.assertFalse(pre['final'])
            with patch('sys.argv', ['weekly', '--output-root', str(root),
                 '--mode', 'final', '--now-utc', '2026-08-31T02:00:00Z']), \
                 patch.object(weekly, 'fetch_klines', side_effect=fetch), \
                 contextlib.redirect_stdout(io.StringIO()):
                weekly.main()
            final = json.loads((root / '2026/W35/WEEKLY_MARKET_CLOSE_PACKAGE.json').read_text())
            self.assertTrue(final['final'])
            self.assertEqual(final['completeness'], 'COMPLETE')

    def test_all_weekly_workflow_python_steps_are_gated_before_execution(self):
        # Contract-level safeguard: every Python command in BOTH existing
        # workflows is downstream of the first strict event-binding source
        # check. A new earlier Python step must fail this test, not silently
        # create another CFGI-like unguarded dispatch.
        sunday = Path(".github/workflows/sunday-market-close-and-cfgi.yml").read_text()
        weekly = Path(".github/workflows/weekly-api-calibration-shadow.yml").read_text()
        sunday_steps = sunday.split("      - name: ")
        weekly_steps = weekly.split("      - name: ")
        first_sunday = next(i for i,s in enumerate(sunday_steps)
                             if s.startswith("Build verified weekly price ranges"))
        first_weekly = next(i for i,s in enumerate(weekly_steps)
                             if s.startswith("Verify and reuse existing final ISO-week close"))
        self.assertIn("build_weekly_market_close_package.py", sunday_steps[first_sunday])
        self.assertIn("--mode", sunday_steps[first_sunday])
        self.assertIn("build_weekly_market_close_package.py", weekly_steps[first_weekly])
        self.assertIn("--require-existing-final", weekly_steps[first_weekly])
        for name, steps, first in (("Sunday", sunday_steps, first_sunday),
                                   ("Monday", weekly_steps, first_weekly)):
            for i, step in enumerate(steps):
                if "python " in step or "python3 " in step:
                    self.assertGreaterEqual(i, first, (name, i, step[:90]))
            self.assertNotIn("continue-on-error: true", steps[first])
        # Paid API work and separate jobs must be gated by the freeze job:
        # a bad dispatch that rejects the first source step cannot continue.
        self.assertIn("needs.freeze.result == 'success'", weekly)
        self.assertIn("needs: freeze", weekly)
        self.assertIn("needs: [freeze, calibration]", weekly)
        self.assertIn("--mode \"${{ steps.mode.outputs.mode }}\"", sunday)

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
