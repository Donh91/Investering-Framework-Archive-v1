# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1347
- First date: 2023-01-01
- Last date: 2026-09-09
- Required latest complete date: 2026-09-09
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `b2587ae20205ed0c8cc5739236fbf2344f04134466311c69155879ebf37d30d7`
- Normalized CSV SHA-256: `7afb5e73fab6e1038aab046087abb5b36a7b572f52deb6ccba01ba8fb2136f92`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-04: 48.4188
- 2024-01-04: 51.2703
- 2024-05-05: 53.5227
- 2024-09-05: 56.4743
- 2025-01-05: 55.5045
- 2025-05-08: 64.383
- 2025-09-07: 57.8583
- 2026-01-07: 58.229
- 2026-05-10: 60.1535
- 2026-09-09: 58.7704

## Latest three complete dates

- 2026-09-07: 59.1639
- 2026-09-08: 59.0344
- 2026-09-09: 58.7704

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
