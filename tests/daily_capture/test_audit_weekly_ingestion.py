import json
import subprocess
import sys
from pathlib import Path

from scripts.daily_capture import build_weekly_calibration as weekly


def csv_fixture(root):
    root.mkdir(exist_ok=True)
    p = root / 'hours.csv'
    p.write_text('timestamp_utc,btc_close,eth_close,ethbtc_close,spot_status\n'
                 '2026-08-24T00:00:00Z,100,100,1,COMPLETE\n'
                 'bad-timestamp,101,101,1,COMPLETE\n'
                 '2026-08-24T02:00:00Z,102,102,1,COMPLETE\n')
    return p


def test_valid_suffix_survives_an_invalid_row(tmp_path):
    p = csv_fixture(tmp_path)
    before = p.read_bytes()
    diagnostics = []
    rows = weekly.load_hourly_rows(tmp_path, 2026, 35, diagnostics=diagnostics)
    assert [x['btc_close'] for x in rows] == ['100', '102']
    assert diagnostics == [{'path': str(p), 'line': 3, 'reason': 'INVALID_TIMESTAMP'}]
    assert p.read_bytes() == before


def test_bad_file_does_not_erase_an_independent_valid_file(tmp_path):
    csv_fixture(tmp_path)
    bad = tmp_path / 'unreadable.csv'
    bad.write_bytes(b'\xff\xfe')
    diagnostics = []
    rows = weekly.load_hourly_rows(tmp_path, 2026, 35, diagnostics=diagnostics)
    assert len(rows) == 2
    assert any(x['path'] == str(bad) and x['reason'] == 'CSV_READ_ERROR' for x in diagnostics)


def test_unreadable_hourly_directory_is_diagnosed(tmp_path, monkeypatch):
    def denied_walk(root, onerror):
        onerror(PermissionError(13, 'denied', str(root)))
        return iter(())
    monkeypatch.setattr(weekly.os, 'walk', denied_walk)
    diagnostics = []
    assert weekly.load_hourly_rows(tmp_path, 2026, 35, diagnostics=diagnostics) == []
    assert diagnostics[0]['reason'] == 'CSV_DIRECTORY_UNREADABLE'


def test_published_pack_distinguishes_ingestion_errors_from_source_gaps(tmp_path):
    inputs = tmp_path / 'inputs'; inputs.mkdir()
    hourly = tmp_path / 'hourly'; csv_fixture(hourly)
    out = tmp_path / 'weekly'
    result = subprocess.run([sys.executable, str(Path(weekly.__file__)), '--input-root', str(inputs),
        '--hourly-root', str(hourly), '--output-root', str(out), '--iso-year', '2026', '--iso-week', '35'],
        text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    facts = json.loads((out / '2026/W35/WEEKLY_SEQUENCE_FACTS.json').read_text())
    assert facts['gap_diagnostics']['observed_hours'] == 2
    assert facts['hourly_ingestion_diagnostics'][0]['reason'] == 'INVALID_TIMESTAMP'
    assert facts['market_interpretation'] is False
    assert facts['forecast_evaluation_performed'] is False
