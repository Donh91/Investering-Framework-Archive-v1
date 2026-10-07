from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone

import pytest
from scripts.cycle_navigator.daily_price_journey import CONTRACT, COPY_CONTRACT, validate_daily_path, validated_public_copy
from scripts.cycle_navigator.build_public_live_precision import daily_observations


def forecast():
    freeze = {'btc_range_low': 80, 'btc_range_high': 120, 'eth_range_low': 80, 'eth_range_high': 120}
    path = {'contract': CONTRACT, 'forecast_week': '2026-W41', **{a: {'status': 'PUBLISHED', 'reason': 'Evidence-supported daily scenario', 'points': [{'day': i, 'low': 90, 'high': 115, 'expected_close': 99+i} for i in range(1, 8)]} for a in ('BTC', 'ETH')}}
    return freeze, path


def test_valid_forecast_is_not_mutated_and_legacy_is_compatible():
    freeze, path = forecast(); before = copy.deepcopy((freeze, path))
    assert validate_daily_path(path, freeze, 2026, 41) == path
    assert (freeze, path) == before
    assert validate_daily_path(None, freeze, 2026, 41) is None


@pytest.mark.parametrize('defect', ['week', 'order', 'missing_day', 'outside_range', 'nan', 'boolean', 'unsupported'])
def test_forecast_cannot_publish_wrong_dates_or_invented_bounds(defect):
    freeze, path = forecast()
    if defect == 'week': path['forecast_week'] = '2026-W40'
    elif defect == 'order': path['BTC']['points'][2]['day'] = 4
    elif defect == 'missing_day': path['BTC']['points'].pop()
    elif defect == 'outside_range': path['BTC']['points'][0]['high'] = 130
    elif defect == 'nan': path['BTC']['points'][0]['expected_close'] = float('nan')
    elif defect == 'boolean': path['BTC']['points'][0]['expected_close'] = True
    else: path['BTC']['status'] = 'UNAVAILABLE'
    with pytest.raises(ValueError): validate_daily_path(path, freeze, 2026, 41)


def observations(hours=24):
    monday = datetime(2026, 10, 5, tzinfo=timezone.utc)
    return [{'timestamp_utc': (monday+timedelta(hours=i)).isoformat(), **{a+'_'+key: str(v) for a in ('btc', 'eth') for key, v in [('low', 99), ('high', 110), ('close', 100+i/10)]}} for i in range(hours)]


def test_daily_actuals_deduplicate_and_stop_at_closed_source_hour():
    rows = observations(); rows.append(rows[3].copy())
    actual = daily_observations(rows, 2026, 41, now=datetime(2026, 10, 5, 12, 30, tzinfo=timezone.utc))
    assert actual['BTC'][0]['observed_hours'] == 12
    assert actual['BTC'][0]['close'] == 101.1
    assert actual['BTC'][0]['status'] == 'LIVE'
    assert actual['BTC'][1]['close'] is None
    assert actual['observed_through_utc'] == '2026-10-05T12:00:00Z'


def test_daily_gap_and_missing_price_are_unplotted_not_backfilled():
    rows = observations(); del rows[7]
    actual = daily_observations(rows, 2026, 41, now=datetime(2026, 10, 6, tzinfo=timezone.utc))
    assert actual['BTC'][0]['status'] == 'GAP'
    assert actual['BTC'][0]['close'] is None
    rows = observations(); rows[7]['btc_close'] = 'NaN'
    actual = daily_observations(rows, 2026, 41, now=datetime(2026, 10, 6, tzinfo=timezone.utc))
    assert actual['BTC'][0]['close'] is None
    assert actual['ETH'][0]['status'] == 'COMPLETE'


def protection_copy():
    return {'pullback_risk_state': 'BUILDING', 'pullback_class': 'ORDINARY_RETEST', 'public_explanation': {'contract': COPY_CONTRACT, 'summary': 'A routine retest is possible; a deep decline is not confirmed.', 'watch_for': 'Watch whether strength survives the next retest.', 'weakens_if': 'The warning weakens if participation and relative strength recover.', 'onset_start_day': 3, 'onset_end_day': 7}}


def test_llm_public_filter_binds_state_and_calendar_without_action_authority():
    p = protection_copy(); before = copy.deepcopy(p)
    value = validated_public_copy(p, 2026, 41)
    assert value['onset_start_utc'] == '2026-10-07T00:00:00Z'
    assert value['onset_end_utc'] == '2026-10-12T00:00:00Z'
    assert value['risk_state'] == 'BUILDING'
    assert value['action_authority'] is False
    assert p == before


@pytest.mark.parametrize('text', ['Sell now and rebuy lower', 'A guaranteed rebound', 'A 90% probability', 'The internal shadow score changed'])
def test_public_filter_rejects_new_actions_numbers_and_internal_jargon(text):
    p = protection_copy(); p['public_explanation']['summary'] = text
    assert validated_public_copy(p, 2026, 41) is None
