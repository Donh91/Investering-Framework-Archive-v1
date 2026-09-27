# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1364
- First date: 2023-01-01
- Last date: 2026-09-26
- Required latest complete date: 2026-09-26
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `ea18c84fd6c09333dbd100c24d61b8604c14a011a6bce678259ba0cbfe23e1d3`
- Normalized CSV SHA-256: `cafc610556c44e1a0181bd59137787beba197b9e112780ee17ae2d699d9eead1`

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
- 2025-01-14: 57.252
- 2025-05-18: 62.6841
- 2025-09-19: 56.9472
- 2026-01-21: 59.1367
- 2026-05-25: 60.0834
- 2026-09-26: 58.5176

## Latest three complete dates

- 2026-09-24: 59.172
- 2026-09-25: 58.87
- 2026-09-26: 58.5176

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
