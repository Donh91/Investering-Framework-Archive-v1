"""Offline BTC/USDT (NOT USD) public Binance kline candidate for Forward Path #1516.

This module constructs source-specific requests and verifies an already acquired
raw provider response. It never performs HTTP, writes data, admits a source,
issues a forecast, scores outcomes, derives USD, or takes portfolio action.

Do not use settlement prices (observed AFTER a forecast) to synthesize an
original forecast. Same-provider observations require original-time custody.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.parse import urlencode

CONTRACT = "FORWARD_PRICE_BINANCE_USDT_SOURCE_DIAGNOSTIC_v1"
REQUEST_CONTRACT = "FORWARD_PRICE_BINANCE_USDT_KLINE_REQUEST_v1"
BASE = "https://data-api.binance.vision/api/v3/klines"
STEPS = {"1h": 3600, "1d": 86400}
UTC_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
POSITIVE = re.compile(r"(?:0|[1-9]\d*)(?:\.\d+)?")

def utc(value: Any) -> datetime:
    if not isinstance(value, str) or not UTC_PATTERN.fullmatch(value):
        raise ValueError("EXACT_UTC_REQUIRED")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("INVALID_UTC") from None

def ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)

def request_window(start_at_utc: str, end_at_utc: str, interval: str) -> dict[str, Any]:
    """Require exact closed UTC window; no keys, write access or live requests."""
    if interval not in STEPS:
        raise ValueError("INTERVAL_NOT_SUPPORTED")
    start, end = utc(start_at_utc), utc(end_at_utc)
    step = STEPS[interval] * 1000
    delta = ms(end) - ms(start)
    if delta < step or delta % step or delta // step > 1000:
        raise ValueError("BINANCE_LIMIT_OR_WINDOW_INVALID")
    if ms(start) % step or ms(end) % step:
        raise ValueError("UTC_INTERVAL_ALIGNMENT_REQUIRED")
    url = BASE + "?" + urlencode({
        "symbol": "BTCUSDT", "interval": interval,
        "startTime": ms(start), "endTime": ms(end) - 1,
        "limit": delta // step,
    })
    return {
        "contract": REQUEST_CONTRACT, "provider": "BINANCE",
        "market": "SPOT", "symbol": "BTCUSDT",
        "asset": "BTC", "quote": "USDT", "interval": interval,
        "window_start_utc": start_at_utc, "window_end_utc": end_at_utc,
        "expected_candles": delta // step, "url": url,
        "requires_api_key": False, "source_admitted": False,
        "forecast_issued": False, "usd_equivalent_assumed": False,
    }

def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result

def _reject_constant(_: str) -> None:
    raise ValueError("NONFINITE_JSON")

def _value(raw: Any, *, allow_zero: bool = False) -> float:
    if not isinstance(raw, str) or not POSITIVE.fullmatch(raw):
        raise ValueError("INVALID_CANDLE_NUMERIC")
    try:
        amount = float(raw)
    except (ValueError, OverflowError):
        raise ValueError("INVALID_CANDLE_NUMERIC") from None
    if not math.isfinite(amount) or amount < 0 or (amount == 0 and not allow_zero):
        raise ValueError("INVALID_CANDLE_NUMERIC")
    return amount

def inspect_response(raw: bytes, request: Mapping[str, Any], *,
                     received_at_utc: str) -> dict[str, Any]:
    """Return value-free verification facts, not source admission."""
    received = utc(received_at_utc)
    if not isinstance(request, Mapping) or request.get("contract") != REQUEST_CONTRACT:
        raise ValueError("REQUEST_CONTRACT_REQUIRED")
    fields = ("window_start_utc", "window_end_utc", "interval")
    if not all(isinstance(request.get(k), str) for k in fields):
        raise ValueError("REQUEST_FIELDS_MISSING")
    expected = request_window(*(request[k] for k in fields))
    if dict(request) != expected:
        raise ValueError("BINANCE_REQUEST_IDENTITY_OR_AUTHORITY_CONFLICT")
    if received < utc(request["window_end_utc"]):
        raise ValueError("RECEIVED_BEFORE_CANDLE_WINDOW_CLOSED")
    if not isinstance(raw, bytes) or not (1 <= len(raw) <= 2_000_000):
        raise ValueError("RAW_SOURCE_BYTES_INVALID")
    try:
        bars = json.loads(raw, object_pairs_hook=_unique_pairs,
                          parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError):
        raise ValueError("BINANCE_CANDLE_JSON_INVALID") from None
    if not isinstance(bars, list) or len(bars) != request["expected_candles"]:
        raise ValueError("BINANCE_CANDLE_COUNT_OR_GAP_INVALID")
    step_ms = STEPS[request["interval"]] * 1000
    min_open_ms = ms(utc(request["window_start_utc"]))
    max_close_ms = ms(utc(request["window_end_utc"])) - 1
    observed_starts = []
    for item in bars:
        if not isinstance(item, list) or len(item) != 12:
            raise ValueError("BINANCE_CANDLE_SCHEMA_INVALID")
        opened, closed = item[0], item[6]
        if type(opened) is not int or type(closed) is not int:
            raise ValueError("BINANCE_CANDLE_TIMESTAMP_INVALID")
        if opened % step_ms or opened < min_open_ms or closed != opened + step_ms - 1 or closed > max_close_ms:
            raise ValueError("BINANCE_CANDLE_OUTSIDE_CLOSED_WINDOW")
        o, h, l, c = (_value(item[i]) for i in (1, 2, 3, 4))
        _value(item[5], allow_zero=True)
        _value(item[7], allow_zero=True)
        _value(item[9], allow_zero=True)
        _value(item[10], allow_zero=True)
        if not (l <= min(o, c) <= max(o, c) <= h):
            raise ValueError("BINANCE_CANDLE_OHLC_INVALID")
        if type(item[8]) is not int or item[8] < 0:
            raise ValueError("BINANCE_CANDLE_TRADE_COUNT_INVALID")
        observed_starts.append(opened)
    if sorted(observed_starts) != list(range(min_open_ms, max_close_ms + 1, step_ms)):
        raise ValueError("BINANCE_CANDLE_NONCONTIGUOUS_OR_DUPLICATED")
    return {
        "contract": CONTRACT, "provider": "BINANCE",
        "market": "SPOT", "symbol": "BTCUSDT", "asset": "BTC",
        "quote": "USDT", "source_raw_sha256": hashlib.sha256(raw).hexdigest(),
        "source_raw_bytes": len(raw), "verified_closed_candles": len(bars),
        "window_start_utc": request["window_start_utc"],
        "window_end_utc": request["window_end_utc"],
        "received_at_utc": received_at_utc,
        "capture_consistency": "PASS",
        "status": "RESEARCH_CAPTURE_ONLY_NOT_ADMITTED",
        "receiver_first_observed_only": True,
        "historical_provider_first_known_verified": False,
        "versioned_collector_verified": False,
        "independent_recovery_verified": False,
        "forecast_issued": False, "source_admitted": False,
        "original_scoring_eligible": False, "public_price_eligible": False,
        "usd_equivalent_assumed": False, "usd_fx_conversion_performed": False,
        "portfolio_action": False, "raw_values_in_public_receipt": False,
    }
