# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1393
- First date: 2023-01-01
- Last date: 2026-10-25
- Required latest complete date: 2026-10-25
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `db3ad580b84ce457b028611e0e8eb44c4bc9d965e3a84b1ccfc7ef204746e7ef`
- Normalized CSV SHA-256: `5f40c7c42fc463b18a2ff07935445378c739ce0b63c4fedb2eb5db84d9ad5100`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-12: 48.6729
- 2024-01-17: 49.7445
- 2024-05-22: 53.0587
- 2024-09-26: 56.2726
- 2025-01-30: 58.7658
- 2025-06-06: 63.6527
- 2025-10-10: 58.5943
- 2026-02-14: 58.4235
- 2026-06-20: 58.336
- 2026-10-25: 60.1089

## Latest three complete dates

- 2026-10-23: 60.0843
- 2026-10-24: 60.0922
- 2026-10-25: 60.1089

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
