# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1340
- First date: 2023-01-01
- Last date: 2026-09-02
- Required latest complete date: 2026-09-02
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `3de13b587a349ceb54c176952c17fa98bd17b1dd304de8ba3d84fdb54a8f0a68`
- Normalized CSV SHA-256: `d66b60d9f121013d990837c3b5dd654abbb1cb76d060598d21edbda47ec1068d`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-02: 48.3273
- 2024-01-02: 50.5456
- 2024-05-03: 52.6565
- 2024-09-02: 56.3349
- 2025-01-01: 56.7671
- 2025-05-03: 63.8073
- 2025-09-02: 57.8286
- 2026-01-02: 58.9757
- 2026-05-03: 60.4187
- 2026-09-02: 59.6186

## Latest three complete dates

- 2026-08-31: 59.6967
- 2026-09-01: 59.7082
- 2026-09-02: 59.6186

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
