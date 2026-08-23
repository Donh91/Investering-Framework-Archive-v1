# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1329
- First date: 2023-01-01
- Last date: 2026-08-22
- Required latest complete date: 2026-08-22
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `87acc39c8099f69163f7d0b0b49506d87dcedff659cf18da135458584fddf9ac`
- Normalized CSV SHA-256: `c4830e435aab2b7067e8b5e95f9f5eb9d6552e3089d28f5b8b3fedec136451de`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-03: 46.9668
- 2023-08-31: 48.9094
- 2023-12-30: 49.9243
- 2024-04-29: 52.9245
- 2024-08-28: 56.309
- 2024-12-26: 57.0358
- 2025-04-26: 63.539
- 2025-08-25: 57.1651
- 2025-12-24: 59.0224
- 2026-04-23: 59.9697
- 2026-08-22: 59.4697

## Latest three complete dates

- 2026-08-20: 58.8085
- 2026-08-21: 59.2811
- 2026-08-22: 59.4697

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
