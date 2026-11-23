# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1421
- First date: 2023-01-01
- Last date: 2026-11-22
- Required latest complete date: 2026-11-22
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `a8870064b075c14d70c54e4dcf4ace32f70a60e1ff292b81511970f8f2a8ebea`
- Normalized CSV SHA-256: `d3706c2a96d146705603032af715b624824fe2041632703dcd988e28eb6d30bf`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-11: 46.8119
- 2023-09-17: 48.8503
- 2024-01-24: 50.3555
- 2024-06-01: 52.7744
- 2024-10-08: 56.7962
- 2025-02-15: 59.6132
- 2025-06-24: 64.5104
- 2025-10-31: 59.2555
- 2026-03-09: 58.1218
- 2026-07-16: 58.358
- 2026-11-22: 58.7187

## Latest three complete dates

- 2026-11-20: 58.6386
- 2026-11-21: 58.5625
- 2026-11-22: 58.7187

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
