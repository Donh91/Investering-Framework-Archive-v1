# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1365
- First date: 2023-01-01
- Last date: 2026-09-27
- Required latest complete date: 2026-09-27
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `6695454fd0addfb3b96c755a470bd0388c4fdf034979242d0937405bfa143688`
- Normalized CSV SHA-256: `566938d65697130eb10551a4220152f7cba1f9a068598be0639d1591f8e23ea7`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-07: 48.1895
- 2024-01-09: 53.2095
- 2024-05-12: 53.2143
- 2024-09-13: 56.1404
- 2025-01-15: 57.074
- 2025-05-19: 62.8405
- 2025-09-20: 57.2351
- 2026-01-22: 59.0726
- 2026-05-26: 60.0261
- 2026-09-27: 58.603

## Latest three complete dates

- 2026-09-25: 58.87
- 2026-09-26: 58.5176
- 2026-09-27: 58.603

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
