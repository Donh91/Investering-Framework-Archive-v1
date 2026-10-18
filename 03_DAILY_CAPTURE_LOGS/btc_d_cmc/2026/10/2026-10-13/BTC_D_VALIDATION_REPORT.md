# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1380
- First date: 2023-01-01
- Last date: 2026-10-12
- Required latest complete date: 2026-10-12
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `0c888af6830b3c8e206033905445d0bec73fae0f2c4519efb8ad1f713086723e`
- Normalized CSV SHA-256: `8bf0b5d931c14e1435975995458f236589125d41e79ebcce2e691707545fe2d3`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-10: 48.3396
- 2024-01-13: 50.1176
- 2024-05-17: 54.5516
- 2024-09-20: 57.1765
- 2025-01-23: 57.4414
- 2025-05-29: 62.7853
- 2025-10-01: 58.2793
- 2026-02-03: 59.3776
- 2026-06-09: 58.1216
- 2026-10-12: 59.4147

## Latest three complete dates

- 2026-10-10: 59.5382
- 2026-10-11: 59.4468
- 2026-10-12: 59.4147

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
