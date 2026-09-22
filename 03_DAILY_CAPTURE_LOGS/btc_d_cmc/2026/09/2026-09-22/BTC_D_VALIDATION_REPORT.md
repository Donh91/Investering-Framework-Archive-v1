# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1359
- First date: 2023-01-01
- Last date: 2026-09-21
- Required latest complete date: 2026-09-21
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `bc128df93ec9e0fe9585c3a3e646dfd1d167d378e2d11df132823b53ccf9d24d`
- Normalized CSV SHA-256: `2cb55bf5e5eb0d1a8aefe69bf03393afb14a06bdd1673a633ff74c7869b8fb56`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-06: 48.231
- 2024-01-07: 52.1815
- 2024-05-10: 53.3589
- 2024-09-10: 56.0264
- 2025-01-12: 56.4512
- 2025-05-15: 61.5572
- 2025-09-16: 57.3892
- 2026-01-17: 59.0675
- 2026-05-21: 60.1647
- 2026-09-21: 58.596

## Latest three complete dates

- 2026-09-19: 58.7544
- 2026-09-20: 58.7637
- 2026-09-21: 58.596

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
