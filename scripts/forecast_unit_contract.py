from __future__ import annotations

from typing import Any

CONTRACT = "FORECAST_TARGET_UNIT_CONTRACT_v2"
DIRECTIONS = {"UP", "DOWN", "RANGE"}
DIRECTIONAL_UNITS = {"ABSOLUTE_VALUE", "PERCENT_MOVE"}
RANGE_UNITS = {"ABSOLUTE_RANGE", "PERCENT_RANGE"}


class UnitContractError(ValueError):
    pass


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _require_null(candidate: dict[str, Any], fields: tuple[str, ...]) -> None:
    for field in fields:
        if candidate.get(field) is not None:
            raise UnitContractError(f"incompatible_field:{field}")


def normalize_target(candidate: dict[str, Any], start_value: float | int | None) -> dict[str, Any]:
    """Normalize an explicit unit-bearing target without inferring semantics."""
    if "threshold" in candidate:
        raise UnitContractError("AMBIGUOUS_LEGACY_THRESHOLD")
    direction = str(candidate.get("direction") or "").upper()
    unit = str(candidate.get("target_unit") or "").upper()
    if direction not in DIRECTIONS:
        raise UnitContractError("invalid_direction")

    target_value = candidate.get("target_value")
    threshold_pct = candidate.get("threshold_pct")
    range_low = candidate.get("range_low")
    range_high = candidate.get("range_high")
    range_lower_pct = candidate.get("range_lower_pct")
    range_upper_pct = candidate.get("range_upper_pct")

    if direction in {"UP", "DOWN"}:
        if unit not in DIRECTIONAL_UNITS:
            raise UnitContractError("directional_target_unit_required")
        _require_null(candidate, ("range_low", "range_high", "range_lower_pct", "range_upper_pct"))
        if unit == "ABSOLUTE_VALUE":
            _require_null(candidate, ("threshold_pct",))
            if not _number(start_value) or float(start_value) == 0:
                raise UnitContractError("start_value_required_for_absolute_target")
            if not _number(target_value):
                raise UnitContractError("absolute_target_value_required")
            start = float(start_value)
            target = float(target_value)
            if direction == "UP" and target <= start:
                raise UnitContractError("absolute_target_direction_mismatch")
            if direction == "DOWN" and target >= start:
                raise UnitContractError("absolute_target_direction_mismatch")
            normalized_threshold = abs((target / start - 1.0) * 100.0)
            if normalized_threshold <= 0:
                raise UnitContractError("threshold_must_be_positive")
            return {
                "unit_contract": CONTRACT,
                "target_unit": unit,
                "target_value": target,
                "threshold_pct": normalized_threshold,
                "range_low": None,
                "range_high": None,
                "range_lower_pct": None,
                "range_upper_pct": None,
            }
        _require_null(candidate, ("target_value",))
        if not _number(threshold_pct) or float(threshold_pct) <= 0:
            raise UnitContractError("positive_threshold_pct_required")
        return {
            "unit_contract": CONTRACT,
            "target_unit": unit,
            "target_value": None,
            "threshold_pct": float(threshold_pct),
            "range_low": None,
            "range_high": None,
            "range_lower_pct": None,
            "range_upper_pct": None,
        }

    if unit not in RANGE_UNITS:
        raise UnitContractError("range_target_unit_required")
    _require_null(candidate, ("target_value", "threshold_pct"))
    if unit == "ABSOLUTE_RANGE":
        _require_null(candidate, ("range_lower_pct", "range_upper_pct"))
        if not _number(start_value) or float(start_value) == 0:
            raise UnitContractError("start_value_required_for_absolute_range")
        if not _number(range_low) or not _number(range_high) or float(range_low) >= float(range_high):
            raise UnitContractError("explicit_absolute_range_required")
        start = float(start_value)
        low = float(range_low)
        high = float(range_high)
        return {
            "unit_contract": CONTRACT,
            "target_unit": unit,
            "target_value": None,
            "threshold_pct": None,
            "range_low": low,
            "range_high": high,
            "range_lower_pct": (low / start - 1.0) * 100.0,
            "range_upper_pct": (high / start - 1.0) * 100.0,
        }

    _require_null(candidate, ("range_low", "range_high"))
    if (
        not _number(range_lower_pct)
        or not _number(range_upper_pct)
        or float(range_lower_pct) >= float(range_upper_pct)
    ):
        raise UnitContractError("explicit_percentage_range_required")
    return {
        "unit_contract": CONTRACT,
        "target_unit": unit,
        "target_value": None,
        "threshold_pct": None,
        "range_low": None,
        "range_high": None,
        "range_lower_pct": float(range_lower_pct),
        "range_upper_pct": float(range_upper_pct),
    }


def validate_frozen_v2(forecast: dict[str, Any]) -> None:
    if forecast.get("contract") != "FROZEN_FORECAST_v2":
        raise UnitContractError("not_v2_forecast")
    if forecast.get("unit_contract") != CONTRACT:
        raise UnitContractError("missing_v2_unit_contract")
    direction = str(forecast.get("direction") or "").upper()
    if direction not in DIRECTIONS:
        raise UnitContractError("invalid_direction")
    raw = {
        "direction": direction,
        "target_unit": forecast.get("target_unit"),
        "target_value": forecast.get("target_value"),
        "threshold_pct": forecast.get("threshold_pct") if forecast.get("target_unit") == "PERCENT_MOVE" else None,
        "range_low": forecast.get("range_low"),
        "range_high": forecast.get("range_high"),
        "range_lower_pct": forecast.get("range_lower_pct") if forecast.get("target_unit") == "PERCENT_RANGE" else None,
        "range_upper_pct": forecast.get("range_upper_pct") if forecast.get("target_unit") == "PERCENT_RANGE" else None,
    }
    normalized = normalize_target(raw, forecast.get("start_value"))
    for key in ("threshold_pct", "range_lower_pct", "range_upper_pct"):
        expected = normalized.get(key)
        actual = forecast.get(key)
        if expected is None and actual is None:
            continue
        if expected is None or actual is None or abs(float(expected) - float(actual)) > 1e-10:
            raise UnitContractError(f"normalized_value_mismatch:{key}")
