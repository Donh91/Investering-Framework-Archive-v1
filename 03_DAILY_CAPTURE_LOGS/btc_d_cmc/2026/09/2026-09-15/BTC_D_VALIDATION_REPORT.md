# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1352
- First date: 2023-01-01
- Last date: 2026-09-14
- Required latest complete date: 2026-09-14
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `36ae2c60b143d2af53144ffb4e932255dcabc819c27f246d66f3ae290211c912`
- Normalized CSV SHA-256: `fa962a23be9cfd4434a20189ad635adf9608b829234518695b58eea6ab07d1ce`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-05: 48.2974
- 2024-01-05: 51.4041
- 2024-05-07: 53.3457
- 2024-09-07: 56.0539
- 2025-01-08: 56.7933
- 2025-05-11: 61.7123
- 2025-09-11: 57.5844
- 2026-01-11: 58.4788
- 2026-05-14: 59.998
- 2026-09-14: 58.906

## Latest three complete dates

- 2026-09-12: 58.727
- 2026-09-13: 58.718
- 2026-09-14: 58.906

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
