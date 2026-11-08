# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1406
- First date: 2023-01-01
- Last date: 2026-11-07
- Required latest complete date: 2026-11-07
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `8e8f5d9f02ced0436525fbda3e344ce5c98073ac3aae9612d30255c655e642ee`
- Normalized CSV SHA-256: `41c456fa2a630b8d3c0af4c34f7e948f441246449f11e2a903fa76dac9ae5b0f`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-14: 49.0705
- 2024-01-20: 49.7512
- 2024-05-27: 52.7643
- 2024-10-02: 56.2534
- 2025-02-06: 60.3696
- 2025-06-14: 63.8481
- 2025-10-20: 58.8992
- 2026-02-25: 57.8675
- 2026-07-02: 57.9257
- 2026-11-07: 59.8744

## Latest three complete dates

- 2026-11-05: 60.1639
- 2026-11-06: 59.9948
- 2026-11-07: 59.8744

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
