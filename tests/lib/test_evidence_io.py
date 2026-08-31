import json
from pathlib import Path

import pytest

from scripts.lib import evidence_io as io


def test_missing_unreadable_and_usable_are_distinct(tmp_path):
    p = tmp_path / 'evidence.json'
    assert io.load_evidence(p).state == 'MISSING'
    p.write_text('{"PRIVATE_INPUT_DO_NOT_DISCLOSE":')
    bad = io.load_evidence(p)
    assert bad.state == 'UNREADABLE'
    assert 'PRIVATE_INPUT' not in repr(bad)
    p.write_text('{"value": 0}')
    good = io.load_evidence(p)
    assert good.state == 'USABLE'
    assert good.value == {'value': 0}
    p.write_text('null')
    assert io.load_evidence(p).state == 'USABLE'  # Caller owns the document schema.


@pytest.mark.parametrize('raw', ['{"x": NaN}', '{"x": Infinity}', '{"x": 1e999}', '{"x": 1, "x": 2}'])
def test_lossy_or_nonfinite_json_is_unusable(tmp_path, raw):
    p = tmp_path / 'evidence.json'
    p.write_text(raw)
    assert io.load_evidence(p).state == 'UNREADABLE'


def test_read_error_is_not_absence(tmp_path, monkeypatch):
    def deny(*args, **kwargs):
        raise PermissionError('PRIVATE_PAYLOAD')
    monkeypatch.setattr(Path, 'read_text', deny)
    result = io.load_evidence(tmp_path / 'evidence.json')
    assert result.state == 'UNREADABLE'
    assert result.reason == 'READ_ERROR'
    assert 'PRIVATE_PAYLOAD' not in repr(result)


def test_unreadable_directory_is_reported(tmp_path, monkeypatch):
    def denied_walk(root, onerror):
        onerror(PermissionError(13, 'private message', str(root / 'hidden')))
        return iter(())
    monkeypatch.setattr(io.os, 'walk', denied_walk)
    paths, errors = io.json_evidence_paths(tmp_path)
    assert not paths
    assert errors == [{'path': str(tmp_path / 'hidden'), 'reason': 'DIRECTORY_UNREADABLE'}]


@pytest.mark.parametrize('value', [True, False, -1, float('nan'), float('inf'), None, '0.1', 10**1000])
def test_cost_number_requires_finite_nonnegative_nonboolean(value):
    assert not io.finite_nonnegative(value)


@pytest.mark.parametrize('raw', ['2026-08-01', '2026-08-01T00:00:00', 'bad', True, None])
def test_timestamp_requires_explicit_timezone(raw):
    assert io.created_utc({'created_at_utc': raw}) is None


def test_offset_is_converted_to_utc_before_billing_month():
    stamp = io.created_utc({'created_at_utc': '2026-08-01T00:30:00+02:00'})
    assert stamp.isoformat() == '2026-07-31T22:30:00+00:00'


def test_malformed_primary_timestamp_cannot_borrow_a_fallback():
    assert io.created_utc({'created_unix': True, 'created_at_utc': '2026-08-01T00:00:00Z'}) is None
