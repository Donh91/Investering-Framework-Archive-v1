# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1419
- First date: 2023-01-01
- Last date: 2026-11-20
- Required latest complete date: 2026-11-20
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `1f1ae049f3ece1b7fa3e9f0097add01ce418efff4e094aa9327a85284f90e075`
- Normalized CSV SHA-256: `da59233c6b1454894829084e1de830801351c59f09de559a9064d684e8d0ae04`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-17: 48.8503
- 2024-01-24: 50.3555
- 2024-06-01: 52.7744
- 2024-10-08: 56.7962
- 2025-02-13: 59.9812
- 2025-06-22: 64.7368
- 2025-10-29: 59.3306
- 2026-03-07: 58.5263
- 2026-07-14: 58.1836
- 2026-11-20: 58.6386

## Latest three complete dates

- 2026-11-18: 59.1974
- 2026-11-19: 58.8857
- 2026-11-20: 58.6386

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
