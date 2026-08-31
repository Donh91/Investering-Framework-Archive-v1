import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.research import shadow_registry_weekly as runtime


def current_registry():
    return json.loads(runtime.REGISTRY.read_text())


def test_current_registry_enforces_existing_owner_schema():
    assert runtime.validate_registry(current_registry())


@pytest.mark.parametrize('field', json.loads(runtime.SCHEMA_PATH.read_text())['required_sensor_fields'])
def test_missing_required_owner_field_is_rejected(field):
    reg = current_registry()
    del reg['sensors'][0][field]
    with pytest.raises(ValueError):
        runtime.validate_registry(reg)


def test_schema_is_loaded_instead_of_duplicated(tmp_path, monkeypatch):
    schema = json.loads(runtime.SCHEMA_PATH.read_text())
    schema['required_sensor_fields'].append('extra_owner_requirement')
    owner = tmp_path / 'owner.json'
    owner.write_text(json.dumps(schema))
    monkeypatch.setattr(runtime, 'SCHEMA_PATH', owner)
    with pytest.raises(ValueError, match='extra_owner_requirement'):
        runtime.validate_registry(current_registry())


@pytest.mark.parametrize('field,value', [('forward_observation_enabled', 1), ('source_definition_paths', 'README.md'),
                                       ('outcome_horizons', [24]), ('input_sources', [None]), ('status', 'SCORABLE')])
def test_invalid_field_types_and_enums_fail_closed(field, value):
    reg = current_registry()
    reg['sensors'][0][field] = value
    with pytest.raises(ValueError):
        runtime.validate_registry(reg)


@pytest.mark.parametrize('field', ['canonical_market_state', 'portfolio_execution', 'automatic_rule_changes'])
def test_authority_cannot_be_enabled(field):
    reg = current_registry()
    reg[field] = True
    with pytest.raises(ValueError):
        runtime.validate_registry(reg)


def test_duplicate_sensor_and_missing_schema_fail(tmp_path, monkeypatch):
    reg = current_registry()
    reg['sensors'].append(copy.deepcopy(reg['sensors'][0]))
    with pytest.raises(ValueError, match='duplicate'):
        runtime.validate_registry(reg)
    monkeypatch.setattr(runtime, 'SCHEMA_PATH', tmp_path / 'missing.json')
    with pytest.raises(ValueError, match='schema'):
        runtime.validate_registry(current_registry())


def test_placeholder_breadth_evaluator_is_not_scorable():
    sensor = next(x for x in current_registry()['sensors'] if x['sensor_id'] == 'BREADTH_FORWARD_FAMILY')
    row = runtime.evaluate_sensor(sensor)
    assert row['missing_path_count'] == 0
    assert row['calibration_readiness'] == 'RECOVERY_REQUIRED'
    assert row['evaluator_binding']['reason'] == 'NO_REGISTERED_EVALUATOR_BINDING'


def evaluator_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'ROOT', tmp_path)
    output = tmp_path / runtime.ENTRY_OUTPUT
    output.parent.mkdir(parents=True)
    producer = tmp_path / runtime.ENTRY_PRODUCER
    producer.parent.mkdir(parents=True)
    producer.write_text('# synthetic existing producer fixture\n')
    value = {'contract': 'ENTRY_SIGNAL_PERFORMANCE_SUMMARY_v1', 'generated_at_utc': '2026-08-31T00:00:00Z',
             'activation_event_count': 0, 'horizons': {h: {'matured_event_count': 0,
              'btc_mean_return_pct': None, 'eth_mean_return_pct': None, 'matched_top100_mean_return_pct': None}
              for h in runtime.ENTRY_HORIZONS}}
    sensor = {'sensor_id': 'ENTRY_SIGNAL_LEDGER', 'evaluator': value['contract'], 'evidence_paths': [runtime.ENTRY_OUTPUT]}
    return output, value, sensor


def test_registered_evaluator_binds_exact_validated_bytes(tmp_path, monkeypatch):
    output, value, sensor = evaluator_fixture(tmp_path, monkeypatch)
    output.write_text(json.dumps(value))
    row = runtime.evaluate_sensor(sensor)
    assert row['calibration_readiness'] == 'SCORABLE'
    assert row['evaluator_binding']['output_sha256'] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert row['evaluator_binding']['scientific_validity'] == 'NOT_CERTIFIED_BY_REGISTRY'
    assert row['entry_signal_summary']['activation_event_count'] == 0


@pytest.mark.parametrize('corruption', ['wrong_contract', 'malformed', 'nan', 'bad_count', 'missing_horizons',
                                      'partial_horizons', 'extra_horizon', 'arbitrary_horizon', 'naive_time'])
def test_unusable_evaluator_output_does_not_become_scorable(tmp_path, monkeypatch, corruption):
    output, value, sensor = evaluator_fixture(tmp_path, monkeypatch)
    if corruption == 'wrong_contract': value['contract'] = 'UNREGISTERED_v1'
    if corruption == 'nan': value['horizons']['24h']['btc_mean_return_pct'] = float('nan')
    if corruption == 'bad_count': value['horizons']['24h']['matured_event_count'] = 1
    if corruption == 'missing_horizons': value['horizons'] = {}
    if corruption == 'partial_horizons': value['horizons'].pop('30d')
    if corruption == 'extra_horizon': value['horizons']['31d'] = copy.deepcopy(value['horizons']['24h'])
    if corruption == 'arbitrary_horizon': value['horizons'] = {'arbitrary': value['horizons']['24h']}
    if corruption == 'naive_time': value['generated_at_utc'] = '2026-08-31T00:00:00'
    output.write_text('{' if corruption == 'malformed' else json.dumps(value))
    assert runtime.evaluate_sensor(sensor)['calibration_readiness'] != 'SCORABLE'


