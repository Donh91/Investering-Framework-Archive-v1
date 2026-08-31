import json
import subprocess
import sys
from datetime import timezone
from pathlib import Path

import pytest

from scripts.evidence_lifecycle import validate_lifecycle_receipt as validator
from scripts.evidence_lifecycle.test_validate_lifecycle_receipt import base_receipt


def cli(tmp_path, value):
    path = tmp_path / 'receipt.json'
    path.write_text(json.dumps(value))
    before = path.read_bytes()
    proc = subprocess.run([sys.executable, validator.__file__, str(path)], text=True, capture_output=True)
    assert path.read_bytes() == before
    return proc, json.loads(proc.stdout)


@pytest.mark.parametrize('bad', ['2026-08-30', '2026-08-30T12:00:00', 'bad', True, 1788087600, [], {},
                                 '9999-12-31T23:59:59-23:59', '0001-01-01T00:00:00+23:59'])
def test_ambiguous_or_invalid_timestamps_return_structured_errors(tmp_path, bad):
    data = base_receipt()
    data['retrieval_start_time'] = bad
    data['retrieval_complete_time'] = '2026-08-30T12:01:00Z'
    data['timestamp_status'].update(retrieval_start_time='KNOWN', retrieval_complete_time='KNOWN')
    proc, result = cli(tmp_path, data)
    assert proc.returncode != 0
    assert result['valid'] is False
    assert any('retrieval_start_time' in error for error in result['errors'])
    assert 'Traceback' not in proc.stderr


def test_mixed_valid_offsets_compare_actual_instants(tmp_path):
    data = base_receipt()
    data.update(retrieval_start_time='2026-08-30T14:00:00+02:00', retrieval_complete_time='2026-08-30T12:01:00Z')
    data['timestamp_status'].update(retrieval_start_time='KNOWN', retrieval_complete_time='KNOWN')
    proc, result = cli(tmp_path, data)
    assert proc.returncode == 0
    assert result['valid'] is True
    assert validator.parse_time(data['retrieval_start_time']).tzinfo == timezone.utc
    assert validator.parse_time(data['retrieval_start_time']).isoformat() == '2026-08-30T12:00:00+00:00'


def test_real_reverse_order_is_still_rejected(tmp_path):
    data = base_receipt()
    data.update(retrieval_start_time='2026-08-30T14:02:00+02:00', retrieval_complete_time='2026-08-30T12:01:00Z')
    data['timestamp_status'].update(retrieval_start_time='KNOWN', retrieval_complete_time='KNOWN')
    proc, result = cli(tmp_path, data)
    assert proc.returncode != 0
    assert any('invalid ordering' in x for x in result['errors'])


@pytest.mark.parametrize('bad_status', [[], {}, True])
def test_invalid_status_type_does_not_crash(tmp_path, bad_status):
    data = base_receipt()
    data['timestamp_status']['retrieval_start_time'] = bad_status
    proc, result = cli(tmp_path, data)
    assert proc.returncode != 0
    assert result['valid'] is False
    assert 'Traceback' not in proc.stderr


def test_unavailable_stages_remain_null_and_are_not_inferred(tmp_path):
    data = base_receipt()
    proc, result = cli(tmp_path, data)
    assert proc.returncode == 0
    assert set(result['missing_or_blocked']) == set(validator.TIME_FIELDS)
    assert all(data[field] is None for field in validator.TIME_FIELDS)


@pytest.mark.parametrize('raw', ['{', '[]', 'null'])
def test_bad_document_returns_json_diagnostic(tmp_path, raw):
    path = tmp_path / 'bad.json'
    path.write_text(raw)
    proc = subprocess.run([sys.executable, validator.__file__, str(path)], text=True, capture_output=True)
    result = json.loads(proc.stdout)
    assert proc.returncode != 0 and result['valid'] is False
    assert result['errors']
