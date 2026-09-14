# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1351
- First date: 2023-01-01
- Last date: 2026-09-13
- Required latest complete date: 2026-09-13
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `4d745b5c822503a3b984d5e4a6c2f96e9a633b45931ada9c8da1e9ec458448f7`
- Normalized CSV SHA-256: `e54bbbbfd96206db10047f36171e1873f432313a0d9689491d56e2b9d2f2056d`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-04: 48.4188
- 2024-01-05: 51.4041
- 2024-05-07: 53.3457
- 2024-09-07: 56.0539
- 2025-01-07: 56.3399
- 2025-05-10: 62.6355
- 2025-09-10: 57.3952
- 2026-01-11: 58.4788
- 2026-05-13: 60.1625
- 2026-09-13: 58.718

## Latest three complete dates

- 2026-09-11: 58.9556
- 2026-09-12: 58.727
- 2026-09-13: 58.718

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
