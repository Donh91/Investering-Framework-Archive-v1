import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.entry_signal import entry_signal_ledger as ledger

START = datetime(2026, 8, 20, 10, tzinfo=timezone.utc)


def market(stamp=START, price=100):
    return {
        'price_observation_utc': stamp.isoformat(),
        'price_timestamp_semantics': 'EXPLICIT_SOURCE_OBSERVATION_UTC',
        'btc_usdt': price, 'eth_usdt': price, 'ethbtc': 0.03 * price / 100,
        'constituents': {'a': price}, 'top100_advance_ratio': 0.7,
        'btc_return_24h_pct': 1, 'eth_return_24h_pct': 2,
    }


@pytest.fixture
def root(tmp_path, monkeypatch):
    for name, path in {'EVENTS': 'events', 'OUTCOMES': 'outcomes', 'STATE': 'STATE.json',
                       'LATEST': 'LATEST.json', 'SUMMARY': 'SUMMARY.json'}.items():
        monkeypatch.setattr(ledger, name, tmp_path / path)
    monkeypatch.setattr(ledger, 'now_utc', lambda: START + timedelta(minutes=10))
    monkeypatch.setattr(ledger, 'latest_market', market)
    return tmp_path


def activation():
    event = {'contract': 'ENTRY_SIGNAL_EVENT_v1', 'event_type': 'ACTIVATION',
             'event_id': 'fixture', 'event_time_utc': START.isoformat(), 'market_snapshot': market()}
    ledger.write_json(ledger.EVENTS / 'fixture.json', event)
    return event


@pytest.mark.parametrize('raw', ['{', 'null', '[]', '{}', '{"contract":"wrong","state":"WAIT"}',
                                   '{"contract":"ENTRY_SIGNAL_STATE_v1","state":"WAIT","state":"WAIT"}'])
def test_corrupt_existing_state_stops_before_any_publication(root, raw):
    ledger.STATE.write_text(raw)
    with pytest.raises(RuntimeError):
        ledger.main()
    assert ledger.STATE.read_text() == raw
    assert not ledger.LATEST.exists()
    assert not ledger.EVENTS.exists()


def test_only_missing_state_allows_safe_wait_initialization(root):
    ledger.main()
    state = ledger.read_json(ledger.STATE)
    latest = ledger.read_json(ledger.LATEST)
    assert state['state'] == 'WAIT'
    assert latest['data_ping_bridge']['canonical_action_authority'] == 'NONE'
    assert latest['authority']['portfolio_execution'] is False
    assert [ledger.read_json(p)['event_type'] for p in ledger.EVENTS.glob('*.json')] == ['INITIAL_STATE']


def test_broken_state_link_is_not_initial_absence(root):
    ledger.STATE.symlink_to(root / 'lost-state.json')
    with pytest.raises(RuntimeError):
        ledger.main()
    assert ledger.STATE.is_symlink()
    assert not ledger.LATEST.exists()


def test_retired_legacy_state_deactivates_and_cannot_restore_permission(root):
    ledger.write_json(ledger.STATE, {'contract': 'ENTRY_SIGNAL_STATE_v1', 'state': 'GRADUATED_ALTCOIN_TOPUP_ACTIVE'})
    ledger.main()
    latest = ledger.read_json(ledger.LATEST)
    assert latest['state'] == 'WAIT'
    assert latest['promotion_authority']['permits_active_state'] is False


@pytest.mark.parametrize('price', [True, 0, -1, float('nan'), float('inf'), '100'])
def test_invalid_price_cannot_publish_learning_state(root, monkeypatch, price):
    monkeypatch.setattr(ledger, 'latest_market', lambda: market(price=price) if type(price) in (int, float) else {**market(), 'btc_usdt': price})
    with pytest.raises(RuntimeError):
        ledger.main()
    assert not ledger.LATEST.exists()
    assert not ledger.STATE.exists()


def test_future_source_cannot_publish_state(root, monkeypatch):
    monkeypatch.setattr(ledger, 'latest_market', lambda: market(START + timedelta(hours=1)))
    with pytest.raises(RuntimeError):
        ledger.main()
    assert not ledger.LATEST.exists()


def test_week_old_return_never_scores_as_day_return(root):
    activation()
    ledger.update_outcomes(market(START + timedelta(hours=168), 125), START + timedelta(hours=168))
    out = ledger.read_json(ledger.OUTCOMES / 'fixture.json')
    assert out['horizons']['24h']['measurement']['status'] == 'CENSORED_EXACT_ENDPOINT_UNAVAILABLE'
    assert out['horizons']['24h']['btc_return_since_signal_pct'] is None
    assert out['horizons']['7d']['btc_return_since_signal_pct'] == 25
    assert out['path_stats']['latest_returns']['btc_pct'] == 25
    ledger.build_summary(START + timedelta(hours=168))
    summary = ledger.read_json(ledger.SUMMARY)
    assert summary['horizons']['24h']['matured_event_count'] == 0
    assert summary['horizons']['24h']['excluded_measurement_count'] == 1
    assert summary['horizons']['7d']['matured_event_count'] == 1


