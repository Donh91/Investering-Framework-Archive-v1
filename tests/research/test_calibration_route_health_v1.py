import json
import tempfile
import unittest
from pathlib import Path
from scripts.research.calibration_route_health_v1 import inspect_routes, PUBLIC_INDEX, V2_LEDGER


class CalibrationRoutes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = '05_CYCLE_NAVIGATOR/public_scorecards/2026/W47/CN34_PUBLIC_SCORECARD.json'
        self.pointer = {'forecast_week': '2026-W47', 'public_issue_number': 34, 'scorecard_path': self.path, 'price_range_score': 47.38}
        self.scorecard = {'contract': 'CN_PUBLIC_WEEKLY_SCORECARD_v1', 'authority': 'PUBLIC_FORECAST_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY', 'forecast_week': '2026-W47', 'outcome_week': '2026-W47', 'public_issue_number': 34, 'status': 'FINAL_DUAL_TRACK', 'price_range_precision': {'score': 47.38}}
        self.write(PUBLIC_INDEX, {'latest_completed_score': self.pointer})
        self.write(self.path, self.scorecard)
        self.write(V2_LEDGER, {'contract': 'CN_FORWARD_RANGE_FREEZE_v2', 'forecast_week': '2026-W47', 'public_issue_number': 34})

    def write(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value) + '\n')

    def test_legacy_empty_with_current_data_is_visible(self):
        result = inspect_routes(self.root, 0)
        self.assertEqual(result['status'], 'LEGACY_LEDGER_EMPTY_NEWER_SCORECARD_PRESENT')
        self.assertEqual(result['current_public_scorecard']['price_range_score'], 47.38)
        self.assertEqual(result['v2_freeze_record_n'], 1)
        self.assertFalse(result['score_method_conversion_performed'])
        self.assertFalse(result['scientific_admission'])

    def test_distinct_nonempty_sources_stay_separate(self):
        self.assertEqual(inspect_routes(self.root, 3)['status'], 'DISTINCT_SCORE_METHODS_PRESENT')

    def test_wrong_identity(self):
        self.scorecard['public_issue_number'] = 35
        self.write(self.path, self.scorecard)
        self.assertEqual(inspect_routes(self.root, 0)['status'], 'CURRENT_ROUTE_UNVERIFIED')

    def test_wrong_path(self):
        self.pointer['scorecard_path'] = '../wrong.json'
        self.write(PUBLIC_INDEX, {'latest_completed_score': self.pointer})
        self.assertEqual(inspect_routes(self.root, 0)['status'], 'CURRENT_ROUTE_UNVERIFIED')

    def test_missing_or_invalid_source(self):
        (self.root / V2_LEDGER).unlink()
        self.assertEqual(inspect_routes(self.root, 0)['status'], 'CURRENT_ROUTE_UNVERIFIED')
