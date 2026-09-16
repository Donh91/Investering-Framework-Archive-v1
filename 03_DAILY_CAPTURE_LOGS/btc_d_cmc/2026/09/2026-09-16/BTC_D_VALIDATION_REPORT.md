# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1353
- First date: 2023-01-01
- Last date: 2026-09-15
- Required latest complete date: 2026-09-15
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `2eca633b5a9df248f4d39a5cab58612034dbbf11021c94e71d9fcc5fb49e6c4b`
- Normalized CSV SHA-256: `8a3cad0847e13212b9bdf92f06a3c310ce7d3628464e1f914e7230237503e589`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-05: 48.2974
- 2024-01-06: 51.7916
- 2024-05-08: 53.4683
- 2024-09-08: 55.7568
- 2025-01-08: 56.7933
- 2025-05-11: 61.7123
- 2025-09-11: 57.5844
- 2026-01-12: 58.4756
- 2026-05-15: 60.2425
- 2026-09-15: 58.9546

## Latest three complete dates

- 2026-09-13: 58.718
- 2026-09-14: 58.906
- 2026-09-15: 58.9546

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
