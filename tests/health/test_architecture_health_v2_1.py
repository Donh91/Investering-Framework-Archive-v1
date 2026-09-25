from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path('scripts/health/build_architecture_health.py')
spec = importlib.util.spec_from_file_location('architecture_health', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class ArchitectureHealthV21Tests(unittest.TestCase):
    def test_daily_director_uses_paired_receipt_created_unix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'research/api_agent/outputs/daily/2026/08/04/120000/DAILY_DIRECTOR_OUTPUT.json'
            output.parent.mkdir(parents=True)
            output.write_text(json.dumps({'status': 'READY'}))
            receipt = output.with_name('DAILY_DIRECTOR_RECEIPT.json')
            receipt.write_text(json.dumps({'contract': 'API_AGENT_RECEIPT_v3', 'created_unix': 1785844800, 'status': 'PASS'}))
            path, value, stamp, receipt_path = module.latest_paired_output(root / 'research/api_agent/outputs/daily', 'DAILY_DIRECTOR_OUTPUT.json', 'DAILY_DIRECTOR_RECEIPT.json')
            self.assertEqual(path, output)
            self.assertEqual(receipt_path, receipt)
            self.assertEqual(stamp, datetime.fromtimestamp(1785844800, timezone.utc))
            self.assertEqual(value['status'], 'READY')

    def test_capture_latest_pointer_cannot_replace_capture_owner_rows(self):
        # The daily capture pointer repeats the target captured_at_utc, so the
        # (timestamp, path) tie-break picks captures/LATEST.json ('L' > '2') and
        # the owner population silently becomes 0/0.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / '03_DAILY_CAPTURE_LOGS/captures'
            capture = root / '2026/09/22/165540_gh-1-1.json'
            capture.parent.mkdir(parents=True)
            stamp = '2026-09-22T16:55:40Z'
            capture.write_text(json.dumps({
                'captured_at_utc': stamp,
                'contract': 'DAILY_LIVE_ANCHOR_INDEX_v3',
                'owners': [{'owner_id': 'a', 'status': 'PASS'}, {'owner_id': 'b', 'status': 'DISABLED'}],
            }))
            (root / 'LATEST.json').write_text(json.dumps({
                'captured_at_utc': stamp,
                'contract': 'DAILY_LIVE_ANCHOR_LATEST_POINTER_v1',
                'path': 'captures/2026/09/22/165540_gh-1-1.json',
            }))
            unfiltered_path, _, _ = module.latest_json(root)
            self.assertEqual(unfiltered_path.name, 'LATEST.json')
            path, value, ts = module.latest_json(root, exclude_names=('LATEST.json',))
            self.assertEqual(path, capture)
            self.assertEqual(len(value['owners']), 2)
            self.assertEqual(ts, datetime(2026, 9, 22, 16, 55, 40, tzinfo=timezone.utc))

    def test_capture_pointer_exclusion_reports_real_owner_coverage_not_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            captures = repo / '03_DAILY_CAPTURE_LOGS/captures'
            capture = captures / '2026/09/22/165540_gh-1-1.json'
            capture.parent.mkdir(parents=True)
            stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
            capture.write_text(json.dumps({'captured_at_utc': stamp, 'owners': [
                {'owner_id': 'a', 'status': 'PASS'},
                {'owner_id': 'b', 'status': 'PASS'},
            ]}))
            (captures / 'LATEST.json').write_text(json.dumps({'captured_at_utc': stamp, 'path': 'x'}))
            out_json = repo / 'health.json'
            out_md = repo / 'health.md'
            import sys
            argv = sys.argv
            sys.argv = ['build_architecture_health.py', '--repo-root', str(repo), '--json-output', str(out_json), '--md-output', str(out_md)]
            try:
                module.main()
            finally:
                sys.argv = argv
            health = json.loads(out_json.read_text())
            self.assertEqual(health['owners']['count'], 2)
            self.assertEqual(health['owners']['pass_count'], 2)
            self.assertNotIn('OWNER_POPULATION_EMPTY', health['blockers'])
            self.assertEqual(health['latest_capture_path'], str(capture))

    def test_nested_cfgi_billing_is_discovered(self):
        owner = {'files': [{'summary': {'billing': {'credits_remaining': 98765}}}]}
        self.assertEqual(module.find_cfgi_remaining(owner), 98765)

    def owner_rows(self, *, fred='DISABLED', binance_spot='DISABLED', micro='PASS', okx='PASS', breadth='PASS', cfgi='PASS'):
        return [
            {'owner_id': 'fred_macro', 'status': fred},
            {'owner_id': 'binance_spot', 'status': binance_spot},
            {'owner_id': 'binance_microstructure', 'status': micro},
            {'owner_id': 'okx_swap', 'status': okx},
            {'owner_id': 'top100_breadth', 'status': breadth},
            {'owner_id': 'cfgi_sentiment', 'status': cfgi},
        ]

    def test_empty_owner_population_cannot_support_green_when_capture_exists(self):
        self.assertEqual(
            module.owner_population_finding({'trigger': 'schedule'}, []),
            ('OWNER_POPULATION_EMPTY', 1),
        )

    def test_missing_capture_does_not_duplicate_empty_owner_finding(self):
        self.assertIsNone(module.owner_population_finding(None, []))

    def test_non_macro_schedule_accepts_only_intentional_disabled_owners(self):
        capture = {'trigger': 'schedule', 'captured_at_utc': '2026-09-24T20:13:00Z'}
        self.assertIsNone(module.owner_population_finding(capture, self.owner_rows()))

    def test_macro_schedule_requires_fred_pass(self):
        capture = {'trigger': 'schedule', 'captured_at_utc': '2026-09-25T04:13:00Z'}
        self.assertEqual(
            module.owner_population_finding(capture, self.owner_rows()),
            ('OWNER_COVERAGE_DEGRADED', 1),
        )
        self.assertIsNone(
            module.owner_population_finding(capture, self.owner_rows(fred='PASS'))
        )

    def test_manual_dispatch_requires_fred_pass(self):
        capture = {'trigger': 'workflow_dispatch', 'captured_at_utc': '2026-09-25T00:00:00Z'}
        self.assertEqual(
            module.owner_population_finding(capture, self.owner_rows()),
            ('OWNER_COVERAGE_DEGRADED', 1),
        )
        self.assertIsNone(
            module.owner_population_finding(capture, self.owner_rows(fred='PASS'))
        )

    def test_sequence_owned_binance_spot_must_stay_disabled_in_anchor_lane(self):
        capture = {'trigger': 'schedule', 'captured_at_utc': '2026-09-24T20:13:00Z'}
        self.assertEqual(
            module.owner_population_finding(capture, self.owner_rows(binance_spot='PASS')),
            ('OWNER_COVERAGE_DEGRADED', 1),
        )

    def test_unexpected_disabled_active_owner_is_degraded(self):
        capture = {'trigger': 'schedule', 'captured_at_utc': '2026-09-24T20:13:00Z'}
        self.assertEqual(
            module.owner_population_finding(capture, self.owner_rows(cfgi='DISABLED')),
            ('OWNER_COVERAGE_DEGRADED', 1),
        )

    def test_missing_or_duplicate_expected_owner_is_degraded(self):
        capture = {'trigger': 'schedule', 'captured_at_utc': '2026-09-24T20:13:00Z'}
        rows = self.owner_rows()
        self.assertEqual(
            module.owner_population_finding(capture, rows[:-1]),
            ('OWNER_COVERAGE_DEGRADED', 1),
        )
        duplicate = rows + [dict(rows[-1])]
        self.assertEqual(
            module.owner_population_finding(capture, duplicate),
            ('OWNER_COVERAGE_DEGRADED', 1),
        )

    def test_missing_experiment_receipt_sync_is_amber_finding(self):
        self.assertEqual(
            module.experiment_receipt_sync_finding(None, None),
            ('NO_EXPERIMENT_RECEIPT_SYNC', 1),
        )

    def test_failed_experiment_receipt_sync_is_red_finding(self):
        self.assertEqual(
            module.experiment_receipt_sync_finding({'status': 'FAIL'}, 1.0),
            ('EXPERIMENT_RECEIPT_SYNC_FAILED', 2),
        )

    def test_stale_experiment_receipt_sync_is_amber_finding(self):
        self.assertEqual(
            module.experiment_receipt_sync_finding({'status': 'PASS'}, 73.0),
            ('EXPERIMENT_RECEIPT_SYNC_STALE', 1),
        )

    def test_unavailable_experiment_receipt_sync_is_amber_even_when_fresh(self):
        self.assertEqual(
            module.experiment_receipt_sync_finding(
                {'status': 'DEGRADED', 'sync_state': 'UNAVAILABLE', 'source_reachable': False},
                0.1,
            ),
            ('EXPERIMENT_RECEIPT_SYNC_UNAVAILABLE', 1),
        )

    def test_source_stale_experiment_receipt_sync_is_amber_even_when_sync_file_is_fresh(self):
        self.assertEqual(
            module.experiment_receipt_sync_finding(
                {'status': 'DEGRADED', 'sync_state': 'STALE', 'source_reachable': True},
                0.1,
            ),
            ('EXPERIMENT_RECEIPT_SOURCE_STALE', 1),
        )

    def test_healthy_experiment_receipt_sync_has_no_finding(self):
        self.assertIsNone(
            module.experiment_receipt_sync_finding(
                {'status': 'PASS', 'sync_state': 'HEALTHY_NO_CHANGE', 'source_reachable': True},
                12.0,
            )
        )

    def test_claimed_healthy_sync_without_verified_source_is_amber(self):
        self.assertEqual(
            module.experiment_receipt_sync_finding(
                {'status': 'PASS', 'sync_state': 'HEALTHY_NO_CHANGE', 'source_reachable': False},
                0.1,
            ),
            ('EXPERIMENT_RECEIPT_SYNC_SOURCE_NOT_VERIFIED', 1),
        )

    def test_status_scope_does_not_claim_aggregate_system_health(self):
        self.assertEqual(
            module.STATUS_SCOPE,
            'ARCHITECTURE_EVIDENCE_ONLY_NOT_AGGREGATE_SYSTEM_HEALTH',
        )


if __name__ == '__main__':
    unittest.main()
