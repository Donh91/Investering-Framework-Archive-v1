#!/usr/bin/env python3
"""
Fetch a reproducible OKX public BTC/ETH futures archive.

Data scope:
- 30-day aligned 1H swap candles
- 30-day aligned 1H mark-price candles
- 30-day aligned 1H index candles
- 30-day aligned 1H open-interest history
- 30-day funding settlements
- 30-day long/short account ratio
- 30-day contract taker-volume
- optional extended retention:
  funding 90d, OI 60d

No authentication is required. Public read-only endpoints only.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE_URL = "https://www.okx.com"
USER_AGENT = "Cycle-Navigator-OKX-Archive/1.0"
HOUR_MS = 3_600_000
DAY_MS = 86_400_000

SWAP_FIELDS = [
    "timestamp_ms", "open", "high", "low", "close",
    "volume_contracts", "volume_coin", "volume_quote", "confirm",
]
MARK_INDEX_FIELDS = [
    "timestamp_ms", "open", "high", "low", "close", "confirm",
]
OI_FIELDS = [
    "timestamp_ms", "open_interest_contracts",
    "open_interest_coin", "open_interest_usd",
]
FUNDING_FIELDS = [
    "instType", "instId", "fundingRate", "realizedRate",
    "fundingTime", "method", "formulaType",
]
RATIO_FIELDS = ["timestamp_ms", "long_short_account_ratio"]
TAKER_FIELDS = ["timestamp_ms", "volume_leg_1", "volume_leg_2"]


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso_utc(ms: int | str) -> str:
    value = int(ms)
    return dt.datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def request_json(path: str, params: dict[str, Any], retries: int = 5) -> dict[str, Any]:
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"{BASE_URL}{path}?{query}" if query else f"{BASE_URL}{path}"
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if str(payload.get("code")) != "0":
                raise RuntimeError(json.dumps(payload, ensure_ascii=False))
            return payload
        except Exception as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(min(2 ** attempt, 16))
    raise RuntimeError(f"Request failed after {retries} attempts: {url}: {last_error}")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, values: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def dedupe_sort_rows(rows: list[list[str]], timestamp_index: int = 0) -> list[list[str]]:
    by_ts: dict[int, list[str]] = {}
    for row in rows:
        if not row:
            continue
        by_ts[int(row[timestamp_index])] = row
    return [by_ts[ts] for ts in sorted(by_ts)]


def filter_window(rows: list[list[str]], start_ms: int, end_ms: int, timestamp_index: int = 0) -> list[list[str]]:
    return [row for row in rows if start_ms <= int(row[timestamp_index]) <= end_ms]


def fetch_candle_pages(endpoint: str, inst_id: str, bar: str, start_ms: int, end_ms: int, limit: str) -> tuple[list[dict[str, Any]], list[list[str]]]:
    pages: list[dict[str, Any]] = []
    all_rows: list[list[str]] = []
    after: str | None = None
    for _ in range(500):
        params = {"instId": inst_id, "bar": bar, "limit": limit, "after": after}
        payload = request_json(endpoint, params)
        pages.append(payload)
        rows = payload.get("data", [])
        if not rows:
            break
        all_rows.extend(rows)
        oldest = min(int(row[0]) for row in rows)
        if oldest <= start_ms:
            break
        after = str(oldest)
        time.sleep(0.12)
    normalized = dedupe_sort_rows(all_rows)
    return pages, filter_window(normalized, start_ms, end_ms)


def fetch_oi_pages(inst_id: str, start_ms: int, end_ms: int) -> tuple[list[dict[str, Any]], list[list[str]]]:
    pages: list[dict[str, Any]] = []
    all_rows: list[list[str]] = []
    cursor_end: str | None = None
    for _ in range(100):
        params = {"instId": inst_id, "period": "1H", "limit": 100, "end": cursor_end}
        payload = request_json("/api/v5/rubik/stat/contracts/open-interest-history", params)
        pages.append(payload)
        rows = payload.get("data", [])
        if not rows:
            break
        all_rows.extend(rows)
        oldest = min(int(row[0]) for row in rows)
        if oldest <= start_ms:
            break
        cursor_end = str(oldest - 1)
        time.sleep(0.12)
    normalized = dedupe_sort_rows(all_rows)
    return pages, filter_window(normalized, start_ms, end_ms)


def fetch_funding_pages(inst_id: str, start_ms: int, end_ms: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pages: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    after: str | None = None
    for _ in range(50):
        params = {"instId": inst_id, "limit": "100", "after": after}
        payload = request_json("/api/v5/public/funding-rate-history", params)
        pages.append(payload)
        batch = payload.get("data", [])
        if not batch:
            break
        records.extend(batch)
        oldest = min(int(item["fundingTime"]) for item in batch)
        if oldest <= start_ms:
            break
        after = str(oldest)
        time.sleep(0.12)
    by_ts: dict[int, dict[str, Any]] = {}
    for item in records:
        ts = int(item["fundingTime"])
        if start_ms <= ts <= end_ms:
            by_ts[ts] = item
    return pages, [by_ts[ts] for ts in sorted(by_ts)]


def fetch_window_rows(endpoint: str, params: dict[str, Any], start_ms: int, end_ms: int) -> tuple[dict[str, Any], list[list[str]]]:
    request_params = dict(params)
    request_params["begin"] = str(start_ms)
    request_params["end"] = str(end_ms)
    payload = request_json(endpoint, request_params)
    rows = dedupe_sort_rows(payload.get("data", []))
    return payload, filter_window(rows, start_ms, end_ms)


def rows_to_dicts(rows: list[list[str]], fields: list[str]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        item = dict(zip(fields, row))
        item["timestamp_utc"] = iso_utc(row[0])
        output.append(item)
    return output


def funding_to_dicts(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for record in records:
        item = dict(record)
        item["timestamp_ms"] = item["fundingTime"]
        item["timestamp_utc"] = iso_utc(item["fundingTime"])
        output.append(item)
    return output


def checksum_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in {"checksums.sha256"}:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result[str(path.relative_to(root))] = digest
    return result


def continuity(rows: list[list[str]], expected_ms: int = HOUR_MS) -> dict[str, Any]:
    timestamps = sorted({int(row[0]) for row in rows})
    gaps = []
    for left, right in zip(timestamps, timestamps[1:]):
        if right - left != expected_ms:
            gaps.append({"left": left, "right": right, "delta_ms": right - left})
    return {
        "record_count": len(rows),
        "unique_timestamp_count": len(timestamps),
        "duplicate_count": len(rows) - len(timestamps),
        "gap_count": len(gaps),
        "gaps": gaps[:100],
        "oldest_timestamp": timestamps[0] if timestamps else None,
        "newest_timestamp": timestamps[-1] if timestamps else None,
    }


def align_hourly(datasets: dict[str, list[dict[str, Any]]], out_path: Path) -> None:
    index: dict[int, dict[str, Any]] = {}
    for name, rows in datasets.items():
        for row in rows:
            ts = int(row["timestamp_ms"])
            target = index.setdefault(ts, {"timestamp_ms": str(ts), "timestamp_utc": iso_utc(ts)})
            for key, value in row.items():
                if key in {"timestamp_ms", "timestamp_utc"}:
                    continue
                target[f"{name}__{key}"] = value
    rows = [index[ts] for ts in sorted(index)]
    fieldnames = sorted({key for row in rows for key in row})
    fieldnames = ["timestamp_ms", "timestamp_utc"] + [field for field in fieldnames if field not in {"timestamp_ms", "timestamp_utc"}]
    write_csv(out_path, rows, fieldnames)


def export_symbol(root: Path, symbol: str, coin: str, start_ms: int, end_ms: int, extended: bool) -> dict[str, Any]:
    slug = coin.lower()
    raw_dir = root / "raw" / slug
    norm_dir = root / "normalized" / slug
    swap_pages, swap_rows = fetch_candle_pages("/api/v5/market/history-candles", symbol, "1H", start_ms, end_ms, "300")
    mark_pages, mark_rows = fetch_candle_pages("/api/v5/market/history-mark-price-candles", symbol, "1H", start_ms, end_ms, "100")
    index_id = f"{coin}-USDT"
    index_pages, index_rows = fetch_candle_pages("/api/v5/market/history-index-candles", index_id, "1H", start_ms, end_ms, "100")
    oi_start = end_ms - (60 * DAY_MS if extended else 30 * DAY_MS)
    oi_pages, oi_rows = fetch_oi_pages(symbol, oi_start, end_ms)
    funding_start = end_ms - (90 * DAY_MS if extended else 30 * DAY_MS)
    funding_pages, funding_records = fetch_funding_pages(symbol, funding_start, end_ms)
    ratio_payload, ratio_rows = fetch_window_rows("/api/v5/rubik/stat/contracts/long-short-account-ratio", {"ccy": coin, "period": "1H"}, start_ms, end_ms)
    taker_payload, taker_rows = fetch_window_rows("/api/v5/rubik/stat/taker-volume", {"ccy": coin, "instType": "CONTRACTS", "period": "1H"}, start_ms, end_ms)
    write_jsonl(raw_dir / "swap_history_pages.jsonl", swap_pages)
    write_jsonl(raw_dir / "mark_history_pages.jsonl", mark_pages)
    write_jsonl(raw_dir / "index_history_pages.jsonl", index_pages)
    write_jsonl(raw_dir / "oi_history_pages.jsonl", oi_pages)
    write_jsonl(raw_dir / "funding_history_pages.jsonl", funding_pages)
    write_json(raw_dir / "account_ratio.json", ratio_payload)
    write_json(raw_dir / "taker_volume.json", taker_payload)
    swap_dicts = rows_to_dicts(swap_rows, SWAP_FIELDS)
    mark_dicts = rows_to_dicts(mark_rows, MARK_INDEX_FIELDS)
    index_dicts = rows_to_dicts(index_rows, MARK_INDEX_FIELDS)
    oi_dicts = rows_to_dicts(oi_rows, OI_FIELDS)
    funding_dicts = funding_to_dicts(funding_records)
    ratio_dicts = rows_to_dicts(ratio_rows, RATIO_FIELDS)
    taker_dicts = rows_to_dicts(taker_rows, TAKER_FIELDS)
    write_csv(norm_dir / "swap_candles_1h.csv", swap_dicts, ["timestamp_ms", "timestamp_utc"] + SWAP_FIELDS[1:])
    write_csv(norm_dir / "mark_candles_1h.csv", mark_dicts, ["timestamp_ms", "timestamp_utc"] + MARK_INDEX_FIELDS[1:])
    write_csv(norm_dir / "index_candles_1h.csv", index_dicts, ["timestamp_ms", "timestamp_utc"] + MARK_INDEX_FIELDS[1:])
    write_csv(norm_dir / "open_interest_1h.csv", oi_dicts, ["timestamp_ms", "timestamp_utc"] + OI_FIELDS[1:])
    funding_fields = ["timestamp_ms", "timestamp_utc", "instType", "instId", "fundingRate", "realizedRate", "fundingTime", "method", "formulaType"]
    write_csv(norm_dir / "funding.csv", funding_dicts, funding_fields)
    write_csv(norm_dir / "long_short_account_ratio_1h.csv", ratio_dicts, ["timestamp_ms", "timestamp_utc"] + RATIO_FIELDS[1:])
    write_csv(norm_dir / "contract_taker_volume_1h.csv", taker_dicts, ["timestamp_ms", "timestamp_utc"] + TAKER_FIELDS[1:])
    align_hourly({
        "swap": swap_dicts,
        "mark": mark_dicts,
        "index": index_dicts,
        "oi": [row for row in oi_dicts if start_ms <= int(row["timestamp_ms"]) <= end_ms],
        "ratio": ratio_dicts,
        "taker": taker_dicts,
    }, root / "aligned" / f"{slug}_okx_30d_1h.csv")
    return {
        "symbol": symbol,
        "coin": coin,
        "swap": continuity(swap_rows),
        "mark": continuity(mark_rows),
        "index": continuity(index_rows),
        "oi": continuity(oi_rows),
        "funding_record_count": len(funding_records),
        "ratio": continuity(ratio_rows),
        "taker": continuity(taker_rows),
        "labels": {
            "open_interest": ["OKX_ONLY", "VENUE_SPECIFIC", "DO_NOT_SUM_ABSOLUTE_OI_ACROSS_VENUES"],
            "long_short_ratio": ["ACCOUNT_COUNT_RATIO", "NOT_POSITION_SIZE_RATIO", "NOT_MARKET_WIDE_POSITIONING"],
            "taker_volume": ["OKX_ONLY", "VENUE_SPECIFIC", "NOT_MARKET_WIDE_CVD", "RAW_LEG_ORDER_PRESERVED"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--days", type=int, default=30, help="Aligned window in days")
    parser.add_argument("--extended", action="store_true", help="Fetch 60d OI and 90d funding")
    args = parser.parse_args()
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)
    retrieval = utc_now()
    end_ms = int(retrieval.timestamp() * 1000)
    start_ms = end_ms - args.days * DAY_MS
    server_time = request_json("/api/v5/public/time", {})
    instruments = {symbol: request_json("/api/v5/public/instruments", {"instType": "SWAP", "instId": symbol}) for symbol in ["BTC-USDT-SWAP", "ETH-USDT-SWAP"]}
    current = {}
    for symbol, index_id in [("BTC-USDT-SWAP", "BTC-USDT"), ("ETH-USDT-SWAP", "ETH-USDT")]:
        current[symbol] = {
            "ticker": request_json("/api/v5/market/ticker", {"instId": symbol}),
            "mark": request_json("/api/v5/public/mark-price", {"instType": "SWAP", "instId": symbol}),
            "index": request_json("/api/v5/market/index-tickers", {"instId": index_id}),
            "funding": request_json("/api/v5/public/funding-rate", {"instId": symbol}),
            "open_interest": request_json("/api/v5/public/open-interest", {"instType": "SWAP", "instId": symbol}),
        }
    write_json(root / "raw" / "server_time.json", server_time)
    write_json(root / "raw" / "instruments.json", instruments)
    write_json(root / "raw" / "current_snapshots.json", current)
    reports = [
        export_symbol(root, "BTC-USDT-SWAP", "BTC", start_ms, end_ms, args.extended),
        export_symbol(root, "ETH-USDT-SWAP", "ETH", start_ms, end_ms, args.extended),
    ]
    validation = {
        "retrieval_timestamp_utc": retrieval.isoformat().replace("+00:00", "Z"),
        "aligned_days": args.days,
        "extended": args.extended,
        "reports": reports,
    }
    write_json(root / "validation_report.json", validation)
    manifest = {
        "package": "OKX_FUTURES_ARCHIVE",
        "version": "1.0.0",
        "source": "OKX public API",
        "retrieval_timestamp_utc": validation["retrieval_timestamp_utc"],
        "aligned_window_days": args.days,
        "extended_retention": {
            "funding_days": 90 if args.extended else args.days,
            "open_interest_days": 60 if args.extended else args.days,
            "account_ratio_days": args.days,
            "taker_volume_days": args.days,
            "candles_days": args.days,
        },
        "instruments": ["BTC-USDT-SWAP", "ETH-USDT-SWAP"],
        "bar": "1H",
        "labels": {
            "taker_volume": "OKX_ONLY / VENUE_SPECIFIC / NOT_MARKET_WIDE_CVD",
            "long_short_ratio": "ACCOUNT_COUNT_RATIO / NOT_POSITION_SIZE_RATIO",
            "open_interest": "OKX_ONLY / DO_NOT_SUM_ABSOLUTE_OI_ACROSS_VENUES",
        },
    }
    write_json(root / "manifest.json", manifest)
    checksums = checksum_tree(root)
    with (root / "checksums.sha256").open("w", encoding="utf-8") as handle:
        for rel, digest in sorted(checksums.items()):
            handle.write(f"{digest}  {rel}\n")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
