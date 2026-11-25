# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1423
- First date: 2023-01-01
- Last date: 2026-11-24
- Required latest complete date: 2026-11-24
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `bf9de5f27c889f81c56f1f8f3281cf3b7bcfeb7ede22338a5dfb5d82eca4b73b`
- Normalized CSV SHA-256: `7cdd8b86f1a078dcca40ebf01d405befb89ea70ca665c3a270c516b4ebf48ac0`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-18: 49.0559
- 2024-01-25: 50.3104
- 2024-06-02: 52.6545
- 2024-10-09: 56.7049
- 2025-02-16: 59.8564
- 2025-06-25: 64.4476
- 2025-11-01: 59.2483
- 2026-03-10: 58.544
- 2026-07-18: 58.516
- 2026-11-24: 58.8459

## Latest three complete dates

- 2026-11-22: 58.7187
- 2026-11-23: 58.8948
- 2026-11-24: 58.8459

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
