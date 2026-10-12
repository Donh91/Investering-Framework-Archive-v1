# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1379
- First date: 2023-01-01
- Last date: 2026-10-11
- Required latest complete date: 2026-10-11
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `ef5ff10f358c1408627881d26d7755b493f7bbc7e6f65e4f53f9d7e00a5c6322`
- Normalized CSV SHA-256: `c87e1c00bd0d7eeed993e70f425b040ae5d1d68a3273f6add8fcf162de5561a5`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-10: 48.3396
- 2024-01-13: 50.1176
- 2024-05-17: 54.5516
- 2024-09-19: 57.3762
- 2025-01-23: 57.4414
- 2025-05-28: 62.929
- 2025-09-30: 58.0413
- 2026-02-02: 59.353
- 2026-06-08: 58.2393
- 2026-10-11: 59.4468

## Latest three complete dates

- 2026-10-09: 59.4709
- 2026-10-10: 59.5382
- 2026-10-11: 59.4468

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
