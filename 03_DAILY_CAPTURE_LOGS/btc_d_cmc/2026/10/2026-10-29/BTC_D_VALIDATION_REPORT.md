# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1396
- First date: 2023-01-01
- Last date: 2026-10-28
- Required latest complete date: 2026-10-28
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `212baa88a19bb7458d413a55bd5b7863f64dab22e9d3082b8d7787ba7ef4df0b`
- Normalized CSV SHA-256: `34ddd9d8ff7b5570a8673a46068e2684bc4630fb6b60fc8e8a0768187145cf9b`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-13: 48.9142
- 2024-01-17: 49.7445
- 2024-05-23: 52.9744
- 2024-09-27: 56.3878
- 2025-02-01: 57.7038
- 2025-06-08: 63.7146
- 2025-10-13: 58.8017
- 2026-02-16: 58.4728
- 2026-06-23: 58.5006
- 2026-10-28: 60.0469

## Latest three complete dates

- 2026-10-26: 60.0359
- 2026-10-27: 60.0301
- 2026-10-28: 60.0469

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
