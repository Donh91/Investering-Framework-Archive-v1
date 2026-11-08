"""Advisory CN weekly range benchmark, not a new forecast/scoring authority.

The prior-close comparator borrows CN's band WIDTH and is NOT an
independently issued price forecast. Preserve v1 official frozen scorecards.
"""
from __future__ import annotations

import math
from datetime import date, datetime, time, timezone, timedelta
from typing import Any, Mapping

CONTRACT = "CN_RANGE_SKILL_SHADOW_v1"
METHOD = "PRIOR_CLOSE_CENTERED_CN_WIDTH_CONDITIONAL_v1"


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name}:FINITE_NUMBER_REQUIRED")
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{name}:FINITE_POSITIVE_REQUIRED")
    return result


def _timestamp(value: Any, name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{name}:OFFSET_TIMESTAMP_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name}:INVALID_TIMESTAMP") from exc
    if parsed.utcoffset() is None:
        raise ValueError(f"{name}:OFFSET_TIMESTAMP_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _band(low: Any, high: Any, name: str) -> tuple[float, float]:
    lo, hi = _number(low, name + "_LOW"), _number(high, name + "_HIGH")
    if lo >= hi:
        raise ValueError(f"{name}:ORDERED_BAND_REQUIRED")
    return lo, hi


def _metrics(band: tuple[float, float], realized: tuple[float, float],
             anchor: float, alpha: float) -> dict[str, float | bool]:
    low, high = band
    rlow, rhigh = realized
    intersection = max(0.0, min(high, rhigh) - max(low, rlow))
    union = (high - low) + (rhigh - rlow) - intersection
    # Custom extreme-envelope miss penalty, NOT a proper quantile interval score.
    loss = ((high - low) + (2 / alpha) *
            (max(0.0, low - rlow) + max(0.0, rhigh - high))) / anchor * 100
    return {
        "both_extrema_contained": low <= rlow and rhigh <= high,
        "width_pct_anchor": (high - low) / anchor * 100,
        "width_to_realized": (high - low) / (rhigh - rlow),
        "jaccard": intersection / union,
        "custom_extreme_miss_loss_pct_anchor": loss,
        "midpoint_error_pct_anchor": abs((low + high - rlow - rhigh) / 2) / anchor * 100,
    }


def evaluate_week(row: Mapping[str, Any], *, alpha: float = 0.10) -> dict[str, Any]:
    """Evaluate one explicit, fully matured weekly range against a conditional benchmark.

    Source hashes and availability clocks must be authenticated by the caller;
    possession of correctly shaped source claims is NOT source verification.
    An issue after Monday 00:00Z cannot earn full-week prospective credit.
    """
    if not isinstance(row, Mapping):
        raise ValueError("ROW_OBJECT_REQUIRED")
    if (isinstance(alpha, bool) or not isinstance(alpha, (int, float))
            or not math.isfinite(alpha) or not 0 < alpha < 1):
        raise ValueError("ALPHA_OUT_OF_RANGE")
    year, week = row.get("target_iso_year"), row.get("target_iso_week")
    if type(year) is not int or type(week) is not int:
        raise ValueError("EXPLICIT_ISO_YEAR_WEEK_REQUIRED")
    try:
        monday = date.fromisocalendar(year, week, 1)
    except ValueError as exc:
        raise ValueError("INVALID_ISO_WEEK") from exc
    start = datetime.combine(monday, time.min, timezone.utc)
    end = start + timedelta(days=7)
    first_issued = _timestamp(row.get("first_issued_at_utc"), "FIRST_ISSUED")
    anchor_known = _timestamp(row.get("prior_close_first_known_at_utc"), "PRIOR_CLOSE_FIRST_KNOWN")
    realization_final = _timestamp(row.get("realized_final_at_utc"), "REALIZED_FINAL")
    if anchor_known > first_issued:
        raise ValueError("PRIOR_CLOSE_NOT_KNOWN_AT_ISSUE")
    if realization_final < end:
        raise ValueError("REALIZED_WEEK_NOT_MATURE")
    if row.get("realized_hours") != 168 or row.get("realized_final") is not True:
        raise ValueError("FULL_168H_FINAL_SOURCE_REQUIRED")
    if row.get("asset") not in {"BTC", "ETH"}:
        raise ValueError("BTC_OR_ETH_REQUIRED")
    quote = row.get("forecast_quote")
    if quote not in {"USD", "USDT"} or row.get("realized_quote") != quote:
        raise ValueError("EXACT_QUOTE_MATCH_REQUIRED")
    for field in ("forecast_source_sha256", "realized_source_sha256", "first_issue_commit_sha"):
        value = row.get(field)
        length = 40 if field == "first_issue_commit_sha" else 64
        if (not isinstance(value, str) or len(value) != length
                or any(c not in "0123456789abcdef" for c in value)):
            raise ValueError(f"{field}:IMMUTABLE_HASH_REQUIRED")
    anchor = _number(row.get("prior_week_close"), "PRIOR_CLOSE")
    cn = _band(row.get("cn_low"), row.get("cn_high"), "CN")
    realized = _band(row.get("realized_low"), row.get("realized_high"), "REALIZED")
    width = cn[1] - cn[0]
    matched = (anchor - width / 2, anchor + width / 2)
    if matched[0] <= 0:
        raise ValueError("NAIVE_WIDTH_EXCEEDS_POSITIVE_PRICE_DOMAIN")
    return {
        "contract": CONTRACT, "method": METHOD,
        "target_iso_year": year, "target_iso_week": week,
        "asset": row["asset"], "quote": quote,
        "source_provenance": {
            k: row[k] for k in ("forecast_source_sha256", "realized_source_sha256",
                                "first_issue_commit_sha")
        },
        "claim_class": ("PIT_CLOCK_COMPATIBLE_SOURCE_UNVERIFIED"
                        if first_issued <= start else "DESCRIPTIVE_ONLY_LATE_ISSUE"),
        "cn": _metrics(cn, realized, anchor, float(alpha)),
        "matched_width_naive": _metrics(matched, realized, anchor, float(alpha)),
        "naive_is_independent_width_forecast": False,
        "alpha": float(alpha),
        "loss_kind": "CUSTOM_EXTREME_ENVELOPE_NOT_PROPER_QUANTILE_SCORE",
        "scientific_admission": False,
        "portfolio_authority": False,
    }
