# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1409
- First date: 2023-01-01
- Last date: 2026-11-10
- Required latest complete date: 2026-11-10
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `f959e6b43d92af132f6b94eb7d34950da742c5b73c0f7a90caeda6756ca23cf1`
- Normalized CSV SHA-256: `6d3b37fea4d9b36cf8744ec637eb8a2d0e39c98cd77a3a1c19abdc50e6ee01a5`

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
- 2025-02-08: 60.9825
- 2025-06-16: 63.8318
- 2025-10-22: 59.0672
- 2026-02-27: 57.9748
- 2026-07-05: 57.9143
- 2026-11-10: 60.401

## Latest three complete dates

- 2026-11-08: 59.9587
- 2026-11-09: 60.2959
- 2026-11-10: 60.401

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
