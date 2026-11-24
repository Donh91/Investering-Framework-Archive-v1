"""Offline MAR challenger. No collection, source authentication or market authority."""
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, localcontext
import re

SERIES = ("VIXCLS", "VXVCLS")


def clock(value):
    if not isinstance(value, str):
        raise ValueError("invalid_clock")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("missing_timezone")
    return dt.astimezone(timezone.utc)


def level(value):
    if type(value) not in (int, float, str):
        raise ValueError("invalid_level")
    try:
        x = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid_level") from exc
    if not x.is_finite() or x <= 0 or x > 10000:
        raise ValueError("invalid_level")
    return x


def features(rows, sessions, cutoff):
    """Four exact consecutive owner-calendar sessions, oldest first.

    Session closes and availability are caller-supplied, not authenticated here.
    No assumption that FRED observation date equals first publication time.
    Missing/late inputs fail closed; do not carry stale values across sessions.
    """
    cutoff = clock(cutoff)
    if not isinstance(sessions, list) or len(sessions) != 4:
        raise ValueError("four_sessions_required")
    days, closes = [], {}
    for session in sessions:
        day = date.fromisoformat(session["date"])
        close = clock(session["close_utc"])
        if day.isoformat() != session["date"] or (days and day <= days[-1]) or close >= cutoff:
            raise ValueError("invalid_session_order_or_clock")
        if days and close <= closes[days[-1]]:
            raise ValueError("invalid_close_order")
        days.append(day)
        closes[day] = close
    observed = {}
    for row in rows:
        day = date.fromisoformat(row["date"])
        series = row["series"]
        key = (day, series)
        if day not in closes or series not in SERIES or key in observed:
            raise ValueError("unexpected_or_duplicate_observation")
        known = clock(row["available_at_utc"])
        captured = clock(row["captured_at_utc"])
        if not closes[day] <= known <= captured < cutoff:
            raise ValueError("late_or_inconsistent_observation")
        digest = row.get("payload_sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("invalid_source_digest")
        observed[key] = level(row["value"])
    if set(observed) != {(d, s) for d in days for s in SERIES}:
        raise ValueError("incomplete_matched_sessions")
    with localcontext() as ctx:
        ctx.prec = 28
        v = [observed[d, SERIES[0]] for d in days]
        long = [observed[d, SERIES[1]] for d in days]
        ratio = [x / y for x, y in zip(v, long)]
        result = {
            "vix_3m_ratio": str(ratio[-1]),
            "vix_minus_3m_index_points": str(v[-1] - long[-1]),
            "vix_change_1_session_points": str(v[-1] - v[-2]),
            "vix_change_3_sessions_points": str(v[-1] - v[0]),
            "ratio_change_3_sessions": str(ratio[-1] - ratio[0]),
            "inverted_index_term_structure": v[-1] > long[-1],
        }
    return {"contract": "VIX_TERM_STRUCTURE_SHADOW_v1", "status": "STRUCTURAL_ONLY",
            "session_dates": [d.isoformat() for d in days], "features": result,
            "source_authenticated": False, "calendar_authenticated": False,
            "first_known_verified": False, "market_signal": None,
            "canonical_authority": False, "portfolio_authority": False}
