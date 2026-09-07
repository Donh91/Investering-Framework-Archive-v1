# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1344
- First date: 2023-01-01
- Last date: 2026-09-06
- Required latest complete date: 2026-09-06
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `be34195ca2cffc840c08146a09bcc458391afc7508246db1708591b25028681a`
- Normalized CSV SHA-256: `d837defc33020c7202c3a5704acf9408ee03b02971f9cce314eae053ee2cb296`

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
- 2025-01-04: 55.5999
- 2025-05-06: 63.849
- 2025-09-05: 58.0284
- 2026-01-05: 58.5183
- 2026-05-07: 60.4407
- 2026-09-06: 59.2871

## Latest three complete dates

- 2026-09-04: 59.8634
- 2026-09-05: 59.6421
- 2026-09-06: 59.2871

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
