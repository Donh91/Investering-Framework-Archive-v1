# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1402
- First date: 2023-01-01
- Last date: 2026-11-03
- Required latest complete date: 2026-11-03
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `0557fd73a5280a71c7075c8bdfb15341bc8d89777a38801b30b3b1d64ca05c9b`
- Normalized CSV SHA-256: `0cf6d33863a0a08697a57db97833c9a368d0a0ada2e71df73122dff33ea4b157`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-14: 49.0705
- 2024-01-19: 49.603
- 2024-05-25: 53.0021
- 2024-09-30: 56.2292
- 2025-02-04: 60.0624
- 2025-06-12: 63.2249
- 2025-10-17: 58.8603
- 2026-02-21: 58.2733
- 2026-06-29: 58.0148
- 2026-11-03: 59.8911

## Latest three complete dates

- 2026-11-01: 59.8406
- 2026-11-02: 60.019
- 2026-11-03: 59.8911

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
