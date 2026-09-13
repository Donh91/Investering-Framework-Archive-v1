# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1346
- First date: 2023-01-01
- Last date: 2026-09-08
- Required latest complete date: 2026-09-08
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `63c77a74e37dfbea8e244a878957ccb8a640b3fd39557a1731d6143e8dbf035f`
- Normalized CSV SHA-256: `f1cd6cd36d567c481ce047c8db043a693ea3f1f13b4068d45bf5c0954e148065`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-04: 48.4188
- 2024-01-04: 51.2703
- 2024-05-05: 53.5227
- 2024-09-04: 56.4435
- 2025-01-05: 55.5045
- 2025-05-07: 64.3098
- 2025-09-06: 57.8475
- 2026-01-06: 58.4391
- 2026-05-09: 60.0308
- 2026-09-08: 59.0344

## Latest three complete dates

- 2026-09-06: 59.2871
- 2026-09-07: 59.1639
- 2026-09-08: 59.0344

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
