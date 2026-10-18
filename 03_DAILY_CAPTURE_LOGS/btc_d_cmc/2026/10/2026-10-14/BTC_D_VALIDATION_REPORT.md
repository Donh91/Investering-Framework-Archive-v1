# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1381
- First date: 2023-01-01
- Last date: 2026-10-13
- Required latest complete date: 2026-10-13
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `54abcb308711578ec1f2a485917ff87f08f9517b7f2f75938db364b78005f4f3`
- Normalized CSV SHA-256: `e47e7a3d349ed9ea287a4be5d08822e12a3c3939284189cef04325f69173c78a`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-10: 48.3396
- 2024-01-13: 50.1176
- 2024-05-18: 54.4198
- 2024-09-20: 57.1765
- 2025-01-24: 57.4712
- 2025-05-29: 62.7853
- 2025-10-02: 58.313
- 2026-02-04: 59.0594
- 2026-06-10: 58.0509
- 2026-10-13: 59.7264

## Latest three complete dates

- 2026-10-11: 59.4468
- 2026-10-12: 59.4147
- 2026-10-13: 59.7264

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
