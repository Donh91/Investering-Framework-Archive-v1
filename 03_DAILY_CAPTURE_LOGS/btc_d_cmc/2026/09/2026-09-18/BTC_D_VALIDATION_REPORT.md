# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1355
- First date: 2023-01-01
- Last date: 2026-09-17
- Required latest complete date: 2026-09-17
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `0fddd2d893ed628b776da1e44d492fa5cbdebe199280d51c5d8a9a56c9fb4171`
- Normalized CSV SHA-256: `50236bf009811e9751123e176d50165b6ac6fa97eeaf18fe31987e5b6f76ece8`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-05: 48.2974
- 2024-01-06: 51.7916
- 2024-05-08: 53.4683
- 2024-09-08: 55.7568
- 2025-01-10: 56.7404
- 2025-05-13: 61.5968
- 2025-09-13: 56.8154
- 2026-01-14: 58.6414
- 2026-05-17: 60.1942
- 2026-09-17: 58.8313

## Latest three complete dates

- 2026-09-15: 58.9546
- 2026-09-16: 58.9692
- 2026-09-17: 58.8313

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
