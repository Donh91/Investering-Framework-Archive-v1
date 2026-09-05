# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1342
- First date: 2023-01-01
- Last date: 2026-09-04
- Required latest complete date: 2026-09-04
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `343c66ce411561ebac1c7bb67b4e65a76586145c1dbb234b0f1089ef31e50e8b`
- Normalized CSV SHA-256: `5e8e8c9030eefcd7661fc78926d73d6e7c635ac366779d0e92c9d0950189dd63`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-03: 48.3222
- 2024-01-03: 51.142
- 2024-05-04: 53.2774
- 2024-09-03: 56.2907
- 2025-01-02: 56.3047
- 2025-05-04: 63.8639
- 2025-09-03: 57.8243
- 2026-01-03: 58.5264
- 2026-05-05: 60.5702
- 2026-09-04: 59.8634

## Latest three complete dates

- 2026-09-02: 59.6186
- 2026-09-03: 59.5756
- 2026-09-04: 59.8634

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
