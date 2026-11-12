# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1410
- First date: 2023-01-01
- Last date: 2026-11-11
- Required latest complete date: 2026-11-11
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `dec0e48eee227aa1c7b1d89ffba07329447206d5d8926f65e8ab55eb8532356b`
- Normalized CSV SHA-256: `b2d6c5c80248210dc91672c1c07d7a3300067a5c71a8e975e07d558eca80901a`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-15: 49.1329
- 2024-01-21: 49.7462
- 2024-05-28: 52.6364
- 2024-10-03: 56.7689
- 2025-02-09: 60.5815
- 2025-06-17: 64.0365
- 2025-10-23: 59.2247
- 2026-02-28: 57.9767
- 2026-07-06: 58.0507
- 2026-11-11: 60.4749

## Latest three complete dates

- 2026-11-09: 60.2959
- 2026-11-10: 60.401
- 2026-11-11: 60.4749

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
