from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

AUTHORITY = {"binding": False, "canonical_acceptance": False, "state_change": False, "portfolio_action": False}
BINANCE_SPOT = "https://data-api.binance.vision/api/v3/klines"
OKX = "https://www.okx.com"
COPENHAGEN = ZoneInfo("Europe/Copenhagen")
SPOT_SYMBOLS = ("BTCUSDT", "ETHUSDT", "ETHBTC")
DERIVATIVE_SYMBOLS = (
    ("BTCUSDT", "BTC-USDT-SWAP", "BTC"),
    ("ETHUSDT", "ETH-USDT-SWAP", "ETH"),
)

FIELDS = [
    "timestamp_utc", "timestamp_copenhagen", "source_window_end_utc",
    "btc_open", "btc_high", "btc_low", "btc_close", "btc_volume", "btc_quote_volume", "btc_trade_count",
    "btc_taker_buy_base_volume", "btc_taker_buy_quote_volume", "btc_taker_sell_quote_volume", "btc_taker_buy_quote_share",
    "btc_return_1h_pct", "btc_range_1h_pct",
    "eth_open", "eth_high", "eth_low", "eth_close", "eth_volume", "eth_quote_volume", "eth_trade_count",
    "eth_taker_buy_base_volume", "eth_taker_buy_quote_volume", "eth_taker_sell_quote_volume", "eth_taker_buy_quote_share",
    "eth_return_1h_pct", "eth_range_1h_pct",
    "ethbtc_open", "ethbtc_high", "ethbtc_low", "ethbtc_close", "ethbtc_return_1h_pct", "ethbtc_range_1h_pct",
    "btc_open_interest", "btc_open_interest_value", "btc_oi_change_1h_pct", "btc_open_interest_source",
    "eth_open_interest", "eth_open_interest_value", "eth_oi_change_1h_pct", "eth_open_interest_source",
    "btc_long_short_ratio", "btc_long_account", "btc_short_account", "btc_long_short_source",
    "eth_long_short_ratio", "eth_long_account", "eth_short_account", "eth_long_short_source",
    "btc_funding_event_rate", "btc_funding_source", "eth_funding_event_rate", "eth_funding_source",
    "btc_price_oi_state", "eth_price_oi_state", "spot_status", "derivatives_status",
]


class SourceError(RuntimeError):
    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


def floor_hour_ms(value: int) -> int:
    return value - value % 3_600_000


def build_url(base: str, params: dict[str, object]) -> str:
    return base + "?" + urllib.parse.urlencode(params)


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Investering-Hourly-Sequence/2.2", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")
        status = "GEO_RESTRICTED" if exc.code in (403, 451) or "restricted location" in text.lower() else "HTTP_ERROR"
        raise SourceError(status, f"HTTP {exc.code}: {text[:200]}") from exc
    except Exception as exc:
        raise SourceError("NETWORK_ERROR", str(exc)) from exc
    if not body:
        raise SourceError("EMPTY_RESPONSE", "empty response")
    return body


def parse_binance_doc(body: bytes):
    try:
        value = json.loads(body)
    except Exception as exc:
        raise SourceError("SCHEMA_DRIFT", "invalid JSON") from exc
    if isinstance(value, dict):
        raise SourceError("SOURCE_ERROR", str(value.get("msg", value)))
    return value


def parse_okx_doc(body: bytes) -> list:
    try:
        value = json.loads(body)
    except Exception as exc:
        raise SourceError("SCHEMA_DRIFT", "invalid OKX JSON") from exc
    if not isinstance(value, dict) or str(value.get("code")) != "0":
        raise SourceError("SOURCE_ERROR", str(value.get("msg", value)))
    data = value.get("data")
    if not isinstance(data, list):
        raise SourceError("SCHEMA_DRIFT", "OKX data not list")
    return data


