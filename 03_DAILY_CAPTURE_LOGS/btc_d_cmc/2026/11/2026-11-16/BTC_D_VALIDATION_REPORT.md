# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1414
- First date: 2023-01-01
- Last date: 2026-11-15
- Required latest complete date: 2026-11-15
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `49592b5ce8d3904719d35199d32a44fccef9c9c62484782aa5d1d3a3bf9dba14`
- Normalized CSV SHA-256: `4bf43e842d716f4ddc456b997cb3d1864bb7c5e345e11f6fee20962434649aa7`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-16: 48.9193
- 2024-01-22: 49.8443
- 2024-05-30: 52.684
- 2024-10-05: 56.8438
- 2025-02-11: 60.593
- 2025-06-19: 64.019
- 2025-10-26: 59.086
- 2026-03-03: 58.4597
- 2026-07-10: 58.4364
- 2026-11-15: 59.5988

## Latest three complete dates

- 2026-11-13: 60.0775
- 2026-11-14: 59.6146
- 2026-11-15: 59.5988

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
