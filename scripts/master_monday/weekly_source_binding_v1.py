"""Byte binding at the weekly producer boundary; never infer historical first-known."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def capture_binding(capture_root: Path, pointer: dict, year: int, week: int, freeze_utc: str) -> dict:
    # The pointer has an intentionally narrow relative path; don't follow arbitrary paths.
    relative = f'weekly/{year}/W{week:02d}.json'
    if pointer.get('contract') != 'LATEST_WEEKLY_CALIBRATION_POINTER_v3' or pointer.get('path') != relative or pointer.get('iso_year') != year or pointer.get('iso_week') != week:
        return {'contract':'MM_WEEKLY_SOURCE_BINDING_v1','status':'UNKNOWN','reason':'POINTER_NOT_BOUND_TO_EXACT_WEEK','first_known_status':'UNKNOWN'}
    root = capture_root.resolve()
    path = (capture_root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return {'contract':'MM_WEEKLY_SOURCE_BINDING_v1','status':'UNKNOWN','reason':'SOURCE_MISSING_OR_OUTSIDE_CAPTURE_ROOT','first_known_status':'UNKNOWN'}
    raw = path.read_bytes()
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError):
        return {'contract':'MM_WEEKLY_SOURCE_BINDING_v1','status':'UNKNOWN','reason':'SOURCE_INVALID_JSON','first_known_status':'UNKNOWN'}
    if not isinstance(data, dict) or data.get('contract') != 'WEEKLY_RAW_CALIBRATION_PACK_v3' or data.get('iso_year') != year or data.get('iso_week') != week:
        return {'contract':'MM_WEEKLY_SOURCE_BINDING_v1','status':'UNKNOWN','reason':'SOURCE_WEEK_OR_CONTRACT_MISMATCH','first_known_status':'UNKNOWN'}
    try:
        generated = datetime.fromisoformat(data['generated_at_utc'].replace('Z','+00:00'))
        frozen = datetime.fromisoformat(freeze_utc.replace('Z','+00:00'))
        if generated.utcoffset() is None or frozen.utcoffset() is None or generated.astimezone(timezone.utc) > frozen.astimezone(timezone.utc):
            raise ValueError('SOURCE_FUTURE_OR_INVALID_CLOCK')
    except (KeyError, AttributeError, TypeError, ValueError):
        return {'contract':'MM_WEEKLY_SOURCE_BINDING_v1','status':'UNKNOWN','reason':'SOURCE_FUTURE_OR_INVALID_CLOCK','first_known_status':'UNKNOWN'}
    return {'contract':'MM_WEEKLY_SOURCE_BINDING_v1','status':'BYTE_BOUND_AT_PRODUCER',
            'source_id':f'WEEKLY_RAW_CALIBRATION_PACK_v3:{year}-W{week:02d}',
            'path':str(capture_root / relative), 'sha256':hashlib.sha256(raw).hexdigest(),
            'iso_year':year,'iso_week':week,
            'first_known_status':'UNKNOWN','first_known_utc':None,
            'availability_evidence':'NO_INDEPENDENT_FIRST_KNOWN_RECEIPT',
            'authority':'SHADOW_ONLY_NO_FORECAST_OR_PORTFOLIO_AUTHORITY'}


def verify_binding(freeze: dict, pointer: dict, capture_root: Path, expected_freeze_sha256: str) -> dict:
    """Verify freeze self-hash, pointer, exact source ID/path/bytes; never attest availability."""
    result = {'contract':'MM_WEEKLY_SOURCE_BINDING_VERIFICATION_v1','status':'UNKNOWN',
              'first_known_status':'UNKNOWN','scientific_pit_eligible':False,
              'authority':'SHADOW_ONLY_NO_FORECAST_OR_PORTFOLIO_AUTHORITY'}
    if not isinstance(freeze, dict) or not isinstance(pointer, dict):
        return {**result,'reason':'FREEZE_OR_POINTER_INVALID'}
    claimed = freeze.get('freeze_sha256')
    # The materializer calculates its digest over a null placeholder; the controller
    # initially calculates over a missing field. Accept both versioned encodings.
    body = dict(freeze); body.pop('freeze_sha256',None)
    hashes = {hashlib.sha256(canonical(body)).hexdigest(),
              hashlib.sha256(canonical({**body,'freeze_sha256':None})).hexdigest()}
    if not isinstance(expected_freeze_sha256, str) or claimed != expected_freeze_sha256 or claimed not in hashes:
        return {**result,'reason':'FREEZE_HASH_MISMATCH'}
    if (freeze.get('weekly_capture_bridge') or {}).get('sha256') != hashlib.sha256(canonical(pointer)).hexdigest():
        return {**result,'reason':'POINTER_HASH_MISMATCH'}
    bound = freeze.get('weekly_source_binding')
    if not isinstance(bound, dict) or bound.get('status') != 'BYTE_BOUND_AT_PRODUCER':
        return {**result,'reason':'SOURCE_BINDING_MISSING'}
    year, week = freeze.get('iso_year'), freeze.get('iso_week')
    if type(year) is not int or type(week) is not int:
        return {**result,'reason':'INVALID_FREEZE_WEEK'}
    current = capture_binding(capture_root, pointer, year, week, freeze.get('created_at_utc'))
    if current != bound:
        return {**result,'reason':'SOURCE_BINDING_OR_BYTES_MISMATCH'}
    return {**result,'status':'BYTE_BINDING_VERIFIED','reason':'FIRST_KNOWN_UNATTESTED',
            'source_id':current['source_id'],'source_sha256':current['sha256'],
            'source_path':current['path'],'freeze_sha256':claimed}


def write_binding_sidecar(week_dir: Path, freeze: dict) -> Path:
    """Write once per freeze digest; an existing different receipt is an error."""
    import re
    freeze_sha = freeze.get('freeze_sha256')
    if not isinstance(freeze_sha, str) or not re.fullmatch(r'[0-9a-f]{64}', freeze_sha):
        raise ValueError('INVALID_FREEZE_SHA')
    body=dict(freeze); body.pop('freeze_sha256',None)
    valid_hashes={hashlib.sha256(canonical(body)).hexdigest(), hashlib.sha256(canonical({**body,'freeze_sha256':None})).hexdigest()}
    if freeze_sha not in valid_hashes:
        raise ValueError('FREEZE_HASH_MISMATCH')
    binding = freeze.get('weekly_source_binding')
    if not isinstance(binding, dict):
        raise ValueError('SOURCE_BINDING_MISSING')
    receipt = {'contract':'MM_WEEKLY_SOURCE_BINDING_RECEIPT_v1', 'freeze_sha256':freeze_sha,
               'freeze_clock_claim_utc':freeze.get('created_at_utc'), 'binding':binding,
               'first_known_independently_verified':False,
               'authority':'SHADOW_ONLY_NO_FORECAST_OR_PORTFOLIO_AUTHORITY'}
    target=week_dir/'SOURCE_BINDINGS'/(freeze_sha+'.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    payload=canonical(receipt)
    try:
        with target.open('xb') as f:
            f.write(payload)
    except FileExistsError:
        if target.read_bytes() != payload:
            raise ValueError('SOURCE_BINDING_WRITE_ONCE_CONFLICT')
    return target


def verify_sidecar(week_dir: Path, freeze: dict, pointer: dict, capture_root: Path, expected_freeze_sha256: str) -> dict:
    """Read the stored receipt and captured bytes; still not proof of first availability."""
    import re
    verified=verify_binding(freeze,pointer,capture_root,expected_freeze_sha256)
    if verified['status'] != 'BYTE_BINDING_VERIFIED':
        return verified
    if not re.fullmatch(r'[0-9a-f]{64}', expected_freeze_sha256):
        return {**verified,'status':'UNKNOWN','reason':'INVALID_FREEZE_SHA'}
    target=week_dir/'SOURCE_BINDINGS'/(expected_freeze_sha256+'.json')
    expected={'contract':'MM_WEEKLY_SOURCE_BINDING_RECEIPT_v1','freeze_sha256':expected_freeze_sha256,
              'freeze_clock_claim_utc':freeze.get('created_at_utc'),'binding':freeze['weekly_source_binding'],
              'first_known_independently_verified':False,
              'authority':'SHADOW_ONLY_NO_FORECAST_OR_PORTFOLIO_AUTHORITY'}
    try:
        actual=target.read_bytes()
    except OSError:
        return {**verified,'status':'UNKNOWN','reason':'SOURCE_BINDING_RECEIPT_MISSING'}
    if actual != canonical(expected):
        return {**verified,'status':'UNKNOWN','reason':'SOURCE_BINDING_RECEIPT_MISMATCH'}
    return {**verified,'status':'BYTE_BINDING_AND_RECEIPT_VERIFIED'}