def parse_spot(body: bytes, symbol: str) -> dict[int, dict[str, float | int]]:
    value = parse_binance_doc(body)
    if not isinstance(value, list):
        raise SourceError("SCHEMA_DRIFT", symbol)
    output: dict[int, dict[str, float | int]] = {}
    for i, row in enumerate(value):
        if not isinstance(row, list) or len(row) < 12:
            raise SourceError("SCHEMA_DRIFT", f"{symbol}:{i}")
        try:
            stamp = floor_hour_ms(int(row[0]))
            open_, high, low, close, base_volume = map(float, row[1:6])
            quote_volume = float(row[7])
            trade_count = int(row[8])
            taker_buy_base = float(row[9])
            taker_buy_quote = float(row[10])
        except Exception as exc:
            raise SourceError("SCHEMA_DRIFT", f"{symbol}:{i}:numeric") from exc
        if high < max(open_, close) or low > min(open_, close):
            raise SourceError("INVALID_OHLC", f"{symbol}:{i}")
        taker_sell_quote = max(0.0, quote_volume - taker_buy_quote)
        taker_buy_quote_share = None if quote_volume <= 0 else taker_buy_quote / quote_volume
        output[stamp] = {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": base_volume,
            "quote_volume": quote_volume,
            "trade_count": trade_count,
            "taker_buy_base_volume": taker_buy_base,
            "taker_buy_quote_volume": taker_buy_quote,
            "taker_sell_quote_volume": taker_sell_quote,
            "taker_buy_quote_share": taker_buy_quote_share,
        }
    return output


def _num(value):
    try:
        return float(value)
    except Exception:
        return None


def _timestamp(value):
    try:
        parsed = int(float(value))
        return parsed if parsed > 1_000_000_000_000 else None
    except Exception:
        return None


def parse_okx_oi(body: bytes, symbol: str) -> dict[int, dict[str, float | str | None]]:
    output = {}
    for row in parse_okx_doc(body):
        stamp = amount = value = None
        if isinstance(row, dict):
            stamp = _timestamp(row.get("ts") or row.get("timestamp"))
            amount = _num(row.get("oiCcy") or row.get("oi") or row.get("openInterest"))
            value = _num(row.get("oiUsd") or row.get("oiValue") or row.get("openInterestValue"))
        elif isinstance(row, list):
            idx = next((j for j, item in enumerate(row) if _timestamp(item) is not None), None)
            if idx is not None:
                stamp = _timestamp(row[idx])
                numbers = [_num(item) for j, item in enumerate(row) if j != idx and _num(item) is not None]
                if numbers:
                    amount = numbers[0]
                if len(numbers) > 1:
                    value = numbers[1]
        if stamp is None or amount is None:
            continue
        output[floor_hour_ms(stamp)] = {"oi": amount, "value": value, "source": "OKX_CONTRACT_OI_HISTORY"}
    if not output:
        raise SourceError("SCHEMA_DRIFT", f"{symbol}:OKX OI no parseable rows")
    return output


def parse_okx_long_short(body: bytes, symbol: str) -> dict[int, dict[str, float | str]]:
    output = {}
    for row in parse_okx_doc(body):
        stamp = ratio = None
        if isinstance(row, dict):
            stamp = _timestamp(row.get("ts") or row.get("timestamp"))
            ratio = _num(row.get("ratio") or row.get("longShortRatio"))
        elif isinstance(row, list) and len(row) >= 2:
            idx = next((j for j, item in enumerate(row) if _timestamp(item) is not None), None)
            if idx is not None:
                stamp = _timestamp(row[idx])
                ratio = next((_num(item) for j, item in enumerate(row) if j != idx and _num(item) is not None), None)
        if stamp is None or ratio is None or ratio < 0:
            continue
        output[floor_hour_ms(stamp)] = {
            "ratio": ratio,
            "long": ratio / (1.0 + ratio),
            "short": 1.0 / (1.0 + ratio),
            "source": "OKX_GLOBAL_ACCOUNT_RATIO",
        }
    if not output:
        raise SourceError("SCHEMA_DRIFT", f"{symbol}:OKX L/S no parseable rows")
    return output


def parse_okx_funding(body: bytes) -> dict[int, dict[str, float | str]]:
    output = {}
    for row in parse_okx_doc(body):
        if not isinstance(row, dict):
            continue
        stamp = _timestamp(row.get("fundingTime") or row.get("ts"))
        raw_rate = row.get("realizedRate") if row.get("realizedRate") not in (None, "") else row.get("fundingRate")
        rate = _num(raw_rate)
        if stamp is not None and rate is not None:
            output[floor_hour_ms(stamp)] = {"rate": rate, "source": "OKX_FUNDING_HISTORY"}
    return output


def pct_change(current, previous):
    return None if current is None or previous in (None, 0) else (current / previous - 1.0) * 100.0


