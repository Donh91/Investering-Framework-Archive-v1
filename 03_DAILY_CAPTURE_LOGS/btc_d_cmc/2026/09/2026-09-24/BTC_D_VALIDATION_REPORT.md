# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1361
- First date: 2023-01-01
- Last date: 2026-09-23
- Required latest complete date: 2026-09-23
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `dd31850f85e1071afea3dd5891934f70eefc9f73138f6667cba5d69313b6624a`
- Normalized CSV SHA-256: `ffbc61c0ce684cc0a871e5b1a570ea68bc8c42bf0e78348552e65e8dfb3e4cc7`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-06: 48.231
- 2024-01-08: 52.6463
- 2024-05-11: 53.2022
- 2024-09-11: 56.0596
- 2025-01-13: 56.7167
- 2025-05-16: 62.3222
- 2025-09-17: 57.5188
- 2026-01-19: 58.9582
- 2026-05-22: 59.9798
- 2026-09-23: 58.9871

## Latest three complete dates

- 2026-09-21: 58.596
- 2026-09-22: 59.2663
- 2026-09-23: 58.9871

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
