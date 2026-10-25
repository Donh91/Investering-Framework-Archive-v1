# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1392
- First date: 2023-01-01
- Last date: 2026-10-24
- Required latest complete date: 2026-10-24
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `14a72ff1a39a458a426b8a4d33dddd1bc1d106c49cc6e65d6c9a133992e984c5`
- Normalized CSV SHA-256: `65de65479cf82172ba282c1e652ebdcc68d15474336f81f6216b8ec99750a74c`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-08: 46.9789
- 2023-09-12: 48.6729
- 2024-01-16: 49.7643
- 2024-05-22: 53.0587
- 2024-09-25: 56.2591
- 2025-01-30: 58.7658
- 2025-06-05: 63.2642
- 2025-10-10: 58.5943
- 2026-02-13: 58.1676
- 2026-06-20: 58.336
- 2026-10-24: 60.0922

## Latest three complete dates

- 2026-10-22: 60.1978
- 2026-10-23: 60.0843
- 2026-10-24: 60.0922

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