def range_pct(high, low):
    return None if high is None or low in (None, 0) else (high / low - 1.0) * 100.0


def fmt(value):
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return ""
    if isinstance(value, float):
        return format(value, ".12g")
    return str(value)


def price_oi_state(price_return, oi_return):
    if price_return is None or oi_return is None:
        return "UNAVAILABLE"
    if price_return < 0 < oi_return:
        return "PRICE_DOWN_OI_UP"
    if price_return > 0 > oi_return:
        return "PRICE_UP_OI_DOWN"
    if price_return > 0 and oi_return > 0:
        return "PRICE_UP_OI_UP"
    if price_return < 0 and oi_return < 0:
        return "PRICE_DOWN_OI_DOWN"
    return "MIXED_FLAT"


def source_read(fixture_dir: Path | None, name: str, url: str):
    try:
        body = (fixture_dir / name).read_bytes() if fixture_dir else fetch_bytes(url)
        return "PASS", body, None
    except SourceError as exc:
        return exc.status, None, str(exc)
    except OSError as exc:
        return "MISSING_FIXTURE", None, str(exc)


def merge_rows(root: Path, rows: list[dict[str, object]]) -> list[str]:
    touched = []
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["timestamp_utc"])[:10], []).append(row)
    for day, incoming in grouped.items():
        path = root / day[:4] / day[5:7] / f"{day}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        old: dict[str, dict[str, str]] = {}
        if path.exists():
            with path.open(newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    if row.get("timestamp_utc"):
                        old[row["timestamp_utc"]] = row
        for new in incoming:
            key = str(new["timestamp_utc"])
            previous = old.get(key, {})
            merged = {}
            for field in FIELDS:
                new_value = fmt(new.get(field))
                merged[field] = new_value if new_value != "" else previous.get(field, "")
            old[key] = merged
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(old[key] for key in sorted(old))
        touched.append(path.as_posix())
    return touched


def build_rows(start, end, spot_data, oi_data, ls_data, funding_data, spot_status, derivatives_status):
    output = []
    previous_close = {symbol: None for symbol in SPOT_SYMBOLS}
    previous_oi = {symbol: None for symbol, _, _ in DERIVATIVE_SYMBOLS}
    stamp = start
    while stamp <= end:
        timestamp_ms = to_ms(stamp)
        row = {
            "timestamp_utc": iso_utc(stamp),
            "timestamp_copenhagen": stamp.astimezone(COPENHAGEN).replace(microsecond=0).isoformat(),
            "source_window_end_utc": iso_utc(end + timedelta(hours=1)),
            "spot_status": spot_status,
            "derivatives_status": derivatives_status,
        }
        for symbol, prefix in (("BTCUSDT", "btc"), ("ETHUSDT", "eth"), ("ETHBTC", "ethbtc")):
            candle = spot_data.get(symbol, {}).get(timestamp_ms)
            if candle:
                for key in ("open", "high", "low", "close"):
                    row[f"{prefix}_{key}"] = candle[key]
                if prefix != "ethbtc":
                    for key in (
                        "volume", "quote_volume", "trade_count", "taker_buy_base_volume",
                        "taker_buy_quote_volume", "taker_sell_quote_volume", "taker_buy_quote_share",
                    ):
                        row[f"{prefix}_{key}"] = candle[key]
                row[f"{prefix}_return_1h_pct"] = pct_change(candle["close"], previous_close[symbol] or candle["open"])
                row[f"{prefix}_range_1h_pct"] = range_pct(candle["high"], candle["low"])
                previous_close[symbol] = candle["close"]

        for symbol, _, _ in DERIVATIVE_SYMBOLS:
            prefix = "btc" if symbol.startswith("BTC") else "eth"
            oi = oi_data.get(symbol, {}).get(timestamp_ms)
            if oi:
                row[f"{prefix}_open_interest"] = oi["oi"]
                row[f"{prefix}_open_interest_value"] = oi.get("value")
                row[f"{prefix}_oi_change_1h_pct"] = pct_change(oi["oi"], previous_oi[symbol])
                row[f"{prefix}_open_interest_source"] = oi.get("source")
                previous_oi[symbol] = oi["oi"]
            ls = ls_data.get(symbol, {}).get(timestamp_ms)
            if ls:
                row[f"{prefix}_long_short_ratio"] = ls["ratio"]
                row[f"{prefix}_long_account"] = ls["long"]
                row[f"{prefix}_short_account"] = ls["short"]
                row[f"{prefix}_long_short_source"] = ls.get("source")
            funding = funding_data.get(symbol, {}).get(timestamp_ms)
            if funding:
                row[f"{prefix}_funding_event_rate"] = funding["rate"]
                row[f"{prefix}_funding_source"] = funding.get("source")
            row[f"{prefix}_price_oi_state"] = price_oi_state(
                row.get(f"{prefix}_return_1h_pct"),
                row.get(f"{prefix}_oi_change_1h_pct"),
            )
        output.append(row)
        stamp += timedelta(hours=1)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--raw-output", type=Path, required=True)
    parser.add_argument("--lookback-hours", type=int, default=26)
    parser.add_argument("--retrieval-timestamp")
    parser.add_argument("--fixture-dir", type=Path)
    args = parser.parse_args()

    now = (
        datetime.fromisoformat(args.retrieval_timestamp.replace("Z", "+00:00"))
        if args.retrieval_timestamp else datetime.now(timezone.utc)
    )
    now = now.astimezone(timezone.utc)
    end = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    start = end - timedelta(hours=max(1, args.lookback_hours) - 1)
    start_ms = to_ms(start)
    end_ms = to_ms(end + timedelta(hours=1)) - 1
    args.raw_output.mkdir(parents=True, exist_ok=True)

    spot_data = {}
    oi_data = {}
    ls_data = {}
    funding_data = {}
    source_records = []
    spot_failures = 0
    derivative_failures = 0

    for symbol in SPOT_SYMBOLS:
        url = build_url(BINANCE_SPOT, {
            "symbol": symbol, "interval": "1h", "startTime": start_ms, "endTime": end_ms, "limit": 1000,
        })
        status, body, error = source_read(args.fixture_dir, f"{symbol}_spot.json", url)
        record = {"name": f"{symbol}_spot", "venue": "BINANCE_SPOT", "status": status, "url": url, "error": error}
        if body:
            path = args.raw_output / f"{symbol}_spot.json"
            path.write_bytes(body)
            record.update(bytes=len(body), sha256=sha256_bytes(body))
            try:
                spot_data[symbol] = parse_spot(body, symbol)
                record["row_count"] = len(spot_data[symbol])
            except SourceError as exc:
                record.update(status=exc.status, error=str(exc))
                spot_failures += 1
        else:
            spot_failures += 1
        source_records.append(record)

    for symbol, instrument, ccy in DERIVATIVE_SYMBOLS:
        queries = {
            "oi": (
                "/api/v5/rubik/stat/contracts/open-interest-history",
                {"instId": instrument, "period": "1H", "begin": start_ms, "end": end_ms, "limit": 100},
            ),
            "long_short": (
                "/api/v5/rubik/stat/contracts/long-short-account-ratio",
                {"ccy": ccy, "period": "1H", "begin": start_ms, "end": end_ms},
            ),
            "funding": (
                "/api/v5/public/funding-rate-history",
                {"instId": instrument, "limit": 100},
            ),
        }
        for key, (path_name, params) in queries.items():
            url = build_url(OKX + path_name, params)
            status, body, error = source_read(args.fixture_dir, f"{symbol}_{key}_okx.json", url)
            record = {"name": f"{symbol}_{key}", "venue": "OKX", "status": status, "url": url, "error": error}
            if body:
                (args.raw_output / f"{symbol}_{key}_okx.json").write_bytes(body)
                record.update(bytes=len(body), sha256=sha256_bytes(body))
                try:
                    if key == "oi":
                        parsed = parse_okx_oi(body, symbol)
                    elif key == "long_short":
                        parsed = parse_okx_long_short(body, symbol)
                    else:
                        parsed = parse_okx_funding(body)
                    parsed = {stamp: value for stamp, value in parsed.items() if start_ms <= stamp <= end_ms}
                    {"oi": oi_data, "long_short": ls_data, "funding": funding_data}[key][symbol] = parsed
                    record["row_count"] = len(parsed)
                    if key in ("oi", "long_short") and not parsed:
                        raise SourceError("EMPTY_WINDOW", f"{symbol}:{key}:no rows in requested window")
                except SourceError as exc:
                    record.update(status=exc.status, error=str(exc))
                    derivative_failures += 1
            else:
                derivative_failures += 1
            source_records.append(record)

    spot_status = "PASS" if spot_failures == 0 else "PARTIAL" if spot_data else "FAIL"
    required_derivative_groups = sum(bool(oi_data.get(symbol)) for symbol, _, _ in DERIVATIVE_SYMBOLS) + sum(
        bool(ls_data.get(symbol)) for symbol, _, _ in DERIVATIVE_SYMBOLS
    )
    derivatives_status = (
        "PASS"
        if all(bool(oi_data.get(symbol)) and bool(ls_data.get(symbol)) for symbol, _, _ in DERIVATIVE_SYMBOLS)
        else "PARTIAL" if required_derivative_groups else "UNAVAILABLE"
    )

    rows = build_rows(
        start, end, spot_data, oi_data, ls_data, funding_data, spot_status, derivatives_status
    )
    permanent_outputs = merge_rows(args.output_root, rows)
    requested_hours = len(rows)
    spot_complete = sum(
        row.get("btc_close") is not None and row.get("eth_close") is not None and row.get("ethbtc_close") is not None
        for row in rows
    )
    oi_complete = sum(
        row.get("btc_open_interest") is not None and row.get("eth_open_interest") is not None for row in rows
    )
    long_short_complete = sum(
        row.get("btc_long_short_ratio") is not None and row.get("eth_long_short_ratio") is not None for row in rows
    )
    spot_flow_complete = sum(
        row.get("btc_taker_buy_quote_share") is not None and row.get("eth_taker_buy_quote_share") is not None
        for row in rows
    )
    status = (
        "COMPLETE"
        if spot_complete == requested_hours and oi_complete == requested_hours and long_short_complete == requested_hours
        else "PARTIAL" if spot_complete else "FAILED"
    )
    run_id = "HOURLY_SEQUENCE_" + now.strftime("%Y%m%dT%H%M%SZ") + "_" + sha256_bytes(
        json.dumps(source_records, sort_keys=True).encode()
    )[:12]
    manifest = {
        "contract": "HOURLY_SEQUENCE_CAPTURE_v2_2",
        "run_id": run_id,
        "retrieved_at_utc": iso_utc(now),
        "window_start_utc": iso_utc(start),
        "window_end_utc": iso_utc(end + timedelta(hours=1)),
        "requested_hours": requested_hours,
        "spot_complete_hours": spot_complete,
        "spot_flow_complete_hours": spot_flow_complete,
        "derivatives_oi_complete_hours": oi_complete,
        "long_short_complete_hours": long_short_complete,
        "status": status,
        "spot_status": spot_status,
        "derivatives_status": derivatives_status,
        "spot_venue": "BINANCE",
        "derivatives_venue": "OKX",
        "interpolation": False,
        "forward_fill": False,
        "permanent_outputs": permanent_outputs,
        "source_records": source_records,
        "authority": AUTHORITY,
    }
    run_dir = args.output_root / "runs" / now.strftime("%Y/%m/%d")
    run_dir.mkdir(parents=True, exist_ok=True)
    run_path = run_dir / f"{now:%H%M%S}_{run_id}.json"
    run_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    pointer = {
        "contract": "HOURLY_SEQUENCE_LATEST_POINTER_v2_2",
        "run_id": run_id,
        "run_path": run_path.as_posix(),
        "retrieved_at_utc": manifest["retrieved_at_utc"],
        "window_start_utc": manifest["window_start_utc"],
        "window_end_utc": manifest["window_end_utc"],
        "status": status,
        "spot_complete_hours": spot_complete,
        "spot_flow_complete_hours": spot_flow_complete,
        "derivatives_oi_complete_hours": oi_complete,
        "long_short_complete_hours": long_short_complete,
        "requested_hours": requested_hours,
    }
    (args.output_root / "LATEST.json").write_text(json.dumps(pointer, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": status,
        "run_id": run_id,
        "hours": requested_hours,
        "spot_complete_hours": spot_complete,
        "spot_flow_complete_hours": spot_flow_complete,
        "derivatives_oi_complete_hours": oi_complete,
        "long_short_complete_hours": long_short_complete,
    }, sort_keys=True))
    raise SystemExit(2 if spot_complete == 0 else 0)


if __name__ == "__main__":
    main()
