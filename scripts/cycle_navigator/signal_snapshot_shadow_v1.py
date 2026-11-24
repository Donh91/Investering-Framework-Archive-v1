"""PIT admission for experimental CN evidence. Never a forecast or trading authority."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import math
import re
from typing import Optional


def _clock(s: str) -> datetime:
    d = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if d.tzinfo is None or d.utcoffset() != timezone.utc.utcoffset(d):
        raise ValueError('CLOCK_MUST_BE_UTC')
    return d


@dataclass(frozen=True)
class Signal:
    source_id: str
    source_sha256: str
    family: str
    independence_group: str
    value: Optional[float]
    unit: str
    observed_at_utc: str
    available_at_utc: str
    quality: str
    max_age_seconds: int
    expected_effect: str
    authority: str = 'SHADOW_ONLY'

    def admit(self, freeze_utc: str) -> dict:
        freeze, observed, available = map(_clock, (freeze_utc, self.observed_at_utc, self.available_at_utc))
        if not all((self.source_id, self.family, self.independence_group, self.unit, self.expected_effect)):
            raise ValueError('MISSING_PROVENANCE')
        if not re.fullmatch(r'[0-9a-f]{64}', self.source_sha256):
            raise ValueError('INVALID_SOURCE_HASH')
        if self.authority != 'SHADOW_ONLY' or self.max_age_seconds <= 0:
            raise ValueError('INVALID_AUTHORITY_OR_AGE')
        if observed > available or available > freeze or observed > freeze:
            return {**asdict(self), 'value': None, 'admission': 'UNKNOWN', 'reason': 'PIT_CLOCK'}
        if self.value is None or not isinstance(self.value, (int, float)) or isinstance(self.value, bool) or not math.isfinite(self.value):
            return {**asdict(self), 'value': None, 'admission': 'UNKNOWN', 'reason': 'MISSING_VALUE'}
        if self.quality != 'VALID' or (freeze - observed).total_seconds() > self.max_age_seconds:
            return {**asdict(self), 'value': None, 'admission': 'UNKNOWN', 'reason': 'QUALITY_OR_STALE'}
        return {**asdict(self), 'admission': 'ADMITTED', 'reason': None}


def snapshot(signals: list[Signal], freeze_utc: str) -> dict:
    _clock(freeze_utc)
    ids = [x.source_id for x in signals]
    if len(ids) != len(set(ids)):
        raise ValueError('DUPLICATE_SOURCE_ID')
    return {'contract': 'CN_SIGNAL_SNAPSHOT_v1', 'freeze_utc': freeze_utc,
            'authority': 'SHADOW_ONLY', 'signals': [x.admit(freeze_utc) for x in signals]}
