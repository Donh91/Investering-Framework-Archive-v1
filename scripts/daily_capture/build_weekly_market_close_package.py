from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SYMBOLS = ["BTCUSDT", "ETHUSDT", "ETHBTC"]
BINANCE_MARKET_DATA_BASE = "https://data-api.binance.vision"
HOUR_MS = 3_600_000


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def fetch_klines(symbol: str, start_ms: int, end_ms: int, base_url: str = BINANCE_MARKET_DATA_BASE) -> list[list[object]]:
    query = urllib.parse.urlencode({"symbol": symbol, "interval": "1h", "startTime": start_ms, "endTime": end_ms - 1, "limit": 1000})
    url = base_url.rstrip("/") + "/api/v3/klines?" + query
    request = urllib.request.Request(url, headers={"User-Agent": "investering-framework-weekly-close/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    if not isinstance(payload, list):
        raise ValueError(f"invalid_kline_payload:{symbol}")
    return payload


def summarize_day(rows: list[list[object]], date: str) -> dict[str, object]:
    return {
        "date_utc": date,
        "open": float(rows[0][1]),
        "high": max(float(r[2]) for r in rows),
        "low": min(float(r[3]) for r in rows),
        "close": float(rows[-1][4]),
        "volume": sum(float(r[5]) for r in rows),
        "hour_count": len(rows),
        "first_open_time_ms": int(rows[0][0]),
        "last_close_time_ms": int(rows[-1][6]),
    }


def validated_closed_rows(rows, start, end, *, final: bool, symbol: str):
    """Validate actual UTC candles before any weekly artifact can be published."""
    if not isinstance(rows, list):
        raise ValueError(f"invalid_kline_payload:{symbol}")
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    closed_end_ms = end_ms - end_ms % HOUR_MS
    seen = set()
    closed = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 7:
            raise ValueError(f"invalid_kline_shape:{symbol}")
        stamp, close_time = row[0], row[6]
        if type(stamp) is not int or type(close_time) is not int:
            raise ValueError(f"invalid_kline_timestamp:{symbol}")
        if stamp % HOUR_MS or close_time != stamp + HOUR_MS - 1:
            raise ValueError(f"invalid_hour_interval:{symbol}")
        # A pre-close request may also return the currently forming candle.
        if not final and stamp == closed_end_ms and closed_end_ms < end_ms:
            continue
        if stamp < start_ms or stamp >= closed_end_ms:
            raise ValueError(f"kline_outside_requested_window:{symbol}")
        if stamp in seen:
            raise ValueError(f"duplicate_hour:{symbol}")
        seen.add(stamp)
        try:
            if any(isinstance(value, bool) for value in row[1:6]):
                raise ValueError("boolean")
            open_, high, low, close, volume = map(float, row[1:6])
            if not all(math.isfinite(n) for n in (open_, high, low, close, volume)):
                raise ValueError("non_finite")
            if min(open_, high, low, close) <= 0 or volume < 0:
                raise ValueError("invalid_range")
            if high < max(open_, close) or low > min(open_, close):
                raise ValueError("invalid_ohlc")
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"invalid_kline_values:{symbol}") from exc
        closed.append(row)
    return sorted(closed, key=lambda row: row[0])


def resolve_window(now: datetime, mode: str) -> tuple[datetime, datetime, bool, str]:
    this_monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    if mode == "final":
        end = this_monday
        start = end - timedelta(days=7)
        return start, end, True, "FINAL_COMPLETED_ISO_WEEK"
    start = this_monday
    end = min(now, start + timedelta(days=7))
    return start, end, False, "PRE_CLOSE_CURRENT_ISO_WEEK"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--mode", choices=["preclose", "final"], required=True)
    parser.add_argument("--now-utc", help="Test-only ISO timestamp")
    parser.add_argument("--base-url", default=BINANCE_MARKET_DATA_BASE, help="Test override; production uses Binance market-data-only endpoint")
    args = parser.parse_args()

    now = datetime.fromisoformat(args.now_utc.replace("Z", "+00:00")) if args.now_utc else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    start, end, final, close_mode = resolve_window(now, args.mode)
    if final and now < end:
        raise SystemExit("FINAL_WINDOW_NOT_YET_CLOSED")

    package: dict[str, object] = {
        "contract": "WEEKLY_MARKET_CLOSE_PACKAGE_v3",
        "iso_year": start.isocalendar().year,
        "iso_week": start.isocalendar().week,
        "window_start_utc": start.isoformat().replace("+00:00", "Z"),
        "window_end_utc": end.isoformat().replace("+00:00", "Z"),
        "generated_at_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "final": final,
        "close_mode": close_mode,
        "source": "BINANCE_MARKET_DATA_ONLY_1H_KLINES",
        "source_base_url": args.base_url,
        "symbols": {},
        "authority": "SHADOW_CALIBRATION_INPUT",
        "canonical_data_ping": False,
        "framework_state_change": False,
        "portfolio_action": False,
    }

    expected_hours = int((end - start).total_seconds() // 3600)
    all_complete = True
    for symbol in SYMBOLS:
        rows = fetch_klines(symbol, int(start.timestamp() * 1000), int(end.timestamp() * 1000), args.base_url)
        rows = validated_closed_rows(rows, start, end, final=final, symbol=symbol)
        if not rows:
            raise SystemExit(f"empty_closed_klines:{symbol}")
        if final and len(rows) != expected_hours:
            all_complete = False
        by_day: dict[str, list[list[object]]] = {}
        for row in rows:
            day = datetime.fromtimestamp(int(row[0]) / 1000, tz=timezone.utc).date().isoformat()
            by_day.setdefault(day, []).append(row)
        daily = [summarize_day(by_day[d], d) for d in sorted(by_day)]
        completeness = "PASS" if len(rows) == expected_hours else "DEGRADED"
        package["symbols"][symbol] = {
            "weekly_open": float(rows[0][1]),
            "weekly_high": max(float(r[2]) for r in rows),
            "weekly_low": min(float(r[3]) for r in rows),
            "weekly_close": float(rows[-1][4]),
            "hour_count": len(rows),
            "expected_hour_count": expected_hours,
            "last_close_time_ms": int(rows[-1][6]),
            "daily_ranges": daily,
            "completeness": completeness,
        }

    package["completeness"] = "COMPLETE" if final and all_complete else ("PARTIAL" if not final else "DEGRADED")
    if final and package["completeness"] != "COMPLETE":
        raise SystemExit("FINAL_WEEK_INCOMPLETE")

    body = canonical(package)
    digest = hashlib.sha256(body).hexdigest()
    out = args.output_root / str(start.isocalendar().year) / f"W{start.isocalendar().week:02d}"
    out.mkdir(parents=True, exist_ok=True)
    package_path = out / "WEEKLY_MARKET_CLOSE_PACKAGE.json"
    package_path.write_bytes(body)
    receipt = {
        "contract": "WEEKLY_MARKET_CLOSE_RECEIPT_v3",
        "sha256": digest,
        "generated_at_utc": package["generated_at_utc"],
        "iso_year": package["iso_year"],
        "iso_week": package["iso_week"],
        "final": final,
        "close_mode": close_mode,
        "completeness": package["completeness"],
        "source_base_url": args.base_url,
        "symbols": SYMBOLS,
        "status": "PASS",
        "handoff_targets": ["CYCLE_NAVIGATOR", "RAW_WEEKLY_CALIBRATION", "MASTER_MONDAY", "FORECAST_LEDGER", "SPECIALIST_REVIEW"],
    }
    (out / "WEEKLY_MARKET_CLOSE_RECEIPT.json").write_bytes(canonical(receipt))
    pointer = {
        "contract": "WEEKLY_MARKET_CLOSE_POINTER_v3",
        "path": str(package_path.relative_to(args.output_root.parent)),
        "sha256": digest,
        "status": "PASS",
        "iso_year": package["iso_year"],
        "iso_week": package["iso_week"],
        "window_end_utc": package["window_end_utc"],
        "final": final,
        "close_mode": close_mode,
        "completeness": package["completeness"],
        "source_base_url": args.base_url,
    }
    (args.output_root / "LATEST_WEEKLY_MARKET_CLOSE.json").write_bytes(canonical(pointer))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
