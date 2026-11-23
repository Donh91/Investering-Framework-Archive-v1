"""Source-bound weekly evidence and ordered, experimental sequences; no trading authority."""
from __future__ import annotations
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from scripts.cycle_navigator.signal_snapshot_shadow_v1 import _clock


def _number(x):
    return type(x) in (float, int) and math.isfinite(x)


def build_weekly_analysis(raw_bytes: bytes, expected_sha256: str, freeze_utc: str, expected_year: int, expected_week: int) -> dict:
    """Evidence available only when the actual bytes and *publication* clock are admissible.

    A self-reported publication clock is not independent proof of first availability.
    The caller must obtain expected_sha256 from a separately governed source binding.
    """
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if digest != expected_sha256:
        raise ValueError('SOURCE_DIGEST_MISMATCH')
    source = json.loads(raw_bytes)
    frozen = _clock(freeze_utc)
    generated = _clock(source['generated_at_utc'])
    end = datetime.fromisocalendar(expected_year, expected_week, 1).replace(tzinfo=timezone.utc) + timedelta(days=7)
    if source.get('contract') != 'WEEKLY_RAW_CALIBRATION_PACK_v3' or source.get('iso_year') != expected_year or source.get('iso_week') != expected_week:
        raise ValueError('SOURCE_WEEK_OR_CONTRACT_MISMATCH')
    if generated > frozen or generated < end or frozen < end:
        raise ValueError('SOURCE_NOT_AVAILABLE_AT_FREEZE')
    diag = source.get('hourly_gap_diagnostics') or {}
    if source.get('readiness') != 'READY' or diag.get('observed_hours') != 168 or diag.get('missing_hour_count') != 0:
        raise ValueError('SOURCE_INCOMPLETE')
    rows = {}
    sequence = source.get('hourly_sequence') or {}
    for asset in ('btc', 'eth', 'ethbtc'):
        r = (sequence.get(asset) or {}).get('week_range') or {}
        start, close = r.get('open'), r.get('close')
        if _number(start) and _number(close) and start > 0 and close > 0:
            delta = 100 * (close / start - 1)
            rows[asset] = {'status':'OBSERVED', 'open': start, 'close': close, 'unit':'ratio' if asset == 'ethbtc' else 'source_quote', 'change_pct': round(delta, 4), 'direction':'UP' if delta > 0 else 'DOWN' if delta < 0 else 'FLAT'}
        else:
            rows[asset] = {'status':'UNKNOWN', 'reason':'MISSING_OR_INVALID_PRICE'}
    return {
        'contract':'MASTER_MONDAY_SOURCE_ANALYSIS_SHADOW_v1', 'authority':'SHADOW_ONLY_NON_TRADING',
        'source_sha256':digest, 'source_clock_claim_utc':source['generated_at_utc'], 'independent_first_known_verified':False, 'pit_status':'SOURCE_CLOCK_CLAIM_ONLY_NOT_INDEPENDENTLY_VERIFIED',
        'freeze_utc':freeze_utc, 'completed_week':f'{expected_year}-W{expected_week:02d}',
        'settled_week':rows,
        'other_families':{k:'UNKNOWN_NOT_INDEPENDENTLY_ADMITTED' for k in ('etf','breadth','btc_dominance','funding','liquidation','oi','rotation')},
        'operational_translation':{
            'contract':'MM_NON_TRADING_TRANSLATION_SHADOW_v1',
            'status':'PARTIAL' if all(x['status']=='OBSERVED' for x in rows.values()) else 'INCOMPLETE',
            'facts':[{ 'family':k, 'direction':v.get('direction'), 'change_pct':v.get('change_pct'), 'source_sha256':digest } for k,v in rows.items() if v['status']=='OBSERVED'],
            'missing_evidence':['etf','breadth','btc_dominance','funding','liquidation','oi','rotation'],
            'next_observation':'Require independently timed, source-bound market signals before claiming broad rotation or confirmation.',
            'portfolio_action':False, 'forecast_authority':False,
        },
    }


SEQUENCES = {
    'leadership_transmission': ('ethbtc', 'btc_dominance', 'breadth'),
    'etf_weakness_breadth': ('etf', 'ethbtc', 'breadth'),
    'stress_reset_reclaim': ('stress', 'reset', 'reclaim'),
}

def ordered_sequence(name: str, events: list[dict], freeze_utc: str, source_bytes: dict[str, bytes]) -> dict:
    """Evaluate preclassified shadow events only. This is not a price forecast.

    True events have to be individually source-bound by the caller; unknown,
    contradictory, late, duplicate, equal-time, or out-of-order steps abstain.
    """
    if name not in SEQUENCES:
        raise ValueError('UNKNOWN_SEQUENCE')
    frozen = _clock(freeze_utc)
    expected = SEQUENCES[name]
    base = {'contract':'CN_SEQUENCE_SHADOW_v1','authority':'SHADOW_ONLY','sequence':name,'status':'UNKNOWN','portfolio_action':False,'forecast_authority':False}
    if len(events) != len(expected) or [e.get('family') for e in events] != list(expected):
        return {**base,'reason':'MISSING_DUPLICATE_OR_WRONG_STEP'}
    clocks=[]
    for event in events:
        digest = event.get('source_sha256')
        payload = source_bytes.get(digest) if isinstance(digest, str) else None
        if event.get('admission') != 'ADMITTED' or event.get('state') is not True or not isinstance(payload, bytes) or hashlib.sha256(payload).hexdigest() != digest:
            return {**base,'reason':'STEP_NOT_VERIFIED_OR_UNKNOWN'}
        observed, available = _clock(event['observed_at_utc']), _clock(event['available_at_utc'])
        if observed > available or available > frozen:
            return {**base,'reason':'PIT_CLOCK'}
        clocks.append(observed)
    if not all(a < b for a,b in zip(clocks,clocks[1:])):
        return {**base,'reason':'PRECEDENCE_NOT_ESTABLISHED'}
    return {**base,'status':'ORDERED_CLAIMS_ONLY','reason':'EVENT_SEMANTICS_AND_FIRST_KNOWN_NOT_INDEPENDENTLY_VERIFIED','steps':events}
