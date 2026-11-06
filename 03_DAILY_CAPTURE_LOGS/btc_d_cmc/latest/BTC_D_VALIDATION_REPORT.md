# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1404
- First date: 2023-01-01
- Last date: 2026-11-05
- Required latest complete date: 2026-11-05
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `fa9cef0b4e7881e68c7dc28be3cf34ed903f5c23918664aa33ac75264ee901fe`
- Normalized CSV SHA-256: `20699f43a12040f0856f8e8f2d5e6993489b8f661b10a4fa3a3aefacffd41d7b`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-14: 49.0705
- 2024-01-20: 49.7512
- 2024-05-26: 53.0431
- 2024-10-01: 56.1202
- 2025-02-05: 60.3659
- 2025-06-13: 63.4355
- 2025-10-18: 58.9681
- 2026-02-23: 58.4373
- 2026-06-30: 57.8966
- 2026-11-05: 60.1639

## Latest three complete dates

- 2026-11-03: 59.8911
- 2026-11-04: 59.917
- 2026-11-05: 60.1639

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
