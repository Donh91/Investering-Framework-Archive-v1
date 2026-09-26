# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1363
- First date: 2023-01-01
- Last date: 2026-09-25
- Required latest complete date: 2026-09-25
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `a34eb1f3f566a2484abed529b959d84f365a35cc4da7e74ca6758070ae5f23b3`
- Normalized CSV SHA-256: `6057dbd1381f50f81619271c61546dfca43feae141042b4635beb0c3c1f1bc7c`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-07: 48.1895
- 2024-01-08: 52.6463
- 2024-05-11: 53.2022
- 2024-09-12: 56.1928
- 2025-01-14: 57.252
- 2025-05-18: 62.6841
- 2025-09-19: 56.9472
- 2026-01-20: 59.0704
- 2026-05-24: 59.9206
- 2026-09-25: 58.87

## Latest three complete dates

- 2026-09-23: 58.9871
- 2026-09-24: 59.172
- 2026-09-25: 58.87

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
