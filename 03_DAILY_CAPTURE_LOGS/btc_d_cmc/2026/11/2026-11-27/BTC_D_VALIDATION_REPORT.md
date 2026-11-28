# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1425
- First date: 2023-01-01
- Last date: 2026-11-26
- Required latest complete date: 2026-11-26
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `7540184cf1a8e9fe52e8e3285a41fc74f6ebeb5c49570b430d23a6b965d2d56b`
- Normalized CSV SHA-256: `3b8ee0c8e3f7dfd5ce5d248f3dd4a35700fe80823d999e7a77e7d04c9a063954`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-18: 49.0559
- 2024-01-25: 50.3104
- 2024-06-03: 52.8211
- 2024-10-10: 56.6185
- 2025-02-17: 59.7272
- 2025-06-26: 64.9175
- 2025-11-03: 59.2448
- 2026-03-12: 58.7023
- 2026-07-20: 58.6991
- 2026-11-26: 58.665

## Latest three complete dates

- 2026-11-24: 58.8459
- 2026-11-25: 58.6146
- 2026-11-26: 58.665

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
