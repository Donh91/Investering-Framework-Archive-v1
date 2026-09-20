# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1357
- First date: 2023-01-01
- Last date: 2026-09-19
- Required latest complete date: 2026-09-19
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `8daa09c81f692abb18c4f92caf3e46951c2e53b5b9779cd96493f71046b882b5`
- Normalized CSV SHA-256: `63db42f1273180a99e608a4734e7697da6202b1e0365663a0b9064bc062220d7`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-06: 48.231
- 2024-01-07: 52.1815
- 2024-05-09: 53.2602
- 2024-09-09: 55.7323
- 2025-01-11: 56.8241
- 2025-05-14: 61.127
- 2025-09-14: 56.7359
- 2026-01-15: 58.9718
- 2026-05-19: 60.114
- 2026-09-19: 58.7544

## Latest three complete dates

- 2026-09-17: 58.8313
- 2026-09-18: 58.5394
- 2026-09-19: 58.7544

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
