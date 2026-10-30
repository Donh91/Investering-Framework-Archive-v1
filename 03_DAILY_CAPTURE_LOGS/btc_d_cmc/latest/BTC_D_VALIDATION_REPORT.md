# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1397
- First date: 2023-01-01
- Last date: 2026-10-29
- Required latest complete date: 2026-10-29
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `ba87194a7de14933549b5996c4af930555b8894054a7219264006a034940c42e`
- Normalized CSV SHA-256: `b761e488cfbb02fa407ebbdfc906778320e10679912115a4030ec4d861d69ddd`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-13: 48.9142
- 2024-01-18: 49.7612
- 2024-05-24: 52.6568
- 2024-09-28: 56.1325
- 2025-02-01: 57.7038
- 2025-06-08: 63.7146
- 2025-10-13: 58.8017
- 2026-02-17: 58.2925
- 2026-06-24: 58.4409
- 2026-10-29: 60.1008

## Latest three complete dates

- 2026-10-27: 60.0301
- 2026-10-28: 60.0469
- 2026-10-29: 60.1008

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
