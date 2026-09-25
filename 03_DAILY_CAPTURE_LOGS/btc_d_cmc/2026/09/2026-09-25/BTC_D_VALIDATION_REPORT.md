# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1362
- First date: 2023-01-01
- Last date: 2026-09-24
- Required latest complete date: 2026-09-24
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `04f6bb23ec2d8048e52df16e60a4748222149aad997dc534cd6d538eafb2ff6b`
- Normalized CSV SHA-256: `bef8da7e12d9cbdc6bd905686f464a1436ec7d275b701e93a2b054741c0afd58`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-06: 48.231
- 2024-01-08: 52.6463
- 2024-05-11: 53.2022
- 2024-09-12: 56.1928
- 2025-01-13: 56.7167
- 2025-05-17: 62.3721
- 2025-09-18: 56.9077
- 2026-01-20: 59.0704
- 2026-05-23: 59.8595
- 2026-09-24: 59.172

## Latest three complete dates

- 2026-09-22: 59.2663
- 2026-09-23: 58.9871
- 2026-09-24: 59.172

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
