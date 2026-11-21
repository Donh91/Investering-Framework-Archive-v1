# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1417
- First date: 2023-01-01
- Last date: 2026-11-18
- Required latest complete date: 2026-11-18
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `410b1d8095071bf177d1272fbd5228f09f72cdf77d76211ace27e3188ae75b43`
- Normalized CSV SHA-256: `805403c270266d03ea9617f3642cfbf5d82f37e66dad42e73a6d7c23b9f3e5cb`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-16: 48.9193
- 2024-01-23: 49.78
- 2024-05-31: 53.0807
- 2024-10-07: 56.828
- 2025-02-12: 60.2812
- 2025-06-21: 64.3162
- 2025-10-28: 59.0789
- 2026-03-06: 58.8972
- 2026-07-12: 58.4779
- 2026-11-18: 59.1974

## Latest three complete dates

- 2026-11-16: 59.4138
- 2026-11-17: 59.4248
- 2026-11-18: 59.1974

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
