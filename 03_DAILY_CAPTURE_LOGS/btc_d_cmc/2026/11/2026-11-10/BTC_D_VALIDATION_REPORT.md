# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1408
- First date: 2023-01-01
- Last date: 2026-11-09
- Required latest complete date: 2026-11-09
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `21f6235d1d4d552ed62e5deca63db0032eced33c7dda5b1c6338fa21edc76584`
- Normalized CSV SHA-256: `7714809e4b90eae98e34dfbe4526403246d4659ddc9697a579f79ec819cd818a`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-15: 49.1329
- 2024-01-21: 49.7462
- 2024-05-28: 52.6364
- 2024-10-03: 56.7689
- 2025-02-07: 60.9692
- 2025-06-15: 64.0106
- 2025-10-21: 58.9732
- 2026-02-26: 57.9181
- 2026-07-04: 57.8341
- 2026-11-09: 60.2959

## Latest three complete dates

- 2026-11-07: 59.8744
- 2026-11-08: 59.9587
- 2026-11-09: 60.2959

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
