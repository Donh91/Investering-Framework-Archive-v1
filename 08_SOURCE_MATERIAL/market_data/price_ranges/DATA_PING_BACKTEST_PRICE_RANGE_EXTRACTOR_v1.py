#!/usr/bin/env python3
"""
DATA_PING_BACKTEST_PRICE_RANGE_EXTRACTOR_v1.py

Deterministic public-source extractor for daily BTC/ETH/ETHBTC price-range backtests.

SPEC_VERSION: DATA_PING_GOVERNANCE_SPEC_v2_6_FREE_ONLY
ROLE: DATA_ONLY
NO_PORTFOLIO_ACTION_FROM_DATASET
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable, Optional

import requests
import pandas as pd


BASE_URL = "https://api.binance.com/api/v3/klines"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "ETHBTC"]
INTERVAL = "1d"
TIMEZONE = "+02:00"

START_DATE = "2024-01-01"
OUTPUT_PREFIX = "DATA_PING_BACKTEST_DAILY_PRICE_RANGE_2024_NOW"

# Framework levels used for feature extraction only.
BTC_LEVELS = {
    "63300": 63300.0,
    "61900": 61900.0,
    "61000": 61000.0,
    "60900": 60900.0,
    "60000": 60000.0,
    "59400": 59400.0,
    "59000": 59000.0,
}

ETHBTC_LEVELS = {
    "0265": 0.0265,
    "0275": 0.0275,
    "0300": 0.0300,
}


def to_ms_utc(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def parse_date_start_utc_for_plus02(date_str: str) -> datetime:
    """
    For timeZone=+02:00, a local day starts at UTC 22:00 on prior calendar day.
    This is a fixed +02 basis, not automatic DST.
    """
    local_midnight = datetime.fromisoformat(date_str + "T00:00:00")
    utc_dt = (local_midnight - timedelta(hours=2)).replace(tzinfo=timezone.utc)
    return utc_dt


def fetch_klines(symbol: str, start_ms: int, end_ms: Optional[int] = None, limit: int = 1000) -> list[list]:
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "startTime": start_ms,
        "limit": limit,
        "timeZone": TIMEZONE,
    }
    if end_ms is not None:
        params["endTime"] = end_ms

    out: list[list] = []
    cursor = start_ms

    while True:
        params["startTime"] = cursor
        r = requests.get(BASE_URL, params=params, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Binance request failed for {symbol}: HTTP {r.status_code}: {r.text[:500]}")

        batch = r.json()
        if not batch:
            break

        out.extend(batch)

        # Next start is previous close_time + 1 ms
        last_close = int(batch[-1][6])
        next_cursor = last_close + 1

        if next_cursor <= cursor:
            break

        cursor = next_cursor

        # Stop if this batch returned fewer rows than max.
        if len(batch) < limit:
            break

        time.sleep(0.15)

    return out


def klines_to_df(symbol: str, klines: list[list]) -> pd.DataFrame:
    cols = [
        "open_time_ms",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time_ms",
        "quote_volume",
        "trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]
    df = pd.DataFrame(klines, columns=cols)
    for c in ["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_base_volume", "taker_buy_quote_volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["open_time_ms", "close_time_ms", "trades"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    # For timeZone +02 daily candles, open_time_ms is UTC timestamp of +02 local midnight.
    df["date"] = pd.to_datetime(df["open_time_ms"], unit="ms", utc=True) + pd.Timedelta(hours=2)
    df["date"] = df["date"].dt.date.astype(str)

    prefix = {
        "BTCUSDT": "btc",
        "ETHUSDT": "eth",
        "ETHBTC": "ethbtc",
    }[symbol]

    keep = ["date", "open", "high", "low", "close", "volume", "quote_volume", "trades", "open_time_ms", "close_time_ms"]
    df = df[keep].copy()
    df = df.rename(columns={c: f"{prefix}_{c}" for c in keep if c != "date"})
    return df


def rolling_streak(series: pd.Series) -> pd.Series:
    count = 0
    out = []
    for v in series.fillna(False).astype(bool):
        if v:
            count += 1
        else:
            count = 0
        out.append(count)
    return pd.Series(out, index=series.index)


def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["time_basis"] = f"Binance spot daily, timeZone={TIMEZONE}"
    out["source"] = "Binance public spot API"
    out["is_current_partial_day"] = out.index == out.index.max()

    # BTC range
    out["btc_range_abs"] = out["btc_high"] - out["btc_low"]
    out["btc_range_pct_open"] = (out["btc_range_abs"] / out["btc_open"]) * 100
    out["btc_close_vs_open_pct"] = ((out["btc_close"] / out["btc_open"]) - 1) * 100
    out["btc_high_vs_open_pct"] = ((out["btc_high"] / out["btc_open"]) - 1) * 100
    out["btc_low_vs_open_pct"] = ((out["btc_low"] / out["btc_open"]) - 1) * 100
    out["btc_close_location_pct"] = ((out["btc_close"] - out["btc_low"]) / (out["btc_high"] - out["btc_low"])) * 100

    prev_close = out["btc_close"].shift(1)
    tr1 = out["btc_high"] - out["btc_low"]
    tr2 = (out["btc_high"] - prev_close).abs()
    tr3 = (out["btc_low"] - prev_close).abs()
    out["btc_true_range"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    out["btc_atr14"] = out["btc_true_range"].rolling(14, min_periods=14).mean()
    out["btc_atr14_pct_close"] = (out["btc_atr14"] / out["btc_close"]) * 100

    # BTC levels
    for label, level in BTC_LEVELS.items():
        out[f"btc_touch_{label}"] = out["btc_high"] >= level
        out[f"btc_close_gt_{label}"] = out["btc_close"] > level

    out["btc_close_lt_59400"] = out["btc_close"] < BTC_LEVELS["59400"]
    out["btc_low_lt_59000"] = out["btc_low"] < BTC_LEVELS["59000"]

    # Reclaim/failure style flags
    for label in ["63300", "61900", "61000", "60900", "60000"]:
        out[f"btc_{label}_touch_no_close"] = out[f"btc_touch_{label}"] & (~out[f"btc_close_gt_{label}"])

    out["btc_59400_lost_close"] = out["btc_close"] < BTC_LEVELS["59400"]

    # ETH and ETHBTC
    out["eth_range_abs"] = out["eth_high"] - out["eth_low"]
    out["eth_range_pct_open"] = (out["eth_range_abs"] / out["eth_open"]) * 100
    out["eth_close_vs_open_pct"] = ((out["eth_close"] / out["eth_open"]) - 1) * 100

    out["ethbtc_range_pct_open"] = ((out["ethbtc_high"] - out["ethbtc_low"]) / out["ethbtc_open"]) * 100
    out["ethbtc_close_vs_open_pct"] = ((out["ethbtc_close"] / out["ethbtc_open"]) - 1) * 100
    for label, level in ETHBTC_LEVELS.items():
        out[f"ethbtc_close_gt_{label}"] = out["ethbtc_close"] > level

    # Returns and relative performance
    out["btc_1d_return_pct"] = out["btc_close"].pct_change() * 100
    out["eth_1d_return_pct"] = out["eth_close"].pct_change() * 100
    out["eth_minus_btc_1d_return_pct"] = out["eth_1d_return_pct"] - out["btc_1d_return_pct"]
    out["eth_outperformed_btc"] = out["eth_minus_btc_1d_return_pct"] > 0

    # Streaks
    out["btc_close_gt_61900_streak"] = rolling_streak(out["btc_close_gt_61900"])
    out["btc_close_gt_63300_streak"] = rolling_streak(out["btc_close_gt_63300"])
    out["ethbtc_close_gt_0275_streak"] = rolling_streak(out["ethbtc_close_gt_0275"])
    out["ethbtc_close_gt_0300_streak"] = rolling_streak(out["ethbtc_close_gt_0300"])
    out["btc_down_close_streak"] = rolling_streak(out["btc_1d_return_pct"] < 0)
    out["btc_up_close_streak"] = rolling_streak(out["btc_1d_return_pct"] > 0)

    # Forward outcomes for offline supervised backtest only.
    for n in [1, 3, 5, 7, 14, 30]:
        out[f"btc_fwd_{n}d_return_pct"] = ((out["btc_close"].shift(-n) / out["btc_close"]) - 1) * 100

        # Max high / max drawdown across next n calendar rows excluding current row.
        fwd_high = pd.concat([out["btc_high"].shift(-i) for i in range(1, n + 1)], axis=1).max(axis=1)
        fwd_low = pd.concat([out["btc_low"].shift(-i) for i in range(1, n + 1)], axis=1).min(axis=1)
        out[f"btc_fwd_{n}d_max_high_pct"] = ((fwd_high / out["btc_close"]) - 1) * 100
        out[f"btc_fwd_{n}d_max_drawdown_pct"] = ((fwd_low / out["btc_close"]) - 1) * 100

    return out


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["month"] = pd.to_datetime(tmp["date"]).dt.to_period("M").astype(str)
    rows = []
    for month, g in tmp.groupby("month", sort=True):
        rows.append({
            "month": month,
            "days": len(g),
            "btc_open_first": g["btc_open"].iloc[0],
            "btc_high": g["btc_high"].max(),
            "btc_low": g["btc_low"].min(),
            "btc_close_last": g["btc_close"].iloc[-1],
            "btc_month_return_pct": ((g["btc_close"].iloc[-1] / g["btc_open"].iloc[0]) - 1) * 100,
            "btc_month_range_pct_open": ((g["btc_high"].max() - g["btc_low"].min()) / g["btc_open"].iloc[0]) * 100,
            "eth_month_return_pct": ((g["eth_close"].iloc[-1] / g["eth_open"].iloc[0]) - 1) * 100,
            "ethbtc_start": g["ethbtc_open"].iloc[0],
            "ethbtc_end": g["ethbtc_close"].iloc[-1],
            "ethbtc_change_pct": ((g["ethbtc_close"].iloc[-1] / g["ethbtc_open"].iloc[0]) - 1) * 100,
        })
    return pd.DataFrame(rows)


def write_markdown(df: pd.DataFrame, monthly: pd.DataFrame, out_path: Path) -> None:
    meta = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Binance public spot API",
        "time_basis": f"1d candles with timeZone={TIMEZONE}",
        "start_date": df["date"].min(),
        "end_date": df["date"].max(),
        "rows": len(df),
        "note": "Last row may be current partial day depending on run time.",
    }

    cols_to_export = [
        "date", "time_basis", "source", "is_current_partial_day",
        "btc_open", "btc_high", "btc_low", "btc_close", "btc_volume", "btc_quote_volume", "btc_trades",
        "btc_range_abs", "btc_range_pct_open", "btc_close_vs_open_pct", "btc_close_location_pct",
        "btc_true_range", "btc_atr14", "btc_atr14_pct_close",
        "btc_touch_63300", "btc_close_gt_63300", "btc_63300_touch_no_close",
        "btc_touch_61900", "btc_close_gt_61900", "btc_61900_touch_no_close",
        "btc_close_lt_59400", "btc_low_lt_59000",
        "eth_open", "eth_high", "eth_low", "eth_close", "eth_close_vs_open_pct",
        "ethbtc_open", "ethbtc_high", "ethbtc_low", "ethbtc_close",
        "ethbtc_close_gt_0265", "ethbtc_close_gt_0275", "ethbtc_close_gt_0300",
        "btc_1d_return_pct", "eth_1d_return_pct", "eth_minus_btc_1d_return_pct", "eth_outperformed_btc",
        "btc_close_gt_61900_streak", "btc_close_gt_63300_streak",
        "ethbtc_close_gt_0275_streak", "ethbtc_close_gt_0300_streak",
        "btc_fwd_1d_return_pct", "btc_fwd_3d_return_pct", "btc_fwd_7d_return_pct",
        "btc_fwd_3d_max_high_pct", "btc_fwd_3d_max_drawdown_pct",
        "btc_fwd_7d_max_high_pct", "btc_fwd_7d_max_drawdown_pct",
        "btc_fwd_14d_return_pct", "btc_fwd_30d_return_pct",
    ]

    md = []
    md.append("# DATA PING Backtest Daily Price Range Dataset\n")
    md.append("SPEC_VERSION: DATA_PING_GOVERNANCE_SPEC_v2_6_FREE_ONLY\n")
    md.append("ROLE: DATA_ONLY\n")
    md.append("\n## Metadata\n")
    for k, v in meta.items():
        md.append(f"- `{k}`: `{v}`\n")

    md.append("\n## Governance\n")
    md.append("This dataset supplies verified inputs only. It does not determine recovery, rotation, rebuy, deployment, official row, or portfolio action.\n")

    md.append("\n## Monthly summary\n\n")
    md.append(monthly.round(6).to_markdown(index=False))
    md.append("\n\n## Daily data table\n\n")
    md.append("The CSV file is preferred for backtests. This markdown table is included for inspection.\n\n")
    md.append(df[cols_to_export].round(8).to_markdown(index=False))
    md.append("\n")

    out_path.write_text("".join(md), encoding="utf-8")


def main() -> int:
    start_dt = parse_date_start_utc_for_plus02(START_DATE)
    start_ms = to_ms_utc(start_dt)

    print(f"Fetching Binance daily klines from {START_DATE}, timeZone={TIMEZONE}")
    frames = {}

    for symbol in SYMBOLS:
        print(f"Fetching {symbol}...")
        klines = fetch_klines(symbol, start_ms=start_ms, limit=1000)
        df = klines_to_df(symbol, klines)
        frames[symbol] = df
        print(f"  rows: {len(df)}")

    merged = frames["BTCUSDT"]
    merged = merged.merge(frames["ETHUSDT"], on="date", how="inner")
    merged = merged.merge(frames["ETHBTC"], on="date", how="inner")
    merged = merged.sort_values("date").reset_index(drop=True)

    enriched = add_price_features(merged)
    monthly = monthly_summary(enriched)

    csv_path = Path(f"{OUTPUT_PREFIX}.csv")
    md_path = Path(f"{OUTPUT_PREFIX}.md")
    parquet_path = Path(f"{OUTPUT_PREFIX}.parquet")

    enriched.to_csv(csv_path, index=False)
    write_markdown(enriched, monthly, md_path)

    try:
        enriched.to_parquet(parquet_path, index=False)
        print(f"Wrote {parquet_path}")
    except Exception as e:
        print(f"Parquet skipped: {e}")

    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
