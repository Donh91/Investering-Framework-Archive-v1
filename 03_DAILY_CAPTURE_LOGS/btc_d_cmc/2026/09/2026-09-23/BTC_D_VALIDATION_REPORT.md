# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1360
- First date: 2023-01-01
- Last date: 2026-09-22
- Required latest complete date: 2026-09-22
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `50b8cb2ee79aca31a0711f80fc5fb96fce2ce25c8e49035e6e0468e6b583dc8d`
- Normalized CSV SHA-256: `6052754951ebc5338dba623be0bbf9215e2f4db6e770d38ed8c930c2bf8d0063`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-06: 48.231
- 2024-01-08: 52.6463
- 2024-05-10: 53.3589
- 2024-09-11: 56.0596
- 2025-01-12: 56.4512
- 2025-05-16: 62.3222
- 2025-09-16: 57.3892
- 2026-01-18: 58.9283
- 2026-05-21: 60.1647
- 2026-09-22: 59.2663

## Latest three complete dates

- 2026-09-20: 58.7637
- 2026-09-21: 58.596
- 2026-09-22: 59.2663

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
