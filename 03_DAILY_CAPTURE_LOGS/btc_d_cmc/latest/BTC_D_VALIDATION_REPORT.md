# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1424
- First date: 2023-01-01
- Last date: 2026-11-25
- Required latest complete date: 2026-11-25
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `9780ccd4deec2f67223353378972542cdb59b746d43e464de25585f71b0f3683`
- Normalized CSV SHA-256: `1fbef53da6eb50fbeaec487277763f83fd13a70ebcfb344a6fee207ce2a2d0da`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-18: 49.0559
- 2024-01-25: 50.3104
- 2024-06-02: 52.6545
- 2024-10-10: 56.6185
- 2025-02-16: 59.8564
- 2025-06-26: 64.9175
- 2025-11-02: 59.2036
- 2026-03-11: 58.776
- 2026-07-19: 58.7837
- 2026-11-25: 58.6146

## Latest three complete dates

- 2026-11-23: 58.8948
- 2026-11-24: 58.8459
- 2026-11-25: 58.6146

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
