from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path('scripts/api_agent/build_weekly_calibration_context.py')
spec = importlib.util.spec_from_file_location('weekly_ctx', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class WeeklyCalibrationContextV4Tests(unittest.TestCase):
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
