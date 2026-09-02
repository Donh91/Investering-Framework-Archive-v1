#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
OWNER_CONTRACT = "FORECAST_SETTLEMENT_PRICE_OWNER_v1"
EVIDENCE_CONTRACT = "FORECAST_SETTLEMENT_EVIDENCE_v1"
SETTLEMENT_CONTRACT = "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1"
RAW_CONTRACT = "FORECAST_SETTLEMENT_RAW_RECEIPT_v1"

BINANCE_BASE = "https://data-api.binance.vision/api/v3/klines"
OKX_BASE = "https://www.okx.com/api/v5/market/history-mark-price-candles"

AUTHORITY = {
    "portfolio_action": False,
    "framework_state_change": False,
    "model_weight_change": False,
    "canonical_promotion": False,
    "scientific_skill_authority": False,
}

SUPPORTED = {
    "spot.BTCUSDT.close": {"kind": "BINANCE_SPOT_1M", "symbol": "BTCUSDT", "output_path": "spot.BTCUSDT.close"},
    "spot.ETHUSDT.close": {"kind": "BINANCE_SPOT_1M", "symbol": "ETHUSDT", "output_path": "spot.ETHUSDT.close"},
    "spot.ETHBTC.close": {"kind": "BINANCE_SPOT_1M", "symbol": "ETHBTC", "output_path": "spot.ETHBTC.close"},
    "derivatives.BTC-USDT-SWAP.mark_price.mark_price": {"kind": "OKX_MARK_1M", "inst_id": "BTC-USDT-SWAP", "output_path": "derivatives.BTC-USDT-SWAP.mark_price.mark_price"},
    "derivatives.ETH-USDT-SWAP.mark_price.mark_price": {"kind": "OKX_MARK_1M", "inst_id": "ETH-USDT-SWAP", "output_path": "derivatives.ETH-USDT-SWAP.mark_price.mark_price"},
}


class SettlementSourceError(RuntimeError):
    pass


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def unix_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def normalize_metric_path(path: str) -> str:
    prefix = "market_metrics."
    return path[len(prefix):] if path.startswith(prefix) else path


def last_closed_minute_open(target: datetime) -> datetime:
    # A 1m candle opened at T is only eligible once the full [T,T+1m) interval
    # is complete. This is therefore the largest minute boundary with T+1m <= target.
    target = target.astimezone(UTC)
    floored = target.replace(second=0, microsecond=0)
    return floored - timedelta(minutes=1)


def set_path(root: dict[str, Any], path: str, value: float) -> None:
    node = root
    parts = path.split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def fetch_bytes(url: str, timeout: float = 20.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Investering-Forecast-Settlement/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise SettlementSourceError(f"HTTP_{exc.code}:{body[:200]}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SettlementSourceError(f"NETWORK_ERROR:{exc}") from exc
    if not payload:
        raise SettlementSourceError("EMPTY_RESPONSE")
    return payload


def binance_request(symbol: str, target: datetime) -> tuple[str, datetime]:
    open_dt = last_closed_minute_open(target)
    start = unix_ms(open_dt)
    params = {"symbol": symbol, "interval": "1m", "startTime": start, "endTime": start + 59_999, "limit": 1}
    return BINANCE_BASE + "?" + urllib.parse.urlencode(params), open_dt


def okx_request(inst_id: str, target: datetime) -> tuple[str, datetime]:
    open_dt = last_closed_minute_open(target)
    # OKX `after` returns records earlier than the supplied timestamp. Request
    # just after the target open so the desired completed bar is in the page.
    params = {"instId": inst_id, "bar": "1m", "after": unix_ms(target), "limit": 100}
    return OKX_BASE + "?" + urllib.parse.urlencode(params), open_dt


def parse_binance(payload: bytes, symbol: str, target: datetime, expected_open: datetime) -> dict[str, Any]:
    try:
        rows = json.loads(payload)
    except Exception as exc:
        raise SettlementSourceError("BINANCE_INVALID_JSON") from exc
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], list) or len(rows[0]) < 7:
        raise SettlementSourceError("BINANCE_SCHEMA_DRIFT")
    row = rows[0]
    try:
        open_ms, close_ms = int(row[0]), int(row[6])
        close = float(row[4])
    except (TypeError, ValueError, OverflowError) as exc:
        raise SettlementSourceError("BINANCE_NUMERIC_PARSE") from exc
    if not math.isfinite(close) or close <= 0:
        raise SettlementSourceError("BINANCE_INVALID_CLOSE")
    if open_ms != unix_ms(expected_open):
        raise SettlementSourceError("BINANCE_WRONG_CANDLE")
    if close_ms > unix_ms(target):
        raise SettlementSourceError("BINANCE_CANDLE_NOT_CLOSED_BY_TARGET")
    return {
        "source": "BINANCE_SPOT_MARKET_DATA_ONLY_KLINES",
        "instrument": symbol,
        "candle_open_utc": iso(datetime.fromtimestamp(open_ms / 1000, tz=UTC)),
        "candle_close_utc": iso(datetime.fromtimestamp(close_ms / 1000, tz=UTC)),
        "close": close,
        "confirmed": True,
    }


