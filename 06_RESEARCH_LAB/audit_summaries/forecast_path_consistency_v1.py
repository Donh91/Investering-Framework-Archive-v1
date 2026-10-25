"""Research-only static consistency checks for proposed price-path forecasts.

This pure module does not create forecasts, score outcomes, call providers, write files,
read restricted data, or authorize any market, model or portfolio action.

The two target families are intentionally distinct:
  WINDOW_EXTREMA = marginal q10(future MIN LOW), q90(future MAX HIGH)
  TERMINAL_CLOSE = q10/q50/q90(final completed CLOSE)
For nested windows with the same start, extrema quantiles must be monotone.
Close quantiles need not be monotone across forecast horizons.
Marginal quantiles DO NOT establish a joint LOW/HIGH coverage probability.
"""
from __future__ import annotations

from datetime import datetime
import math
import re
from typing import Any

INPUT = "RESEARCH_PRICE_PATH_CONSISTENCY_INPUT_v1"
OUTPUT = "RESEARCH_PRICE_PATH_CONSISTENCY_RESULT_v1"
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
_ROOT = {"contract", "authority", "forecast_id", "issued_at_utc", "asset", "quote", "venue", "model_id", "source_binding_sha256", "anchor_price", "paths"}
_COMMON = {"target", "window_start_utc", "window_end_utc"}
_EXTREMA = _COMMON | {"low_q10", "high_q90", "joint_coverage_probability"}
_CLOSE = _COMMON | {"q10", "q50", "q90"}


def _time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not _UTC.fullmatch(value):
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return stamp if stamp.strftime("%Y-%m-%dT%H:%M:%SZ") == value else None
    except ValueError:
        return None


def _price(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        out = float(value)
    except (OverflowError, ValueError):
        return None
    return out if math.isfinite(out) and out > 0 else None


def _text(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value.strip()) <= 128


def validate_bundle(payload: Any) -> dict[str, Any]:
    """Fail-closed semantic audit. PASS is NOT source/PIT/forecast/coverage admission."""
    problems: set[str] = set()
    comparisons = 0
    observations: list[tuple[str, datetime, datetime, dict[str, float]]] = []
    if not isinstance(payload, dict) or set(payload) != _ROOT:
        problems.add("ROOT_SCHEMA_INVALID")
    else:
        if payload["contract"] != INPUT or payload["authority"] != "RESEARCH_ONLY":
            problems.add("AUTHORITY_OR_CONTRACT_INVALID")
        if not all(_text(payload[k]) for k in ("forecast_id", "venue", "model_id")):
            problems.add("IDENTITY_INVALID")
        if payload["asset"] not in ("BTC", "ETH") or payload["quote"] != "USD":
            problems.add("ASSET_QUOTE_INVALID")
        sha = payload["source_binding_sha256"]
        if not isinstance(sha, str) or not _SHA.fullmatch(sha):
            problems.add("SOURCE_DIGEST_INVALID")
        if _price(payload["anchor_price"]) is None:
            problems.add("ANCHOR_INVALID")
        issued = _time(payload["issued_at_utc"])
        if issued is None:
            problems.add("ISSUE_TIME_INVALID")
        paths = payload["paths"]
        if not isinstance(paths, list) or not 1 <= len(paths) <= 24:
            problems.add("PATH_COLLECTION_INVALID")
        else:
            seen: set[tuple[str, datetime, datetime]] = set()
            for row in paths:
                if not isinstance(row, dict) or row.get("target") not in ("WINDOW_EXTREMA", "TERMINAL_CLOSE"):
                    problems.add("PATH_TARGET_INVALID")
                    continue
                target = row["target"]
                if set(row) != (_EXTREMA if target == "WINDOW_EXTREMA" else _CLOSE):
                    problems.add("PATH_SCHEMA_INVALID")
                    continue
                start, end = _time(row["window_start_utc"]), _time(row["window_end_utc"])
                if start is None or end is None or not start < end or issued is None or not issued < start:
                    problems.add("WINDOW_OR_ISSUE_TIME_INVALID")
                    continue
                unique = (target, start, end)
                if unique in seen:
                    problems.add("DUPLICATE_TARGET_WINDOW")
                seen.add(unique)
                if target == "WINDOW_EXTREMA":
                    # The code knows only marginal quantiles, not the JOINT distribution.
                    if row["joint_coverage_probability"] is not None:
                        problems.add("JOINT_COVERAGE_NOT_ESTABLISHED")
                    lo, hi = _price(row["low_q10"]), _price(row["high_q90"])
                    if lo is None or hi is None or lo > hi:
                        problems.add("EXTREMA_QUANTILES_INVALID")
                        continue
                    observations.append((target, start, end, {"low": lo, "high": hi}))
                else:
                    q = [_price(row[k]) for k in ("q10", "q50", "q90")]
                    if any(x is None for x in q) or not q[0] <= q[1] <= q[2]:
                        problems.add("CLOSE_QUANTILES_INVALID")
                        continue
                    observations.append((target, start, end, {}))
            # These inequalities are necessary for quantiles of true *nested* extrema
            # with an identical origin and start. Separate close targets do not obey them.
            extrema = [(start, end, values) for target, start, end, values in observations if target == "WINDOW_EXTREMA"]
            for index, (start_a, end_a, values_a) in enumerate(extrema):
                for start_b, end_b, values_b in extrema[index + 1:]:
                    if start_a != start_b or end_a == end_b:
                        continue
                    earlier, later = ((values_a, values_b) if end_a < end_b else (values_b, values_a))
                    comparisons += 1
                    tol = 1e-10 * max(earlier["low"], earlier["high"], later["low"], later["high"])
                    if later["low"] > earlier["low"] + tol:
                        problems.add("NESTED_LOW_QUANTILE_INCREASED")
                    if later["high"] + tol < earlier["high"]:
                        problems.add("NESTED_HIGH_QUANTILE_DECREASED")
    return {
        "contract": OUTPUT,
        "status": "FAIL" if problems else "PASS_LOGICAL_CHECKS_ONLY",
        "findings": sorted(problems),
        "nested_extrema_comparisons": comparisons,
        "source_admitted": False,
        "forecast_issued": False,
        "joint_coverage_calibrated": False,
        "production_or_portfolio_authority": False,
    }
