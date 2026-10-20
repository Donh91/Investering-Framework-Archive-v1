# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1377
- First date: 2023-01-01
- Last date: 2026-10-09
- Required latest complete date: 2026-10-09
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `84fe0ff7475b5392563c0a9fecfdddf6aed09c0170502e7f64cc544718540407`
- Normalized CSV SHA-256: `eb0c8271aa952e67e2084c416a67130109fbd70c72bfd2756d81536387ebbd0a`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-09: 48.3306
- 2024-01-12: 51.2
- 2024-05-16: 54.5738
- 2024-09-18: 57.1998
- 2025-01-22: 57.7211
- 2025-05-27: 63.4069
- 2025-09-29: 57.7738
- 2026-02-01: 59.0654
- 2026-06-06: 58.1748
- 2026-10-09: 59.4709

## Latest three complete dates

- 2026-10-07: 59.0147
- 2026-10-08: 59.0986
- 2026-10-09: 59.4709

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
