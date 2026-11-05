# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1403
- First date: 2023-01-01
- Last date: 2026-11-04
- Required latest complete date: 2026-11-04
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `1fc067ca3cde7040b11550c0f77701beb7a67a2055d115612c0825fafe421fb1`
- Normalized CSV SHA-256: `12f208c5d9cd1d08d323bdd36b57bf6adb11a636c013cefe895263f4a96d6aad`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-09: 46.9594
- 2023-09-14: 49.0705
- 2024-01-19: 49.603
- 2024-05-26: 53.0431
- 2024-09-30: 56.2292
- 2025-02-05: 60.3659
- 2025-06-12: 63.2249
- 2025-10-18: 58.9681
- 2026-02-22: 58.2659
- 2026-06-30: 57.8966
- 2026-11-04: 59.917

## Latest three complete dates

- 2026-11-02: 60.019
- 2026-11-03: 59.8911
- 2026-11-04: 59.917

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
