from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SYMBOLS = ["BTCUSDT", "ETHUSDT", "ETHBTC"]


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def fetch_klines(symbol: str, start_ms: int, end_ms: int) -> list[list[object]]:
    query = urllib.parse.urlencode({"symbol": symbol, "interval": "1h", "startTime": start_ms, "endTime": end_ms, "limit": 1000})
    with urllib.request.urlopen("https://api.binance.com/api/v3/klines?" + query, timeout=60) as response:
        return json.loads(response.read())


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    # At Sunday-night execution this is the current ISO week's Monday.
    start = monday
    end = min(now, monday + timedelta(days=7))
    package: dict[str, object] = {
        "contract": "WEEKLY_MARKET_CLOSE_PACKAGE_v1",
        "iso_year": start.isocalendar().year,
        "iso_week": start.isocalendar().week,
        "window_start_utc": start.isoformat().replace("+00:00", "Z"),
        "window_end_utc": end.isoformat().replace("+00:00", "Z"),
        "source": "BINANCE_PUBLIC_1H_KLINES",
        "symbols": {},
        "authority": "SHADOW_CALIBRATION_INPUT",
        "canonical_data_ping": False,
        "framework_state_change": False,
        "portfolio_action": False,
    }
    for symbol in SYMBOLS:
        rows = fetch_klines(symbol, int(start.timestamp() * 1000), int(end.timestamp() * 1000))
        if not rows:
            raise SystemExit(f"empty_klines:{symbol}")
        by_day: dict[str, list[list[object]]] = {}
        for row in rows:
            day = datetime.fromtimestamp(int(row[0]) / 1000, tz=timezone.utc).date().isoformat()
            by_day.setdefault(day, []).append(row)
        daily = [summarize_day(by_day[d], d) for d in sorted(by_day)]
        package["symbols"][symbol] = {
            "weekly_open": float(rows[0][1]),
            "weekly_high": max(float(r[2]) for r in rows),
            "weekly_low": min(float(r[3]) for r in rows),
            "weekly_close": float(rows[-1][4]),
            "hour_count": len(rows),
            "daily_ranges": daily,
            "completeness": "PASS" if len(rows) >= 24 * len(daily) - 1 else "DEGRADED",
        }
    body = canonical(package)
    digest = hashlib.sha256(body).hexdigest()
    out = args.output_root / str(start.isocalendar().year) / f"W{start.isocalendar().week:02d}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "WEEKLY_MARKET_CLOSE_PACKAGE.json").write_bytes(body)
    receipt = {
        "contract": "WEEKLY_MARKET_CLOSE_RECEIPT_v1",
        "sha256": digest,
        "generated_at_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "symbols": SYMBOLS,
        "status": "PASS",
        "handoff_targets": ["CYCLE_NAVIGATOR", "RAW_WEEKLY_CALIBRATION", "MASTER_MONDAY", "FORECAST_LEDGER", "SPECIALIST_REVIEW"],
    }
    (out / "WEEKLY_MARKET_CLOSE_RECEIPT.json").write_bytes(canonical(receipt))
    latest = args.output_root / "LATEST_WEEKLY_MARKET_CLOSE.json"
    latest.write_bytes(canonical({"path": str((out / "WEEKLY_MARKET_CLOSE_PACKAGE.json").relative_to(args.output_root.parent)), "sha256": digest, "status": "PASS"}))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
