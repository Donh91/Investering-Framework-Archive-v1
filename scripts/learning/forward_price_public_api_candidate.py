"""Source-identity and public Coinbase BTC/USD OHLC probe for Forward Path #1516.

PURE / OFFLINE / RESEARCH-ONLY. This module neither fetches a provider nor
stores price values, modifies a data-source contract, admits source history,
issues price forecasts, scores outcomes or changes trade decisions.

Existing Binance BTCUSDT is an observed NAVIGATION/SETTLEMENT source, not an
automatic USD substitute; Kraken BTCUSD capture is NOT ADMITTED.
A prospective Coinbase first-receiver capture requires separate private
custody, versioned collector and owner source-admission release.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.parse import urlencode

CONTRACT = "FORWARD_PRICE_PUBLIC_USD_API_RESEARCH_PROBE_v1"
REQUEST_CONTRACT = "COINBASE_PUBLIC_BTC_USD_REQUEST_v1"
COINBASE_URL = "https://api.coinbase.com/api/v3/brokerage/market/products/BTC-USD/candles"
GRANULARITIES = {"ONE_HOUR": 3600, "ONE_DAY": 86400}
UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
INTEGER = re.compile(r"(?:0|[1-9][0-9]*)")
DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?")

def stamp(value: Any) -> datetime:
    if not isinstance(value, str) or not UTC.fullmatch(value):
        raise ValueError("EXACT_UTC_REQUIRED")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("INVALID_UTC") from None

def unix(dt: datetime) -> int:
    return int(dt.timestamp())

def positive_decimal(raw: Any, *, may_zero: bool = False) -> float:
    if not isinstance(raw, str) or not DECIMAL.fullmatch(raw):
        raise ValueError("CANDLE_DECIMAL_INVALID")
    try:
        value = float(raw)
    except (ValueError, OverflowError):
        raise ValueError("CANDLE_DECIMAL_INVALID") from None
    if not math.isfinite(value) or value < 0 or (not may_zero and value == 0):
        raise ValueError("CANDLE_DECIMAL_INVALID")
    return value

def request_window(start_utc: str, end_utc: str, granularity: str) -> dict[str, Any]:
    """Build an explicit unauthenticated USD endpoint URL WITHOUT invoking it.

    Coinbase Advanced Public Product Candles documents maximum 350 buckets.
    This construction does not prove endpoint reachability or availability.
    """
    if granularity not in GRANULARITIES:
        raise ValueError("GRANULARITY_NOT_ALLOWLISTED")
    start, end = stamp(start_utc), stamp(end_utc)
    step = GRANULARITIES[granularity]
    seconds = unix(end) - unix(start)
    if seconds <= 0 or seconds % step or not 1 <= seconds // step <= 350:
        raise ValueError("WINDOW_LENGTH_NOT_SUPPORTED")
    if unix(start) % step or unix(end) % step:
        raise ValueError("WINDOW_BOUNDARY_NOT_ALIGNED")
    url = COINBASE_URL + "?" + urlencode({
        "start": str(unix(start)), "end": str(unix(end)),
        "granularity": granularity, "limit": str(seconds // step),
    })
    return {
        "contract": REQUEST_CONTRACT, "provider": "COINBASE",
        "market": "SPOT", "product_id": "BTC-USD", "asset": "BTC",
        "quote": "USD", "granularity": granularity,
        "window_start_utc": start_utc, "window_end_utc": end_utc,
        "requested_candles": seconds // step, "url": url,
        "requires_api_key": False, "source_admitted": False,
        "forecast_issued": False,
    }

def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out

def nonfinite(_: str) -> None:
    raise ValueError("NONFINITE_JSON")

def inspect_candle_response(raw: bytes, request: Mapping[str, Any], *,
                            received_at_utc: str) -> dict[str, Any]:
    """Validate CLOSED, CONTIGUOUS, EXACT BTC/USD candles; return metadata only.

    This verifies internal response consistency and receiver presence, NOT
    provider first-publication, original source vintages, or source admission.
    """
    received = stamp(received_at_utc)
    if not isinstance(request, Mapping) or request.get("contract") != REQUEST_CONTRACT:
        raise ValueError("REQUEST_CONTRACT_REQUIRED")
    fields = ("window_start_utc", "window_end_utc", "granularity")
    if any(not isinstance(request.get(k), str) for k in fields):
        raise ValueError("REQUEST_FIELDS_INVALID")
    expected = request_window(*(request[k] for k in fields))
    if dict(request) != expected:
        raise ValueError("REQUEST_IDENTITY_OR_AUTHORITY_CONFLICT")
    if received < stamp(request["window_end_utc"]):
        raise ValueError("SOURCE_RESPONSE_RECEIVED_BEFORE_CLOSED_WINDOW")
    if not isinstance(raw, bytes) or not 1 <= len(raw) <= 500_000:
        raise ValueError("RAW_BYTES_INVALID")
    try:
        doc = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=nonfinite)
    except (UnicodeError, json.JSONDecodeError):
        raise ValueError("CANDLE_JSON_INVALID") from None
    if not isinstance(doc, dict) or set(doc) != {"candles"} or not isinstance(doc["candles"], list):
        raise ValueError("CANDLE_RESPONSE_SCHEMA_INVALID")
    bars = doc["candles"]
    if len(bars) != request["requested_candles"]:
        raise ValueError("CANDLE_COUNT_OR_GAP_INVALID")
    starts = []
    step = GRANULARITIES[request["granularity"]]
    for row in bars:
        if not isinstance(row, dict) or set(row) != {"start", "low", "high", "open", "close", "volume"}:
            raise ValueError("CANDLE_ROW_SCHEMA_INVALID")
        start = row["start"]
        if not isinstance(start, str) or not INTEGER.fullmatch(start):
            raise ValueError("CANDLE_TIMESTAMP_INVALID")
        start_s = int(start)
        if start_s % step or start_s < unix(stamp(request["window_start_utc"])) or (
            start_s + step > unix(stamp(request["window_end_utc"]))
        ):
            raise ValueError("CANDLE_OUTSIDE_CLOSED_WINDOW")
        o, h, l, c = (positive_decimal(row[k]) for k in ("open", "high", "low", "close"))
        positive_decimal(row["volume"], may_zero=True)
        if not l <= min(o, c) <= max(o, c) <= h:
            raise ValueError("CANDLE_OHLC_CONFLICT")
        starts.append(start_s)
    starts.sort()
    first = unix(stamp(request["window_start_utc"]))
    if starts != list(range(first, unix(stamp(request["window_end_utc"])), step)):
        raise ValueError("CANDLE_CONTIGUITY_DUPLICATE_OR_GAP")
    return {
        "contract": CONTRACT,
        "provider": "COINBASE", "market": "SPOT", "asset": "BTC",
        "quote": "USD", "product_id": "BTC-USD",
        "status": "CAPTURE_VALIDATED_SOURCE_NOT_ADMITTED",
        "request_contract": REQUEST_CONTRACT,
        "source_raw_sha256": hashlib.sha256(raw).hexdigest(),
        "source_raw_bytes": len(raw),
        "complete_closed_candles": len(starts),
        "gap_count": 0, "received_at_utc": received_at_utc,
        "receiver_first_observed_only": True,
        "historical_provider_first_known_verified": False,
        "versioned_collector_verified": False,
        "separate_private_manifest_required": True,
        "source_admitted": False, "historical_replay_allowed": False,
        "forecast_issued": False, "eligible_for_canonical_score": False,
        "eligible_for_public_price": False, "portfolio_action": False,
    }

def existing_source_roles(hourly_pointer: Mapping[str, Any],
                          weekly_pointer: Mapping[str, Any],
                          kraken_binding: Mapping[str, Any]) -> dict[str, Any]:
    """Evidence-role comparison only; NEVER choose/promote a price feed."""
    if any(not isinstance(v, Mapping)
           for v in (hourly_pointer, weekly_pointer, kraken_binding)):
        raise ValueError("SOURCE_POINTER_OBJECT_REQUIRED")
    hourly_ok = (
        hourly_pointer.get("contract") == "HOURLY_SEQUENCE_LATEST_POINTER_v2_2"
        and hourly_pointer.get("status") == "COMPLETE"
        and type(hourly_pointer.get("spot_complete_hours")) is int
        and hourly_pointer["spot_complete_hours"] > 0
    )
    weekly_ok = (
        weekly_pointer.get("contract") == "WEEKLY_MARKET_CLOSE_POINTER_v3"
        and weekly_pointer.get("status") == "PASS"
        and weekly_pointer.get("source_base_url") == "https://data-api.binance.vision"
        and weekly_pointer.get("final") is True
        and weekly_pointer.get("completeness") == "COMPLETE"
    )
    kraken_ok = (
        kraken_binding.get("contract") == "FORWARD_PRICE_SOURCE_CUSTODY_PUBLIC_BINDING_v1"
        and kraken_binding.get("provider") == "KRAKEN"
        and kraken_binding.get("asset") == "BTC"
        and kraken_binding.get("quote") == "USD"
        and kraken_binding.get("instrument_id") == "XXBTZUSD"
        and kraken_binding.get("status") == "CAPTURED_NOT_ADMITTED"
        and kraken_binding.get("source_admitted") is False
        and kraken_binding.get("forecast_issued") is False
    )
    return {
        "contract": "FORWARD_PRICE_SOURCE_ROLE_COMPARISON_v1",
        "sources": [
            {"id": "EXISTING_BINANCE_SPOT", "asset": "BTC",
             "quote": "USDT", "price_basis": "EXCHANGE_SPOT",
             "navigation_hourly_source_present": hourly_ok,
             "settled_weekly_source_present": weekly_ok,
             "eligible_for_usd_priced_forecast": False,
             "reason": "BTCUSDT_IS_NOT_BTCUSD"},
            {"id": "EXISTING_KRAKEN_CAPTURE", "asset": "BTC",
             "quote": "USD", "price_basis": "EXCHANGE_SPOT",
             "captured_metadata_matches": kraken_ok,
             "eligible_for_usd_priced_forecast": False,
             "reason": "CAPTURED_NOT_ADMITTED"},
            {"id": "COINBASE_PUBLIC_API_CANDIDATE", "asset": "BTC",
             "quote": "USD", "price_basis": "EXCHANGE_SPOT",
             "api_design_documented": True,
             "collector_deployed": False,
             "eligible_for_usd_priced_forecast": False,
             "reason": "NO_ORIGINAL_PRIVATE_SOURCE_RECEIPT"},
        ],
        "approved_forecast_price_owner": None,
        "market_rule_change": False, "portfolio_action": False,
    }
