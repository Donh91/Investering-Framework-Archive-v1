# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1343
- First date: 2023-01-01
- Last date: 2026-09-05
- Required latest complete date: 2026-09-05
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `b285f9ea3d03c04e10293cae3570280f8a38bde3916fc892c5cdb6249eea9524`
- Normalized CSV SHA-256: `c0b9d966a21779338ecf48913a9fbc8c311de7906f0e414622a350cba4cc6cd8`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-03: 48.3222
- 2024-01-03: 51.142
- 2024-05-04: 53.2774
- 2024-09-03: 56.2907
- 2025-01-03: 56.3374
- 2025-05-05: 63.8009
- 2025-09-04: 57.6162
- 2026-01-04: 58.5689
- 2026-05-06: 60.5409
- 2026-09-05: 59.6421

## Latest three complete dates

- 2026-09-03: 59.5756
- 2026-09-04: 59.8634
- 2026-09-05: 59.6421

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
