# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1416
- First date: 2023-01-01
- Last date: 2026-11-17
- Required latest complete date: 2026-11-17
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `2ad313c0088bfdf46006cbbeb897924038d41dd07cc311bebdaba35b222039b6`
- Normalized CSV SHA-256: `68eaf972bc77fb2936d71c0ca033e1004ce952891a74c212b14783790ec1aa2a`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-16: 48.9193
- 2024-01-23: 49.78
- 2024-05-31: 53.0807
- 2024-10-06: 56.8935
- 2025-02-12: 60.2812
- 2025-06-20: 63.9933
- 2025-10-27: 58.9506
- 2026-03-05: 59.1958
- 2026-07-11: 58.4887
- 2026-11-17: 59.4248

## Latest three complete dates

- 2026-11-15: 59.5988
- 2026-11-16: 59.4138
- 2026-11-17: 59.4248

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
