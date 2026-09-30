# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1367
- First date: 2023-01-01
- Last date: 2026-09-29
- Required latest complete date: 2026-09-29
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `cd62e73664f7c763a1ecf8c2b5042b2f9ca7613cc708340e990c596c81b318e0`
- Normalized CSV SHA-256: `701c9de29bf35b4ab3e7afd531f3bb7af0cbecf07b66f07e91da8aea43c1a793`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-07: 48.1895
- 2024-01-10: 52.9863
- 2024-05-13: 53.4662
- 2024-09-14: 56.5869
- 2025-01-16: 56.3235
- 2025-05-20: 62.9163
- 2025-09-21: 57.0694
- 2026-01-24: 59.2154
- 2026-05-28: 59.7148
- 2026-09-29: 58.5627

## Latest three complete dates

- 2026-09-27: 58.603
- 2026-09-28: 58.5443
- 2026-09-29: 58.5627

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
