# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1337
- First date: 2023-01-01
- Last date: 2026-08-30
- Required latest complete date: 2026-08-30
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `5ff57f3435bd510c3dfbf3e594671d081fdc8a7857997b588182a6fe963465b4`
- Normalized CSV SHA-256: `620ec51d8fcc4f3b58cf3fbb9102d27350c6fde046126a1cf51fc72df2c68aac`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-03: 46.9668
- 2023-09-02: 48.3273
- 2024-01-01: 50.2434
- 2024-05-02: 52.4211
- 2024-08-31: 56.1117
- 2024-12-31: 56.4801
- 2025-05-01: 63.5229
- 2025-08-31: 57.3714
- 2025-12-30: 58.9435
- 2026-05-01: 60.0353
- 2026-08-30: 59.5129

## Latest three complete dates

- 2026-08-28: 59.7101
- 2026-08-29: 59.561
- 2026-08-30: 59.5129

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
