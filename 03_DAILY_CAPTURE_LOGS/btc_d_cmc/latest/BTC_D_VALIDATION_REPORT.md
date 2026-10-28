# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1395
- First date: 2023-01-01
- Last date: 2026-10-27
- Required latest complete date: 2026-10-27
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `de394a0812d6b8e4259b856382888d635912c0026a514568a66bfaa773506dab`
- Normalized CSV SHA-256: `2d236c07c0761c35cc97c67a5daaa5760df041e30f4e47b6ab93905046b7e709`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-12: 48.6729
- 2024-01-17: 49.7445
- 2024-05-23: 52.9744
- 2024-09-27: 56.3878
- 2025-01-31: 58.1759
- 2025-06-07: 63.825
- 2025-10-12: 59.8352
- 2026-02-16: 58.4728
- 2026-06-22: 58.3109
- 2026-10-27: 60.0301

## Latest three complete dates

- 2026-10-25: 60.1089
- 2026-10-26: 60.0359
- 2026-10-27: 60.0301

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