def parse_okx(payload: bytes, inst_id: str, target: datetime, expected_open: datetime) -> dict[str, Any]:
    try:
        doc = json.loads(payload)
    except Exception as exc:
        raise SettlementSourceError("OKX_INVALID_JSON") from exc
    if not isinstance(doc, dict) or str(doc.get("code")) != "0" or not isinstance(doc.get("data"), list):
        raise SettlementSourceError("OKX_SCHEMA_OR_SOURCE_ERROR")
    desired_ms = unix_ms(expected_open)
    selected = None
    for row in doc["data"]:
        if not isinstance(row, list) or len(row) < 6:
            continue
        try:
            if int(row[0]) == desired_ms:
                selected = row
                break
        except (TypeError, ValueError):
            continue
    if selected is None:
        raise SettlementSourceError("OKX_EXPECTED_CANDLE_MISSING")
    try:
        close = float(selected[4])
        confirm = str(selected[-1])
    except (TypeError, ValueError, IndexError) as exc:
        raise SettlementSourceError("OKX_NUMERIC_PARSE") from exc
    if confirm != "1":
        raise SettlementSourceError("OKX_CANDLE_UNCONFIRMED")
    if not math.isfinite(close) or close <= 0:
        raise SettlementSourceError("OKX_INVALID_CLOSE")
    close_dt = expected_open + timedelta(minutes=1)
    if close_dt > target:
        raise SettlementSourceError("OKX_CANDLE_NOT_CLOSED_BY_TARGET")
    return {
        "source": "OKX_MARK_PRICE_CANDLES_HISTORY",
        "instrument": inst_id,
        "candle_open_utc": iso(expected_open),
        "candle_close_utc": iso(close_dt),
        "close": close,
        "confirmed": True,
    }


def load_fixture(fixture_dir: Path, kind: str, identity: str) -> bytes:
    name = f"{kind}__{identity}.json"
    path = fixture_dir / name
    if not path.is_file():
        raise SettlementSourceError(f"FIXTURE_MISSING:{name}")
    return path.read_bytes()


def source_observation(spec: dict[str, Any], target: datetime, fixture_dir: Path | None) -> tuple[bytes, str, dict[str, Any]]:
    if spec["kind"] == "BINANCE_SPOT_1M":
        url, expected_open = binance_request(spec["symbol"], target)
        payload = load_fixture(fixture_dir, spec["kind"], spec["symbol"]) if fixture_dir else fetch_bytes(url)
        return payload, url, parse_binance(payload, spec["symbol"], target, expected_open)
    url, expected_open = okx_request(spec["inst_id"], target)
    payload = load_fixture(fixture_dir, spec["kind"], spec["inst_id"]) if fixture_dir else fetch_bytes(url)
    return payload, url, parse_okx(payload, spec["inst_id"], target, expected_open)


def validate_forecast(forecast: dict[str, Any]) -> tuple[str, dict[str, Any], datetime]:
    if forecast.get("contract") != "FROZEN_FORECAST_v1":
        raise ValueError("NOT_FROZEN_FORECAST")
    if forecast.get("settlement_contract_version") != SETTLEMENT_CONTRACT:
        raise ValueError("FORECAST_NOT_EXACT_SETTLEMENT_ENABLED")
    metric_path = str(forecast.get("metric_path") or "")
    normalized = normalize_metric_path(metric_path)
    if normalized not in SUPPORTED:
        raise ValueError(f"UNSUPPORTED_SETTLEMENT_METRIC:{metric_path}")
    target = parse_dt(str(forecast["outcome_due_utc"]))
    return normalized, SUPPORTED[normalized], target


