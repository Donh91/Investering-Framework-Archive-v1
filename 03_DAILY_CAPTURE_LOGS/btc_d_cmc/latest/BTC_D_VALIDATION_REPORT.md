# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1391
- First date: 2023-01-01
- Last date: 2026-10-23
- Required latest complete date: 2026-10-23
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `a0a7253cc762cc38d99568efc99ba3fedca6ae672159eb78eb5cbfe8846608be`
- Normalized CSV SHA-256: `3eaa09943cce23957e14bb3439ab5bfefb0263380cc3a4b946b470bb14b38d4f`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-12: 48.6729
- 2024-01-16: 49.7643
- 2024-05-21: 53.8069
- 2024-09-25: 56.2591
- 2025-01-29: 58.4987
- 2025-06-05: 63.2642
- 2025-10-09: 58.2586
- 2026-02-12: 58.5552
- 2026-06-19: 58.0882
- 2026-10-23: 60.0843

## Latest three complete dates

- 2026-10-21: 60.0977
- 2026-10-22: 60.1978
- 2026-10-23: 60.0843

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
