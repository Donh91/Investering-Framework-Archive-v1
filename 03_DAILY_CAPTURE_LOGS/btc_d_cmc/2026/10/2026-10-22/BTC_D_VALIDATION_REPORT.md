# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1389
- First date: 2023-01-01
- Last date: 2026-10-21
- Required latest complete date: 2026-10-21
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `008cd0d2d88ba3b39e05fe9d57f139b4e4bf320afeaabd07447688ab9db04c2f`
- Normalized CSV SHA-256: `08e3d902900bd476ee315f918cbdc3629ce269827c4c9a73447927fc2c1ade78`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-11: 48.5997
- 2024-01-16: 49.7643
- 2024-05-21: 53.8069
- 2024-09-24: 56.2265
- 2025-01-28: 57.9842
- 2025-06-03: 63.3375
- 2025-10-07: 58.1387
- 2026-02-11: 58.7084
- 2026-06-17: 58.4218
- 2026-10-21: 60.0977

## Latest three complete dates

- 2026-10-19: 60.1977
- 2026-10-20: 60.1165
- 2026-10-21: 60.0977

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
