"""Offline private-source health inspection for existing Forward Path #1516.

This is not a collector, source admission, forecaster or ledger writer. Raw
provider bytes stay in the caller's restricted plane; returned metadata has no
prices. Receiver capture is never substituted for original provider first-known.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Mapping

CONTRACT = 'FORWARD_PRICE_SOURCE_CUSTODY_RESEARCH_RECEIPT_v1'


def _stamp(value: Any) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z', value
    ):
        raise ValueError('EXACT_UTC_REQUIRED')
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def _json(raw: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result: raise ValueError('DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    def invalid(_): raise ValueError('NONFINITE_JSON')
    try:
        value = json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('SOURCE_JSON_INVALID') from exc
    if not isinstance(value, dict) or value.get('error') != [] or not isinstance(value.get('result'), dict):
        raise ValueError('PROVIDER_RESPONSE_INVALID')
    return value['result']


def _number(value: Any, *, positive=True) -> float:
    if not isinstance(value, str): raise ValueError('PROVIDER_NUMERIC_STRING_REQUIRED')
    try:
        number = float(value)
    except (ValueError, OverflowError):
        # Raw malformed provider strings must not enter public logs or a
        # chained traceback when this inspector runs in the private plane.
        raise ValueError('PROVIDER_VALUE_INVALID') from None
    if not math.isfinite(number) or (number <= 0 if positive else number < 0):
        raise ValueError('PROVIDER_VALUE_INVALID')
    return number


def inspect_custody(manifest: Mapping[str, Any], blobs: Mapping[str, bytes], *, as_of_utc: str) -> dict:
    """Validate record-only custody; always return source_admitted=False.

    Git reachability/private-main binding must separately be established by the
    existing owner. No manifest field can self-authorize issuance or scoring.
    """
    if not isinstance(manifest, dict) or not isinstance(blobs, dict):
        raise ValueError('CUSTODY_SCHEMA_INVALID')
    expected = {'contract': CONTRACT, 'private_repository': 'Donh91/secrets',
        'provider': 'KRAKEN', 'status': 'CAPTURED_NOT_ADMITTED',
        'validation_status': 'CAPTURED_NOT_ADMITTED',
        'original_historical_provider_first_known_verified': False,
        'collector_commit_sha': None, 'new_forecast_issued': False,
        'outcome_scoring_performed': False, 'round3_access': False}
    if any(key not in manifest or type(manifest[key]) is not type(value) or manifest[key] != value
           for key, value in expected.items()):
        raise ValueError('RECORD_ONLY_AUTHORITY_REQUIRED')
    now = _stamp(as_of_utc)
    items = manifest.get('items')
    if (not isinstance(items, list) or len(items) != 3 or
        any(not isinstance(item, dict) for item in items) or
        {item.get('name') for item in items} != {'pair', 'daily', 'hourly'} or
        set(blobs) != {'pair', 'daily', 'hourly'}):
        raise ValueError('EXACT_THREE_SOURCE_MEMBERS_REQUIRED')
    decoded, captures, digests = {}, {}, {}
    for item in items:
        name = item['name']; raw = blobs[name]
        if (not isinstance(raw, bytes) or not raw or len(raw) > 1_000_000 or
            type(item.get('bytes')) is not int or item['bytes'] != len(raw) or
            item.get('sha256') != hashlib.sha256(raw).hexdigest()):
            raise ValueError('SOURCE_BYTES_HASH_MISMATCH')
        if (item.get('exact_relative_path') != name + '.json' or
            item.get('instrument_id') != 'XXBTZUSD' or item.get('base') != 'BTC' or
            item.get('quote') != 'USD' or type(item.get('http_status')) is not int or
            item['http_status'] != 200):
            raise ValueError('INSTRUMENT_PATH_OR_STATUS_INVALID')
        start = _stamp(item.get('retrieval_start_utc')); end = _stamp(item.get('retrieval_end_utc'))
        if not start <= end <= now: raise ValueError('CAPTURE_CLOCK_INVALID')
        try: server = parsedate_to_datetime(item['response_headers']['date'])
        except (ValueError, TypeError, KeyError) as exc: raise ValueError('HTTP_CLOCK_INVALID') from exc
        if server.tzinfo is None or not start - timedelta(seconds=1) <= server <= end + timedelta(seconds=1):
            raise ValueError('HTTP_CLOCK_INVALID')
        decoded[name] = _json(raw); captures[name] = (start, end); digests[name] = item['sha256']
    pair = decoded['pair']
    if (set(pair) != {'XXBTZUSD'} or not isinstance(pair['XXBTZUSD'], dict) or
        pair['XXBTZUSD'].get('base') != 'XXBT' or pair['XXBTZUSD'].get('quote') != 'ZUSD'):
        raise ValueError('PROVIDER_BTC_USD_IDENTITY_REQUIRED')
    counts, closes = {}, {}
    for name, step in [('daily', 86400), ('hourly', 3600)]:
        result = decoded[name]; item = next(x for x in items if x['name'] == name)
        rows = result.get('XXBTZUSD')
        if set(result) != {'XXBTZUSD', 'last'} or not isinstance(rows, list) or not 2 <= len(rows) <= 1000:
            raise ValueError('OHLC_MEMBER_SCHEMA_INVALID')
        previous = None
        for row in rows:
            if (not isinstance(row, list) or len(row) != 8 or type(row[0]) is not int or
                row[0] < 0 or row[0] % step or
                (previous is not None and row[0] != previous + step)):
                raise ValueError('BAR_CLOCK_GAP_OR_DUPLICATE')
            previous = row[0]
            opening, high, low, close, vwap = [_number(row[i]) for i in (1, 2, 3, 4, 5)]
            _number(row[6], positive=False)
            if (not low <= min(opening, close) <= max(opening, close) <= high or
                type(row[7]) is not int or row[7] < 0): raise ValueError('OHLC_INVALID')
        start, end = captures[name]
        final_open = datetime.fromtimestamp(rows[-1][0], timezone.utc)
        # Kraken always returns the current uncommitted final interval. Exclude
        # it even if a response was captured across an interval boundary.
        if not start - timedelta(seconds=step) < final_open <= end < final_open + timedelta(seconds=step):
            raise ValueError('CURRENT_FINAL_INTERVAL_CLOCK_INVALID')
        last_close = datetime.fromtimestamp(rows[-2][0] + step, timezone.utc)
        if last_close > start or now - last_close > timedelta(hours=48):
            raise ValueError('SOURCE_UNCOMPLETED_OR_STALE')
        if name == 'daily' and len(rows) - 1 < 252: raise ValueError('DAILY_HISTORY_INSUFFICIENT')
        required = {'interval_seconds': step, 'completed_rows': len(rows)-1,
            'returned_rows': len(rows), 'excluded_final_current_interval': 1, 'gap_count': 0}
        if any(type(item.get(k)) is not int or item[k] != v for k, v in required.items()):
            raise ValueError('FALSE_COMPLETENESS_METADATA')
        if (_stamp(item.get('latest_completed_close_utc')) != last_close or
            _stamp(item.get('first_completed_open_utc')) != datetime.fromtimestamp(rows[0][0], timezone.utc)):
            raise ValueError('FALSE_SOURCE_CLOCK_METADATA')
        counts[name] = len(rows)-1
        closes[name] = last_close.isoformat().replace('+00:00', 'Z')
    return {'contract': 'FORWARD_PRICE_SOURCE_CUSTODY_HEALTH_v1', 'health_status': 'PASS',
        'status': 'CAPTURED_NOT_ADMITTED', 'reason': 'ORIGINAL_PROVIDER_FIRST_KNOWN_UNVERIFIED',
        'source_admitted': False, 'forecast_issued': False, 'forecast_status': 'UNAVAILABLE',
        'historical_replay_allowed': False, 'collector_lineage_verified': False,
        'private_main_reachability_verified': False, 'outcome_scoring_allowed': False,
        'completed_rows': counts, 'latest_completed_close_utc': closes,
        'source_sha256': digests, 'quote': 'USD', 'asset': 'BTC'}
