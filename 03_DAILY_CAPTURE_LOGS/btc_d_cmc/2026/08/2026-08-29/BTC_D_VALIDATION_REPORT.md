# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1335
- First date: 2023-01-01
- Last date: 2026-08-28
- Required latest complete date: 2026-08-28
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `77851026d969bf4561601107ed92296923c9be58e3d71d59bdff878e4a314eb3`
- Normalized CSV SHA-256: `2f3b88a3b513172bbe944fe79bdca4bcd5ce8945f31ba685ba1c8bee4be1cc95`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-03: 46.9668
- 2023-09-02: 48.3273
- 2024-01-01: 50.2434
- 2024-05-01: 53.4133
- 2024-08-30: 56.2013
- 2024-12-30: 56.6932
- 2025-04-30: 63.4611
- 2025-08-29: 57.5132
- 2025-12-28: 58.9539
- 2026-04-29: 59.8556
- 2026-08-28: 59.7101

## Latest three complete dates

- 2026-08-26: 59.8131
- 2026-08-27: 59.5586
- 2026-08-28: 59.7101

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
