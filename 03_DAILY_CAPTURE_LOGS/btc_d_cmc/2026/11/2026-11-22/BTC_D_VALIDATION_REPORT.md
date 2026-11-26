# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1420
- First date: 2023-01-01
- Last date: 2026-11-21
- Required latest complete date: 2026-11-21
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `fb60bad4a9dc2f0f97544c63000f65a6e4f53e35e4be2b14280d9c258b315956`
- Normalized CSV SHA-256: `6f7bfbe7dfb67ae9263129a46338f2b09dd35b2f5c9c25ab514d6df4dbebfeaf`

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
- 2025-02-14: 59.9444
- 2025-06-23: 64.9398
- 2025-10-30: 58.8832
- 2026-03-08: 58.3604
- 2026-07-15: 58.504
- 2026-11-21: 58.5625

## Latest three complete dates

- 2026-11-19: 58.8857
- 2026-11-20: 58.6386
- 2026-11-21: 58.5625

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
