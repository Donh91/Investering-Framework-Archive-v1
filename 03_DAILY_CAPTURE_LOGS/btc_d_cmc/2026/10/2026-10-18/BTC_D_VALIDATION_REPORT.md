# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1385
- First date: 2023-01-01
- Last date: 2026-10-17
- Required latest complete date: 2026-10-17
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `3de460c0a3f04cf1f3ba03e05eca74d3e5ad6d01a88979ad6b5d0830c787aba0`
- Normalized CSV SHA-256: `6e64a15e60e3a5970eb00558359626e4c4f1b869aeddb866c0aa38bf02f67bf0`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-11: 48.5997
- 2024-01-14: 49.691
- 2024-05-19: 54.2811
- 2024-09-22: 56.3715
- 2025-01-26: 57.7389
- 2025-06-01: 63.4887
- 2025-10-05: 58.4075
- 2026-02-07: 58.7204
- 2026-06-13: 58.5673
- 2026-10-17: 59.8935

## Latest three complete dates

- 2026-10-15: 59.8558
- 2026-10-16: 59.8856
- 2026-10-17: 59.8935

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
