# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1330
- First date: 2023-01-01
- Last date: 2026-08-23
- Required latest complete date: 2026-08-23
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `8f1916c9aabd8292baabd6837ec7424e65c12ad1b608a06306c7a387810929d6`
- Normalized CSV SHA-256: `c606eb6f464e09f0559710ed4e5560e17ce69d0ddffa50b579dba50ccffef106`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-03: 46.9668
- 2023-09-01: 48.2708
- 2023-12-30: 49.9243
- 2024-04-29: 52.9245
- 2024-08-28: 56.309
- 2024-12-27: 57.15
- 2025-04-27: 63.3053
- 2025-08-26: 58.0185
- 2025-12-24: 59.0224
- 2026-04-24: 60.0894
- 2026-08-23: 59.2835

## Latest three complete dates

- 2026-08-21: 59.2811
- 2026-08-22: 59.4697
- 2026-08-23: 59.2835

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