def build_evidence(
    forecast: dict[str, Any], normalized_path: str, spec: dict[str, Any], target: datetime,
    raw_path: Path, raw_payload: bytes, source_url: str, obs: dict[str, Any], retrieved_at: datetime,
) -> dict[str, Any]:
    market_metrics: dict[str, Any] = {}
    set_path(market_metrics, spec["output_path"], float(obs["close"]))
    source_close = parse_dt(obs["candle_close_utc"])
    source_offset = (source_close - target).total_seconds()
    if source_offset > 0 or source_offset < -60.001:
        raise SettlementSourceError("SOURCE_CANDLE_OUTSIDE_LAST_CLOSED_MINUTE_WINDOW")
    evidence = {
        "contract": EVIDENCE_CONTRACT,
        "owner_contract": OWNER_CONTRACT,
        "forecast_id": forecast["forecast_id"],
        "forecast_sha256": digest(forecast),
        "settlement_contract_version": SETTLEMENT_CONTRACT,
        "metric_path": forecast["metric_path"],
        "normalized_metric_path": normalized_path,
        "settlement_target_utc": iso(target),
        "captured_at_utc": iso(target),
        "captured_at_semantics": "ADJUDICATION_TARGET_TIME_NOT_SOURCE_OBSERVATION",
        "source_candle_open_utc": obs["candle_open_utc"],
        "source_candle_close_utc": obs["candle_close_utc"],
        "source_candle_offset_seconds": round(source_offset, 6),
        "source_candle_confirmed": bool(obs["confirmed"]),
        "source_retrieved_at_utc": iso(retrieved_at),
        "source_publication_lag_seconds": round((retrieved_at - target).total_seconds(), 6),
        "source_id": obs["source"],
        "source_instrument": obs["instrument"],
        "source_request_url": source_url,
        "source_raw_path": raw_path.as_posix(),
        "source_raw_sha256": digest_bytes(raw_payload),
        "source_raw_bytes": len(raw_payload),
        "market_metrics": market_metrics,
        "authority": AUTHORITY,
    }
    evidence["evidence_sha256"] = digest(evidence)
    return evidence


def run_one(forecast_path: Path, output_root: Path, raw_root: Path, now: datetime, fixture_dir: Path | None) -> str:
    forecast = json.loads(forecast_path.read_text())
    normalized, spec, target = validate_forecast(forecast)
    if target > now:
        return "PENDING_FUTURE_DUE"
    evidence_path = output_root / f"{forecast['forecast_id']}.json"
    if evidence_path.exists():
        existing = json.loads(evidence_path.read_text())
        if existing.get("forecast_sha256") != digest(forecast) or existing.get("contract") != EVIDENCE_CONTRACT:
            raise RuntimeError(f"EVIDENCE_COLLISION:{forecast['forecast_id']}")
        return "DUPLICATE_NOOP"
    payload, url, obs = source_observation(spec, target, fixture_dir)
    raw_dir = raw_root / forecast["forecast_id"]
    raw_path = raw_dir / "source.json"
    raw_dir.mkdir(parents=True, exist_ok=True)
    if raw_path.exists() and digest_bytes(raw_path.read_bytes()) != digest_bytes(payload):
        raise RuntimeError(f"RAW_COLLISION:{forecast['forecast_id']}")
    raw_path.write_bytes(payload)
    evidence = build_evidence(forecast, normalized, spec, target, raw_path, payload, url, obs, now)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_bytes(canon(evidence))
    return "CREATED"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--raw-root", type=Path, required=True)
    ap.add_argument("--fixture-dir", type=Path)
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(UTC)
    counts: dict[str, int] = {}
    errors: list[dict[str, str]] = []
    for path in sorted(args.forecast_root.rglob("*.json")) if args.forecast_root.exists() else []:
        try:
            forecast = json.loads(path.read_text())
            if forecast.get("contract") != "FROZEN_FORECAST_v1" or forecast.get("settlement_contract_version") != SETTLEMENT_CONTRACT:
                continue
            status = run_one(path, args.output_root, args.raw_root, now, args.fixture_dir)
            counts[status] = counts.get(status, 0) + 1
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})
    result = {"contract": RAW_CONTRACT, "owner_contract": OWNER_CONTRACT, "counts": counts, "errors": errors, "authority": AUTHORITY}
    print(json.dumps(result, sort_keys=True))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
