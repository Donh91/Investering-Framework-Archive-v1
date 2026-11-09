# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1407
- First date: 2023-01-01
- Last date: 2026-11-08
- Required latest complete date: 2026-11-08
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `84e7bedfaf9d98cae7b6fe1e8f0c14e11ad35d5b37ed640ceec84dba10d18741`
- Normalized CSV SHA-256: `ffcf8607dfa1cede0fec21412e7e453cad8d2e0de61988461749d621f0121f8a`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-15: 49.1329
- 2024-01-20: 49.7512
- 2024-05-27: 52.7643
- 2024-10-02: 56.2534
- 2025-02-07: 60.9692
- 2025-06-15: 64.0106
- 2025-10-21: 58.9732
- 2026-02-25: 57.8675
- 2026-07-03: 57.9463
- 2026-11-08: 59.9587

## Latest three complete dates

- 2026-11-06: 59.9948
- 2026-11-07: 59.8744
- 2026-11-08: 59.9587

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
