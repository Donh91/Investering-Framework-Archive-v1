# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1348
- First date: 2023-01-01
- Last date: 2026-09-10
- Required latest complete date: 2026-09-10
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `c53670c06c92f45ea7dd9bc59140a6b7bac71b5347076568578d89a86189288a`
- Normalized CSV SHA-256: `5cda6c9343bd0d53b6f9c9611b2d0f4c174b77aa7e64a9f95ee99b62e68cc7e1`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-04: 48.4188
- 2024-01-04: 51.2703
- 2024-05-06: 53.3944
- 2024-09-05: 56.4743
- 2025-01-06: 55.6628
- 2025-05-08: 64.383
- 2025-09-08: 57.7037
- 2026-01-08: 58.3237
- 2026-05-11: 60.1625
- 2026-09-10: 59.0414

## Latest three complete dates

- 2026-09-08: 59.0344
- 2026-09-09: 58.7704
- 2026-09-10: 59.0414

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
