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
    def make_capture(self, root: Path, name: str, ts: str, statuses: dict[str, str], metrics: dict | None = None) -> None:
        value = {
            'contract': 'DAILY_RAW_CAPTURE_INDEX_v2' if metrics is not None else 'DAILY_RAW_CAPTURE_INDEX_v1',
            'captured_at_utc': ts,
            'run_id': name,
            'capture_status': 'PASS',
            'calibration_eligible': True,
            'market_metrics': metrics or {},
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

    def make_live_anchor(self, root: Path, name: str, ts: str, metrics: dict) -> None:
        value = {
            'contract': 'DAILY_LIVE_ANCHOR_INDEX_v3',
            'captured_at_utc': ts,
            'run_id': name,
            'status': 'COMPLETE',
            'capture_lane': 'LIVE_POINT_IN_TIME_ANCHOR',
            'anchor_core_passed': 3,
            'anchor_core_planned': 3,
            'market_metrics': metrics,
        }
        (root / f'{name}.json').write_text(json.dumps(value))

    def make_legacy(self, root: Path) -> Path:
        legacy = root / 'legacy'
        hypotheses = legacy / '02_HYPOTHESIS_REGISTRY'
        crosswalk = legacy / '05_NEW_SYSTEM_CROSSWALK'
        hypotheses.mkdir(parents=True)
        crosswalk.mkdir(parents=True)
        row = {
            'legacy_observation_id': 'LKO-PULLBACK-TEST',
            'topic': 'PULLBACK_WARNING',
            'claim': 'Breadth and leverage may warn before a pullback.',
            'sensors': ['breadth_change', 'open_interest_change'],
            'horizon_claimed': '5-7_days',
            'legacy_ruling': 'PLAUSIBLE_NOT_PROVEN',
            'evidence_level': 'L2',
            'canonical_evidence': False,
        }
        (hypotheses / 'ACTIVE_LEGACY_HYPOTHESES.jsonl').write_text(json.dumps(row) + '\n')
        (crosswalk / 'PROSPECTIVE_VALIDATION_QUEUE.json').write_text(json.dumps({'queue': [{'hypothesis_id': 'LKO-PULLBACK-TEST', 'priority': 'P0', 'target_event': 'PULLBACK', 'required_live_sensors': ['breadth_change'], 'current_status': 'WAITING_FOR_PROSPECTIVE_MATCH', 'candidate_creation_allowed': True, 'candidate_freeze_allowed': False, 'automatic_promotion': False}]}))
        return legacy

    def test_builds_latest_and_transition_without_inference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_capture(root, 'a', '2026-08-02T10:00:00Z', {'macro': 'PASS', 'spot': 'FAIL'}, {'x': 1})
            self.make_capture(root, 'b', '2026-08-02T14:00:00Z', {'macro': 'PASS', 'spot': 'PASS'}, {'x': 2})
            context = module.build_context(module.load_capture_indexes(root))
            self.assertEqual(context['contract'], 'OWNER_BOUND_DAILY_DIRECTOR_CONTEXT_v4')
            self.assertEqual(context['latest_capture']['run_id'], 'b')
            self.assertEqual(context['coverage']['pass_ratio'], 1.0)
            spot = next(x for x in context['owner_status_transitions'] if x['owner_id'] == 'spot')
            self.assertTrue(spot['changed'])
            self.assertEqual(context['coverage']['comparable_numeric_metrics'], 1)
            self.assertFalse(context['canonical_data_ping'])
            self.assertEqual(context['authority'], 'SHADOW_ONLY')
            self.assertIn('context_hash', context)

    def test_live_anchor_v3_becomes_latest_metric_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_capture(root, 'raw', '2026-08-08T14:00:00Z', {'spot': 'PASS'}, {'spot': {'btc': 65015.0}, 'breadth': {'advancers': 44}})
            self.make_live_anchor(root, 'live', '2026-08-15T09:01:46Z', {'spot': {'btc': 62900.0}, 'breadth': {'advancers': 48}})
            context = module.build_context(module.load_capture_indexes(root))
            self.assertEqual(context['latest_capture']['run_id'], 'live')
            self.assertEqual(context['latest_capture']['capture_contract'], 'DAILY_LIVE_ANCHOR_INDEX_v3')
            self.assertEqual(context['latest_capture']['capture_lane'], 'LIVE_POINT_IN_TIME_ANCHOR')
            self.assertEqual(context['latest_capture']['anchor_core_passed'], 3)
            self.assertEqual(context['previous_capture']['run_id'], 'raw')
            self.assertEqual(context['coverage']['capture_contract'], 'DAILY_LIVE_ANCHOR_INDEX_v3')
            self.assertEqual(context['coverage']['anchor_core_passed'], 3)
            self.assertEqual(context['coverage']['comparable_numeric_metrics'], 2)
            self.assertEqual(context['predecessor_selection_rule'], 'latest_supported_metric_bearing_capture')

    def test_newer_non_metric_raw_v1_does_not_hide_live_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_capture(root, 'raw', '2026-08-08T14:00:00Z', {'spot': 'PASS'}, {'x': 1})
            self.make_live_anchor(root, 'live', '2026-08-15T09:01:46Z', {'x': 2})
            self.make_capture(root, 'newer_v1', '2026-08-15T10:00:00Z', {'spot': 'PASS'}, None)
            context = module.build_context(module.load_capture_indexes(root))
            self.assertEqual(context['latest_capture']['run_id'], 'live')
            self.assertEqual(context['previous_capture']['run_id'], 'raw')
            self.assertEqual(context['coverage']['comparable_numeric_metrics'], 1)

    def test_legacy_lane_is_available_but_non_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            captures = root / 'captures'
            captures.mkdir()
            self.make_capture(captures, 'a', '2026-08-02T10:00:00Z', {'spot': 'PASS'}, {'x': 1})
            self.make_capture(captures, 'b', '2026-08-02T14:00:00Z', {'spot': 'PASS'}, {'x': 2})
            context = module.build_context(module.load_capture_indexes(captures), self.make_legacy(root))
            legacy = context['legacy_research_context']
            self.assertEqual(legacy['status'], 'AVAILABLE_RESEARCH_ONLY')
            self.assertFalse(legacy['canonical_evidence'])
            self.assertEqual(len(legacy['hypotheses']), 1)
            self.assertFalse(legacy['validation_queue'][0]['candidate_freeze_allowed'])
            self.assertFalse(legacy['validation_queue'][0]['automatic_promotion'])

    def test_missing_legacy_lane_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_capture(root, 'a', '2026-08-02T10:00:00Z', {'spot': 'PASS'}, {'x': 1})
            context = module.build_context(module.load_capture_indexes(root))
            self.assertEqual(context['legacy_research_context']['status'], 'UNAVAILABLE')
            self.assertFalse(context['legacy_research_context']['canonical_evidence'])

    def test_no_indexes_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, 'no_daily_capture_indexes'):
            module.build_context([])


if __name__ == '__main__':
    unittest.main()
