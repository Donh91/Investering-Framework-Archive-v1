# DATA PING Backtest Historical Price Range Extractor — BTC/ETH Daily

SPEC_VERSION: DATA_PING_GOVERNANCE_SPEC_v2_6_FREE_ONLY  
FILE_VERSION: DATA_PING_BACKTEST_PRICE_RANGE_EXTRACTOR_v1  
CREATED_UTC: 2026-07-06T21:45:00Z

## Purpose

This package defines a deterministic historical extractor for daily crypto backtests from 2024-01-01 to "now".

Primary use:
- BTC daily price ranges
- ETH daily price ranges
- ETH/BTC relative-strength ledger
- Framework level/rung testing
- Reclaim/failure counting
- ATR/range/close persistence studies
- Outcome testing across alternative framework rules

The extractor is designed for backtest data generation, not trading advice.

## Why this is an extractor and not a pasted 900+ row table

The live tool response limit blocks a single full 2024-now Binance daily candle dump in-chat. A 1000-row Binance kline pull returned `ResponseTooLargeError`.

Therefore this download contains a reproducible script that fetches the full dataset directly from free public sources and writes backtest-ready CSV + Markdown locally.

This avoids:
- truncated data
- hand-copied rows
- invented/backfilled rows
- silent formatting errors
- token-limit corruption

## Primary source

Binance Spot public REST API:

`GET https://api.binance.com/api/v3/klines`

Used symbols:
- `BTCUSDT`
- `ETHUSDT`
- `ETHBTC`

Used interval:
- `1d`

Used timezone parameter:
- `timeZone=+02:00`

Important:
- Binance docs specify that kline intervals can be interpreted in a supplied timezone, while `startTime` and `endTime` are always interpreted in UTC.
- Binance kline response contains open time, open, high, low, close, volume, close time, quote volume, number of trades, taker buy base volume, taker buy quote volume.

## Output files created by the script

When run, the script writes:

1. `DATA_PING_BACKTEST_DAILY_PRICE_RANGE_2024_NOW.csv`

Main row-per-day backtest dataset.

2. `DATA_PING_BACKTEST_DAILY_PRICE_RANGE_2024_NOW.md`

Long markdown document with:
- metadata
- column dictionary
- summary stats
- monthly range table
- full CSV-style daily table in markdown

3. `DATA_PING_BACKTEST_DAILY_PRICE_RANGE_2024_NOW.parquet`

Optional if `pyarrow` is installed. If not, skipped.

## Core columns

### Date and source
- `date`
- `time_basis`
- `source`
- `is_current_partial_day`

### BTC raw OHLCV
- `btc_open`
- `btc_high`
- `btc_low`
- `btc_close`
- `btc_volume`
- `btc_quote_volume`
- `btc_trades`

### BTC derived range
- `btc_range_abs`
- `btc_range_pct_open`
- `btc_close_vs_open_pct`
- `btc_high_vs_open_pct`
- `btc_low_vs_open_pct`
- `btc_close_location_pct`
- `btc_true_range`
- `btc_atr14`
- `btc_atr14_pct_close`

### Framework/rung fields
- `btc_touch_63300`
- `btc_close_gt_63300`
- `btc_touch_61900`
- `btc_close_gt_61900`
- `btc_touch_61000`
- `btc_close_gt_61000`
- `btc_touch_60900`
- `btc_close_gt_60900`
- `btc_touch_60000`
- `btc_close_gt_60000`
- `btc_touch_59400`
- `btc_close_lt_59400`
- `btc_low_lt_59000`

### BTC reclaim/failure fields
- `btc_63300_touch_no_close`
- `btc_61900_touch_no_close`
- `btc_61000_touch_no_close`
- `btc_60900_touch_no_close`
- `btc_60000_touch_no_close`
- `btc_59400_lost_close`

### ETH raw OHLCV
- `eth_open`
- `eth_high`
- `eth_low`
- `eth_close`
- `eth_volume`
- `eth_quote_volume`
- `eth_trades`

### ETH/BTC direct
- `ethbtc_open`
- `ethbtc_high`
- `ethbtc_low`
- `ethbtc_close`
- `ethbtc_range_pct_open`
- `ethbtc_close_vs_open_pct`
- `ethbtc_close_gt_0265`
- `ethbtc_close_gt_0275`
- `ethbtc_close_gt_0300`

### BTC/ETH relative performance
- `btc_1d_return_pct`
- `eth_1d_return_pct`
- `eth_minus_btc_1d_return_pct`
- `eth_outperformed_btc`

### Rolling/persistence fields
- `btc_close_gt_61900_streak`
- `btc_close_gt_63300_streak`
- `ethbtc_close_gt_0275_streak`
- `ethbtc_close_gt_0300_streak`
- `btc_down_close_streak`
- `btc_up_close_streak`

### Multi-day outcome windows
Forward-looking outcome columns are included for supervised backtests. These columns must never be used in live decision logic without shifting.

- `btc_fwd_1d_return_pct`
- `btc_fwd_3d_return_pct`
- `btc_fwd_5d_return_pct`
- `btc_fwd_7d_return_pct`
- `btc_fwd_14d_return_pct`
- `btc_fwd_30d_return_pct`
- `btc_fwd_3d_max_high_pct`
- `btc_fwd_3d_max_drawdown_pct`
- `btc_fwd_7d_max_high_pct`
- `btc_fwd_7d_max_drawdown_pct`
- `btc_fwd_14d_max_high_pct`
- `btc_fwd_14d_max_drawdown_pct`
- `btc_fwd_30d_max_high_pct`
- `btc_fwd_30d_max_drawdown_pct`

## Governance

This dataset is DATA_ONLY.

It must not itself decide:
- recovery
- rotation
- rebuy
- deployment
- official row
- portfolio action

Framework interpretation remains external to DATA PING.

## How to run

```bash
python DATA_PING_BACKTEST_PRICE_RANGE_EXTRACTOR_v1.py
```

Dependencies:
```bash
pip install pandas requests
```

Optional:
```bash
pip install pyarrow
```

## Notes

If Binance is unavailable in your environment:
- retry later
- try a VPN/location where Binance public API works
- or adapt the script to a free alternative OHLC source
- mark any non-Binance source clearly as fallback

Never mix Binance CEST-like close ledger with UTC fallback candles without marking `time_basis`.
