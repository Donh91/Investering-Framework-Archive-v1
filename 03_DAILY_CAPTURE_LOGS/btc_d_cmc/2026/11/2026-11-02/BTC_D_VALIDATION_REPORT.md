# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1400
- First date: 2023-01-01
- Last date: 2026-11-01
- Required latest complete date: 2026-11-01
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `2458ace9d248988009e0751a5e8f58626fb4d5446dcaa7f59677de18f49132b9`
- Normalized CSV SHA-256: `4ba04a131f5b628445942e0132782f361ae91beb4ace1ada6fcd0d3ada936c8d`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-13: 48.9142
- 2024-01-19: 49.603
- 2024-05-25: 53.0021
- 2024-09-29: 56.3107
- 2025-02-03: 59.7831
- 2025-06-10: 63.7291
- 2025-10-15: 58.5948
- 2026-02-20: 58.2124
- 2026-06-27: 58.0008
- 2026-11-01: 59.8406

## Latest three complete dates

- 2026-10-30: 60.0041
- 2026-10-31: 59.7013
- 2026-11-01: 59.8406

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
