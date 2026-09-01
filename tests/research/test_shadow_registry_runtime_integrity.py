import copy
import hashlib
import json
from pathlib import Path

import pytest

from scripts.research import shadow_registry_weekly as runtime


WORKFLOW = Path('.github/workflows/shadow-registry-weekly.yml')


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


@pytest.mark.parametrize(
    'field,value',
    [
        ('forward_observation_enabled', 1),
        ('source_definition_paths', 'README.md'),
        ('outcome_horizons', [24]),
        ('input_sources', [None]),
        ('status', 'SCORABLE'),
    ],
)
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
    value = {
        'contract': 'ENTRY_SIGNAL_PERFORMANCE_SUMMARY_v1',
        'generated_at_utc': '2026-09-01T00:00:00Z',
        'activation_event_count': 0,
        'horizons': {
            h: {
                'matured_event_count': 0,
                'btc_mean_return_pct': None,
                'eth_mean_return_pct': None,
                'matched_top100_mean_return_pct': None,
            }
            for h in runtime.ENTRY_HORIZONS
        },
    }
    sensor = {
        'sensor_id': 'ENTRY_SIGNAL_LEDGER',
        'evaluator': value['contract'],
        'evidence_paths': [runtime.ENTRY_OUTPUT],
    }
    return output, value, sensor


def test_registered_evaluator_binds_exact_validated_bytes(tmp_path, monkeypatch):
    output, value, sensor = evaluator_fixture(tmp_path, monkeypatch)
    output.write_text(json.dumps(value))
    row = runtime.evaluate_sensor(sensor)
    assert row['calibration_readiness'] == 'SCORABLE'
    assert row['evaluator_binding']['output_sha256'] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert row['evaluator_binding']['scientific_validity'] == 'NOT_CERTIFIED_BY_REGISTRY'


@pytest.mark.parametrize(
    'corruption',
    [
        'wrong_contract',
        'malformed',
        'nan',
        'bad_count',
        'missing_horizons',
        'partial_horizons',
        'extra_horizon',
        'arbitrary_horizon',
        'naive_time',
    ],
)
def test_unusable_evaluator_output_does_not_become_scorable(tmp_path, monkeypatch, corruption):
    output, value, sensor = evaluator_fixture(tmp_path, monkeypatch)
    if corruption == 'wrong_contract':
        value['contract'] = 'UNREGISTERED_v1'
    if corruption == 'nan':
        value['horizons']['24h']['btc_mean_return_pct'] = float('nan')
    if corruption == 'bad_count':
        value['horizons']['24h']['matured_event_count'] = 1
    if corruption == 'missing_horizons':
        value['horizons'] = {}
    if corruption == 'partial_horizons':
        value['horizons'].pop('30d')
    if corruption == 'extra_horizon':
        value['horizons']['31d'] = copy.deepcopy(value['horizons']['24h'])
    if corruption == 'arbitrary_horizon':
        value['horizons'] = {'arbitrary': value['horizons']['24h']}
    if corruption == 'naive_time':
        value['generated_at_utc'] = '2026-09-01T00:00:00'
    output.write_text('{' if corruption == 'malformed' else json.dumps(value))
    assert runtime.evaluate_sensor(sensor)['calibration_readiness'] != 'SCORABLE'


@pytest.mark.parametrize(
    'count,field,value',
    [
        (0, 'btc_mean_return_pct', 1.0),
        (0, 'eth_mean_return_pct', 0.0),
        (0, 'matched_top100_mean_return_pct', 2.0),
        (1, 'btc_mean_return_pct', None),
        (1, 'eth_mean_return_pct', None),
    ],
)
def test_count_mean_contradictions_are_not_scorable(tmp_path, monkeypatch, count, field, value):
    output, doc, sensor = evaluator_fixture(tmp_path, monkeypatch)
    doc['activation_event_count'] = 1
    row = doc['horizons']['24h']
    row.update(
        matured_event_count=count,
        btc_mean_return_pct=0.0 if count else None,
        eth_mean_return_pct=0.0 if count else None,
    )
    row[field] = value
    output.write_text(json.dumps(doc))
    assert runtime.evaluate_sensor(sensor)['calibration_readiness'] != 'SCORABLE'


def test_matured_returns_can_lack_matched_constituents(tmp_path, monkeypatch):
    output, doc, sensor = evaluator_fixture(tmp_path, monkeypatch)
    doc['activation_event_count'] = 1
    doc['horizons']['24h'].update(
        matured_event_count=1,
        btc_mean_return_pct=0.0,
        eth_mean_return_pct=-1.0,
        matched_top100_mean_return_pct=None,
    )
    output.write_text(json.dumps(doc))
    assert runtime.evaluate_sensor(sensor)['calibration_readiness'] == 'SCORABLE'


def weekly_fixture():
    return {
        'contract': 'SHADOW_WEEKLY_RELEVANCE_SNAPSHOT_v1',
        'week': '2026-W36',
        'generated_at_utc': '2026-09-01T00:00:00Z',
        'authority': 'RESEARCH_ONLY_NON_CANONICAL',
        'automatic_rule_changes': False,
        'portfolio_execution': False,
        'promotion_requires_separate_review': True,
        'anti_double_counting': 'RELATED_SHADOWS_MUST_NOT_BE_TREATED_AS_INDEPENDENT_CONFIRMATIONS',
        'interpretation_rule': 'Synthetic fixture, not production evidence.',
        'sensors': [
            {
                'sensor_id': 'SYNTHETIC',
                'family': 'fixture',
                'status': 'ACTIVE_SHADOW',
                'registry_relevance_state': 'KEEP',
                'evaluator': 'UNAVAILABLE',
                'calibration_readiness': 'RECOVERY_REQUIRED',
                'evidence_path_count': 1,
                'missing_path_count': 0,
                'evidence': [
                    {'path': 'synthetic.json', 'exists': True, 'commit': None, 'committed_at': None}
                ],
            }
        ],
        'summary': {
            'sensor_count': 1,
            'scorable_count': 0,
            'recovery_required_count': 1,
            'source_missing_count': 0,
            'promotion_candidates': [],
        },
    }


