# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1378
- First date: 2023-01-01
- Last date: 2026-10-10
- Required latest complete date: 2026-10-10
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `b0e565beed38263f71191fe49fec3bc9612401412010a7f85b0e7f7f8166a87c`
- Normalized CSV SHA-256: `bbec1dc69d6c0111639e66473b20607b72d1a2b2bda67df1cf53ca40d9863cee`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-09: 48.3306
- 2024-01-13: 50.1176
- 2024-05-17: 54.5516
- 2024-09-19: 57.3762
- 2025-01-22: 57.7211
- 2025-05-27: 63.4069
- 2025-09-29: 57.7738
- 2026-02-02: 59.353
- 2026-06-07: 58.2034
- 2026-10-10: 59.5382

## Latest three complete dates

- 2026-10-08: 59.0986
- 2026-10-09: 59.4709
- 2026-10-10: 59.5382

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
