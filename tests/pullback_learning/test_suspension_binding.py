import copy
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.pullback_learning import pullback_learning_ledger as ledger

OWNER = json.loads(ledger.ELIGIBILITY_STATUS.read_text())
NOW = datetime(2026, 8, 31, 12, tzinfo=timezone.utc)


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    for name, relative in {'ROOT': '.', 'OBS': 'observations', 'EPISODES': 'episodes',
                           'LATEST': 'LATEST.json', 'STATE': 'STATE.json', 'SUMMARY': 'PERFORMANCE_SUMMARY.json',
                           'ELIGIBILITY_STATUS': 'ELIGIBILITY_STATUS_v1.json'}.items():
        monkeypatch.setattr(ledger, name, tmp_path / relative)
    ledger.ELIGIBILITY_STATUS.write_text(json.dumps(OWNER))
    monkeypatch.setattr(ledger, 'now_utc', lambda: NOW)
    return tmp_path


def observation(when=NOW, **overrides):
    return {'captured_at_utc': when.isoformat(), 'price_observation_utc': when.isoformat(),
            'hourly_sequence_run_id': 'SYNTHETIC-HOURLY', 'entry_state': 'WAIT',
            'btc_usdt': 100., 'eth_usdt': 100., 'ethbtc': 1., 'breadth': .5,
            'constituents': {'SYNTHETIC': 100.}, 'synthetic_top100_index': 100.,
            'drawdown_from_running_peak_pct': 0., 'matched_top100_step_return_pct': 0.,
            **overrides}


def write_history(count):
    for i in range(count):
        when = NOW - timedelta(hours=count-i)
        row = observation(when)
        path = ledger.OBS / f'{when:%Y/%m/%d}/{when:%Y%m%dT%H%M%SZ}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(row))


def immutable_bytes():
    return {str(p): p.read_bytes() for root in [ledger.OBS, ledger.EPISODES] for p in root.rglob('*.json')}


def assert_firewall(value):
    assert value['research_state'] == 'REGIME_NOT_ACTIVE'
    assert value['authority']['research_only'] is True
    assert value['authority']['portfolio_execution'] is False
    assert value['authority']['canonical_market_state'] is False
    assert value['authority']['automatic_rule_changes'] is False
    assert value['adaptive_evidence']['classification_reason'] == 'ELIGIBILITY_CONTRACT_UNAVAILABLE'


@pytest.mark.parametrize('count', [0, 25])
def test_observations_and_descriptive_statistics_remain_live(sandbox, monkeypatch, count):
    write_history(count)
    before = immutable_bytes()
    monkeypatch.setattr(ledger, 'current_snapshot', lambda: observation())
    ledger.main()
    assert len(ledger.observation_files()) == count + 1
    assert all(Path(p).read_bytes() == raw for p, raw in before.items())
    assert not ledger.episode_files()
    latest = json.loads(ledger.LATEST.read_text())
    state = json.loads(ledger.STATE.read_text())
    assert_firewall(latest)
    assert_firewall(state)
    assert latest['adaptive_evidence']['adaptive_percentiles_ready'] is (count >= 24)
    assert latest['eligibility_status']['owner_sha256'] == hashlib.sha256(ledger.ELIGIBILITY_STATUS.read_bytes()).hexdigest()
    assert 'ELIGIBILITY_CONTRACT_UNAVAILABLE' in latest['data_ping_bridge']['display_line']
    assert latest['performance_summary']['closed_episode_count'] == 0


@pytest.mark.parametrize('context', ['retired_entry', 'proxy_breadth', 'source_quality', 'direction_confidence', 't12'])
def test_non_authoritative_context_cannot_override_suspension(sandbox, context):
    cur = observation(drawdown_from_running_peak_pct=-20, breadth=.01, matched_top100_step_return_pct=-10)
    if context == 'retired_entry': cur['entry_state'] = 'GRADUATED_ALTCOIN_TOPUP_ACTIVE'
    if context == 'proxy_breadth': cur['breadth'] = 1.
    if context == 'source_quality': cur['canonical_compatible'] = True
    if context == 'direction_confidence': cur['direction_confidence'] = {'UP': .99}
    if context == 't12': cur['registered_test_id'] = 'INTRADAY_DIRECTION_CONFIDENCE_V1'
    state, evidence = ledger.classify([observation() for _ in range(25)], cur, 'PULLBACK_ACTIVE_RESEARCH')
    assert state == 'REGIME_NOT_ACTIVE'
    assert evidence['adaptive_percentiles_ready'] is True


@pytest.mark.parametrize('state', ['NORMAL', 'PULLBACK_RISK_RESEARCH', 'PULLBACK_ACTIVE_RESEARCH', 'RELOAD_WATCH_RESEARCH'])
@pytest.mark.parametrize('existing', [False, True])
def test_no_episode_creation_or_maturation_even_from_direct_calls(sandbox, state, existing):
    if existing:
        ledger.EPISODES.mkdir()
        (ledger.EPISODES / 'historical.json').write_text(json.dumps({'status': 'OPEN', 'trough': {'synthetic_top100_index': 100}}))
    before = immutable_bytes()
    result = ledger.update_episode(state, observation(synthetic_top100_index=50), NOW)
    assert result['status'] == 'SUSPENDED_NO_EPISODE_MUTATION'
    assert immutable_bytes() == before


