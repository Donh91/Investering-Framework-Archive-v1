# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1376
- First date: 2023-01-01
- Last date: 2026-10-08
- Required latest complete date: 2026-10-08
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `4188adeba0a63d7c5c4bc78be116d702da1450c936489f21617eab31103a2077`
- Normalized CSV SHA-256: `a9e5771fa12f59a49d05a5155137903a0ad235c2911c9cd1ada021074b507e05`

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
- 2025-01-21: 57.3344
- 2025-05-26: 63.2434
- 2025-09-28: 57.771
- 2026-01-31: 59.1663
- 2026-06-05: 57.9126
- 2026-10-08: 59.0986

## Latest three complete dates

- 2026-10-06: 58.9546
- 2026-10-07: 59.0147
- 2026-10-08: 59.0986

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
