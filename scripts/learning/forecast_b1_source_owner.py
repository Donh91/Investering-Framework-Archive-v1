from __future__ import annotations

import hashlib
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

UTC = timezone.utc
BINANCE = "https://data-api.binance.vision/api/v3/klines"
OKX = "https://www.okx.com/api/v5/market/history-mark-price-candles"
SPEC = {
    "spot.BTCUSDT.close": ("BINANCE", "BTCUSDT"),
    "spot.ETHUSDT.close": ("BINANCE", "ETHUSDT"),
    "spot.ETHBTC.close": ("BINANCE", "ETHBTC"),
    "derivatives.BTC-USDT-SWAP.mark_price.mark_price": ("OKX", "BTC-USDT-SWAP"),
    "derivatives.ETH-USDT-SWAP.mark_price.mark_price": ("OKX", "ETH-USDT-SWAP"),
}


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def fetch_bytes(url: str, timeout: float = 20.0) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Investering-Forecast-B1/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP_{exc.code}:{exc.read()[:120]!r}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"NETWORK_ERROR:{exc}") from exc
    if not payload:
        raise RuntimeError("EMPTY_RESPONSE")
    return payload


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def last_pre_freeze_utc_day_end(freeze: datetime) -> datetime:
    midnight = datetime(freeze.year, freeze.month, freeze.day, tzinfo=UTC)
    return midnight - timedelta(milliseconds=1)


def binance_url(symbol: str, freeze: datetime, days: int = 270) -> str:
    end = last_pre_freeze_utc_day_end(freeze)
    start = end - timedelta(days=days)
    query = {
        "symbol": symbol,
        "interval": "1d",
        "startTime": int(start.timestamp() * 1000),
        "endTime": int(end.timestamp() * 1000),
        "limit": 1000,
    }
    return BINANCE + "?" + urllib.parse.urlencode(query)


def parse_binance(raw: bytes, freeze: datetime) -> list[dict[str, Any]]:
    doc = json.loads(raw)
    if not isinstance(doc, list):
        raise RuntimeError("BINANCE_SCHEMA")
    out = []
    for row in doc:
        if not isinstance(row, list) or len(row) < 7:
            continue
        open_ms, close_ms = int(row[0]), int(row[6])
        close = float(row[4])
        open_dt = datetime.fromtimestamp(open_ms / 1000, tz=UTC)
        close_dt = datetime.fromtimestamp(close_ms / 1000, tz=UTC)
        if close_dt >= freeze:
            continue
        if not math.isfinite(close) or close <= 0:
            raise RuntimeError("BINANCE_INVALID_CLOSE")
        out.append({"open_utc": iso(open_dt), "close_utc": iso(close_dt), "close": close})
    out.sort(key=lambda item: item["close_utc"])
    return out


def okx_url(inst_id: str, after_ms: int) -> str:
    query = {"instId": inst_id, "bar": "1Dutc", "after": after_ms, "limit": 100}
    return OKX + "?" + urllib.parse.urlencode(query)


def parse_okx_page(raw: bytes, freeze: datetime) -> list[dict[str, Any]]:
    doc = json.loads(raw)
    if not isinstance(doc, dict) or str(doc.get("code")) != "0" or not isinstance(doc.get("data"), list):
        raise RuntimeError("OKX_SCHEMA")
    out = []
    for row in doc["data"]:
        if not isinstance(row, list) or len(row) < 6:
            continue
        open_ms = int(row[0])
        close = float(row[4])
        confirm = str(row[-1])
        if confirm != "1":
            continue
        open_dt = datetime.fromtimestamp(open_ms / 1000, tz=UTC)
        close_dt = open_dt + timedelta(days=1)
        if close_dt >= freeze:
            continue
        if not math.isfinite(close) or close <= 0:
            raise RuntimeError("OKX_INVALID_CLOSE")
        out.append({"open_utc": iso(open_dt), "close_utc": iso(close_dt), "close": close, "open_ms": open_ms})
    return out


def _dedupe_and_validate_daily(bars: list[dict[str, Any]], min_bars: int) -> list[dict[str, Any]]:
    unique = {str(row["close_utc"]): row for row in bars}
    result = sorted(unique.values(), key=lambda item: item["close_utc"])
    if len(result) < min_bars:
        raise RuntimeError(f"B1_INSUFFICIENT_DAILY_BARS:{len(result)}")
    closes = [parse_dt(str(row["close_utc"])) for row in result]
    for i in range(len(closes) - 1):
        if abs((closes[i + 1] - closes[i]).total_seconds() - 86400.0) > 0.01:
            raise RuntimeError("B1_DAILY_HISTORY_GAP_OR_DUPLICATE")
    return result


def fetch_daily_history(metric_path: str, freeze_utc: str, fixture: dict[str, Any] | None = None, min_bars: int = 190) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if metric_path not in SPEC:
        raise RuntimeError("B1_UNSUPPORTED_METRIC")
    freeze = parse_dt(freeze_utc)
    provider_kind, identity = SPEC[metric_path]
    requests: list[dict[str, Any]] = []
    bars: list[dict[str, Any]] = []
    if fixture is not None:
        if fixture.get("kind") != provider_kind:
            raise RuntimeError("FIXTURE_KIND_MISMATCH")
        raws = [json.dumps(value, separators=(",", ":")).encode() for value in fixture.get("responses", [])]
        urls = fixture.get("urls") or ["fixture://page"] * len(raws)
        for raw, url in zip(raws, urls):
            requests.append({"url": url, "raw_sha256": sha_bytes(raw), "raw_bytes": len(raw)})
            bars.extend(parse_binance(raw, freeze) if provider_kind == "BINANCE" else parse_okx_page(raw, freeze))
    elif provider_kind == "BINANCE":
        url = binance_url(identity, freeze)
        raw = fetch_bytes(url)
        requests.append({"url": url, "raw_sha256": sha_bytes(raw), "raw_bytes": len(raw)})
        bars = parse_binance(raw, freeze)
    else:
        after = int(datetime(freeze.year, freeze.month, freeze.day, tzinfo=UTC).timestamp() * 1000)
        for _ in range(5):
            url = okx_url(identity, after)
            raw = fetch_bytes(url)
            requests.append({"url": url, "raw_sha256": sha_bytes(raw), "raw_bytes": len(raw)})
            page = parse_okx_page(raw, freeze)
            if not page:
                break
            bars.extend(page)
            oldest = min(int(row["open_ms"]) for row in page)
            after = oldest
            if len({row["close_utc"] for row in bars}) >= min_bars:
                break
        for row in bars:
            row.pop("open_ms", None)
    bars = _dedupe_and_validate_daily(bars, min_bars)
    if not all(parse_dt(str(row["close_utc"])) < freeze for row in bars):
        raise RuntimeError("B1_POST_FREEZE_OBSERVATION")
    receipt = {
        "contract": "B1_DAILY_HISTORY_SOURCE_RECEIPT_v1",
        "metric_path": metric_path,
        "freeze_utc": iso(freeze),
        "provider_kind": provider_kind,
        "instrument": identity,
        "request_count": len(requests),
        "requests": requests,
        "parsed_bar_count": len(bars),
        "parsed_bars_sha256": hashlib.sha256((json.dumps(bars, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest(),
        "all_observations_pre_freeze": True,
        "daily_continuity_verified": True,
        "outcome_data_read": False,
        "authority": {"forecast_skill_claim": False, "portfolio_action": False, "model_weight_change": False},
    }
    return bars, receipt
