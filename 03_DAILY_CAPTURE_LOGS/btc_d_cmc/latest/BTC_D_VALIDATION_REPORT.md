# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1382
- First date: 2023-01-01
- Last date: 2026-10-14
- Required latest complete date: 2026-10-14
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `ca8cd42989a53a64d82686239f86a5eca36b21015240719b5136d9bedb0adf39`
- Normalized CSV SHA-256: `6070e6fa9675bf2338fbf87879b25f6d38236b54929180cb9407d8eab879eb67`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-10: 48.3396
- 2024-01-14: 49.691
- 2024-05-18: 54.4198
- 2024-09-21: 56.7851
- 2025-01-24: 57.4712
- 2025-05-30: 62.7573
- 2025-10-02: 58.313
- 2026-02-05: 58.868
- 2026-06-10: 58.0509
- 2026-10-14: 59.817

## Latest three complete dates

- 2026-10-12: 59.4147
- 2026-10-13: 59.7264
- 2026-10-14: 59.817

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
