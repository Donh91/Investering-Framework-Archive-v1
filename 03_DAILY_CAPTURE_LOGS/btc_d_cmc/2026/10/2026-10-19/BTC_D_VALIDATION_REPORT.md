# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1386
- First date: 2023-01-01
- Last date: 2026-10-18
- Required latest complete date: 2026-10-18
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `eecfa15ab1f327a654b3ab23dfcd289effc6f403774f9a4b1c75d3671ba894ed`
- Normalized CSV SHA-256: `0291b19d6c4b2d348ffbfc94c94b5453605412f1a906fec5ee17c1b0c0174ad2`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-11: 48.5997
- 2024-01-15: 49.7217
- 2024-05-20: 54.5158
- 2024-09-23: 56.7862
- 2025-01-26: 57.7389
- 2025-06-01: 63.4887
- 2025-10-05: 58.4075
- 2026-02-08: 58.3231
- 2026-06-14: 58.6627
- 2026-10-18: 60.08

## Latest three complete dates

- 2026-10-16: 59.8856
- 2026-10-17: 59.8935
- 2026-10-18: 60.08

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