def test_same_week_preserves_history_and_refreshes_latest(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'OUTDIR', tmp_path / 'weekly')
    monkeypatch.setattr(runtime, 'LATEST', tmp_path / 'LATEST.json')
    first = weekly_fixture()
    assert runtime.persist_snapshot(first) == 'CREATED'
    original = (runtime.OUTDIR / '2026-W36.json').read_bytes()
    second = {**first, 'generated_at_utc': '2026-09-01T01:00:00Z'}
    assert runtime.persist_snapshot(second) == 'PRESERVED_EXISTING'
    assert (runtime.OUTDIR / '2026-W36.json').read_bytes() == original
    assert json.loads(runtime.LATEST.read_text()) == second


def test_corrupt_existing_week_is_preserved_and_blocks_latest(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime, 'OUTDIR', tmp_path / 'weekly')
    monkeypatch.setattr(runtime, 'LATEST', tmp_path / 'LATEST.json')
    runtime.OUTDIR.mkdir()
    history = runtime.OUTDIR / '2026-W36.json'
    history.write_text('{')
    with pytest.raises(ValueError, match='preserved'):
        runtime.persist_snapshot(weekly_fixture())
    assert history.read_text() == '{'
    assert not runtime.LATEST.exists()


@pytest.mark.parametrize('defect', ['week_only', 'wrong_contract', 'authority', 'empty_sensors', 'wrong_counts'])
def test_schema_incomplete_existing_week_blocks_without_rewrite(tmp_path, monkeypatch, defect):
    monkeypatch.setattr(runtime, 'OUTDIR', tmp_path / 'weekly')
    monkeypatch.setattr(runtime, 'LATEST', tmp_path / 'LATEST.json')
    runtime.OUTDIR.mkdir()
    bad = weekly_fixture()
    if defect == 'week_only':
        bad = {'week': bad['week']}
    if defect == 'wrong_contract':
        bad['contract'] = 'UNKNOWN'
    if defect == 'authority':
        bad['portfolio_execution'] = True
    if defect == 'empty_sensors':
        bad['sensors'] = []
    if defect == 'wrong_counts':
        bad['summary']['scorable_count'] = 99
    history = runtime.OUTDIR / '2026-W36.json'
    history.write_text(json.dumps(bad))
    before = history.read_bytes()
    with pytest.raises(ValueError, match='preserved'):
        runtime.persist_snapshot(weekly_fixture())
    assert history.read_bytes() == before


@pytest.mark.parametrize('failure', ['flush', 'install'])
def test_failed_weekly_publication_leaves_no_partial_history(tmp_path, monkeypatch, failure):
    monkeypatch.setattr(runtime, 'OUTDIR', tmp_path / 'weekly')
    monkeypatch.setattr(runtime, 'LATEST', tmp_path / 'LATEST.json')
    runtime.LATEST.write_text('{"original_latest": true}\n')
    original = runtime.LATEST.read_bytes()

    def disk_failure(*args, **kwargs):
        raise OSError('injected disk failure')

    monkeypatch.setattr(runtime.os, 'fsync' if failure == 'flush' else 'link', disk_failure)
    with pytest.raises(OSError, match='injected'):
        runtime.persist_snapshot(weekly_fixture())
    assert not (runtime.OUTDIR / '2026-W36.json').exists()
    assert runtime.LATEST.read_bytes() == original


def test_production_shaped_read_only_evaluation():
    reg = current_registry()
    assert runtime.validate_registry(reg)
    rows = [runtime.evaluate_sensor(x) for x in reg['sensors']]
    assert [x['sensor_id'] for x in rows if x['calibration_readiness'] == 'SCORABLE'] == ['ENTRY_SIGNAL_LEDGER']
    assert all(x['evaluator_binding']['scientific_validity'] == 'NOT_CERTIFIED_BY_REGISTRY' for x in rows)


def test_weekly_workflow_uses_reviewed_pr_lane_not_direct_main():
    text = WORKFLOW.read_text()
    assert 'pull-requests: write' in text
    assert 'gh pr create' in text
    assert 'automation/shadow-registry-' in text
    assert 'SHADOW_REGISTRY_REVIEW_PR_CREATED' in text
    assert 'HEAD:main' not in text
    assert 'git push origin main' not in text
    assert 'git push origin HEAD:main' not in text
    assert 'group: framework-main-writer' in text
    assert 'git rebase --abort' in text
    assert 'git merge-base --is-ancestor origin/main HEAD' in text


def test_weekly_workflow_retains_bounded_schedule_and_runtime_gate():
    text = WORKFLOW.read_text()
    assert "cron: '41 7 * * 1'" in text
    assert "timezone: 'Europe/Copenhagen'" in text
    assert "github.ref == 'refs/heads/main'" in text
    assert 'python scripts/research/shadow_registry_weekly.py --validate-only' in text
    assert 'tests/research/test_shadow_registry_runtime_integrity.py' in text
