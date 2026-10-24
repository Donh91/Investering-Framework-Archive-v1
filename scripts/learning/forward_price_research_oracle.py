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
    if type(value) not in (float, int) or not math.isfinite(value) or value <= 0:
        raise ValueError('POSITIVE_FINITE_PRICE_REQUIRED')
    return float(value)


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
    actual_low, actual_high = min(lows), max(highs)
    rows = []
    for entry in issue['candidates']:
        if entry['status'] != 'CANDIDATE':
            rows.append({'method': entry['method'], 'status': entry['status'], 'joint_contained': None,
                         'width_pct': None, 'breach_pct': None, 'research_loss': None})
            continue
        low, high = positive(entry['low_usd']), positive(entry['high_usd'])
        width = (high - low) / anchor * 100
        breach = (max(0.0, low - actual_low) + max(0.0, actual_high - high)) / anchor * 100
        # Width + 2 x observed breach is a *descriptive research loss*, not a
        # proper interval score, predicted coverage or calibrated probability.
        rows.append({'method': entry['method'], 'status': 'DESCRIPTIVE_ONLY',
                     'joint_contained': actual_low >= low and actual_high <= high,
                     'width_pct': width, 'breach_pct': breach,
                     'research_loss': width + 2.0 * breach})
    return {'status': 'MATURED_DESCRIPTIVE_ONLY', 'eligible_for_canonical_score': False,
            'research_only': True, 'calibration': 'INCONCLUSIVE',
            'effective_independent_n': 0, 'candidate_results': rows}
