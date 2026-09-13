# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1350
- First date: 2023-01-01
- Last date: 2026-09-12
- Required latest complete date: 2026-09-12
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `8c96463d39ddc41323095c73c2977c5510798b2f7609c9cdce213c1ddbb59fa5`
- Normalized CSV SHA-256: `725ad06eab9453d620183bcebf430d22d0bd72c68c7df4471e82af108517b683`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-04: 48.4188
- 2024-01-05: 51.4041
- 2024-05-07: 53.3457
- 2024-09-06: 56.1746
- 2025-01-07: 56.3399
- 2025-05-09: 63.5161
- 2025-09-09: 57.5593
- 2026-01-10: 58.5158
- 2026-05-12: 60.1544
- 2026-09-12: 58.727

## Latest three complete dates

- 2026-09-10: 59.0414
- 2026-09-11: 58.9556
- 2026-09-12: 58.727

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
