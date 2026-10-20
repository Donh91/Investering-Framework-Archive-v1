# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1375
- First date: 2023-01-01
- Last date: 2026-10-07
- Required latest complete date: 2026-10-07
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `b3423d474b5d7daaa7004cb1f4726f3d43ff64bd2f91c933d9aa47a9cf464d61`
- Normalized CSV SHA-256: `7ce4c39efec02e626a090793318c8e3bc13f652406a033ceeb61b777a0d0487f`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-09: 48.3306
- 2024-01-12: 51.2
- 2024-05-16: 54.5738
- 2024-09-18: 57.1998
- 2025-01-20: 57.3799
- 2025-05-25: 63.1047
- 2025-09-27: 57.754
- 2026-01-30: 58.7564
- 2026-06-04: 57.3313
- 2026-10-07: 59.0147

## Latest three complete dates

- 2026-10-05: 59.1546
- 2026-10-06: 58.9546
- 2026-10-07: 59.0147

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
