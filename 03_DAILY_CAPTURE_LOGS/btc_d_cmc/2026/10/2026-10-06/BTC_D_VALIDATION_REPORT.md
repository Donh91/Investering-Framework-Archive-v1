# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1373
- First date: 2023-01-01
- Last date: 2026-10-05
- Required latest complete date: 2026-10-05
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `cf99adde30000c443bc903632e7d16474c29bf9eafeb1e67c8bae886a7415cae`
- Normalized CSV SHA-256: `488944eaae78ef82420eb86c2e1dd65ff1514881260a438e8e6e44e2dd93f174`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-07: 47.1537
- 2023-09-08: 48.5181
- 2024-01-11: 51.664
- 2024-05-15: 54.0329
- 2024-09-17: 56.7041
- 2025-01-19: 56.8622
- 2025-05-24: 63.1658
- 2025-09-26: 58.3411
- 2026-01-29: 58.9858
- 2026-06-02: 58.6363
- 2026-10-05: 59.1546

## Latest three complete dates

- 2026-10-03: 59.0606
- 2026-10-04: 58.9048
- 2026-10-05: 59.1546

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
