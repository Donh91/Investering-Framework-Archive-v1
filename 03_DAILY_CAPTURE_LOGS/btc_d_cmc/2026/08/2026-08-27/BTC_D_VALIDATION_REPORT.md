# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1333
- First date: 2023-01-01
- Last date: 2026-08-26
- Required latest complete date: 2026-08-26
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `6cd65b3ad09b4c682ee5ffa0eb29c0f1fdf784da8207e5616647ecf6b3a94f48`
- Normalized CSV SHA-256: `4e3c464e39380531e50a6c94b95caef054868b7cee7f7dfc3d01c3de84a29873`

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
- 2024-12-29: 56.4627
- 2025-04-29: 63.4169
- 2025-08-28: 57.5426
- 2025-12-27: 59.1404
- 2026-04-27: 60.0425
- 2026-08-26: 59.8131

## Latest three complete dates

- 2026-08-24: 59.1695
- 2026-08-25: 59.5987
- 2026-08-26: 59.8131

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
