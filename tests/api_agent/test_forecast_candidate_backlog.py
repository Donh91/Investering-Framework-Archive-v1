from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MATERIALIZER = REPO_ROOT / 'scripts/api_agent/materialize_forecast_candidates.py'
HANDOFF = REPO_ROOT / 'scripts/architecture/build_latest_handoff.py'


class ForecastCandidateBacklogTests(unittest.TestCase):
    def test_materializer_is_idempotent_across_full_pending_tree(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pending = root / 'PENDING'
            output = root / 'output.json'
            receipt = root / 'receipt.json'
            candidate = {
                'metric_path': 'spot.BTCUSDT.close',
                'direction': 'UP',
                'target_mode': 'PCT_MOVE',
                'threshold_pct': 3.0,
                'target_value': None,
                'range_low': None,
                'range_high': None,
                'horizon_days': 3,
                'rationale': 'fixture',
            }
            output.write_text(json.dumps({'forecast_candidates': [candidate]}))
            receipt.write_text(json.dumps({
                'output_hash': 'a' * 64,
                'model': 'gpt-5.6-luna',
                'task': 'DAILY_DIRECTOR_SHADOW',
                'prompt_hash': 'b' * 64,
                'context_hash': 'c' * 64,
            }))

            first = subprocess.run([
                sys.executable, str(MATERIALIZER), '--output', str(output), '--receipt', str(receipt), '--pending-root', str(pending)
            ], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
            first_result = json.loads(first.stdout)
            self.assertEqual(first_result['created_count'], 1)
            created = Path(first_result['paths'][0])
            old_dir = pending / '2026/08/01'
            old_dir.mkdir(parents=True, exist_ok=True)
            old_path = old_dir / created.name
            shutil.move(str(created), old_path)
            for parent in [created.parent, created.parent.parent, created.parent.parent.parent]:
                try:
                    parent.rmdir()
                except OSError:
                    pass

            second = subprocess.run([
                sys.executable, str(MATERIALIZER), '--output', str(output), '--receipt', str(receipt), '--pending-root', str(pending)
            ], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
            second_result = json.loads(second.stdout)
            self.assertEqual(second_result['created_count'], 0)
            self.assertEqual(second_result['existing_candidate_count'], 1)
            self.assertTrue(second_result['idempotent_across_pending_tree'])
            self.assertEqual(len(list(pending.rglob('*.json'))), 1)

    def test_handoff_deduplicates_and_quarantines_legacy_target_units(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pending = root / 'research/api_agent/forecast_candidates/PENDING'

            legacy = {
                'contract': 'FORECAST_CANDIDATE_v1',
                'candidate_id': 'legacy-1',
                'created_at_utc': '2026-08-03T00:00:00Z',
                'ratification_status': 'PENDING',
                'candidate': {'metric_path': 'spot.ETHUSDT.close', 'direction': 'DOWN', 'threshold': 1800.0, 'horizon_days': 1},
            }
            actionable = {
                'contract': 'FORECAST_CANDIDATE_v1',
                'candidate_id': 'valid-1',
                'created_at_utc': '2026-08-10T00:00:00Z',
                'ratification_status': 'PENDING',
                'candidate': {
                    'metric_path': 'spot.BTCUSDT.close', 'direction': 'UP', 'target_mode': 'ABSOLUTE_VALUE',
                    'threshold_pct': None, 'target_value': 70000.0, 'range_low': None, 'range_high': None, 'horizon_days': 3,
                },
            }
            for day, row in [('03', legacy), ('04', legacy), ('10', actionable)]:
                path = pending / f'2026/08/{day}' / f"{row['candidate_id']}.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(row))

            subprocess.run([
                sys.executable, str(HANDOFF), '--repo-root', str(root)
            ], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
            handoff = json.loads((root / 'LATEST_HANDOFF.json').read_text())

            self.assertEqual(handoff['pending_forecast_candidate_file_count'], 3)
            self.assertEqual(handoff['pending_forecast_candidate_distinct_count'], 2)
            self.assertEqual(handoff['pending_forecast_candidate_count'], 1)
            self.assertEqual(handoff['quarantined_legacy_forecast_candidate_count'], 1)
            self.assertEqual(handoff['duplicate_forecast_candidate_file_count'], 1)
            self.assertEqual(len(handoff['pending_forecast_candidates']), 1)
            self.assertTrue(handoff['pending_forecast_candidates'][0].endswith('valid-1.json'))
            self.assertEqual(len(handoff['quarantined_legacy_forecast_candidates']), 1)
            self.assertTrue(handoff['quarantined_legacy_forecast_candidates'][0].endswith('legacy-1.json'))


if __name__ == '__main__':
    unittest.main()
