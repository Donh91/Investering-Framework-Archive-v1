# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1341
- First date: 2023-01-01
- Last date: 2026-09-03
- Required latest complete date: 2026-09-03
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `19b95ae99796d456bdb36a1c569793c3205a9af35301aa5c3a195ebb183089a9`
- Normalized CSV SHA-256: `ac2c0cfea516bde6b22405414099eb59c9e47d3577206e5c204af3bd7d6425ab`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-03: 48.3222
- 2024-01-02: 50.5456
- 2024-05-03: 52.6565
- 2024-09-02: 56.3349
- 2025-01-02: 56.3047
- 2025-05-04: 63.8639
- 2025-09-03: 57.8243
- 2026-01-02: 58.9757
- 2026-05-04: 60.3608
- 2026-09-03: 59.5756

## Latest three complete dates

- 2026-09-01: 59.7082
- 2026-09-02: 59.6186
- 2026-09-03: 59.5756

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
