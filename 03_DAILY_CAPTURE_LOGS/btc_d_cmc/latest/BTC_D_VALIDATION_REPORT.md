# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1415
- First date: 2023-01-01
- Last date: 2026-11-16
- Required latest complete date: 2026-11-16
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `e935b0068037aa9f87d432b406c96473e2cf8c2a0259eac5fd4cdc8a6abd9fb1`
- Normalized CSV SHA-256: `cb3287440f5bcdb1a7b0f3633d4df99543aaeeebfa9030cba8644c769823aa7f`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-16: 48.9193
- 2024-01-23: 49.78
- 2024-05-30: 52.684
- 2024-10-06: 56.8935
- 2025-02-11: 60.593
- 2025-06-20: 63.9933
- 2025-10-26: 59.086
- 2026-03-04: 58.5303
- 2026-07-10: 58.4364
- 2026-11-16: 59.4138

## Latest three complete dates

- 2026-11-14: 59.6146
- 2026-11-15: 59.5988
- 2026-11-16: 59.4138

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
