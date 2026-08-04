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


if __name__ == '__main__':
    unittest.main()
