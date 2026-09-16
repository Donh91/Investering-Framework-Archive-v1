from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module

preflight = load_module('mm_preflight_v3_precision', ROOT / 'scripts/master_monday/build_preflight_package_v3.py')
publisher = load_module('mm_publisher_precision', ROOT / 'scripts/master_monday/publish_master_monday_outputs.py')

class WeeklyPrecisionRegressionTests(unittest.TestCase):
    def test_labor_day_week_has_four_expected_sessions(self):
        self.assertEqual(
            preflight.expected_nyse_sessions(2026, 37),
            ['2026-09-08', '2026-09-09', '2026-09-10', '2026-09-11'],
        )

    def test_normal_week_has_five_expected_sessions(self):
        sessions = preflight.expected_nyse_sessions(2026, 36)
        self.assertEqual(len(sessions), 5)
        self.assertEqual(sessions[0], '2026-08-31')
        self.assertEqual(sessions[-1], '2026-09-04')

    def test_available_registry_with_incomplete_outcomes_is_not_called_unavailable(self):
        score = publisher.fallback_scorecard({
            'experiment_learning': {
                'status': 'AVAILABLE',
                'matured_outcome_evidence_available': False,
                'outcome_ingestion_status': 'INCOMPLETE',
                'new_matured_outcomes': None,
            }
        })
        self.assertEqual(score['experiment_registry_status'], 'AVAILABLE')
        self.assertEqual(score['status'], 'INCOMPLETE_EXPERIMENT_OUTCOME_INGESTION')
        self.assertEqual(score['outcome_ingestion_status'], 'INCOMPLETE')

    def test_missing_registry_still_fails_closed(self):
        score = publisher.fallback_scorecard({
            'experiment_learning': {
                'status': 'UNAVAILABLE_REGISTRY_MISSING',
                'matured_outcome_evidence_available': False,
                'new_matured_outcomes': None,
            }
        })
        self.assertEqual(score['status'], 'UNAVAILABLE_EXPERIMENT_REGISTRY')

if __name__ == '__main__':
    unittest.main()
