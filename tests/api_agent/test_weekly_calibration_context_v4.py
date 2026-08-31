from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path('scripts/api_agent/build_weekly_calibration_context.py')
spec = importlib.util.spec_from_file_location('weekly_ctx', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class WeeklyCalibrationContextV4Tests(unittest.TestCase):
    def experiment_fixture(self, root):
        registry = root / 'registry.json'
        registry.write_text(json.dumps({'contract': 'EXPERIMENT_LIFECYCLE_REGISTRY_v1', 'candidates': []}))
        outcomes = root / 'outcomes'
        outcomes.mkdir()
        return registry, outcomes, datetime(2026, 8, 24, tzinfo=timezone.utc), datetime(2026, 8, 31, tzinfo=timezone.utc)

    def test_current_and_legacy_outcomes_preserve_censorship_and_utc_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry, outcomes, start, end = self.experiment_fixture(Path(tmp))
            rows = [
                {'contract': 'MATURED_OUTCOME_v2', 'forecast_id': 'legacy', 'status': 'CENSORED', 'reason': 'METRIC_UNAVAILABLE', 'created_at_utc': '2026-08-24T00:00:00Z'},
                {'contract': 'MATURED_OUTCOME_v3', 'forecast_id': 'current', 'status': 'MATURED', 'result': 'MISS', 'return_pct': -1., 'created_at_utc': '2026-08-30T23:59:59Z', 'authority': {'portfolio_action': False}},
                {'contract': 'MATURED_OUTCOME_v3', 'forecast_id': 'censored', 'status': 'CENSORED', 'reason': 'METRIC_UNAVAILABLE', 'created_at_utc': '2026-08-24T01:00:00Z'},
                {'contract': 'MATURED_OUTCOME_v3', 'forecast_id': 'end_excluded', 'status': 'CENSORED', 'reason': 'METRIC_UNAVAILABLE', 'created_at_utc': '2026-08-31T00:00:00Z'},
                {'contract': 'MATURED_OUTCOME_v3', 'forecast_id': 'offset_before_start', 'status': 'CENSORED', 'reason': 'METRIC_UNAVAILABLE', 'created_at_utc': '2026-08-24T00:30:00+02:00'},
            ]
            for i, row in enumerate(rows):
                (outcomes / f'{i}.json').write_text(json.dumps(row))
            before = {p: p.read_bytes() for p in outcomes.iterdir()}
            data = module.load_experiment_learning(registry, outcomes, start, end)
            selected = {x['forecast_id']: x for x in data['new_matured_outcomes']}
            self.assertEqual(set(selected), {'legacy', 'current', 'censored'})
            self.assertIsNone(selected['censored']['return_pct'])
            self.assertEqual(selected['current']['result'], 'MISS')
            self.assertEqual(selected['current']['source_contract'], 'MATURED_OUTCOME_v3')
            self.assertEqual(selected['current']['source_authority'], {'portfolio_action': False})
            self.assertFalse(data['outcome_scoring_performed'])
            self.assertTrue(data['matured_outcome_evidence_available'])
            self.assertEqual(before, {p: p.read_bytes() for p in outcomes.iterdir()})

    def test_invalid_outcomes_are_diagnosed_without_losing_usable_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry, outcomes, start, end = self.experiment_fixture(Path(tmp))
            good = {'contract': 'MATURED_OUTCOME_v3', 'forecast_id': 'good', 'status': 'CENSORED', 'reason': 'METRIC_UNAVAILABLE', 'created_at_utc': '2026-08-25T00:00:00Z'}
            for defect in ['truncated', 'wrong_contract', 'contract_type', 'naive_time', 'bad_time', 'not_object', 'nonfinite', 'wrong_status', 'censored_with_score', 'matured_without_return']:
                with self.subTest(defect=defect):
                    for p in outcomes.iterdir(): p.unlink()
                    (outcomes / 'good.json').write_text(json.dumps(good))
                    bad = dict(good)
                    if defect == 'wrong_contract': bad['contract'] = 'UNKNOWN_v9'
                    if defect == 'contract_type': bad['contract'] = []
                    if defect == 'naive_time': bad['created_at_utc'] = '2026-08-25T00:00:00'
                    if defect == 'bad_time': bad['created_at_utc'] = 'invalid'
                    if defect == 'not_object': bad = []
                    if defect == 'nonfinite': bad['return_pct'] = float('nan')
                    if defect == 'wrong_status': bad['status'] = 'UNKNOWN_STATUS'
                    if defect == 'censored_with_score': bad['result'] = 'HIT'
                    if defect == 'matured_without_return': bad.update(status='MATURED', result='HIT')
                    (outcomes / 'bad.json').write_text('{' if defect == 'truncated' else json.dumps(bad))
                    data = module.load_experiment_learning(registry, outcomes, start, end)
                    self.assertEqual([x['forecast_id'] for x in data['new_matured_outcomes']], ['good'])
                    self.assertFalse(data['matured_outcome_evidence_available'])
                    self.assertTrue(data['outcome_ingestion_diagnostics'])
                    self.assertTrue(data['outcome_ingestion_diagnostics'][0]['path'].endswith('bad.json'))

    def test_unreadable_outcome_directory_is_not_confirmed_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry, outcomes, start, end = self.experiment_fixture(Path(tmp))
            def denied_walk(root, onerror):
                onerror(PermissionError(13, 'denied', str(root)))
                return iter(())
            with patch.object(module.os, 'walk', side_effect=denied_walk):
                data = module.load_experiment_learning(registry, outcomes, start, end)
            self.assertFalse(data['matured_outcome_evidence_available'])
            self.assertEqual(data['outcome_ingestion_diagnostics'][0]['reason'], 'OUTCOME_DIRECTORY_UNREADABLE')

    def test_missing_outcome_root_is_not_a_confirmed_empty_interval(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry, outcomes, start, end = self.experiment_fixture(Path(tmp))
            empty = module.load_experiment_learning(registry, outcomes, start, end)
            self.assertEqual(empty['new_matured_outcomes'], [])
            self.assertTrue(empty['matured_outcome_evidence_available'])
            outcomes.rmdir()
            missing = module.load_experiment_learning(registry, outcomes, start, end)
            self.assertIsNone(missing['new_matured_outcomes'])
            self.assertFalse(missing['matured_outcome_evidence_available'])

    def test_created_unix_is_supported(self):
        stamp = 1785845400
        result = module.find_time({}, {'created_unix': stamp})
        self.assertEqual(result, datetime.fromtimestamp(stamp, timezone.utc))

    def test_legacy_context_is_non_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / 'legacy'
            (legacy / '02_HYPOTHESIS_REGISTRY').mkdir(parents=True)
            (legacy / '05_NEW_SYSTEM_CROSSWALK').mkdir(parents=True)
            row = {
                'legacy_observation_id': 'LKO-TEST-001',
                'topic': 'PULLBACK_WARNING',
                'claim': 'Test hypothesis for weekly review.',
                'sensors': ['breadth_change'],
                'horizon_claimed': '5_days',
                'legacy_ruling': 'PLAUSIBLE_NOT_PROVEN',
                'canonical_evidence': False,
            }
            (legacy / '02_HYPOTHESIS_REGISTRY/ACTIVE_LEGACY_HYPOTHESES.jsonl').write_text(json.dumps(row) + '\n')
            (legacy / '05_NEW_SYSTEM_CROSSWALK/PROSPECTIVE_VALIDATION_QUEUE.json').write_text(json.dumps({'queue': [{'hypothesis_id': 'LKO-TEST-001', 'target_event': 'PULLBACK', 'priority': 'P0', 'current_status': 'WAITING_FOR_PROSPECTIVE_MATCH'}]}))
            context = module.load_legacy_context(legacy)
            self.assertEqual(context['status'], 'AVAILABLE_RESEARCH_ONLY')
            self.assertFalse(context['canonical_evidence'])
            self.assertFalse(context['validation_queue'][0]['candidate_freeze_allowed'])
            self.assertFalse(context['validation_queue'][0]['automatic_promotion'])

    def test_weekly_context_binds_final_168h_close_separately_from_enriched_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            capture = root / '03_DAILY_CAPTURE_LOGS'
            weekly = capture / 'weekly'
            (weekly / '2026/W32').mkdir(parents=True)
            pointer = {
                'contract': 'LATEST_WEEKLY_CALIBRATION_POINTER_v3',
                'iso_year': 2026,
                'iso_week': 32,
                'path': 'weekly/2026/W32.json',
                'sequence_facts_path': 'weekly/2026/W32/WEEKLY_SEQUENCE_FACTS.json',
                'readiness': 'DEGRADED',
                'hourly_rows': 40,
                'missing_hour_count': 128,
            }
            (weekly / 'LATEST_WEEKLY_CALIBRATION.json').write_text(json.dumps(pointer))
            (weekly / '2026/W32.json').write_text(json.dumps({'contract': 'WEEKLY_CAPTURE_PACK_v2', 'hourly_rows': 40}))
            (weekly / '2026/W32/WEEKLY_SEQUENCE_FACTS.json').write_text(json.dumps({'gap_diagnostics': {'observed_hours': 40, 'missing_hour_count': 128}}))
            symbols = {
                asset: {'hour_count': 168, 'weekly_open': 1.0, 'weekly_high': 2.0, 'weekly_low': 0.5, 'weekly_close': 1.5}
                for asset in ('BTCUSDT', 'ETHUSDT', 'ETHBTC')
            }
            preflight = {
                'packet': {'status': 'FULL_MASTER_MONDAY_INPUT'},
                'quality': {'required_capabilities': {'final_completed_iso_week_BTC_ETH_ETHBTC_available': True}},
                'settled_week': {
                    'contract': 'WEEKLY_MARKET_CLOSE_PACKAGE_v3',
                    'final': True,
                    'close_mode': 'FINAL_COMPLETED_ISO_WEEK',
                    'completeness': 'COMPLETE',
                    'symbols': symbols,
                },
                'missing': [{'field': 'weekly_v2_2_enriched_sequence', 'blocking_level': 'CONFIDENCE_REDUCING'}],
                'package_sha256': 'abc',
            }
            preflight_path = root / 'MASTER_MONDAY_GAP_FILL_PACKAGE.json'
            preflight_path.write_text(json.dumps(preflight))
            value = module.load_weekly_owned_context(weekly / 'LATEST_WEEKLY_CALIBRATION.json', capture, preflight_path)
            self.assertTrue(value['master_monday_preflight']['final_168h_market_close_available'])
            self.assertEqual(value['weekly_sequence_facts']['gap_diagnostics']['missing_hour_count'], 128)
            self.assertEqual(value['master_monday_preflight']['settled_week']['symbols']['BTCUSDT']['hour_count'], 168)
            self.assertEqual(value['weekly_capture_pointer']['readiness'], 'DEGRADED')


if __name__ == '__main__':
    unittest.main()
