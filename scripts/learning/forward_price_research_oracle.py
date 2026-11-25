"""Offline synthetic/reference oracle for #1516 F3/F4 acceptance tests.

No network, file access, source admission, forecast issuance, canonical scorer,
public projection, automation, model selection, or investment authority.
Input prices and full results belong in the restricted owner if used with real data.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timedelta
from typing import Any

CONTRACT = 'FORWARD_PRICE_RANGE_RESEARCH_ORACLE_v0_1'
UTC = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z')
HEX = re.compile(r'[0-9a-f]{64}')


def stamp(value: Any) -> datetime:
    if not isinstance(value, str) or not UTC.fullmatch(value):
        raise ValueError('EXACT_UTC_REQUIRED')
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('INVALID_UTC') from None


def positive(value: Any) -> float:
    if type(value) not in (float, int):
        raise ValueError('POSITIVE_FINITE_PRICE_REQUIRED')
    try:
        number = float(value)
    except (OverflowError, ValueError):
        raise ValueError('POSITIVE_FINITE_PRICE_REQUIRED') from None
    if not math.isfinite(number) or number <= 0:
        raise ValueError('POSITIVE_FINITE_PRICE_REQUIRED')
    return number


def digest(value: Any) -> str:
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False) + '\n').encode()).hexdigest()


def check_issue(issue: Any) -> dict:
    """Validate immutable *research fixture*, never independent custody proof."""
    if not isinstance(issue, dict) or set(issue) != {
        'contract', 'freeze_sha256', 'forecast_id', 'asset', 'quote', 'venue',
        'issued_at_utc', 'published_at_utc', 'source_as_of_utc',
        'source_manifest_sha256', 'source_authority', 'target_start_utc',
        'target_end_utc', 'anchor_usd', 'candidates', 'authority'
    }:
        raise ValueError('ORIGINAL_ISSUE_SCHEMA_INVALID')
    if issue['contract'] != CONTRACT or issue['asset'] not in ('BTC', 'ETH') or issue['quote'] != 'USD':
        raise ValueError('ASSET_QUOTE_CONTRACT_INVALID')
    if not isinstance(issue['venue'], str) or not issue['venue'].strip():
        raise ValueError('VENUE_REQUIRED')
    if not isinstance(issue['forecast_id'], str) or not issue['forecast_id'].strip():
        raise ValueError('ISSUE_ID_REQUIRED')
    if issue['source_authority'] != 'NOT_INDEPENDENTLY_ADMITTED':
        raise ValueError('SELF_PROMOTION_FORBIDDEN')
    if issue['authority'] != {'research_only': True, 'issuer': False, 'canonical_score': False,
                              'public_release': False, 'portfolio_action': False}:
        raise ValueError('RESEARCH_ONLY_AUTHORITY_REQUIRED')
    for h in ('freeze_sha256', 'source_manifest_sha256'):
        if not isinstance(issue[h], str) or not HEX.fullmatch(issue[h]):
            raise ValueError('DIGEST_FORMAT_INVALID')
    if digest({k: v for k, v in issue.items() if k != 'freeze_sha256'}) != issue['freeze_sha256']:
        raise ValueError('ORIGINAL_FREEZE_MUTATED')
    source = stamp(issue['source_as_of_utc']); issued = stamp(issue['issued_at_utc'])
    published = stamp(issue['published_at_utc']); start = stamp(issue['target_start_utc'])
    end = stamp(issue['target_end_utc'])
    if not source <= issued <= published <= start < end:
        raise ValueError('PIT_ISSUE_PUBLISH_TARGET_CLOCK_INVALID')
    if issued - source > timedelta(hours=48):
        raise ValueError('SOURCE_STALE_AT_ISSUE')
    anchor = positive(issue['anchor_usd'])
    if not isinstance(issue['candidates'], list) or not 1 <= len(issue['candidates']) <= 8:
        raise ValueError('CANDIDATE_COUNT_INVALID')
    names = set()
    for row in issue['candidates']:
        if not isinstance(row, dict) or set(row) != {'method', 'status', 'low_usd', 'high_usd', 'reason'}:
            raise ValueError('CANDIDATE_SCHEMA_INVALID')
        method = row['method']
        if not isinstance(method, str) or not method.strip() or method in names:
            raise ValueError('DUPLICATE_OR_BLANK_METHOD')
        names.add(method)
        if row['status'] == 'CANDIDATE':
            lo = positive(row['low_usd']); hi = positive(row['high_usd'])
            if not lo < hi or row['reason'] is not None:
                raise ValueError('ENVELOPE_INVALID')
        elif row['status'] in ('ABSTAIN', 'UNAVAILABLE'):
            if row['low_usd'] is not None or row['high_usd'] is not None or not isinstance(row['reason'], str) or not row['reason'].strip():
                raise ValueError('ABSTENTION_MUST_HAVE_NULL_PRICES')
        else:
            raise ValueError('CANDIDATE_STATUS_INVALID')
    return {'start': start, 'end': end, 'anchor': anchor}


def inspect_completed_window(issue: dict, observations: Any, *, observed_as_of_utc: str) -> dict:
    """Compute NONCANONICAL diagnostics only on complete, post-issue UTC OHLC.

    Incomplete or late/unbound observations never earn a prospective 'hit'.
    Results require independent source admission before an owner can score them.
    """
    context = check_issue(issue)
    start, end, anchor = context['start'], context['end'], context['anchor']
    asof = stamp(observed_as_of_utc)
    if asof < end:
        return {'status': 'PENDING_MATURITY', 'eligible_for_canonical_score': False,
                'research_only': True, 'candidate_results': None}
    if not isinstance(observations, list) or not observations:
        return {'status': 'UNAVAILABLE_NO_COMPLETE_OBSERVATIONS', 'eligible_for_canonical_score': False,
                'research_only': True, 'candidate_results': None}
    cursor = start; lows = []; highs = []
    for bar in observations:
        if not isinstance(bar, dict) or set(bar) != {
            'start_utc', 'end_utc', 'first_known_at_utc', 'low_usd', 'high_usd'
        }:
            raise ValueError('OBSERVATION_SCHEMA_INVALID')
        left = stamp(bar['start_utc']); right = stamp(bar['end_utc'])
        first_known = stamp(bar['first_known_at_utc'])
        if left != cursor or not left < right <= end or not right < first_known <= asof:
            return {'status': 'INELIGIBLE_GAPPED_PARTIAL_OR_FUTURE_WINDOW',
                    'eligible_for_canonical_score': False, 'research_only': True,
                    'candidate_results': None}
        lo = positive(bar['low_usd']); hi = positive(bar['high_usd'])
        if lo > hi:
            raise ValueError('OBSERVATION_OHLC_INVERTED')
        cursor = right; lows.append(lo); highs.append(hi)
    if cursor != end:
        return {'status': 'INELIGIBLE_INCOMPLETE_WINDOW', 'eligible_for_canonical_score': False,
                'research_only': True, 'candidate_results': None}
    return _score_ranges(issue['candidates'], min(lows), max(highs), anchor, quote='USD')


def _score_ranges(candidates, actual_low, actual_high, anchor, *, quote):
    """Same unit-preserving loss for the two explicitly distinct contracts."""
    if quote not in ('USD','USDT'):
        raise ValueError('ASSET_QUOTE_CONTRACT_INVALID')
    lo_field,hi_field='low_'+quote.lower(),'high_'+quote.lower()
    rows = []
    for entry in candidates:
        if entry['status'] != 'CANDIDATE':
            rows.append({'method': entry['method'], 'status': entry['status'], 'joint_contained': None,
                         'width_pct': None, 'breach_pct': None, 'research_loss': None})
            continue
        low, high = positive(entry[lo_field]), positive(entry[hi_field])
        width = (high - low) / anchor * 100
        breach = (max(0.0, low - actual_low) + max(0.0, actual_high - high)) / anchor * 100
        if not math.isfinite(width) or not math.isfinite(breach) or not math.isfinite(width + 2.0 * breach):
            raise ValueError('RESEARCH_DIAGNOSTIC_NONFINITE')
        # Width + 2 x observed breach is a *descriptive research loss*, not a
        # proper interval score, predicted coverage or calibrated probability.
        rows.append({'method': entry['method'], 'status': 'DESCRIPTIVE_ONLY',
                     'joint_contained': actual_low >= low and actual_high <= high,
                     'width_pct': width, 'breach_pct': breach,
                     'research_loss': width + 2.0 * breach})
    return {'status': 'MATURED_DESCRIPTIVE_ONLY', 'eligible_for_canonical_score': False,
            'research_only': True, 'calibration': 'INCONCLUSIVE',
            'effective_independent_n': 0, 'candidate_results': rows}


NATIVE_COMPARISON_CONTRACT = 'FORWARD_PRICE_NATIVE_USDT_MATCHED_WINDOW_RESEARCH_v1'
NATIVE_OBSERVATION_CONTRACT = 'FORWARD_PRICE_NATIVE_USDT_DAILY_OUTCOME_RESEARCH_v1'


def inspect_native_usdt_candidate(payload, freeze, observations, *, observed_as_of_utc):
    """Recompute the existing BTCUSDT model and inspect one complete future window.

    No issue writer: both the frozen comparison and outcome binding are supplied
    by the original owner. Digests prove consistency, not network origin, main
    custody, original provider vintage or actual first delivery. The evaluation
    is noncanonical, descriptive only, and never converts USDT to USD.
    Target begins at the first full UTC day at or after claimed delivery.
    The last settled model anchor can predate target start; record that lead
    gap explicitly. No calibrated coverage or equivalence to zero-gap training.
    """
    from scripts.learning.forward_price_shadow import build_native_usdt_shadow, USDT_HORIZONS

    required={'contract','authority','asset','quote','venue','horizon_days',
              'candidate_sha256','source_manifest_sha256','source_rows_sha256',
              'issued_at_utc','delivery_clock_claim_utc','target_start_utc','target_end_utc',
              'freeze_sha256'}
    authority={'research_only':True,'issuer':False,'canonical_score':False,
               'public_release':False,'portfolio_action':False}
    if not isinstance(freeze,dict) or set(freeze)!=required:
        raise ValueError('NATIVE_COMPARISON_FREEZE_SCHEMA_INVALID')
    if (freeze['contract']!=NATIVE_COMPARISON_CONTRACT or freeze['asset']!='BTC'
            or freeze['quote']!='USDT' or freeze['venue']!='BINANCE_SPOT_BTCUSDT'
            or freeze['authority']!=authority or any(type(freeze['authority'][k]) is not bool for k in authority)
            or type(freeze['horizon_days']) is not int or freeze['horizon_days'] not in USDT_HORIZONS):
        raise ValueError('NATIVE_COMPARISON_IDENTITY_INVALID')
    if freeze['freeze_sha256']!=digest({k:v for k,v in freeze.items() if k!='freeze_sha256'}):
        raise ValueError('NATIVE_COMPARISON_FREEZE_MUTATED')
    # Recompute, rather than accepting any caller-supplied target prices or
    # candidate digest whose preimage was not independently evaluated here.
    candidate=build_native_usdt_shadow(payload)
    if (freeze['candidate_sha256']!=candidate['candidate_sha256']
            or freeze['source_manifest_sha256']!=candidate['input_source_sha256']
            or freeze['source_rows_sha256']!=candidate['input_canonical_rows_sha256']
            or freeze['issued_at_utc']!=candidate['issued_at_utc']):
        raise ValueError('NATIVE_COMPARISON_MODEL_BINDING_MISMATCH')
    issued=stamp(freeze['issued_at_utc']); delivered=stamp(freeze['delivery_clock_claim_utc'])
    start=stamp(freeze['target_start_utc']);end=stamp(freeze['target_end_utc'])
    asof=stamp(observed_as_of_utc)
    day_start=delivered.replace(hour=0,minute=0,second=0,microsecond=0)
    first_full_day=day_start if delivered==day_start else day_start+timedelta(days=1)
    if (not issued<=delivered<=start or delivered-issued>timedelta(hours=48)
            or start!=first_full_day or end!=start+timedelta(days=freeze['horizon_days'])):
        raise ValueError('NATIVE_COMPARISON_TARGET_CLOCK_INVALID')
    anchor_close=stamp(payload['bars'][-1]['day_utc']+'T00:00:00Z')+timedelta(days=1)
    if not anchor_close<=issued:
        raise ValueError('NATIVE_COMPARISON_ANCHOR_CLOCK_INVALID')
    h=str(freeze['horizon_days'])
    entries=[]
    for method,bands in ((candidate['method'],candidate['horizons_days']),
                         (candidate['descriptive_alternative_method'],candidate['descriptive_q25_q75_horizons_days'])):
        b=bands[h]
        entries.append({'method':method,'status':'CANDIDATE' if b['status']=='SHADOW_BASELINE_ONLY' else 'ABSTAIN',
                        'low_usdt':b['low_usdt'],'high_usdt':b['high_usdt']})
    base={'contract':NATIVE_COMPARISON_CONTRACT,'asset':'BTC','quote':'USDT','venue':'BINANCE_SPOT_BTCUSDT',
          'horizon_days':freeze['horizon_days'],'freeze_sha256':freeze['freeze_sha256'],
          'candidate_sha256':candidate['candidate_sha256'],
          'anchor_to_target_start_hours':(start-anchor_close).total_seconds()/3600,
          'target_start_utc':freeze['target_start_utc'],'target_end_utc':freeze['target_end_utc'],
          'eligible_for_canonical_score':False,'research_only':True,'effective_independent_n':0,
          'calibration':'INCONCLUSIVE','source_custody_verified':False,'first_delivery_verified':False,
          'coverage_probability':None,'candidate_results':None,'forecast_issued':False}
    if asof<end:
        return {**base,'status':'PENDING_MATURITY'}
    if observations is None:
        return {**base,'status':'UNAVAILABLE_NO_COMPLETE_OBSERVATIONS'}
    required_out={'contract','asset','quote','venue','freeze_sha256','source_manifest_sha256','rows','rows_sha256'}
    if (not isinstance(observations,dict) or set(observations)!=required_out
            or observations['contract']!=NATIVE_OBSERVATION_CONTRACT
            or observations['asset']!='BTC' or observations['quote']!='USDT'
            or observations['venue']!='BINANCE_SPOT_BTCUSDT'
            or observations['freeze_sha256']!=freeze['freeze_sha256']
            or not isinstance(observations['source_manifest_sha256'],str)
            or not HEX.fullmatch(observations['source_manifest_sha256'])):
        raise ValueError('NATIVE_OUTCOME_SOURCE_BINDING_INVALID')
    rows=observations['rows']
    if not isinstance(rows,list) or len(rows)>freeze['horizon_days'] or observations['rows_sha256']!=digest(rows):
        raise ValueError('NATIVE_OUTCOME_ROWS_BINDING_INVALID')
    lows=[];highs=[];cursor=start
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'start_utc','end_utc','first_known_at_utc','low_usdt','high_usdt','close_usdt'}:
            raise ValueError('NATIVE_OUTCOME_ROW_SCHEMA_INVALID')
        left=stamp(row['start_utc']);right=stamp(row['end_utc']);known=stamp(row['first_known_at_utc'])
        if not (left==cursor and right==left+timedelta(days=1) and right<=end and right<known<=asof):
            return {**base,'status':'INELIGIBLE_GAPPED_PARTIAL_OR_FUTURE_WINDOW'}
        lo,hi,close=map(positive,(row['low_usdt'],row['high_usdt'],row['close_usdt']))
        if not lo<=close<=hi:
            raise ValueError('NATIVE_OUTCOME_OHLC_INVALID')
        lows.append(lo);highs.append(hi);cursor=right
    if cursor!=end or len(rows)!=freeze['horizon_days']:
        return {**base,'status':'INELIGIBLE_INCOMPLETE_WINDOW'}
    evaluated=_score_ranges(entries,min(lows),max(highs),positive(candidate['anchor_usdt']),quote='USDT')
    return {**base,**evaluated,'outcome_rows_sha256':observations['rows_sha256'],
            'outcome_source_manifest_sha256':observations['source_manifest_sha256']}
