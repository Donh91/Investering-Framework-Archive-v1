#!/usr/bin/env python3
"""Read-only/offline aggregator evidence QA, no market/trade authority.

Input: {"case_id": "ASCII_ID", "observations": [{"provider": "DEXPAPRIKA"|
"DEXSCREENER"|"GECKOTERMINAL", "captured_at_utc": RFC3339,
"payload": provider JSON, "http_status": optional HTTP integer}, ...]}.
Outputs only source-health flags and SHA-256 hashes, never raw market data.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import re
from pathlib import Path
import sys
from typing import Any

CONTRACT = 'INHOUSE_AGGREGATOR_SOURCE_QA_V1'
PROVIDERS = ('DEXPAPRIKA', 'DEXSCREENER', 'GECKOTERMINAL')
CHAIN_ALIASES = {'eth': 'ethereum', 'ethereum-mainnet': 'ethereum',
                 'sol': 'solana', 'robinhood-chain': 'robinhood'}


def _time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if d.tzinfo is None:
            return None
        return d.astimezone(timezone.utc)
    except ValueError:
        return None


def _timestamp_ms(value: Any) -> datetime | None:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        return None
    try:
        return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
    except (ValueError, OverflowError, OSError):
        return None


def _amount(value: Any) -> tuple[str, float | None]:
    if value is None or value == '':
        return 'UNKNOWN', None
    try:
        if isinstance(value, bool):
            raise ValueError('boolean is not number')
        v = float(value)
        if not math.isfinite(v) or v < 0:
            return 'INVALID', None
        return ('ZERO' if v == 0 else 'POSITIVE'), v
    except (ValueError, TypeError, OverflowError):
        return 'INVALID', None


def _chain(value: Any) -> str:
    c = str(value or '').lower()
    return CHAIN_ALIASES.get(c, c)


def _addr(chain: str, value: Any) -> str:
    s = str(value or '').strip()
    return s if chain == 'solana' else s.lower()


def _nested(obj: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _gecko_token_id(obj: Any, network: str) -> str:
    s = str(_nested(obj, 'data', 'id') or '')
    prefix = network + '_'
    return s[len(prefix):] if s.startswith(prefix) else ''


def _extract(provider: str, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError('PAYLOAD_NOT_OBJECT')
    if provider == 'DEXPAPRIKA':
        # Pool details endpoint, not search index: search results lack base/quote roles.
        ch = _chain(payload.get('chain'))
        return {'chain': ch, 'pool': _addr(ch, payload.get('id')),
                'base': _addr(ch, payload.get('base_token_id')),
                'quote': _addr(ch, payload.get('quote_token_id')),
                'liquidity': payload.get('liquidity_usd'),
                'volume': payload.get('volume_usd_24h'),
                'pool_created': _time(payload.get('created_at')),
                'market_updated': _time(payload.get('price_time'))}
    if provider == 'DEXSCREENER':
        pair = payload.get('pair')
        if not isinstance(pair, dict):
            pairs = payload.get('pairs')
            pair = pairs[0] if isinstance(pairs, list) and len(pairs) == 1 else None
        if not isinstance(pair, dict):
            raise ValueError('PAIR_MISSING_OR_AMBIGUOUS')
        ch = _chain(pair.get('chainId'))
        return {'chain': ch, 'pool': _addr(ch, pair.get('pairAddress')),
                'base': _addr(ch, _nested(pair, 'baseToken', 'address')),
                'quote': _addr(ch, _nested(pair, 'quoteToken', 'address')),
                'liquidity': _nested(pair, 'liquidity', 'usd'),
                'volume': _nested(pair, 'volume', 'h24'),
                'pool_created': _timestamp_ms(pair.get('pairCreatedAt')),
                'market_updated': None}
    if provider == 'GECKOTERMINAL':
        data = payload.get('data')
        if not isinstance(data, dict):
            raise ValueError('DATA_MISSING')
        attrs = data.get('attributes')
        if not isinstance(attrs, dict):
            raise ValueError('ATTRIBUTES_MISSING')
        rid = str(data.get('id') or '')
        network = rid.split('_', 1)[0]
        ch = _chain(network)
        return {'chain': ch, 'pool': _addr(ch, attrs.get('address')),
                'base': _addr(ch, _gecko_token_id(_nested(data, 'relationships', 'base_token'), network)),
                'quote': _addr(ch, _gecko_token_id(_nested(data, 'relationships', 'quote_token'), network)),
                'liquidity': attrs.get('reserve_in_usd'),
                'volume': _nested(attrs, 'volume_usd', 'h24'),
                'pool_created': _time(attrs.get('pool_created_at')),
                'market_updated': None}
    raise ValueError('PROVIDER_UNSUPPORTED')


def _digest(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def evaluate_case(case: dict[str, Any], *, max_age_seconds: int = 120,
                  max_birth_disagreement_seconds: int = 3600) -> dict[str, Any]:
    if not isinstance(case, dict) or not isinstance(case.get('case_id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', case['case_id']):
        raise ValueError('CASE_ID_REQUIRED')
    observations = case.get('observations')
    if not isinstance(observations, list) or not observations:
        raise ValueError('OBSERVATIONS_REQUIRED')
    parsed = []
    results = []
    seen_providers = set()
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError('OBSERVATION_NOT_OBJECT')
        provider = str(row.get('provider') or '').upper()
        if provider not in PROVIDERS or provider in seen_providers:
            raise ValueError('PROVIDER_UNKNOWN_OR_DUPLICATE')
        seen_providers.add(provider)
        flags: set[str] = set()
        captured = _time(row.get('captured_at_utc'))
        if not captured:
            flags.add('CAPTURE_TIME_UNKNOWN')
        status = row.get('http_status', 200)
        payload = row.get('payload')
        digest = None
        try:
            digest = _digest(payload)
        except (ValueError, TypeError):
            flags.add('PAYLOAD_UNHASHABLE')
        if not isinstance(status, int) or isinstance(status, bool) or not 200 <= status < 300:
            flags.add('SOURCE_UNAVAILABLE')
        else:
            try:
                item = _extract(provider, payload)
                if not all(item[k] for k in ('chain', 'pool', 'base', 'quote')):
                    flags.add('IDENTITY_INCOMPLETE')
                else:
                    parsed.append((provider, item))
                for key, label in [('liquidity', 'LIQUIDITY'), ('volume', 'VOLUME')]:
                    value_state, _ = _amount(item.get(key))
                    if value_state == 'UNKNOWN':
                        flags.add(label + '_UNKNOWN')
                    elif value_state == 'INVALID':
                        flags.add(label + '_INVALID')
                    elif value_state == 'ZERO':
                        flags.add(label + '_ZERO')
                market = item.get('market_updated')
                if not market or not captured:
                    flags.add('SOURCE_FRESHNESS_UNKNOWN')
                elif market > captured:
                    flags.add('SOURCE_TIME_IN_FUTURE')
                elif (captured - market).total_seconds() > max_age_seconds:
                    flags.add('SOURCE_STALE')
            except (KeyError, ValueError, TypeError, AttributeError) as err:
                flags.add('PARSE_UNAVAILABLE')
                flags.add('PARSE_' + str(err).upper()[:64].replace(' ', '_'))
        results.append({'provider': provider, 'payload_sha256': digest, 'flags': sorted(flags)})
    conflicts = set()
    if len(parsed) >= 2:
        captures = [_time(row.get('captured_at_utc')) for row in observations]
        captures = [c for c in captures if c is not None]
        if len(captures) >= 2 and (max(captures) - min(captures)).total_seconds() > 60:
            conflicts.add('CAPTURE_WINDOW_MISMATCH')
        identities = {(item['chain'], item['pool'], item['base'], item['quote']) for _, item in parsed}
        if len(identities) > 1:
            conflicts.add('POOL_OR_TOKEN_IDENTITY_CONFLICT')
        dates = [item['pool_created'] for _, item in parsed if item.get('pool_created')]
        if len(dates) >= 2 and (max(dates) - min(dates)).total_seconds() > max_birth_disagreement_seconds:
            conflicts.add('POOL_CREATION_CLAIM_CONFLICT')
    if len(parsed) < 2:
        conflicts.add('NO_MULTI_SOURCE_COMPARISON')
    if any(set(x['flags']) & {'SOURCE_UNAVAILABLE', 'PARSE_UNAVAILABLE', 'IDENTITY_INCOMPLETE'} for x in results):
        conflicts.add('SOURCE_COVERAGE_PARTIAL')
    if any(set(x['flags']) & {'LIQUIDITY_INVALID', 'VOLUME_INVALID', 'SOURCE_TIME_IN_FUTURE'} for x in results):
        conflicts.add('SOURCE_FIELD_INVALID')
    if any('SOURCE_STALE' in x['flags'] for x in results):
        conflicts.add('SOURCE_STALE')
    if any('CAPTURE_TIME_UNKNOWN' in x['flags'] for x in results):
        conflicts.add('CAPTURE_TIME_UNKNOWN')
    if 'POOL_OR_TOKEN_IDENTITY_CONFLICT' in conflicts:
        state = 'CONFLICT'
    elif 'SOURCE_FIELD_INVALID' in conflicts:
        state = 'INVALID'
    elif 'SOURCE_STALE' in conflicts:
        state = 'STALE'
    elif len(parsed) != len(observations) or len(parsed) < 2 or {'CAPTURE_WINDOW_MISMATCH', 'CAPTURE_TIME_UNKNOWN'} & conflicts:
        state = 'INCOMPLETE'
    else:
        state = 'COMPARABLE_AS_AGGREGATORS_ONLY'
    return {'contract': CONTRACT, 'case_id': case['case_id'],
            'mode': 'READ_ONLY_OFFLINE', 'independent_onchain_validation': False,
            'sellability_proven': False, 'trade_signal': None,
            'source_qa_state': state,
            'comparison_flags': sorted(conflicts),
            'provider_observations': results, 'outcome_evidence': 'NOT_EVALUATED',
            'rea_evidence_class': 'OBSERVED_AGGREGATOR_CLAIMS_ONLY'}


def main() -> None:
    parser = argparse.ArgumentParser(description='Offline value-free DEX source QA, not a scanner')
    parser.add_argument('--input', type=Path, required=True, help='Local input only; never committed')
    parser.add_argument('--output', type=Path, help='Value-free QA result only')
    args = parser.parse_args()
    try:
        with args.input.open('r', encoding='utf-8') as f:
            case = json.load(f)
        result = evaluate_case(case)
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        # No original provider values or exception text in public failure output.
        result = {'contract': CONTRACT, 'source_qa_state': 'UNAVAILABLE',
                  'reason': 'INPUT_INVALID_OR_UNAVAILABLE', 'trade_signal': None,
                  'sellability_proven': False}
    output = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.output:
        args.output.write_text(output, encoding='utf-8')
    else:
        sys.stdout.write(output)
    if result['source_qa_state'] in {'UNAVAILABLE', 'INVALID', 'CONFLICT', 'INCOMPLETE', 'STALE'}:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
