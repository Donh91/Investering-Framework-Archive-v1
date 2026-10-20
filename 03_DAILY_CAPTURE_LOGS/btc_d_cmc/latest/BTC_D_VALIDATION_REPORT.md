# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1387
- First date: 2023-01-01
- Last date: 2026-10-19
- Required latest complete date: 2026-10-19
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `46389d47fe2c43313b1caca1aead7ab0baa03cf852d2ca768514fec21c20e99e`
- Normalized CSV SHA-256: `360c966d30257772a214e1000ba55dd4097d9529cb0e1e0bdb85951468ae138e`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-11: 48.5997
- 2024-01-15: 49.7217
- 2024-05-20: 54.5158
- 2024-09-23: 56.7862
- 2025-01-27: 57.9022
- 2025-06-02: 63.5764
- 2025-10-06: 58.5459
- 2026-02-09: 58.7483
- 2026-06-15: 58.7646
- 2026-10-19: 60.1977

## Latest three complete dates

- 2026-10-17: 59.8935
- 2026-10-18: 60.08
- 2026-10-19: 60.1977

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
