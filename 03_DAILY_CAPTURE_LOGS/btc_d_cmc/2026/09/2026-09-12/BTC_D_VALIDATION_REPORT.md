# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1349
- First date: 2023-01-01
- Last date: 2026-09-11
- Required latest complete date: 2026-09-11
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `323e57153d58fb79959fe83575cef4e01e74967cba120106791d286a25807379`
- Normalized CSV SHA-256: `087d4930f64222a3a7977ce1fe36cb814c79c892cabe2b62c91993efbdacc2a6`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-04: 48.4188
- 2024-01-05: 51.4041
- 2024-05-06: 53.3944
- 2024-09-06: 56.1746
- 2025-01-06: 55.6628
- 2025-05-09: 63.5161
- 2025-09-08: 57.7037
- 2026-01-09: 58.5242
- 2026-05-11: 60.1625
- 2026-09-11: 58.9556

## Latest three complete dates

- 2026-09-09: 58.7704
- 2026-09-10: 59.0414
- 2026-09-11: 58.9556

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
