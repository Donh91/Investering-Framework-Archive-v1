# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1336
- First date: 2023-01-01
- Last date: 2026-08-29
- Required latest complete date: 2026-08-29
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `c6d9c38cd23fb52d71e9db5e8f9088b5b003b9189721e6c9ba711dac984e8976`
- Normalized CSV SHA-256: `0302e7c7d10e99ffdafe597cdb6c378c3e41a1fe50326b957235efd619e25fbf`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-03: 46.9668
- 2023-09-02: 48.3273
- 2024-01-01: 50.2434
- 2024-05-01: 53.4133
- 2024-08-31: 56.1117
- 2024-12-30: 56.6932
- 2025-05-01: 63.5229
- 2025-08-30: 57.3532
- 2025-12-29: 58.9301
- 2026-04-30: 59.8359
- 2026-08-29: 59.561

## Latest three complete dates

- 2026-08-27: 59.5586
- 2026-08-28: 59.7101
- 2026-08-29: 59.561

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
