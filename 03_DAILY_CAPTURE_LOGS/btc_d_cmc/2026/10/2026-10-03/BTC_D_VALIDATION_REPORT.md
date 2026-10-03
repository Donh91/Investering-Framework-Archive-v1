# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1370
- First date: 2023-01-01
- Last date: 2026-10-02
- Required latest complete date: 2026-10-02
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `5ce28b7aed82c498b6bb695e0799178499d424986bf5814e41a469525b5d1fcb`
- Normalized CSV SHA-256: `0141a13bafeeb781af8428eaa56888a673182990f5ddeb43d205c149bfb11858`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-06: 46.8861
- 2023-09-08: 48.5181
- 2024-01-10: 52.9863
- 2024-05-14: 53.9647
- 2024-09-15: 56.5118
- 2025-01-18: 56.4296
- 2025-05-22: 63.3104
- 2025-09-24: 57.719
- 2026-01-26: 59.2585
- 2026-05-31: 59.298
- 2026-10-02: 58.9816

## Latest three complete dates

- 2026-09-30: 58.7193
- 2026-10-01: 58.6257
- 2026-10-02: 58.9816

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
