# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1401
- First date: 2023-01-01
- Last date: 2026-11-02
- Required latest complete date: 2026-11-02
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `8f026beb3aa5c3a8ea1c5b9af4ae59a9474737a1b6d285a2f92c49f84ff85246`
- Normalized CSV SHA-256: `e776c65066ee88ee67915105991b7c68871ae8b20199c5606e698d970e549a78`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-14: 49.0705
- 2024-01-19: 49.603
- 2024-05-25: 53.0021
- 2024-09-29: 56.3107
- 2025-02-04: 60.0624
- 2025-06-11: 63.1665
- 2025-10-16: 58.8506
- 2026-02-20: 58.2124
- 2026-06-28: 58.1403
- 2026-11-02: 60.019

## Latest three complete dates

- 2026-10-31: 59.7013
- 2026-11-01: 59.8406
- 2026-11-02: 60.019

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