def test_source_horizon_is_not_processing_age(root):
    activation()
    ledger.update_outcomes(market(START + timedelta(hours=24), 110), START + timedelta(hours=100))
    out = ledger.read_json(ledger.OUTCOMES / 'fixture.json')
    row = out['horizons']['24h']
    assert row['measurement']['elapsed_hours'] == 24
    assert row['age_hours'] == 100
    assert row['btc_return_since_signal_pct'] == pytest.approx(10)
    assert '72h' not in out['horizons']
    assert row['matched_top100_equal_weight_return_since_signal_pct'] is None
    assert out['path_stats']['latest_returns']['matched_top100_equal_weight_pct'] == pytest.approx(10)
    before = {p: p.read_bytes() for p in root.rglob('*.json')}
    ledger.build_summary(START + timedelta(hours=100))
    assert all(p.read_bytes() == raw for p, raw in before.items())
    summary = ledger.read_json(ledger.SUMMARY)['horizons']['24h']
    assert summary['matured_event_count'] == 1
    assert summary['btc_mean_return_pct'] == pytest.approx(10)


def test_existing_horizon_payload_is_preserved_on_later_updates(root):
    activation()
    ledger.update_outcomes(market(START + timedelta(hours=24), 110), START + timedelta(hours=24))
    before = ledger.read_json(ledger.OUTCOMES / 'fixture.json')['horizons']['24h']
    event_bytes = (ledger.EVENTS / 'fixture.json').read_bytes()
    ledger.update_outcomes(market(START + timedelta(hours=72), 120), START + timedelta(hours=72))
    after = ledger.read_json(ledger.OUTCOMES / 'fixture.json')
    assert after['horizons']['24h'] == before
    assert (ledger.EVENTS / 'fixture.json').read_bytes() == event_bytes


def test_aligned_constituent_source_keeps_measurable_relative_returns(root):
    event = activation()
    event['market_snapshot']['constituent_price_observation_utc'] = START.isoformat()
    ledger.write_json(ledger.EVENTS / 'fixture.json', event)
    end = START + timedelta(hours=24)
    current = {**market(end, 110), 'constituents': {'a': 105},
               'constituent_price_observation_utc': end.isoformat()}
    ledger.update_outcomes(current, end)
    ledger.build_summary(end)
    h = ledger.read_json(ledger.SUMMARY)['horizons']['24h']
    assert h['matched_top100_available_count'] == 1
    assert h['matched_top100_mean_return_pct'] == pytest.approx(5)
    assert h['matched_top100_minus_btc_mean_pp'] == pytest.approx(-5)


def test_summary_recomputes_measurement_and_returns_not_just_a_validity_flag(root):
    activation()
    ledger.update_outcomes(market(START + timedelta(hours=24), 110), START + timedelta(hours=24))
    path = ledger.OUTCOMES / 'fixture.json'
    value = ledger.read_json(path)
    value['horizons']['24h']['btc_return_since_signal_pct'] = 999
    ledger.write_json(path, value)
    before = path.read_bytes()
    ledger.build_summary(START + timedelta(hours=24))
    summary = ledger.read_json(ledger.SUMMARY)['horizons']['24h']
    assert summary['matured_event_count'] == 0
    assert summary['excluded_measurement_reasons'] == {'SOURCE_RETURN_MISMATCH': 1}
    assert path.read_bytes() == before


@pytest.mark.parametrize('bad', [None, '2026-08-20T10:00:00', 'invalid'])
def test_missing_or_ambiguous_baseline_time_is_not_invented(root, bad):
    event = activation()
    event['market_snapshot']['price_observation_utc'] = bad
    ledger.write_json(ledger.EVENTS / 'fixture.json', event)
    ledger.update_outcomes(market(START + timedelta(hours=24), 110), START + timedelta(hours=24))
    row = ledger.read_json(ledger.OUTCOMES / 'fixture.json')['horizons']['24h']
    assert row['measurement']['status'] == 'CENSORED_SOURCE_TIMESTAMP_UNAVAILABLE'
    assert row['btc_return_since_signal_pct'] is None


def test_legacy_hourly_row_open_and_explicit_close_resolve_same_instant():
    legacy = {**market(), 'price_source': 'GITHUB_HOURLY_SEQUENCE_DIRECT_CLOSES'}
    legacy.pop('price_timestamp_semantics')
    modern = {**legacy, 'price_timestamp_semantics': 'HOURLY_CLOSE_UTC_v1',
              'price_observation_utc': (START + timedelta(hours=1)).isoformat()}
    assert ledger.source_price_time(legacy) == ledger.source_price_time(modern) == START + timedelta(hours=1)
