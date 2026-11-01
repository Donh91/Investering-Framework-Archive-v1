# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1399
- First date: 2023-01-01
- Last date: 2026-10-31
- Required latest complete date: 2026-10-31
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `c5b4fa9847e11debff12f8f7980acf9115d56d78a7af7c2361374c0574754d90`
- Normalized CSV SHA-256: `d9734e79e9073caade4e9004fd7fe4e34bb39055bc3e6b26d69c47c4b1356744`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-13: 48.9142
- 2024-01-18: 49.7612
- 2024-05-24: 52.6568
- 2024-09-28: 56.1325
- 2025-02-03: 59.7831
- 2025-06-10: 63.7291
- 2025-10-15: 58.5948
- 2026-02-19: 57.9903
- 2026-06-26: 58.0728
- 2026-10-31: 59.7013

## Latest three complete dates

- 2026-10-29: 60.1008
- 2026-10-30: 60.0041
- 2026-10-31: 59.7013

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
