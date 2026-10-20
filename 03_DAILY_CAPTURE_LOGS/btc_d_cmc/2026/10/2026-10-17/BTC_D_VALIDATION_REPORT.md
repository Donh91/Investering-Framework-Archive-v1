# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1384
- First date: 2023-01-01
- Last date: 2026-10-16
- Required latest complete date: 2026-10-16
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `9865334cf93f1ca9e28af5e77069797c646157d96aef33e68bbec77dd3d2c4b3`
- Normalized CSV SHA-256: `9e9fccc5fa9e917fb1748da93f28c2de152c7ae6ec66e4292651becdf5068bc0`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-10: 48.3396
- 2024-01-14: 49.691
- 2024-05-19: 54.2811
- 2024-09-22: 56.3715
- 2025-01-25: 57.8867
- 2025-05-31: 63.4427
- 2025-10-04: 58.0396
- 2026-02-07: 58.7204
- 2026-06-12: 58.4698
- 2026-10-16: 59.8856

## Latest three complete dates

- 2026-10-14: 59.817
- 2026-10-15: 59.8558
- 2026-10-16: 59.8856

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
