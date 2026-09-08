# BTC.D Validation Report

- Validation status: `PASS`
- Normalized rows: 1345
- First date: 2023-01-01
- Last date: 2026-09-07
- Required latest complete date: 2026-09-07
- Future/current partial rows excluded: 0
- Duplicate dates rejected: 0
- Parse errors: 0
- Genuine date-gap ranges: 1
- Raw SHA-256: `5078372997451eb583e3871a115fd1ac3bafd1921e0109b6677516f9686b2f43`
- Normalized CSV SHA-256: `1d283854fc1b69eac36da006b7e4888a28aa1114f0ab07d33f44f00244ec2064`

## Convention

`CMC_DIRECT_SOURCE_CONVENTION`: BTC market cap divided by the total market cap of cryptoassets tracked by CoinMarketCap.

This is not the TradingView top-125 convention.

## Twelve dispersed anchor dates

- 2023-01-01: 40.0387
- 2023-05-04: 46.9852
- 2023-09-03: 48.3222
- 2024-01-04: 51.2703
- 2024-05-05: 53.5227
- 2024-09-04: 56.4435
- 2025-01-04: 55.5999
- 2025-05-06: 63.849
- 2025-09-05: 58.0284
- 2026-01-06: 58.4391
- 2026-05-08: 60.3362
- 2026-09-07: 59.1639

## Latest three complete dates

- 2026-09-05: 59.6421
- 2026-09-06: 59.2871
- 2026-09-07: 59.1639

## Genuine gap ranges

- 2023-01-05 through 2023-01-05

## Issues

- None

## Readiness

A `PASS` result supports a daily CoinMarketCap direct-source BTC-dominance replay.
It does not reproduce `CRYPTOCAP:BTC.D` or TradingView's top-125 denominator.