def test_evaluator_label_cannot_be_borrowed_by_another_sensor(tmp_path, monkeypatch):
    output, value, sensor = evaluator_fixture(tmp_path, monkeypatch)
    output.write_text(json.dumps(value))
    sensor['sensor_id'] = 'BREADTH_FORWARD_FAMILY'
    assert runtime.evaluate_sensor(sensor)['calibration_readiness'] == 'RECOVERY_REQUIRED'


def weekly_fixture():
    return {'contract': 'SHADOW_WEEKLY_RELEVANCE_SNAPSHOT_v1', 'week': '2026-W36',
            'generated_at_utc': '2026-08-31T00:00:00Z', 'authority': 'RESEARCH_ONLY_NON_CANONICAL',
            'automatic_rule_changes': False, 'portfolio_execution': False, 'promotion_requires_separate_review': True,
            'anti_double_counting': 'RELATED_SHADOWS_MUST_NOT_BE_TREATED_AS_INDEPENDENT_CONFIRMATIONS',
            'interpretation_rule': 'SYNTHETIC fixture, not production evidence',
            'sensors': [{'sensor_id': 'SYNTHETIC', 'family': 'fixture', 'status': 'ACTIVE_SHADOW',
                         'registry_relevance_state': 'KEEP', 'evaluator': 'UNAVAILABLE',
                         'calibration_readiness': 'RECOVERY_REQUIRED', 'evidence_path_count': 1, 'missing_path_count': 0,
                         'evidence': [{'path': 'synthetic.json', 'exists': True, 'commit': None, 'committed_at': None}]}],
            'summary': {'sensor_count': 1, 'scorable_count': 0, 'recovery_required_count': 1,
                        'source_missing_count': 0, 'promotion_candidates': []}}


def test_same_week_preserves_history_and_refreshes_latest(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'OUTDIR', tmp_path / 'weekly')
    monkeypatch.setattr(runtime, 'LATEST', tmp_path / 'LATEST.json')
    first = weekly_fixture()
    assert runtime.persist_snapshot(first) == 'CREATED'
    original = (runtime.OUTDIR / '2026-W36.json').read_bytes()
    second = {**first, 'generated_at_utc': '2026-08-31T01:00:00Z'}
    assert runtime.persist_snapshot(second) == 'PRESERVED_EXISTING'
    assert (runtime.OUTDIR / '2026-W36.json').read_bytes() == original
    assert json.loads(runtime.LATEST.read_text()) == second


def test_corrupt_existing_week_is_not_overwritten(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'OUTDIR', tmp_path / 'weekly')
    monkeypatch.setattr(runtime, 'LATEST', tmp_path / 'LATEST.json')
    runtime.OUTDIR.mkdir()
    history = runtime.OUTDIR / '2026-W36.json'
    history.write_text('{')
    with pytest.raises(ValueError, match='preserved'):
        runtime.persist_snapshot(weekly_fixture())
    assert history.read_text() == '{'
    assert not runtime.LATEST.exists()


@pytest.mark.parametrize('defect', ['week_only', 'wrong_contract', 'authority', 'bool_type', 'empty_sensors',
                                  'missing_sensor_field', 'duplicate_sensor', 'missing_evidence',
                                  'missing_summary', 'wrong_counts', 'wrong_promotions', 'naive_time', 'wrong_week'])
def test_incomplete_existing_week_blocks_without_mutating_either_artifact(tmp_path, monkeypatch, defect):
    monkeypatch.setattr(runtime, 'OUTDIR', tmp_path / 'weekly')
    monkeypatch.setattr(runtime, 'LATEST', tmp_path / 'LATEST.json')
    runtime.OUTDIR.mkdir()
    bad = weekly_fixture()
    if defect == 'week_only': bad = {'week': bad['week']}
    if defect == 'wrong_contract': bad['contract'] = 'UNKNOWN'
    if defect == 'authority': bad['portfolio_execution'] = True
    if defect == 'bool_type': bad['automatic_rule_changes'] = 0
    if defect == 'empty_sensors': bad['sensors'] = []
    if defect == 'missing_sensor_field': bad['sensors'][0].pop('evaluator')
    if defect == 'duplicate_sensor': bad['sensors'].append(copy.deepcopy(bad['sensors'][0]))
    if defect == 'missing_evidence': bad['sensors'][0]['evidence'][0].pop('exists')
    if defect == 'missing_summary': bad.pop('summary')
    if defect == 'wrong_counts': bad['summary']['scorable_count'] = 100
    if defect == 'wrong_promotions': bad['summary']['promotion_candidates'] = ['FAKE']
    if defect == 'naive_time': bad['generated_at_utc'] = '2026-08-31T00:00:00'
    if defect == 'wrong_week': bad['week'] = '2026-W35'
    history = runtime.OUTDIR / '2026-W36.json'
    history.write_text(json.dumps(bad))
    runtime.LATEST.write_text('{"original_latest": true}\n')
    before = history.read_bytes(), runtime.LATEST.read_bytes()
    with pytest.raises(ValueError, match='preserved'):
        runtime.persist_snapshot(weekly_fixture())
    assert (history.read_bytes(), runtime.LATEST.read_bytes()) == before


def test_production_shaped_read_only_evaluation():
    reg = current_registry()
    assert runtime.validate_registry(reg)
    rows = [runtime.evaluate_sensor(x) for x in reg['sensors']]
    assert [x['sensor_id'] for x in rows if x['calibration_readiness'] == 'SCORABLE'] == ['ENTRY_SIGNAL_LEDGER']
    assert all(x['evaluator_binding']['scientific_validity'] == 'NOT_CERTIFIED_BY_REGISTRY' for x in rows)
