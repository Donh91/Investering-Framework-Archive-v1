# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1418
- First date: 2023-01-01
- Last date: 2026-11-19
- Required latest complete date: 2026-11-19
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `00bba483923bff28991c5d1615d289dcf0d7ef608ab49217998e30e9c2e72940`
- Normalized CSV SHA-256: `47b32b71594b1f28191bf1c50cb8cf6638198de5a13e48296bfe088effb97b6d`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-17: 48.8503
- 2024-01-23: 49.78
- 2024-05-31: 53.0807
- 2024-10-07: 56.828
- 2025-02-13: 59.9812
- 2025-06-22: 64.7368
- 2025-10-29: 59.3306
- 2026-03-06: 58.8972
- 2026-07-13: 58.4112
- 2026-11-19: 58.8857

## Latest three complete dates

- 2026-11-17: 59.4248
- 2026-11-18: 59.1974
- 2026-11-19: 58.8857

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
