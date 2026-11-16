# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1412
- First date: 2023-01-01
- Last date: 2026-11-13
- Required latest complete date: 2026-11-13
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `ebc67de9a938e6e98946de361aeda3bc9239bc5aaf1675edb7292047e082f2bb`
- Normalized CSV SHA-256: `5e03187e5d7648fa7a596111523ca0abf6c63fb03b86297e73d8de6cd982c659`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-10: 46.9142
- 2023-09-16: 48.9193
- 2024-01-22: 49.8443
- 2024-05-29: 52.4616
- 2024-10-04: 56.9929
- 2025-02-10: 60.6678
- 2025-06-18: 63.9744
- 2025-10-24: 59.268
- 2026-03-01: 58.1458
- 2026-07-08: 58.2362
- 2026-11-13: 60.0775

## Latest three complete dates

- 2026-11-11: 60.4749
- 2026-11-12: 60.6109
- 2026-11-13: 60.0775

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
