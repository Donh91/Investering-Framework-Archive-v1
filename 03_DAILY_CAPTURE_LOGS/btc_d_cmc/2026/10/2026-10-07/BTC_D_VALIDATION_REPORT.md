# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1374
- First date: 2023-01-01
- Last date: 2026-10-06
- Required latest complete date: 2026-10-06
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `f79a2f976f52865050d560d0f488097a9c791a852d367b9060c6616642b6d366`
- Normalized CSV SHA-256: `9139d67ca01190b29dac6d5ca45f5a046be4fc02f6058f8501b9b245b8ad3277`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-09: 48.3306
- 2024-01-11: 51.664
- 2024-05-15: 54.0329
- 2024-09-17: 56.7041
- 2025-01-20: 57.3799
- 2025-05-25: 63.1047
- 2025-09-27: 57.754
- 2026-01-29: 58.9858
- 2026-06-03: 58.0881
- 2026-10-06: 58.9546

## Latest three complete dates

- 2026-10-04: 58.9048
- 2026-10-05: 59.1546
- 2026-10-06: 58.9546

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
