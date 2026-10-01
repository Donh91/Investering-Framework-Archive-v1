# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1368
- First date: 2023-01-01
- Last date: 2026-09-30
- Required latest complete date: 2026-09-30
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `874e8c6e56f17304b8267f28e55cd1647280045b05047fae193d22a684f13fad`
- Normalized CSV SHA-256: `2f7507101d4d74c986ea82fdd4d7f64f2efb57fcc6fb068c2b22a04710365f95`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-08: 48.5181
- 2024-01-10: 52.9863
- 2024-05-13: 53.4662
- 2024-09-14: 56.5869
- 2025-01-17: 56.4343
- 2025-05-21: 63.1336
- 2025-09-22: 57.1508
- 2026-01-24: 59.2154
- 2026-05-29: 59.6052
- 2026-09-30: 58.7193

## Latest three complete dates

- 2026-09-28: 58.5443
- 2026-09-29: 58.5627
- 2026-09-30: 58.7193

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
