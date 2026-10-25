"""Deterministic, offline PRICE-ONLY challenger for existing Forward Path (#1516).

Absolutely NO live forecast, publication, trading, autonomous model, source fetch,
scoring, persistence or model selection. Source ownership/first-known timestamps
must be independently admitted before this output may be used outside research.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

CONTRACT = "FORWARD_PRICE_SHADOW_PRICE_ONLY_CHALLENGER_v0_1"
INPUT_CONTRACT = "FORWARD_PRICE_DAILY_BAR_INPUT_v0_1"
METHOD = "CLOSED_DAILY_HISTORICAL_BLOCK_EXTREMA_Q10_Q90_v0_1"
ALTERNATIVE_METHOD = "CLOSED_DAILY_HISTORICAL_BLOCK_EXTREMA_Q25_Q75_DESCRIPTIVE_v0_1"
HORIZONS = (1, 7, 14, 21)
# Separate native-quote USDT evidence class. Original USD v0.1 remains
# output-compatible; no synthetic USD=USDT or cross-quote scoring.
USDT_CONTRACT = "FORWARD_PRICE_SHADOW_PRICE_ONLY_USDT_CHALLENGER_v0_1"
USDT_INPUT_CONTRACT = "FORWARD_PRICE_DAILY_BAR_INPUT_USDT_v0_1"
USDT_METHOD = "CLOSED_DAILY_HISTORICAL_BLOCK_EXTREMA_Q10_Q90_USDT_v0_1"
USDT_ALTERNATIVE_METHOD = "CLOSED_DAILY_HISTORICAL_BLOCK_EXTREMA_Q25_Q75_USDT_DESCRIPTIVE_v0_1"
USDT_HORIZONS = (1, 7, 14, 21, 30, 56)
UTC_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
HASH_PATTERN = re.compile(r"[a-f0-9]{64}")


def _timestamp(s: Any) -> datetime:
    if not isinstance(s, str) or not UTC_PATTERN.fullmatch(s):
        raise ValueError("timestamp_requires_exact_utc")
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid_utc_date") from exc


def _price(x: Any) -> float:
    if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or x <= 0:
        raise ValueError("invalid_price")
    return float(x)


def _quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("no_empirical_samples")
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (position - lo) * (ordered[hi] - ordered[lo])


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def build_shadow(payload: dict[str, Any]) -> dict[str, Any]:
    """Original USD-only research contract; never accept USD-labelled USDT."""
    return _build_quote_shadow(payload, target_quote="USD")


def build_native_usdt_shadow(payload: dict[str, Any]) -> dict[str, Any]:
    """Distinct Binance Spot BTCUSDT/USDT research contract; NOT a forecast issuer.

    USDT is NEVER converted, asserted equal, aliased or represented as USD.
    Source first-known is a caller assertion and is NOT independently proven here.
    """
    return _build_quote_shadow(payload, target_quote="USDT")


def _build_quote_shadow(payload: dict[str, Any], *, target_quote: str) -> dict[str, Any]:
    """Compute prospective uncalibrated ranges from complete historic OHLC bars.

    *Counterfactual reproducibility* != verified first-known or real issuer.
    Caller must bind genuine source bytes outside this public control plane.
    """
    if not isinstance(payload, dict) or set(payload) != {
        "contract", "asset", "quote", "venue", "issued_at_utc", "cutoff_utc",
        "provider_first_known_proven", "source_manifest_sha256", "source_rows_sha256", "bars"
    }:
        raise ValueError("input_schema_invalid")
    if target_quote not in ("USD", "USDT"):
        raise ValueError("quote_scope_invalid")
    expected_contract = INPUT_CONTRACT if target_quote == "USD" else USDT_INPUT_CONTRACT
    valid_assets = ("BTC", "ETH") if target_quote == "USD" else ("BTC",)
    if payload["contract"] != expected_contract or payload["asset"] not in valid_assets:
        raise ValueError("input_asset_contract_invalid")
    if payload["quote"] != target_quote or not isinstance(payload["venue"], str) or not payload["venue"].strip():
        raise ValueError("usd_venue_required" if target_quote == "USD" else "usdt_venue_required")
    if target_quote == "USDT" and payload["venue"] != "BINANCE_SPOT_BTCUSDT":
        raise ValueError("native_usdt_spot_owner_required")
    low_field, high_field, close_field = (
        f"low_{target_quote.lower()}", f"high_{target_quote.lower()}", f"close_{target_quote.lower()}"
    )
    if payload["provider_first_known_proven"] is not True:
        raise ValueError("provider_knowledge_requires_independent_proof")
    if not isinstance(payload["source_manifest_sha256"], str) or not HASH_PATTERN.fullmatch(payload["source_manifest_sha256"]):
        raise ValueError("invalid_source_manifest_sha")
    issued, cutoff = _timestamp(payload["issued_at_utc"]), _timestamp(payload["cutoff_utc"])
    if issued < cutoff or issued - cutoff > timedelta(hours=48):
        raise ValueError("cutoff_future_or_stale")
    bars = payload["bars"]
    if not isinstance(payload["source_rows_sha256"], str) or not HASH_PATTERN.fullmatch(payload["source_rows_sha256"]):
        raise ValueError("invalid_source_rows_sha")
    if hashlib.sha256(canonical(bars)).hexdigest() != payload["source_rows_sha256"]:
        raise ValueError("source_rows_content_hash_mismatch")
    if not isinstance(bars, list) or len(bars) < 252 or len(bars) > 366:
        raise ValueError("insufficient_or_oversized_closed_daily_history")
    cleaned = []
    last_date = None
    for row in bars:
        if not isinstance(row, dict) or set(row) != {
            "day_utc", low_field, high_field, close_field, "first_known_at_utc"
        }:
            raise ValueError("bar_schema_invalid")
        if not isinstance(row["day_utc"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["day_utc"]):
            raise ValueError("day_format_invalid")
        try:
            day = date.fromisoformat(row["day_utc"])
        except ValueError as exc:
            raise ValueError("day_invalid") from exc
        if last_date is not None and day != last_date + timedelta(days=1):
            raise ValueError("non_contiguous_closed_daily_bars")
        last_date = day
        first_known = _timestamp(row["first_known_at_utc"])
        day_closed = datetime.combine(day + timedelta(days=1), datetime.min.time(), timezone.utc)
        if not day_closed < first_known <= cutoff:
            raise ValueError("lookahead_or_unsettled_bar")
        lo, high, close = (_price(row[k]) for k in (low_field, high_field, close_field))
        if not lo <= close <= high:
            raise ValueError("ohlc_invalid")
        cleaned.append((lo, high, close))
    last_closed = datetime.combine(last_date + timedelta(days=1), datetime.min.time(), timezone.utc)
    if cutoff < last_closed or cutoff - last_closed > timedelta(hours=48):
        raise ValueError("last_bar_not_fresh_to_cutoff")
    # Source freshness is end-to-end: two individually permitted 48h lags
    # must not compound into a 96h stale issued candidate.
    if issued - last_closed > timedelta(hours=48):
        raise ValueError("issued_forecast_older_than_closed_source")

    anchor = cleaned[-1][2]  # Last *settled* close, NOT an invented intraday spot.
    horizons: dict[str, dict[str, Any]] = {}
    descriptive_q25_q75: dict[str, dict[str, Any]] = {}
    for horizon in (HORIZONS if target_quote == "USD" else USDT_HORIZONS):
        lows: list[float] = []
        highs: list[float] = []
        # Historical excursion samples use only previously closed bars;
        # no outcome from the forecast window enters the calculation.
        for end in range(horizon + 1, len(cleaned) + 1):
            base = cleaned[end - horizon - 1][2]
            segment = cleaned[end - horizon:end]
            lows.append(math.log(min(bar[0] for bar in segment) / base))
            highs.append(math.log(max(bar[1] for bar in segment) / base))
        nonoverlap_max = (len(cleaned) - 1) // horizon
        if nonoverlap_max < 12:
            horizons[str(horizon)] = {
                "status": "ABSTAIN", "reason": "TOO_FEW_INDEPENDENT_HORIZON_BLOCKS",
                low_field: None, high_field: None,
                "overlapping_windows": len(lows), "nonoverlap_upper_bound": nonoverlap_max,
            }
            descriptive_q25_q75[str(horizon)] = {
                "status": "ABSTAIN", "reason": "TOO_FEW_INDEPENDENT_HORIZON_BLOCKS",
                low_field: None, high_field: None,
                "overlapping_windows": len(lows), "nonoverlap_upper_bound": nonoverlap_max,
                "joint_coverage_probability": None,
            }
            continue
        # Separate fixed research hypothesis: marginal low q25 and high q75.
        # Neither pair of marginal quantiles implies any joint coverage probability.
        q25_low = anchor * math.exp(_quantile(lows, 0.25))
        q75_high = anchor * math.exp(_quantile(highs, 0.75))
        if not (0 < q25_low < q75_high and math.isfinite(q25_low) and math.isfinite(q75_high)):
            # A rejected optional comparator must not invalidate the original
            # q10/q90 challenger, even when its own interval is well-formed.
            descriptive_q25_q75[str(horizon)] = {
                "status": "ABSTAIN", "reason": "DEGENERATE_DESCRIPTIVE_ENVELOPE",
                low_field: None, high_field: None,
                "overlapping_windows": len(lows), "nonoverlap_upper_bound": nonoverlap_max,
                "joint_coverage_probability": None,
            }
        else:
            descriptive_q25_q75[str(horizon)] = {
                "status": "SHADOW_BASELINE_ONLY", low_field: q25_low, high_field: q75_high,
                "overlapping_windows": len(lows), "nonoverlap_upper_bound": nonoverlap_max,
                "marginal_low_quantile": 0.25, "marginal_high_quantile": 0.75,
                "joint_coverage_probability": None, "calibration_status": "NOT_CALIBRATED",
            }
        low = anchor * math.exp(_quantile(lows, 0.10))
        high = anchor * math.exp(_quantile(highs, 0.90))
        if not (0 < low < high and math.isfinite(low) and math.isfinite(high)):
            raise ValueError("degenerate_empirical_envelope")
        horizons[str(horizon)] = {
            "status": "SHADOW_BASELINE_ONLY", low_field: low,
            high_field: high, "overlapping_windows": len(lows),
            "nonoverlap_upper_bound": nonoverlap_max,
            "coverage_probability": None, "calibration_status": "NOT_CALIBRATED",
        }
    body = {
        "contract": CONTRACT if target_quote == "USD" else USDT_CONTRACT,
        "method": METHOD if target_quote == "USD" else USDT_METHOD,
        "authority": "SHADOW_NOT_ISSUED",
        "asset": payload["asset"], "quote": target_quote, "venue": payload["venue"],
        "issued_at_utc": payload["issued_at_utc"], "cutoff_utc": payload["cutoff_utc"],
        "input_source_sha256": payload["source_manifest_sha256"],
        "input_canonical_rows_sha256": payload["source_rows_sha256"],
        "source_first_known_asserted": True, "source_first_known_independently_rechecked": False,
        "source_bars": len(cleaned), "anchor_source": "LAST_SETTLED_DAILY_CLOSE",
        f"anchor_{target_quote.lower()}": anchor, "horizons_days": horizons,
        "descriptive_alternative_method": ALTERNATIVE_METHOD if target_quote == "USD" else USDT_ALTERNATIVE_METHOD,
        "descriptive_q25_q75_horizons_days": descriptive_q25_q75,
        "alternative_is_unissued_non_authoritative": True,
        "direction_used_in_price_construction": False,
        "probabilities_claimed": False, "outcome_matured": False,
        "no_publication": True, "no_model_selection": True,
        "no_portfolio_action": True, "no_autonomous_reweight": True,
    }
    body["candidate_sha256"] = hashlib.sha256(canonical(body)).hexdigest()
    return body
