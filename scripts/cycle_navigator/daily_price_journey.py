"""Presentation contracts for prospective daily paths; no scoring/action authority."""
from __future__ import annotations

import math
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any, Mapping


CONTRACT = "CN_FROZEN_DAILY_PRICE_PATH_v1"
COPY_CONTRACT = "CN_PUBLIC_PROTECTION_COPY_v1"


def daily_path_schema() -> dict[str, Any]:
    point = {"type": "object", "additionalProperties": False,
             "required": ["day", "expected_close", "low", "high"], "properties": {
                 "day": {"type": "integer", "minimum": 1, "maximum": 7},
                 **{k: {"type": "number", "exclusiveMinimum": 0} for k in ("expected_close", "low", "high")}}}
    asset = {"type": "object", "additionalProperties": False,
             "required": ["status", "reason", "points"], "properties": {
                 "status": {"type": "string", "enum": ["PUBLISHED", "UNAVAILABLE"]},
                 "reason": {"type": "string"},
                 "points": {"type": "array", "maxItems": 7, "items": point}}}
    return {"type": "object", "additionalProperties": False,
            "required": ["contract", "forecast_week", "BTC", "ETH"], "properties": {
                "contract": {"type": "string", "const": CONTRACT},
                "forecast_week": {"type": "string"}, "BTC": asset, "ETH": asset}}


def validate_daily_path(value: Any, freeze: Mapping[str, Any], year: int, week: int) -> dict[str, Any] | None:
    if value is None:  # Immutable legacy archives remain compatible.
        return None
    if not isinstance(value, dict) or value.get("contract") != CONTRACT or value.get("forecast_week") != f"{year:04d}-W{week:02d}":
        raise ValueError("daily_path_identity_invalid")
    monday = date.fromisocalendar(year, week, 1)
    for asset in ("BTC", "ETH"):
        item = value.get(asset)
        if not isinstance(item, dict) or item.get("status") not in {"PUBLISHED", "UNAVAILABLE"}:
            raise ValueError("daily_path_asset_invalid")
        points = item.get("points")
        if item["status"] == "UNAVAILABLE":
            if points != [] or not str(item.get("reason") or "").strip():
                raise ValueError("daily_path_unavailable_invalid")
            continue
        if not isinstance(points, list) or len(points) != 7:
            raise ValueError("daily_path_seven_days_required")
        lo, hi = freeze.get(asset.lower() + "_range_low"), freeze.get(asset.lower() + "_range_high")
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x > 0 for x in (lo, hi)) or lo >= hi:
            raise ValueError("daily_path_weekly_bounds_required")
        for day, point in enumerate(points, 1):
            if not isinstance(point, dict) or point.get("day") != day:
                raise ValueError("daily_path_order_invalid")
            values = [point.get(k) for k in ("low", "expected_close", "high")]
            if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in values) or not lo <= values[0] <= values[1] <= values[2] <= hi or values[0] == values[2]:
                raise ValueError("daily_path_price_bounds_invalid")
    return value


def daily_path_issue_summary(value: Any, freeze: Mapping[str, Any], year: int, week: int) -> dict[str, Any]:
    """Value-free coverage readback for an ORIGINAL weekly analytical issue.

    Only the already validated frozen CN path may enter this summary.  This
    does NOT synthesize prices, add action permission or claim forecast edge.
    """
    validated = validate_daily_path(value, freeze, year, week)
    assets: dict[str, dict[str, Any]] = {}
    for asset in ("BTC", "ETH"):
        item = (validated or {}).get(asset) if isinstance(validated, dict) else None
        issued = isinstance(item, dict) and item.get("status") == "PUBLISHED"
        assets[asset] = {
            "status": "PUBLISHED" if issued else "UNAVAILABLE",
            "point_count": 7 if issued else 0,
        }
    published = sum(row["status"] == "PUBLISHED" for row in assets.values())
    return {
        "contract": "CN_DAILY_PATH_ISSUANCE_READBACK_v1",
        "forecast_week": f"{year:04d}-W{week:02d}",
        "source": "EXISTING_WEEKLY_CYCLE_NAVIGATOR_SYNTHESIS",
        "status": "PUBLISHED_BOTH" if published == 2 else "PARTIAL" if published else "UNAVAILABLE",
        "assets": assets,
        "prospective_price_model_authority": False,
        "scoring_authority": False,
        "portfolio_execution": False,
    }


def public_copy_schema() -> dict[str, Any]:
    return {"type": "object", "additionalProperties": False,
            "required": ["contract", "summary", "watch_for", "weakens_if", "onset_start_day", "onset_end_day"],
            "properties": {
                "contract": {"type": "string", "const": COPY_CONTRACT},
                **{k: {"type": "string", "maxLength": 180} for k in ("summary", "watch_for", "weakens_if")},
                **{k: {"type": ["integer", "null"], "minimum": 1, "maximum": 7} for k in ("onset_start_day", "onset_end_day")}}}


