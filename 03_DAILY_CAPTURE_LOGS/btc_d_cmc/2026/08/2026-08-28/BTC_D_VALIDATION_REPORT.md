# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1334
- First date: 2023-01-01
- Last date: 2026-08-27
- Required latest complete date: 2026-08-27
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `359879217560acf13acd640ba06c8edd1bc64bbdc46bef80fa62ebb4899c1e71`
- Normalized CSV SHA-256: `1b4be4b6cfdf077aebb9cc0ab373a86fc563651a3542d55455c54d0f3ff034ec`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-03: 46.9668
- 2023-09-01: 48.2708
- 2024-01-01: 50.2434
- 2024-05-01: 53.4133
- 2024-08-30: 56.2013
- 2024-12-29: 56.4627
- 2025-04-29: 63.4169
- 2025-08-28: 57.5426
- 2025-12-28: 58.9539
- 2026-04-28: 60.0384
- 2026-08-27: 59.5586

## Latest three complete dates

- 2026-08-25: 59.5987
- 2026-08-26: 59.8131
- 2026-08-27: 59.5586

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
