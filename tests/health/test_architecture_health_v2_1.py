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

    def test_nested_cfgi_billing_is_discovered(self):
        owner = {'files': [{'summary': {'billing': {'credits_remaining': 98765}}}]}
        self.assertEqual(module.find_cfgi_remaining(owner), 98765)

    def test_empty_owner_population_cannot_support_green_when_capture_exists(self):
        self.assertEqual(
            module.owner_population_finding(True, [], 0),
            ('OWNER_POPULATION_EMPTY', 1),
        )

    def test_missing_capture_does_not_duplicate_empty_owner_finding(self):
        self.assertIsNone(module.owner_population_finding(False, [], 0))

    def test_healthy_owner_population_has_no_owner_finding(self):
        owners = [
            {'owner_id': 'a', 'status': 'PASS'},
            {'owner_id': 'b', 'status': 'PASS'},
        ]
        self.assertIsNone(module.owner_population_finding(True, owners, 2))

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
