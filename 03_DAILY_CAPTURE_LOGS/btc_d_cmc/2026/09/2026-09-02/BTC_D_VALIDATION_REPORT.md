# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1339
- First date: 2023-01-01
- Last date: 2026-09-01
- Required latest complete date: 2026-09-01
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `d222bae2a627d49856cf664fcca57e4d20d8fe89808972f150c72e0a1fe42efc`
- Normalized CSV SHA-256: `9645a5af147363049ea51378267840bd1b24cf6459876485ba863fb6f08afec6`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-02: 48.3273
- 2024-01-02: 50.5456
- 2024-05-03: 52.6565
- 2024-09-01: 56.2327
- 2025-01-01: 56.7671
- 2025-05-02: 63.7525
- 2025-09-01: 57.3442
- 2026-01-01: 58.9858
- 2026-05-02: 60.3784
- 2026-09-01: 59.7082

## Latest three complete dates

- 2026-08-30: 59.5129
- 2026-08-31: 59.6967
- 2026-09-01: 59.7082

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
