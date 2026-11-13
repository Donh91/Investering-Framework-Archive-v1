# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1411
- First date: 2023-01-01
- Last date: 2026-11-12
- Required latest complete date: 2026-11-12
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `9a6b4f6f93b3247a45f186650c1c3f320f108ac43a201252b47537aff6f2b874`
- Normalized CSV SHA-256: `ed04474547e2afd1e9e0650b5a642a939d8baed50fb1771bd0098be63267aa4a`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-15: 49.1329
- 2024-01-22: 49.8443
- 2024-05-29: 52.4616
- 2024-10-04: 56.9929
- 2025-02-09: 60.5815
- 2025-06-17: 64.0365
- 2025-10-23: 59.2247
- 2026-03-01: 58.1458
- 2026-07-07: 58.2153
- 2026-11-12: 60.6109

## Latest three complete dates

- 2026-11-10: 60.401
- 2026-11-11: 60.4749
- 2026-11-12: 60.6109

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
