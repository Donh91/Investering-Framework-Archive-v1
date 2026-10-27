# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1394
- First date: 2023-01-01
- Last date: 2026-10-26
- Required latest complete date: 2026-10-26
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `74009aa226f35fa657fd82ee8b49488ecd68002b6ab7d3bae2e14b3862e0b553`
- Normalized CSV SHA-256: `6061415ccfe4b2f0975e4c8dcc50d644dcdc716d8ef227d3351c50de2f393ed0`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-12: 48.6729
- 2024-01-17: 49.7445
- 2024-05-23: 52.9744
- 2024-09-26: 56.2726
- 2025-01-31: 58.1759
- 2025-06-06: 63.6527
- 2025-10-11: 60.1327
- 2026-02-15: 58.0978
- 2026-06-21: 58.4439
- 2026-10-26: 60.0359

## Latest three complete dates

- 2026-10-24: 60.0922
- 2026-10-25: 60.1089
- 2026-10-26: 60.0359

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
