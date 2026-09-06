from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path('scripts/api_agent/build_weekly_calibration_context.py')
spec = importlib.util.spec_from_file_location('weekly_ctx_issue754', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class WeeklyDirectorIntradaySequenceTests(unittest.TestCase):
    def write_run(self, root: Path, name: str, stamp: str, *, phase: str = 'PRE_ROTATION',
                  receipt: bool = True, receipt_extra: dict | None = None,
                  evidence_count: int = 3, forecast_count: int = 3) -> Path:
        run = root / name
        run.mkdir(parents=True)
        output = {
            'summary': f'CYCLE_HEADER | PHASE={phase} | WARNING=NONE | DIRECTION=ADVANCING | CONFIDENCE=LOW\nDetails',
            'evidence_for': [f'for-{i}' for i in range(evidence_count)],
            'evidence_against': [f'against-{i}' for i in range(evidence_count)],
            'uncertainties': [f'uncertain-{i}' for i in range(evidence_count)],
            'forecast_candidates': [
                {
                    'metric_path': f'metric.{i}',
                    'horizon_days': 3,
                    'direction': 'UP',
                    'target_mode': 'PCT_MOVE',
                    'threshold_pct': float(i),
                    'rationale': 'intentionally omitted from compact representation',
                }
                for i in range(forecast_count)
            ],
        }
        (run / 'DAILY_DIRECTOR_OUTPUT.json').write_text(json.dumps(output), encoding='utf-8')
        if receipt:
            value = {
                'contract': 'API_AGENT_RECEIPT_v3',
                'created_at_utc': stamp,
                'output_hash': f'declared-{name}',
                'status': 'PASS',
                'task': 'DAILY_DIRECTOR_SHADOW',
            }
            if receipt_extra:
                value.update(receipt_extra)
            (run / 'DAILY_DIRECTOR_RECEIPT.json').write_text(json.dumps(value), encoding='utf-8')
        else:
            output['generated_at_utc'] = stamp
            (run / 'DAILY_DIRECTOR_OUTPUT.json').write_text(json.dumps(output), encoding='utf-8')
        return run

    def collect(self, root: Path):
        return module.collect_director_context(
            root,
            datetime(2026, 9, 3, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 4, 0, 0, tzinfo=timezone.utc),
        )

    def test_same_day_runs_are_preserved_compactly_while_legacy_surface_stays_latest_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name, stamp, phase in (
                ('090656', '2026-09-03T09:06:56Z', 'PRE_ROTATION'),
                ('132458', '2026-09-03T13:24:58Z', 'PRE_ROTATION'),
                ('171420', '2026-09-03T17:14:20Z', 'ROTATION_WATCH'),
            ):
                self.write_run(root, name, stamp, phase=phase)
            data = self.collect(root)
            self.assertEqual(data['daily_director_count'], 1)
            self.assertTrue(data['daily_director_rows'][0]['path'].endswith('171420/DAILY_DIRECTOR_OUTPUT.json'))
            self.assertEqual(data['daily_director_intraday_count'], 3)
            self.assertEqual(
                [row['source_timestamp_utc'] for row in data['daily_director_intraday_sequence']],
                ['2026-09-03T09:06:56Z', '2026-09-03T13:24:58Z', '2026-09-03T17:14:20Z'],
            )
            first = data['daily_director_intraday_sequence'][0]
            self.assertEqual(first['phase'], 'PRE_ROTATION')
            self.assertEqual(first['direction'], 'ADVANCING')
            self.assertEqual(first['confidence'], 'LOW')
            self.assertEqual(first['source_timestamp_origin'], 'receipt.created_at_utc')
            self.assertEqual(first['binding_status'], 'PASS')
            self.assertEqual(len(first['output_sha256']), 64)
            self.assertEqual(len(first['receipt_sha256']), 64)
            self.assertNotIn('output', first)
            self.assertNotIn('receipt', first)
            self.assertNotIn('rationale', first['forecast_candidates'][0])
            self.assertEqual(data['daily_director_intraday_status'], 'COMPLETE')

    def test_only_exact_timestamp_output_and_receipt_duplicates_are_collapsed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self.write_run(root, 'a', '2026-09-03T09:00:00Z')
            duplicate = root / 'b'
            duplicate.mkdir()
            (duplicate / 'DAILY_DIRECTOR_OUTPUT.json').write_bytes((first / 'DAILY_DIRECTOR_OUTPUT.json').read_bytes())
            (duplicate / 'DAILY_DIRECTOR_RECEIPT.json').write_bytes((first / 'DAILY_DIRECTOR_RECEIPT.json').read_bytes())
            variant = root / 'c'
            variant.mkdir()
            (variant / 'DAILY_DIRECTOR_OUTPUT.json').write_bytes((first / 'DAILY_DIRECTOR_OUTPUT.json').read_bytes())
            receipt = json.loads((first / 'DAILY_DIRECTOR_RECEIPT.json').read_text())
            receipt['response_id'] = 'different-receipt-binding'
            (variant / 'DAILY_DIRECTOR_RECEIPT.json').write_text(json.dumps(receipt))
            data = self.collect(root)
            self.assertEqual(data['daily_director_intraday_source_count'], 3)
            self.assertEqual(data['daily_director_intraday_count'], 2)
            self.assertEqual(data['daily_director_intraday_exact_duplicate_count'], 1)
            self.assertEqual(len({row['receipt_sha256'] for row in data['daily_director_intraday_sequence']}), 2)

    def test_missing_receipt_remains_visible_and_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_run(root, 'missing', '2026-09-03T10:00:00Z', receipt=False)
            data = self.collect(root)
            self.assertEqual(data['daily_director_intraday_count'], 1)
            row = data['daily_director_intraday_sequence'][0]
            self.assertEqual(row['source_timestamp_origin'], 'output.generated_at_utc')
            self.assertIsNone(row['receipt_sha256'])
            self.assertEqual(row['binding_status'], 'INCOMPLETE')
            self.assertEqual(data['daily_director_intraday_status'], 'INCOMPLETE')
            self.assertEqual(data['daily_director_intraday_diagnostics'][0]['reason'], 'RECEIPT_MISSING')

    def test_compaction_is_bounded_without_hiding_source_counts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_run(root, 'large', '2026-09-03T11:00:00Z', evidence_count=5, forecast_count=10)
            row = self.collect(root)['daily_director_intraday_sequence'][0]
            self.assertEqual(row['evidence_for_count'], 5)
            self.assertEqual(len(row['key_evidence_for']), module.DIRECTOR_COMPACT_EVIDENCE_LIMIT)
            self.assertTrue(row['key_evidence_for_truncated'])
            self.assertEqual(row['forecast_candidate_count'], 10)
            self.assertEqual(len(row['forecast_candidates']), module.DIRECTOR_COMPACT_FORECAST_LIMIT)
            self.assertTrue(row['forecast_candidates_truncated'])


if __name__ == '__main__':
    unittest.main()
