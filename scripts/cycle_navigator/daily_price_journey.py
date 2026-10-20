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
