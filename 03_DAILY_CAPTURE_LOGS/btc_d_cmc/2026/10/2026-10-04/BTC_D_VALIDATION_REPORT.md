# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1371
- First date: 2023-01-01
- Last date: 2026-10-03
- Required latest complete date: 2026-10-03
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `01803f9447d4cc166af0c4dea5225b5db49eb4b8a4f24ad82b63bfd7316df875`
- Normalized CSV SHA-256: `cd528aea164972dfcedbcf538101503294b303eaf1fe116d4954fe8df77a06ff`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-08: 48.5181
- 2024-01-11: 51.664
- 2024-05-14: 53.9647
- 2024-09-16: 56.8071
- 2025-01-18: 56.4296
- 2025-05-23: 63.0212
- 2025-09-24: 57.719
- 2026-01-27: 59.0879
- 2026-05-31: 59.298
- 2026-10-03: 59.0606

## Latest three complete dates

- 2026-10-01: 58.6257
- 2026-10-02: 58.9816
- 2026-10-03: 59.0606

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
