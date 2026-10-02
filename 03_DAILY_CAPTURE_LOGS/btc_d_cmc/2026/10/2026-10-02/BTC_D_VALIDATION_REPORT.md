# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1369
- First date: 2023-01-01
- Last date: 2026-10-01
- Required latest complete date: 2026-10-01
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `f46635502a2d7452bc39397e790384b069d3811f72661d850cdf2667df5b1039`
- Normalized CSV SHA-256: `8826cefde90d52beb7d2bdd0d128ffc78e0c5d71684726700e109d187107849e`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-08: 48.5181
- 2024-01-10: 52.9863
- 2024-05-13: 53.4662
- 2024-09-15: 56.5118
- 2025-01-17: 56.4343
- 2025-05-22: 63.3104
- 2025-09-23: 57.7248
- 2026-01-25: 59.1336
- 2026-05-30: 59.476
- 2026-10-01: 58.6257

## Latest three complete dates

- 2026-09-29: 58.5627
- 2026-09-30: 58.7193
- 2026-10-01: 58.6257

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
