# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1413
- First date: 2023-01-01
- Last date: 2026-11-14
- Required latest complete date: 2026-11-14
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `b9543cf5e721b69aecf7bb8d1d7ab87ec13cec6e04b9723050f11d643c0f4200`
- Normalized CSV SHA-256: `a59ba19c6cf8d290934e46c76509faa0b92b6dd24a036a052e5f0daa3bbea3d6`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-16: 48.9193
- 2024-01-22: 49.8443
- 2024-05-29: 52.4616
- 2024-10-05: 56.8438
- 2025-02-10: 60.6678
- 2025-06-19: 64.019
- 2025-10-25: 59.1298
- 2026-03-02: 57.9156
- 2026-07-09: 58.1037
- 2026-11-14: 59.6146

## Latest three complete dates

- 2026-11-12: 60.6109
- 2026-11-13: 60.0775
- 2026-11-14: 59.6146

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