def validated_public_copy(protection: Mapping[str, Any], year: int, week: int) -> dict[str, Any] | None:
    copy = protection.get("public_explanation")
    if not isinstance(copy, dict) or copy.get("contract") != COPY_CONTRACT:
        return None
    texts = [copy.get(k) for k in ("summary", "watch_for", "weakens_if")]
    # Copy explains evidence only. Numbers/dates/actions remain typed owner fields.
    if any(not isinstance(s, str) or not s.strip() or len(s) > 180 or re.search(r"\d|%|\b(?:buy|sell|short|rebuy|guaranteed|probability|internal|shadow|data_ping)\b", s, re.I) for s in texts):
        return None
    a, b = copy.get("onset_start_day"), copy.get("onset_end_day")
    if (a is None) != (b is None) or (a is not None and (type(a) is not int or type(b) is not int or not 1 <= a <= b <= 7)):
        return None
    monday = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), timezone.utc)
    result = {"contract": COPY_CONTRACT, **dict(zip(("summary", "watch_for", "weakens_if"), texts)),
              "risk_state": protection.get("pullback_risk_state"), "risk_class": str(protection.get("pullback_class") or "").upper(),
              "forecast_week": f"{year:04d}-W{week:02d}", "method": "EXISTING_WEEKLY_LLM_PUBLIC_LANGUAGE_FILTER", "action_authority": False}
    result["onset_start_utc"] = (monday + timedelta(days=a-1)).isoformat().replace("+00:00", "Z") if a else None
    result["onset_end_utc"] = (monday + timedelta(days=b)).isoformat().replace("+00:00", "Z") if b else None
    return result


# Separate original daily high/low research ranges; not a smoothed
# reconstruction from the 3-window range, nor a daily expected close.
DAILY_RANGE_CONTRACT = "CN_FROZEN_DAILY_RANGE_PLAN_v1"


def daily_range_plan_schema() -> dict[str, Any]:
    point = {"type": "object", "additionalProperties": False,
             "required": ["day", "low", "high", "why", "invalidate_if"],
             "properties": {
                 "day": {"type": "integer", "minimum": 1, "maximum": 7},
                 "low": {"type": "number", "exclusiveMinimum": 0},
                 "high": {"type": "number", "exclusiveMinimum": 0},
                 "why": {"type": "string", "minLength": 12, "maxLength": 340},
                 "invalidate_if": {"type": "string", "minLength": 8, "maxLength": 240}}}
    asset = {"type": "object", "additionalProperties": False,
             "required": ["status", "reason", "points"],
             "properties": {
                 "status": {"type": "string", "enum": ["PUBLISHED", "UNAVAILABLE"]},
                 "reason": {"type": "string"},
                 "points": {"type": "array", "maxItems": 7, "items": point}}}
    return {"type": "object", "additionalProperties": False,
            "required": ["contract", "forecast_week", "BTC", "ETH"],
            "properties": {"contract": {"type": "string", "const": DAILY_RANGE_CONTRACT},
                           "forecast_week": {"type": "string"},
                           "BTC": asset, "ETH": asset}}


def validate_daily_range_plan(value: Any, freeze: Mapping[str, Any], year: int, week: int) -> dict[str, Any] | None:
    """Original point-in-time DAILY range research, no score/action permission.

    Legacy freezes without this additive field stay immutable and compatible.
    Cross-check independently against both the canonical whole-week envelope
    and its actual original 1-2/3-4/5-7 window, NEVER derive a point from it.
    """
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("contract") != DAILY_RANGE_CONTRACT or value.get("forecast_week") != f"{year:04d}-W{week:02d}":
        raise ValueError("daily_range_identity_invalid")
    for asset in ("BTC", "ETH"):
        block = value.get(asset)
        if not isinstance(block, dict) or block.get("status") not in ("PUBLISHED", "UNAVAILABLE"):
            raise ValueError("daily_range_asset_invalid")
        points = block.get("points")
        if block["status"] == "UNAVAILABLE":
            if points != [] or not str(block.get("reason") or "").strip():
                raise ValueError("daily_range_abstention_invalid")
            continue
        if not isinstance(points, list) or len(points) != 7:
            raise ValueError("daily_range_seven_days_required")
        wlow, whigh = freeze.get(asset.lower() + "_range_low"), freeze.get(asset.lower() + "_range_high")
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0 for v in (wlow, whigh)) or wlow >= whigh:
            raise ValueError("daily_range_week_bounds_missing")
        for i, point in enumerate(points, 1):
            if not isinstance(point, dict) or point.get("day") != i:
                raise ValueError("daily_range_day_sequence_invalid")
            lo, hi = point.get("low"), point.get("high")
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (lo, hi)) or not wlow <= lo < hi <= whigh:
                raise ValueError("daily_range_outside_frozen_week")
            if any(not isinstance(point.get(key), str) or len(point[key].strip()) < 8 for key in ("why", "invalidate_if")):
                raise ValueError("daily_range_explanation_missing")
    return value
