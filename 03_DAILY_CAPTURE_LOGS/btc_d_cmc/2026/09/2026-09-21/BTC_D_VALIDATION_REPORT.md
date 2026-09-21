# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1358
- First date: 2023-01-01
- Last date: 2026-09-20
- Required latest complete date: 2026-09-20
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `1e6c42fa12ab2930825ab29cf76df11a30c7dd56fe44d9c1de2cae3d065db1d9`
- Normalized CSV SHA-256: `7c426ac02a49e69ea56f16bdf874f3b48ce12e6bf42ab8d2e7f7088741ee21b1`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-06: 48.231
- 2024-01-07: 52.1815
- 2024-05-09: 53.2602
- 2024-09-10: 56.0264
- 2025-01-11: 56.8241
- 2025-05-15: 61.5572
- 2025-09-15: 57.0097
- 2026-01-16: 59.0676
- 2026-05-20: 60.2126
- 2026-09-20: 58.7637

## Latest three complete dates

- 2026-09-18: 58.5394
- 2026-09-19: 58.7544
- 2026-09-20: 58.7637

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
