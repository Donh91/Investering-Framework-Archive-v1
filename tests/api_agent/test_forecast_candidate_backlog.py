from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
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
                'created_unix': time.time(),
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

    def test_materializer_censors_frozen_legacy_target_unit_shape_without_rewrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pending = root / 'PENDING'
            output = root / 'output.json'
            receipt = root / 'receipt.json'
            output.write_text(json.dumps({'forecast_candidates': [{
                'metric_path': 'spot.BTCUSDT.close',
                'direction': 'DOWN',
                'threshold': 64699.1,
                'range_low': None,
                'range_high': None,
                'horizon_days': 3,
                'rationale': 'legacy fixture',
            }]}))
            receipt.write_text(json.dumps({
                'output_hash': 'd' * 64,
                'model': 'gpt-5.6-luna',
                'task': 'DAILY_DIRECTOR_SHADOW',
                'prompt_hash': 'e' * 64,
                'context_hash': 'f' * 64,
            }))

            run = subprocess.run([
                sys.executable, str(MATERIALIZER), '--output', str(output), '--receipt', str(receipt), '--pending-root', str(pending)
            ], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
            result = json.loads(run.stdout)
            self.assertEqual(result['created_count'], 0)
            self.assertEqual(result['legacy_censored_count'], 1)
            self.assertFalse(result['legacy_rewrite_performed'])
            self.assertFalse(result['legacy_rescore_performed'])
            self.assertEqual(result['legacy_censored'][0]['reason'], 'LEGACY_V1_TARGET_UNIT_AMBIGUOUS')
            self.assertEqual(list(pending.rglob('*.json')), [])

    def test_materializer_still_fails_closed_for_new_malformed_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pending = root / 'PENDING'
            output = root / 'output.json'
            receipt = root / 'receipt.json'
            output.write_text(json.dumps({'forecast_candidates': [{
                'metric_path': 'spot.BTCUSDT.close',
                'direction': 'DOWN',
                'threshold_pct': 2.0,
                'target_value': None,
                'range_low': None,
                'range_high': None,
                'horizon_days': 3,
                'rationale': 'malformed v2 fixture',
            }]}))
            receipt.write_text(json.dumps({'output_hash': '1' * 64}))

            run = subprocess.run([
                sys.executable, str(MATERIALIZER), '--output', str(output), '--receipt', str(receipt), '--pending-root', str(pending)
            ], cwd=REPO_ROOT, check=False, capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('FORECAST_CANDIDATE_TARGET_MODE_REQUIRED', run.stderr + run.stdout)
            self.assertEqual(list(pending.rglob('*.json')), [])

    def test_handoff_deduplicates_and_quarantines_legacy_target_units(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'research/api_agent/forecast_candidates/PENDING/2026/08/01').mkdir(parents=True, exist_ok=True)
            (root / 'research/api_agent/forecast_candidates/PENDING/2026/08/02').mkdir(parents=True, exist_ok=True)
            (root / 'research/api_agent/forecast_candidates/PENDING/2026/08/03').mkdir(parents=True, exist_ok=True)
            (root / 'research/api_agent/forecast_candidates/PENDING/2026/08/04').mkdir(parents=True, exist_ok=True)
            base = {
                'contract': 'FORECAST_CANDIDATE_v1',
                'candidate_id': 'dup-id',
                'candidate': {'target_mode': 'PCT_MOVE'},
            }
            (root / 'research/api_agent/forecast_candidates/PENDING/2026/08/01/a.json').write_text(json.dumps(base))
            (root / 'research/api_agent/forecast_candidates/PENDING/2026/08/02/b.json').write_text(json.dumps(base))
            legacy = {
                'contract': 'FORECAST_CANDIDATE_v1',
                'candidate_id': 'legacy-id',
                'candidate': {'threshold': 64699.1, 'direction': 'DOWN'},
            }
            (root / 'research/api_agent/forecast_candidates/PENDING/2026/08/03/c.json').write_text(json.dumps(legacy))
            normal = {
                'contract': 'FORECAST_CANDIDATE_v1',
                'candidate_id': 'normal-id',
                'candidate': {'target_mode': 'ABSOLUTE_VALUE'},
            }
            (root / 'research/api_agent/forecast_candidates/PENDING/2026/08/04/d.json').write_text(json.dumps(normal))
            subprocess.run([sys.executable, str(HANDOFF), '--repo-root', str(root)], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
            handoff = json.loads((root / 'LATEST_HANDOFF.json').read_text())
            backlog = handoff['api_agent']['forecast_candidate_backlog']
            self.assertEqual(backlog['file_count'], 4)
            self.assertEqual(backlog['distinct_candidate_count'], 3)
            self.assertEqual(backlog['duplicate_count'], 1)
            self.assertEqual(backlog['legacy_target_unit_ambiguous_count'], 1)
            self.assertEqual(backlog['actionable_count'], 2)
            self.assertEqual(backlog['censored_reason_counts'][LEGACY_TARGET_UNIT_REASON], 1)


if __name__ == '__main__':
    unittest.main()
