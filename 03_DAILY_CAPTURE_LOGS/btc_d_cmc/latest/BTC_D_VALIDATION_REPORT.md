# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1390
- First date: 2023-01-01
- Last date: 2026-10-22
- Required latest complete date: 2026-10-22
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `6826065f5c6b2ae10369218246466239b492c717c1fbd5f3ea5277a065c367ba`
- Normalized CSV SHA-256: `5785cf99eff96b61261bc3edbc03becfbbc9b241ff2068737de28a1e47abdbec`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-12: 48.6729
- 2024-01-16: 49.7643
- 2024-05-21: 53.8069
- 2024-09-24: 56.2265
- 2025-01-29: 58.4987
- 2025-06-04: 63.2486
- 2025-10-08: 58.225
- 2026-02-11: 58.7084
- 2026-06-18: 58.2482
- 2026-10-22: 60.1978

## Latest three complete dates

- 2026-10-20: 60.1165
- 2026-10-21: 60.0977
- 2026-10-22: 60.1978

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
