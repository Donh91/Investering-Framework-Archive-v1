"""Research-only synthetic oracles for Birdeye-inspired Alpha Lab falsifiers.
No provider requests, external datasets, live scoring, trading, or API keys.
Every function models a research question, not an alpha signal.
"""
from __future__ import annotations

from math import isfinite
from typing import Iterable


def coverage_safe_hull(signals: Iterable[tuple[str, float, float | None, bool]]) -> dict:
    """Return fixed-weight score bounds, not a vendor rating.

    Each tuple: (name, positive_weight, observed_0_to_100_or_None, critical).
    An unknown signal can contribute anything from 0 to 100.
    """
    items = list(signals)
    if not items:
        raise ValueError("At least one declared signal is required")
    total_weight = 0.0
    known_weight = 0.0
    weighted_known = 0.0
    missing = []
    critical_missing = []
    for name, weight, value, critical in items:
        if not isfinite(weight) or weight <= 0:
            raise ValueError("All weights must be finite and positive")
        total_weight += weight
        if value is None:
            missing.append(name)
            if critical:
                critical_missing.append(name)
            continue
        if not isfinite(value) or not 0 <= value <= 100:
            raise ValueError("Scores must be finite numbers between 0 and 100")
        known_weight += weight
        weighted_known += weight * value
    missing_weight = total_weight - known_weight
    return {
        "observed_mean": round(weighted_known / known_weight, 6) if known_weight else None,
        "lower_bound": round(weighted_known / total_weight, 6),
        "upper_bound": round((weighted_known + 100 * missing_weight) / total_weight, 6),
        "coverage": round(known_weight / total_weight, 6),
        "status": "UNKNOWN_CRITICAL" if critical_missing else "PARTIAL" if missing else "COMPLETE",
        "missing": missing,
        "critical_missing": critical_missing,
    }


def liquidity_path_diagnostics(values: Iterable[float]) -> dict:
    """Separate unordered value range from true chronological drawdown."""
    points = list(values)
    if not points or any(not isfinite(v) or v <= 0 for v in points):
        raise ValueError("Nonempty finite positive liquidity series required")
    peak = points[0]
    temporal_max = 0.0
    for value in points:
        peak = max(peak, value)
        temporal_max = max(temporal_max, (peak - value) / peak)
    unordered_range = (max(points) - min(points)) / max(points)
    return {
        "unordered_range_pct": round(100 * unordered_range, 6),
        "temporal_max_drawdown_pct": round(100 * temporal_max, 6),
        "current_from_peak_pct": round(100 * (max(points) - points[-1]) / max(points), 6),
        "sample_count": len(points),
    }


def first_known_gate(event_utc: int | None, published_utc: int | None,
                     first_seen_utc: int | None, decision_utc: int) -> str:
    """Prevent retrospectively published events from original-time evidence."""
    if not isinstance(decision_utc, int) or decision_utc < 0:
        raise ValueError("decision_utc must be a nonnegative Unix timestamp")
    if any(t is None for t in (event_utc, published_utc, first_seen_utc)):
        return "UNKNOWN_CLOCK"
    times = (event_utc, published_utc, first_seen_utc)
    if any(not isinstance(t, int) or t < 0 for t in times):
        raise ValueError("Source timestamps must be nonnegative Unix seconds")
    return "ELIGIBLE_AS_OF" if max(times) <= decision_utc else "NOT_KNOWN_AT_CUTOFF"


def full_exit_capacity_gate(position_tokens: float, verified_sellable_tokens: float | None,
                            quote_utc: int | None, decision_utc: int,
                            quote_ttl_seconds: int = 60) -> str:
    """Capacity-only research gate; never asserts profit or trading permission."""
    if not isfinite(position_tokens) or position_tokens <= 0:
        raise ValueError("Positive finite position required")
    if verified_sellable_tokens is None or quote_utc is None:
        return "UNKNOWN_ROUTE"
    if not isfinite(verified_sellable_tokens) or verified_sellable_tokens < 0:
        raise ValueError("Finite nonnegative capacity required")
    if quote_utc > decision_utc or decision_utc - quote_utc > quote_ttl_seconds:
        return "UNKNOWN_STALE_QUOTE"
    return "CAPACITY_ONLY_PASS" if verified_sellable_tokens >= position_tokens else "CAPACITY_INSUFFICIENT"
