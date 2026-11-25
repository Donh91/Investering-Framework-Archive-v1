# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1422
- First date: 2023-01-01
- Last date: 2026-11-23
- Required latest complete date: 2026-11-23
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `f049ed386c0f3b7e1e7e7d443248a68dd25b048f06da2a2a100eee22e5c48a1a`
- Normalized CSV SHA-256: `191a7ccc7232109481e5be6ab718c424be72d112c3768c0cce10f304ffd755f7`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-17: 48.8503
- 2024-01-25: 50.3104
- 2024-06-02: 52.6545
- 2024-10-09: 56.7049
- 2025-02-15: 59.6132
- 2025-06-24: 64.5104
- 2025-10-31: 59.2555
- 2026-03-10: 58.544
- 2026-07-17: 58.4248
- 2026-11-23: 58.8948

## Latest three complete dates

- 2026-11-21: 58.5625
- 2026-11-22: 58.7187
- 2026-11-23: 58.8948

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
