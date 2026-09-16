from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path('scripts/master_monday/publish_master_monday_outputs.py')
spec = importlib.util.spec_from_file_location('publish_master_monday_outputs', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def packet(*, generated='2026-09-15T08:00:00Z', ids=None, contradictions=None):
    return {
        'contract': 'MASTER_MONDAY_LEARNING_PACKET_v1',
        'generated_at_utc': generated,
        'live_consumption_allowed': False,
        'new_learning': [{'semantic_identity': item} for item in (ids or [])],
        'negative_findings': [],
        'range_context': [],
        'contradictions': contradictions or [],
        'method_improvement_candidates': [],
        'strengthened': [],
        'weakened': [],
    }


def receipt(at='2026-09-15T09:00:00Z'):
    return {'created_unix': int(module.parse_time(at).timestamp())}


def test_no_incremental_input_is_evaluable_false():
    context = {'experiment_learning': {'active_candidates': [{'semantic_identity': 'A'}]}}
    impact = module.build_learning_decision_impact(context, packet(ids=['A']), receipt(), 2026, 38)
    assert impact['assessment_status'] == 'EVALUABLE_NO_INCREMENTAL_INPUT'
    assert impact['learning_input_present'] is True
    assert impact['changed_calibration_decision'] is False
    assert impact['exact_input_responsible'] == []
    assert impact['potential_incremental_inputs'] == []


def test_novel_input_is_not_falsely_scored_as_zero_value():
    context = {'experiment_learning': {'active_candidates': [{'semantic_identity': 'A'}]}}
    impact = module.build_learning_decision_impact(context, packet(ids=['A', 'B']), receipt(), 2026, 38)
    assert impact['assessment_status'] == 'NOT_EVALUABLE_NOVEL_INPUT_NOT_CONSUMED'
    assert impact['changed_calibration_decision'] is None
    assert impact['potential_incremental_inputs'] == ['B']
    assert impact['automatic_deletion'] is False


def test_structured_delta_without_semantic_identity_remains_not_evaluable():
    context = {'experiment_learning': {}}
    impact = module.build_learning_decision_impact(context, packet(contradictions=[{'claim': 'x'}]), receipt(), 2026, 38)
    assert impact['assessment_status'] == 'NOT_EVALUABLE_NOVEL_INPUT_NOT_CONSUMED'
    assert impact['changed_calibration_decision'] is None
    assert impact['potential_incremental_inputs'] == ['NONEMPTY:contradictions']


def test_late_packet_is_excluded_prospectively():
    context = {'experiment_learning': {}}
    impact = module.build_learning_decision_impact(
        context,
        packet(generated='2026-09-15T10:00:00Z', ids=['B']),
        receipt('2026-09-15T09:00:00Z'),
        2026,
        38,
    )
    assert impact['assessment_status'] == 'NOT_EVALUABLE_LATE_PACKET'
    assert impact['changed_calibration_decision'] is None


def test_missing_packet_is_not_counted_as_zero_value():
    impact = module.build_learning_decision_impact({}, None, receipt(), 2026, 38)
    assert impact['assessment_status'] == 'NO_VALID_LEARNING_INPUT'
    assert impact['learning_input_present'] is False
    assert impact['changed_calibration_decision'] is None
