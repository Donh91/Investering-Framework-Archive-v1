# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1405
- First date: 2023-01-01
- Last date: 2026-11-06
- Required latest complete date: 2026-11-06
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `e88aeb43c6bba3a4540874537588bdd1c0d90e1710c3de322b2181f59acfa154`
- Normalized CSV SHA-256: `d7d1f2c35bf4c4959e050668ee7d9862fde21e00b3f726506d0dc9d122cba0fc`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-14: 49.0705
- 2024-01-20: 49.7512
- 2024-05-27: 52.7643
- 2024-10-01: 56.1202
- 2025-02-06: 60.3696
- 2025-06-13: 63.4355
- 2025-10-19: 58.7614
- 2026-02-24: 58.0576
- 2026-07-01: 57.6599
- 2026-11-06: 59.9948

## Latest three complete dates

- 2026-11-04: 59.917
- 2026-11-05: 60.1639
- 2026-11-06: 59.9948

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
