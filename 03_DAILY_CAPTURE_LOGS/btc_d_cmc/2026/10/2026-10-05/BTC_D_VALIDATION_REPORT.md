# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1372
- First date: 2023-01-01
- Last date: 2026-10-04
- Required latest complete date: 2026-10-04
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `e0b4da1a657648f28568f02b610c7045b06b1d28e0e19e5a2e86d931221452f5`
- Normalized CSV SHA-256: `472e718f8279100afad3d2f624b6c00880e604e914e3b0f90b3088b3c7b09c25`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-08: 48.5181
- 2024-01-11: 51.664
- 2024-05-15: 54.0329
- 2024-09-16: 56.8071
- 2025-01-19: 56.8622
- 2025-05-23: 63.0212
- 2025-09-25: 57.8942
- 2026-01-28: 58.9068
- 2026-06-01: 59.2305
- 2026-10-04: 58.9048

## Latest three complete dates

- 2026-10-02: 58.9816
- 2026-10-03: 59.0606
- 2026-10-04: 58.9048

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
