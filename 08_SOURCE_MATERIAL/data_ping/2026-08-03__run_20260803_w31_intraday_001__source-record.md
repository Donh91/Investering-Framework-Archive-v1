# DATA PING Source Record

## Identity

- run_id: `run_20260803_w31_intraday_001`
- snapshot_id: `snap_20260803_w31_intraday_001`
- snapshot_utc: `2026-08-03T04:49:59.958Z`
- contract: `DATA_PING_RUN_FIRST_STATELESS_v1`
- version: `15.1.1`
- runtime: `DATA_PING_LONGITUDINAL_COLLECTOR_v1`
- collector status: `PARTIAL`
- supplemental request: `BINANCE_SPOT_INTRADAY_BTC_ETH_ISO_WEEK_31_2026`

## Execution coverage

- planned core actions: 60
- attempted core actions: 10
- passed core actions: 10
- skipped due to runtime limit: 50
- optional attempted: 0 of 1
- full sensor coverage: false
- freeze count: 1
- post-freeze calls: 0

This run is a runtime-limited supplemental capture. It is not a complete DATA PING and cannot replace the latest decision-bearing bounded observation.

## Current direct spot observations

```yaml
BTCUSDT_last: 62932.01
BTCUSDT_24h_pct: -0.941
ETHUSDT_last: 1860.41
ETHUSDT_24h_pct: -0.960
ETHBTC_last: 0.02957
ETHBTC_24h_pct: 0.0
coingecko_total_market_cap_usd: 2244608763124.3364
coingecko_total_volume_usd: 38524407358.72457
coingecko_market_cap_change_24h_pct: -0.7796
coingecko_volume_change_24h_pct: 3.0005
BTC_dominance_pct: 56.2280
ETH_dominance_pct: 9.9958
```

## ISO week 31 settled intraday capture

Window: `2026-07-27T00:00:00+02:00` through `2026-08-03T00:00:00+02:00`, Europe/Copenhagen.

```yaml
BTCUSDT:
  settled_1h_rows: 168
  open: 64858.03
  high: 65744.60
  low: 62275.00
  close: 63578.00
  return_pct: -1.9736
  high_low_range_pct: 5.5714
  gaps: 0
  duplicates: 0
ETHUSDT:
  settled_1h_rows: 168
  open: 1925.91
  high: 1981.24
  low: 1822.06
  close: 1890.43
  return_pct: -1.8422
  high_low_range_pct: 8.7363
  gaps: 0
  duplicates: 0
```

Source: Binance Spot `GET /api/v3/klines`, one-hour non-revising exchange candles. Total settled rows: 336. Two rows beginning at `2026-08-02T22:00:00Z` were correctly excluded as outside Copenhagen ISO week 31.

## Missing decision sensors

Breadth source pages were retrieved, but filtering and aggregation did not complete before freeze. Derivatives, funding, open interest, taker ratios, OKX cross-check, macro, ETF, CFGI, stablecoins, chain TVL and DEX sensors were not collected because the runtime budget was exhausted.
