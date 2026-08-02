from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path('scripts/api_agent/build_owner_bound_director_context.py')
spec = importlib.util.spec_from_file_location('ctx', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class OwnerBoundDirectorContextTests(unittest.TestCase):
    def make_capture(self, root: Path, name: str, ts: str, statuses: dict[str, str]) -> None:
        value = {
            'contract': 'DAILY_RAW_CAPTURE_INDEX_v1',
            'captured_at_utc': ts,
            'run_id': name,
            'capture_status': 'PASS',
            'calibration_eligible': True,
            'owners': [
                {
                    'owner_id': key,
                    'status': status,
                    'collector_exit_code': 0 if status == 'PASS' else 1,
                    'file_count': 1,
                    'total_bytes': 10,
                    'files': [{'path': f'{key}/receipt.json', 'sha256': key * 8, 'summary': {'status': status}}],
                }
                for key, status in statuses.items()
            ],
        }
        (root / f'{name}.json').write_text(json.dumps(value))

    def test_builds_latest_and_transition_without_inference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_capture(root, 'a', '2026-08-02T10:00:00Z', {'macro': 'PASS', 'spot': 'FAIL'})
            self.make_capture(root, 'b', '2026-08-02T14:00:00Z', {'macro': 'PASS', 'spot': 'PASS'})
            rows = module.load_capture_indexes(root)
            context = module.build_context(rows)
            self.assertEqual(context['latest_capture']['run_id'], 'b')
            self.assertEqual(context['coverage']['pass_ratio'], 1.0)
            spot = next(x for x in context['owner_status_transitions'] if x['owner_id'] == 'spot')
            self.assertTrue(spot['changed'])
            self.assertFalse(context['canonical_data_ping'])
            self.assertEqual(context['authority'], 'SHADOW_ONLY')
            self.assertIn('context_hash', context)

    def test_no_indexes_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, 'no_daily_capture_indexes'):
            module.build_context([])


if __name__ == '__main__':
    unittest.main()
