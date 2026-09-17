# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1354
- First date: 2023-01-01
- Last date: 2026-09-16
- Required latest complete date: 2026-09-16
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `028047832341ad44d0a0ecc91632ff56e084bcb41345849c227749f1b04062c2`
- Normalized CSV SHA-256: `ef7fd51c60521f58cc28f596584d2d7b8e3fad9f8e1a46400e95757e6ef15d18`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-05: 48.2974
- 2024-01-06: 51.7916
- 2024-05-08: 53.4683
- 2024-09-08: 55.7568
- 2025-01-09: 56.6258
- 2025-05-12: 62.1463
- 2025-09-12: 57.4948
- 2026-01-13: 58.6883
- 2026-05-16: 60.1658
- 2026-09-16: 58.9692

## Latest three complete dates

- 2026-09-14: 58.906
- 2026-09-15: 58.9546
- 2026-09-16: 58.9692

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
