# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1332
- First date: 2023-01-01
- Last date: 2026-08-25
- Required latest complete date: 2026-08-25
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `4ccce3d00cff1425b0fefa43636bd8e0966d81d19ddb6c807cf9da2bb9b869b1`
- Normalized CSV SHA-256: `f664c362aa5052bc61d78d47a3182a3d3c5ee005e4b41706fb35cc020ca8b850`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-03: 46.9668
- 2023-09-01: 48.2708
- 2023-12-31: 50.0225
- 2024-04-30: 53.424
- 2024-08-29: 55.9813
- 2024-12-28: 56.7789
- 2025-04-28: 63.3001
- 2025-08-27: 57.4464
- 2025-12-26: 59.3462
- 2026-04-26: 59.9978
- 2026-08-25: 59.5987

## Latest three complete dates

- 2026-08-23: 59.2835
- 2026-08-24: 59.1695
- 2026-08-25: 59.5987

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
