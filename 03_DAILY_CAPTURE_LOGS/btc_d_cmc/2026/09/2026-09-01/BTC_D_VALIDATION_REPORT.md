# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1338
- First date: 2023-01-01
- Last date: 2026-08-31
- Required latest complete date: 2026-08-31
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `56f1da7dbb9579658f2320a6c17c401e229c6510fa727cc3c31d3e06ae569f4a`
- Normalized CSV SHA-256: `69e8fbc408d57b98fb36fa1f86858218e3e7fb5e7442b841d3592df542095340`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-02: 48.3273
- 2024-01-02: 50.5456
- 2024-05-02: 52.4211
- 2024-09-01: 56.2327
- 2024-12-31: 56.4801
- 2025-05-02: 63.7525
- 2025-08-31: 57.3714
- 2025-12-31: 59.0733
- 2026-05-01: 60.0353
- 2026-08-31: 59.6967

## Latest three complete dates

- 2026-08-29: 59.561
- 2026-08-30: 59.5129
- 2026-08-31: 59.6967

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
