# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1398
- First date: 2023-01-01
- Last date: 2026-10-30
- Required latest complete date: 2026-10-30
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `1d5408a372145ae569c417611a6bf1ea9b5fc69677803be5a66fa85fdab1f089`
- Normalized CSV SHA-256: `82fe33036f03d4ef47c7023ae7dd060df1a989be69b78bacce4f48eecd93df10`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-13: 48.9142
- 2024-01-18: 49.7612
- 2024-05-24: 52.6568
- 2024-09-28: 56.1325
- 2025-02-02: 58.5817
- 2025-06-09: 63.6821
- 2025-10-14: 58.3302
- 2026-02-18: 57.9461
- 2026-06-25: 58.1805
- 2026-10-30: 60.0041

## Latest three complete dates

- 2026-10-28: 60.0469
- 2026-10-29: 60.1008
- 2026-10-30: 60.0041

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
