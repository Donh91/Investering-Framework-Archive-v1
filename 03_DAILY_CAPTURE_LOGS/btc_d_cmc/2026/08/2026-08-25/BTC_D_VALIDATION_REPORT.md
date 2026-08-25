# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1331
- First date: 2023-01-01
- Last date: 2026-08-24
- Required latest complete date: 2026-08-24
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `c5bea4b5315bde5c154793f142d0f1242e8c7979ed0f73aadb1d4605eac3d645`
- Normalized CSV SHA-256: `39bd5f1e155255b917334b5dffa2246349f661d0a15602792cc1123ec51d5b86`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-03: 46.9668
- 2023-09-01: 48.2708
- 2023-12-31: 50.0225
- 2024-04-30: 53.424
- 2024-08-29: 55.9813
- 2024-12-27: 57.15
- 2025-04-27: 63.3053
- 2025-08-26: 58.0185
- 2025-12-25: 59.1383
- 2026-04-25: 59.9157
- 2026-08-24: 59.1695

## Latest three complete dates

- 2026-08-22: 59.4697
- 2026-08-23: 59.2835
- 2026-08-24: 59.1695

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
