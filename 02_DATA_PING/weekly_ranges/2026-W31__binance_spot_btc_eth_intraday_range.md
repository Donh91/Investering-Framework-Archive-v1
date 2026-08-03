# 2026-W31 Binance Spot BTC/ETH Intraday Range

## Scope

- Timezone: `Europe/Copenhagen`
- Local window: `2026-07-27 00:00` to `2026-08-03 00:00`
- UTC window: `2026-07-26T22:00:00Z` to `2026-08-02T22:00:00Z` exclusive
- Source: Binance Spot one-hour klines
- Method: `BINANCE_SPOT_1H_COPENHAGEN_ISO_WEEK_v1`
- Revision status: `NON_REVISING_EXCHANGE_CANDLES`

## Weekly ranges

| Instrument | Open | High | Low | Close | Weekly return | High-low range | Settled hours | Gaps | Duplicates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTCUSDT | 64,858.03 | 65,744.60 | 62,275.00 | 63,578.00 | -1.9736% | 5.5714% | 168 | 0 | 0 |
| ETHUSDT | 1,925.91 | 1,981.24 | 1,822.06 | 1,890.43 | -1.8422% | 8.7363% | 168 | 0 | 0 |

## QA

- Total settled hourly rows: 336.
- Complete seven-day window for both instruments.
- No gaps or duplicate timestamps.
- Candles beginning at `2026-08-02T22:00:00Z` were excluded because they belong to Copenhagen ISO week 32.

## Interpretation boundary

This artifact is a price-range and calibration input only. It contains no breadth, derivatives, ETF, macro or portfolio-action authority and cannot independently change framework state.
