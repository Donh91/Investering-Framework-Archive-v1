import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TASK = 'SYNTHETIC_BUDGET_AUDIT'


def receipt(**changes):
    return {'contract': 'API_AGENT_RECEIPT_v3', 'task': TASK, 'response_id': 'synthetic-response',
            'created_at_utc': datetime.now(timezone.utc).isoformat(), 'estimated_cost_usd': .25, **changes}


def run_guard(root, kind, *extra):
    script = 'check_api_lane_budget.py' if kind == 'lane' else 'check_monthly_cost_guard.py'
    options = ['--task', TASK, '--cap-usd', '10'] if kind == 'lane' else ['--hard-stop-usd', '10']
    proc = subprocess.run([sys.executable, str(ROOT / 'scripts/api_agent' / script), '--receipt-root', str(root),
                           *options, '--reserve-usd', '1', *extra], text=True, capture_output=True)
    def nonfinite(raw):
        raise AssertionError('Guard emitted non-standard JSON: ' + raw)
    value = json.loads(proc.stdout, parse_constant=nonfinite)
    return proc, value


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
@pytest.mark.parametrize('defect', ['truncated', 'nan', 'infinity', 'bool', 'negative', 'null', 'numeric_string',
                                  'missing_cost', 'bad_time', 'naive_time', 'bad_unix', 'not_object'])
def test_invalid_cost_evidence_never_authorizes_spend(tmp_path, kind, defect):
    v = receipt()
    if defect == 'nan': v['estimated_cost_usd'] = float('nan')
    if defect == 'infinity': v['estimated_cost_usd'] = float('inf')
    if defect == 'bool': v['estimated_cost_usd'] = True
    if defect == 'negative': v['estimated_cost_usd'] = -1
    if defect == 'null': v['estimated_cost_usd'] = None
    if defect == 'numeric_string': v['estimated_cost_usd'] = '0.25'
    if defect == 'missing_cost': v.pop('estimated_cost_usd')
    if defect == 'bad_time': v['created_at_utc'] = 'not-a-date'
    if defect == 'naive_time': v['created_at_utc'] = '2026-08-31T00:00:00'
    if defect == 'bad_unix': v['created_unix'] = True
    if defect == 'not_object': v = []
    path = tmp_path / 'cost.json'
    path.write_text('{"PRIVATE_PAYLOAD":' if defect == 'truncated' else json.dumps(v))
    proc, result = run_guard(tmp_path, kind)
    assert proc.returncode != 0
    assert result['status'] == 'BLOCKED'
    assert result['cost_evidence_errors'][0]['path'] == str(path)
    assert 'PRIVATE_PAYLOAD' not in proc.stdout + proc.stderr


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
def test_valid_zero_cost_and_identical_duplicates_count_once(tmp_path, kind):
    v = receipt(estimated_cost_usd=0)
    (tmp_path / 'a.json').write_text(json.dumps(v))
    (tmp_path / 'b.json').write_text(json.dumps(v))
    proc, result = run_guard(tmp_path, kind)
    assert proc.returncode == 0
    assert result['status'] == 'PASS'
    assert result['spent_usd'] == 0
    assert result['receipts'] == 1
    assert result['remaining_usd'] == 10
    assert result['reserve_usd'] == 1


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
def test_conflicting_duplicate_costs_cannot_be_hidden_by_file_order(tmp_path, kind):
    for a, b in [(.1, 1.), (1., .1)]:
        (tmp_path / 'a.json').write_text(json.dumps(receipt(estimated_cost_usd=a)))
        (tmp_path / 'b.json').write_text(json.dumps(receipt(estimated_cost_usd=b)))
        proc, result = run_guard(tmp_path, kind)
        assert proc.returncode != 0
        assert any(x['reason'] == 'CONFLICTING_DUPLICATE_COST' for x in result['cost_evidence_errors'])


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
def test_same_request_repeated_at_different_times_is_not_one_bill(tmp_path, kind):
    first = receipt(response_id=None, request_hash='SYNTHETIC_REQUEST', estimated_cost_usd=1)
    # Fix both timestamps within the current UTC month, without using future time.
    stamp = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first['created_at_utc'] = stamp.isoformat()
    second = {**first, 'created_at_utc': (stamp + timedelta(seconds=1)).isoformat()}
    (tmp_path / 'a.json').write_text(json.dumps(first))
    (tmp_path / 'b.json').write_text(json.dumps(second))
    proc, result = run_guard(tmp_path, kind)
    assert proc.returncode == 0
    assert result['receipts'] == 2
    assert result['spent_usd'] == 2


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
def test_latest_and_history_copy_of_one_request_count_once(tmp_path, kind):
    first = receipt(response_id=None, request_hash='SYNTHETIC_REQUEST', estimated_cost_usd=1)
    (tmp_path / 'LATEST.json').write_text(json.dumps(first))
    (tmp_path / 'history.json').write_text(json.dumps(first))
    proc, result = run_guard(tmp_path, kind)
    assert proc.returncode == 0
    assert result['receipts'] == 1
    assert result['spent_usd'] == 1


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
def test_cap_and_reserve_boundary_remains_blocking(tmp_path, kind):
    (tmp_path / 'cost.json').write_text(json.dumps(receipt(estimated_cost_usd=9)))
    proc, result = run_guard(tmp_path, kind)
    assert proc.returncode != 0
    assert result['remaining_usd'] == result['reserve_usd'] == 1


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
def test_missing_required_root_differs_from_empty_existing_root(tmp_path, kind):
    proc, result = run_guard(tmp_path / 'missing', kind)
    assert proc.returncode != 0 and result['cost_evidence_errors']
    proc, result = run_guard(tmp_path, kind)
    assert proc.returncode == 0 and result['receipts'] == 0


def test_missing_optional_pending_ledger_is_explicit(tmp_path):
    proc, result = run_guard(tmp_path, 'monthly', '--pending-ledger-root', str(tmp_path / 'optional'))
    assert proc.returncode == 0
    assert result['missing_optional_roots'] == [str(tmp_path / 'optional')]
    assert not result['cost_evidence_errors']


def test_optional_alias_cannot_hide_missing_required_root(tmp_path):
    missing = tmp_path / 'missing'
    proc, result = run_guard(missing, 'monthly', '--pending-ledger-root', str(missing))
    assert proc.returncode != 0
    assert result['status'] == 'BLOCKED'


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
def test_other_month_is_not_current_spend(tmp_path, kind):
    (tmp_path / 'cost.json').write_text(json.dumps(receipt(created_at_utc='2020-01-01T00:00:00Z', estimated_cost_usd=100)))
    proc, result = run_guard(tmp_path, kind)
    assert proc.returncode == 0
    assert result['receipts'] == 0


@pytest.mark.parametrize('kind', ['lane', 'monthly'])
def test_overflowed_sum_blocks_with_standard_json(tmp_path, kind):
    for i in range(2):
        (tmp_path / f'{i}.json').write_text(json.dumps(receipt(response_id=f'overflow-{i}', estimated_cost_usd=1e308)))
    proc, result = run_guard(tmp_path, kind)
    assert proc.returncode != 0
    assert result['spent_usd'] is None
    assert result['remaining_usd'] is None
