"""Read-only admission of an existing continuity bridge to an exact forecast clock.

This checks technical input eligibility, never scientific admission or range skill.
It cannot create a bridge or upgrade the independent benchmark into model input.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BRIDGE_PATH = Path('05_CYCLE_NAVIGATOR/LATEST_PROSPECTIVE_RANGE.json')


def _time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError('timestamp_missing')
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.utcoffset() is None:
        raise ValueError('timezone_missing')
    return stamp.astimezone(timezone.utc)


def load_bridge(repo: Path, *, target_year: int, target_week: int,
                freeze_at: datetime, path: Path = BRIDGE_PATH) -> dict[str, Any]:
    """Exclude all range values on failure; retain actionable diagnostics only."""
    expected = f'{target_year:04d}-W{target_week:02d}'
    result: dict[str, Any] = {'contract': 'CN_PROSPECTIVE_RANGE_CONSUMER_READBACK_v1',
        'status': 'SOURCE_UNAVAILABLE', 'target_week': expected, 'reason_codes': [],
        'producer': 'CN_PROSPECTIVE_RANGE_BRIDGE_v1',
        'consumer': 'WEEKLY_CN_AND_MASTER_MONDAY_CONTEXT', 'range_values_admitted': False,
        'scientific_admission': False, 'portfolio_authority': False}
    def reject(reason: str, status: str = 'CONFLICTED') -> dict[str, Any]:
        result['status'] = status
        result['reason_codes'] = [reason]
        return result
    try:
        raw = (repo / path).read_bytes()
        bridge = json.loads(raw)
    except (OSError, ValueError):
        return reject('BRIDGE_MISSING_OR_INVALID', 'SOURCE_UNAVAILABLE')
    result['source_path'] = path.as_posix()
    result['content_sha256'] = hashlib.sha256(raw).hexdigest()
    if not isinstance(bridge, dict) or bridge.get('contract') != 'CN_PROSPECTIVE_RANGE_BRIDGE_v1':
        return reject('BRIDGE_CONTRACT_INVALID')
    result['observed_target_week'] = bridge.get('target_week')
    if bridge.get('target_week') != expected:
        return reject('BRIDGE_TARGET_WEEK_MISMATCH', 'STALE')
    monday = date.fromisocalendar(target_year, target_week, 1)
    prior = (monday - timedelta(days=7)).isocalendar()
    if bridge.get('source_week') != f'{prior.year:04d}-W{prior.week:02d}':
        return reject('BRIDGE_SOURCE_WEEK_MISMATCH')
    try:
        generated = _time(bridge.get('generated_at_utc'))
        cutoff = _time(bridge.get('source_cutoff_utc'))
        if freeze_at.utcoffset() is None:
            raise ValueError('freeze_timezone_missing')
    except (TypeError, ValueError):
        return reject('BRIDGE_OR_FREEZE_TIMESTAMP_UNVERIFIED')
    expected_cutoff = datetime.combine(monday, datetime.min.time(), timezone.utc)
    if cutoff != expected_cutoff or generated < cutoff:
        return reject('BRIDGE_SOURCE_PERIOD_NOT_CLOSED')
    if generated > freeze_at:
        return reject('BRIDGE_GENERATED_AFTER_FORECAST_FREEZE')
    if bridge.get('generated_after_source_week_close') is not True:
        return reject('BRIDGE_SOURCE_FINALITY_UNVERIFIED')
    if bridge.get('status') != 'READY_CONTINUITY_BASELINE':
        return reject('BRIDGE_NOT_READY', 'SOURCE_UNAVAILABLE')
    provenance = bridge.get('provenance')
    if not isinstance(provenance, dict):
        return reject('BRIDGE_SOURCE_BINDINGS_MISSING', 'SOURCE_UNAVAILABLE')
    for key in ('prior_published_ranges', 'completed_week_actuals'):
        source = provenance.get(key)
        expected_hash = provenance.get(key + '_sha256')
        if not isinstance(source, str) or not isinstance(expected_hash, str):
            return reject('BRIDGE_SOURCE_BINDING_MISSING:' + key, 'SOURCE_UNAVAILABLE')
        resolved = (repo / source).resolve()
        if not resolved.is_relative_to(repo.resolve()):
            return reject('BRIDGE_SOURCE_PATH_INVALID:' + key)
        try:
            source_raw = resolved.read_bytes()
        except OSError:
            return reject('BRIDGE_SOURCE_MISSING:' + key, 'SOURCE_UNAVAILABLE')
        if hashlib.sha256(source_raw).hexdigest() != expected_hash:
            return reject('BRIDGE_SOURCE_HASH_MISMATCH:' + key)
        commit = provenance.get(key + '_commit')
        if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
            return reject('BRIDGE_SOURCE_COMMIT_MISSING:' + key, 'SOURCE_UNAVAILABLE')
        try:
            subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', commit, 'HEAD'],
                           check=True, capture_output=True, timeout=10)
            frozen = subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + source],
                                              stderr=subprocess.DEVNULL, timeout=10)
            committed_at = _time(subprocess.check_output(
                ['git', '-C', str(repo), 'show', '-s', '--format=%cI', commit],
                stderr=subprocess.DEVNULL, timeout=10).decode().strip())
        except (subprocess.SubprocessError, OSError, ValueError):
            return reject('BRIDGE_SOURCE_COMMIT_UNVERIFIED:' + key, 'SOURCE_UNAVAILABLE')
        if hashlib.sha256(frozen).hexdigest() != expected_hash:
            return reject('BRIDGE_FROZEN_SOURCE_HASH_MISMATCH:' + key)
        if committed_at > generated or committed_at > freeze_at:
            return reject('BRIDGE_SOURCE_COMMITTED_AFTER_GENERATION:' + key)
        if key == 'completed_week_actuals':
            try:
                actuals = json.loads(source_raw)
                if (actuals.get('iso_year'), actuals.get('iso_week')) != (prior.year, prior.week):
                    return reject('BRIDGE_ACTUALS_WEEK_MISMATCH')
                if actuals.get('readiness') != 'READY' or _time(actuals.get('generated_at_utc')) > generated:
                    return reject('BRIDGE_ACTUALS_NOT_FINAL_AT_GENERATION')
            except (ValueError, TypeError, AttributeError):
                return reject('BRIDGE_ACTUALS_INVALID')
    windows = [bridge.get('weekly')]
    intraday = bridge.get('intraday')
    if not isinstance(intraday, dict):
        return reject('BRIDGE_RANGES_INVALID')
    windows.extend(intraday.get(key) for key in ('day_1_2', 'day_3_4', 'day_5_7'))
    for window in windows:
        if not isinstance(window, dict):
            return reject('BRIDGE_RANGES_INVALID')
        for asset in ('BTC', 'ETH'):
            band = window.get(asset)
            if not isinstance(band, dict):
                return reject('BRIDGE_RANGES_INVALID')
            low, high = band.get('low'), band.get('high')
            if (type(low) not in (int, float) or type(high) not in (int, float)
                    or not math.isfinite(low) or not math.isfinite(high) or not 0 < low < high):
                return reject('BRIDGE_RANGES_INVALID')
    # Source custody alone cannot freeze a mutable bridge. Bind its own exact
    # bytes to the latest path commit reachable from HEAD before the forecast.
    try:
        bridge_commit = subprocess.check_output(
            ['git', '-C', str(repo), 'log', '-1', '--format=%H', 'HEAD', '--', path.as_posix()],
            stderr=subprocess.DEVNULL, timeout=10).decode().strip()
        if not re.fullmatch(r'[0-9a-f]{40}', bridge_commit):
            return reject('BRIDGE_COMMIT_UNVERIFIED', 'SOURCE_UNAVAILABLE')
        subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', bridge_commit, 'HEAD'],
                       check=True, capture_output=True, timeout=10)
        committed_bridge = subprocess.check_output(
            ['git', '-C', str(repo), 'show', bridge_commit + ':' + path.as_posix()],
            stderr=subprocess.DEVNULL, timeout=10)
        bridge_committed_at = _time(subprocess.check_output(
            ['git', '-C', str(repo), 'show', '-s', '--format=%cI', bridge_commit],
            stderr=subprocess.DEVNULL, timeout=10).decode().strip())
    except (subprocess.SubprocessError, OSError, ValueError):
        return reject('BRIDGE_COMMIT_UNVERIFIED', 'SOURCE_UNAVAILABLE')
    if committed_bridge != raw:
        return reject('BRIDGE_COMMITTED_BYTES_MISMATCH')
    if bridge_committed_at > freeze_at:
        return reject('BRIDGE_COMMITTED_AFTER_FORECAST_FREEZE')
    result['bridge_commit'] = bridge_commit
    result['bridge_committed_at_utc'] = bridge_committed_at.isoformat()
    return {**bridge, 'consumer_receipt': {**result, 'status': 'READY',
        'range_values_admitted': True, 'validated_for_freeze_at_utc': freeze_at.isoformat()}}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--target-year', type=int, required=True)
    parser.add_argument('--target-week', type=int, required=True)
    parser.add_argument('--freeze-at', required=True)
    args = parser.parse_args()
    print(json.dumps(load_bridge(args.repo_root, target_year=args.target_year,
        target_week=args.target_week, freeze_at=_time(args.freeze_at)), sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
