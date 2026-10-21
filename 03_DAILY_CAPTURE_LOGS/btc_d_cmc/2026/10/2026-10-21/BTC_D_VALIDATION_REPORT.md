# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1388
- First date: 2023-01-01
- Last date: 2026-10-20
- Required latest complete date: 2026-10-20
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `66f655d21367f53766f4273111ca1c329599dcdff558c3a27c1ba3565a0c419a`
- Normalized CSV SHA-256: `176dcc02f13e637135f670f9f791c8998602c091ac41f2a795bb48b5bd77af95`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-11: 48.5997
- 2024-01-15: 49.7217
- 2024-05-20: 54.5158
- 2024-09-23: 56.7862
- 2025-01-28: 57.9842
- 2025-06-03: 63.3375
- 2025-10-07: 58.1387
- 2026-02-10: 58.6644
- 2026-06-16: 58.5397
- 2026-10-20: 60.1165

## Latest three complete dates

- 2026-10-18: 60.08
- 2026-10-19: 60.1977
- 2026-10-20: 60.1165

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
