# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1383
- First date: 2023-01-01
- Last date: 2026-10-15
- Required latest complete date: 2026-10-15
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `3fcc1e5c4dfe4a1e7de035dd71a391f59fbe7310adf1e1be930f76e31289e5a9`
- Normalized CSV SHA-256: `bbbefba9bf323e312088183053ed6d010aed968bc0e4d3c61cf756090dd49d2b`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-10: 48.3396
- 2024-01-14: 49.691
- 2024-05-19: 54.2811
- 2024-09-21: 56.7851
- 2025-01-25: 57.8867
- 2025-05-30: 62.7573
- 2025-10-03: 57.9579
- 2026-02-06: 57.9165
- 2026-06-11: 58.2979
- 2026-10-15: 59.8558

## Latest three complete dates

- 2026-10-13: 59.7264
- 2026-10-14: 59.817
- 2026-10-15: 59.8558

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