@pytest.mark.parametrize('defect', ['missing', 'malformed', 'wrong_contract', 'future_status', 'authority', 'classification', 'new_episodes', 'maturation', 'boolean_type'])
def test_missing_or_invalid_owner_cannot_enable_classification_or_episodes(sandbox, monkeypatch, defect):
    owner = copy.deepcopy(OWNER)
    if defect == 'missing': ledger.ELIGIBILITY_STATUS.unlink()
    elif defect == 'malformed': ledger.ELIGIBILITY_STATUS.write_text('{')
    else:
        if defect == 'wrong_contract': owner['contract'] = 'UNKNOWN_v1'
        if defect == 'future_status': owner['status'] = 'ACTIVE'
        if defect == 'authority': owner['authority'] = 'PORTFOLIO_AUTHORITY'
        if defect == 'classification': owner['permissions']['mechanical_research_classification'] = True
        if defect == 'new_episodes': owner['permissions']['new_episode_creation'] = True
        if defect == 'maturation': owner['permissions']['existing_episode_maturation'] = True
        if defect == 'boolean_type': owner['permissions']['portfolio_execution'] = 0
        ledger.ELIGIBILITY_STATUS.write_text(json.dumps(owner))
    assert ledger.eligibility_binding()['owner_valid'] is False
    state, _ = ledger.classify([observation() for _ in range(25)], observation(entry_state='GRADUATED_ALTCOIN_TOPUP_ACTIVE'), None)
    assert state == 'REGIME_NOT_ACTIVE'
    assert ledger.update_episode('PULLBACK_ACTIVE_RESEARCH', observation(), NOW)['status'] == 'SUSPENDED_NO_EPISODE_MUTATION'
    monkeypatch.setattr(ledger, 'current_snapshot', lambda: pytest.fail('invalid owner must block new collection'))
    ledger.main()
    assert_firewall(json.loads(ledger.LATEST.read_text()))
    assert not ledger.episode_files()


@pytest.mark.parametrize('older', [False, True])
def test_duplicate_and_old_observations_preserve_bytes_and_refresh_suspended_state(sandbox, monkeypatch, older):
    write_history(25)
    recent = ledger.load_recent_observations()
    last = recent[-1]
    ledger.LATEST.write_text(json.dumps({'research_state': 'PULLBACK_ACTIVE_RESEARCH', 'authority': {'portfolio_execution': True}}))
    ledger.STATE.write_text(json.dumps({'research_state': 'PULLBACK_ACTIVE_RESEARCH'}))
    current = recent[-2] if older else last
    monkeypatch.setattr(ledger, 'current_snapshot', lambda: current)
    before = immutable_bytes()
    ledger.main()
    assert immutable_bytes() == before
    latest = json.loads(ledger.LATEST.read_text())
    assert_firewall(latest)
    assert_firewall(json.loads(ledger.STATE.read_text()))
    assert latest['duplicate_price_observation_skipped'] is True
    assert latest['out_of_order_price_observation_skipped'] is older


def test_missing_step_return_is_not_imputed_as_zero(sandbox):
    state, evidence = ledger.classify([observation() for _ in range(25)], observation(matched_top100_step_return_pct=None), None)
    assert state == 'REGIME_NOT_ACTIVE'
    assert evidence['step_return_percentile_rank'] is None


def test_immutable_observation_write_cannot_replace_history(sandbox):
    p = ledger.OBS / 'existing.json'
    p.parent.mkdir()
    p.write_text('{"original": true}\n')
    before = p.read_bytes()
    with pytest.raises(FileExistsError):
        ledger.write_json(p, {'original': False}, immutable=True)
    assert p.read_bytes() == before


def test_missing_legacy_entry_is_only_missing_context(sandbox, monkeypatch):
    monkeypatch.setattr(ledger, 'ENTRY_LATEST', sandbox / 'missing-entry.json')
    breadth = sandbox / 'breadth.json'
    breadth.write_text(json.dumps({'aggregate': {'advance_ratio': .5}, 'constituents': [{'asset_id': 'SYNTHETIC', 'price_usd': 100}]}))
    monkeypatch.setattr(ledger, 'BREADTH_LATEST', breadth)
    monkeypatch.setattr(ledger, 'hourly_latest_row', lambda: ({'run_id': 'SYNTHETIC'}, NOW,
        {'btc_close': '100', 'eth_close': '100', 'ethbtc_close': '1'}))
    snapshot = ledger.current_snapshot()
    assert snapshot['entry_state'] is None
    assert snapshot['hourly_sequence_run_id'] == 'SYNTHETIC'
