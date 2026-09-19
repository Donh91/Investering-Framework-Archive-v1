# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1356
- First date: 2023-01-01
- Last date: 2026-09-18
- Required latest complete date: 2026-09-18
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `bd7e35436fea2f7f9db8f690fdcfaa48ecfa2cf4ed4c70474ab112b74b25bb69`
- Normalized CSV SHA-256: `198ed3024112f84f905f2a72a99dbfd0e9d813627ccaaabfd44de6c2e5998380`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-05: 47.1072
- 2023-09-05: 48.2974
- 2024-01-07: 52.1815
- 2024-05-09: 53.2602
- 2024-09-09: 55.7323
- 2025-01-10: 56.7404
- 2025-05-13: 61.5968
- 2025-09-13: 56.8154
- 2026-01-15: 58.9718
- 2026-05-18: 60.2516
- 2026-09-18: 58.5394

## Latest three complete dates

- 2026-09-16: 58.9692
- 2026-09-17: 58.8313
- 2026-09-18: 58.5394

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
