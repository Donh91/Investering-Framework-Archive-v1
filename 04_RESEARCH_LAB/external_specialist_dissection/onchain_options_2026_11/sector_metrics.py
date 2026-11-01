"""RESEARCH ONLY: point-in-time mechanics for the existing S10/REA lane.

No collector, trading signal, model, forecast or production authority.
Input rows must come from separately qualified source owners.
"""
from datetime import date, datetime, timedelta, timezone
from math import isfinite
from typing import Any


class EvidenceGap(ValueError):
    """Reject unsupported or incomparable evidence rather than invent zeros."""


def _utc(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError) as exc:
        raise EvidenceGap("INVALID_TIMESTAMP") from exc
    if dt.tzinfo is None:
        raise EvidenceGap("NAIVE_TIMESTAMP")
    return dt.astimezone(timezone.utc)


def _amount(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvidenceGap("INVALID_" + field.upper())
    out = float(value)
    if not isfinite(out) or out < 0:
        raise EvidenceGap("INVALID_" + field.upper())
    return out


def _admit(row: dict, cutoff: datetime) -> None:
    if row.get("options_only_verified") is not True:
        raise EvidenceGap("OPTIONS_ONLY_UNVERIFIED")
    if row.get("period_final") is not True:
        raise EvidenceGap("IN_PROGRESS_PERIOD")
    if not row.get("source_id") or not row.get("venue"):
        raise EvidenceGap("SOURCE_OR_VENUE_MISSING")
    if _utc(row.get("source_available_at_utc")) > cutoff:
        raise EvidenceGap("FUTURE_AVAILABLE_DATA")
    day = date.fromisoformat(row["day_utc"])
    if datetime.combine(day + timedelta(days=1), datetime.min.time(), timezone.utc) > cutoff:
        raise EvidenceGap("INCOMPLETE_DAY")
    _amount(row.get("premium_usd"), "premium")
    _amount(row.get("notional_usd"), "notional")


def weekly_comparison(rows: list[dict], venue: str, last_day: str,
                      cutoff_utc: str) -> dict:
    """Compare 7 complete days to the preceding 7, or report the reason unavailable.

    Exactly one valid row per UTC day/venue is required, with no after-cutoff data.
    Fees are not assumed options-only; no tokenholder metric is computed.
    """
    cutoff = _utc(cutoff_utc)
    end = date.fromisoformat(last_day)
    window = [end - timedelta(days=k) for k in range(13, -1, -1)]
    by_day = {}
    try:
        for row in rows:
            if row.get("venue") != venue:
                continue
            day = date.fromisoformat(row["day_utc"])
            if day not in window:
                continue
            if day in by_day:
                raise EvidenceGap("DUPLICATE_VENUE_DAY")
            _admit(row, cutoff)
            by_day[day] = row
        if any(day not in by_day for day in window):
            raise EvidenceGap("INCOMPLETE_14_DAY_COHORT")
        first = [by_day[d] for d in window[:7]]
        last = [by_day[d] for d in window[7:]]
        prev = sum(_amount(r["premium_usd"], "premium") for r in first)
        now = sum(_amount(r["premium_usd"], "premium") for r in last)
        notion = sum(_amount(r["notional_usd"], "notional") for r in last)
        fee_rate = None
        if all(r.get("fee_scope") == "OPTIONS_ONLY" and r.get("fees_usd") is not None
               for r in last):
            fee_rate = (sum(_amount(r["fees_usd"], "fees") for r in last) / now
                        if now > 0 else None)
        return {
            "status": "DESCRIPTIVE_ONLY",
            "venue": venue,
            "last_day": last_day,
            "cutoff_utc": cutoff_utc,
            "previous_7d_premium_usd": prev,
            "current_7d_premium_usd": now,
            "premium_growth_7d_vs_prior_7d": now / prev - 1 if prev > 0 else None,
            "premium_to_notional": now / notion if notion > 0 else None,
            "options_only_fees_to_premium": fee_rate,
            "tokenholder_capture": None,  # requires separate scope/rights evidence
            "economic_edge": "UNTESTED",
            "predictive_edge": "UNTESTED",
        }
    except (ValueError, KeyError, TypeError) as exc:
        return {
            "status": "UNKNOWN",
            "venue": venue,
            "last_day": last_day,
            "reason": str(exc) if isinstance(exc, EvidenceGap) else "INVALID_INPUT",
            "economic_edge": "UNTESTED",
            "predictive_edge": "UNTESTED",
        }


def premium_hhi(rows: list[dict], day_utc: str, cutoff_utc: str,
                expected_venues: set[str]) -> dict:
    """Concentration of a complete, explicitly declared same-day venue census."""
    cutoff = _utc(cutoff_utc)
    try:
        matched = [r for r in rows if r.get("day_utc") == day_utc]
        if not expected_venues or len(matched) != len(expected_venues):
            raise EvidenceGap("INCOMPLETE_VENUE_CENSUS")
        venues = [r.get("venue") for r in matched]
        if set(venues) != expected_venues or len(venues) != len(set(venues)):
            raise EvidenceGap("DUPLICATE_OR_MISSING_VENUE")
        for r in matched:
            _admit(r, cutoff)
        total = sum(_amount(r["premium_usd"], "premium") for r in matched)
        if total <= 0:
            raise EvidenceGap("ZERO_TOTAL_PREMIUM")
        return {
            "status": "DESCRIPTIVE_ONLY",
            "premium_hhi": sum((r["premium_usd"] / total) ** 2 for r in matched),
            "venue_count": len(matched),
            "source_cohort": day_utc,
        }
    except (ValueError, KeyError, TypeError) as exc:
        return {"status": "UNKNOWN", "reason": str(exc) if isinstance(exc, EvidenceGap)
                else "INVALID_INPUT"}
