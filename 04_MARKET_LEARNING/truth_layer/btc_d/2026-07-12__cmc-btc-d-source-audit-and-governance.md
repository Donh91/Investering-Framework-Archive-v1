# BTC.D CoinMarketCap Direct-Source Audit and Governance

**Date:** 2026-07-12  
**Status:** SOURCE_GOVERNANCE

## Access-path note

The user could not use the TradingView export route because that route required payment in the user's access path. This is preserved as an access limitation, not generalized into a claim that every TradingView account or export route is paid.

## Source

- Provider: CoinMarketCap
- Endpoint: `https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/historical?convertId=2781&timeStart=1672531200&timeEnd=1783728000&interval=1d`
- Convention: `CMC_DIRECT_SOURCE_CONVENTION`
- Definition: BTC market capitalization divided by total market capitalization of cryptoassets tracked by CoinMarketCap, including tokens and stablecoins.
- TradingView `CRYPTOCAP:BTC.D` equivalence: `NO`

## Integrity

```text
Numeric rows: 1287
Period: 2023-01-01 through 2026-07-11
Expected days: 1288
Preserved source gap: 2023-01-05
Coverage: 99.922360%
Duplicates: 0
Raw-to-normalized mismatches: 0
Interpolation/backfill/proxy insertion: none
Two-run numeric revision: zero
Latest package value: 58.4887 on 2026-07-11
```

The missing date lies outside the M1 evaluation window beginning 2025-03-01 and does not remove an M1 B1 observation.

## Source checksums

```text
Outer recovery ZIP:
b05c1c420e3cbc01adb63a4f48ed4c0c54a3371cd56635f65d3760d2a0c159cd

Raw provider JSON:
26273beb3a626c405e0eeb7e4601a1d91d33a39ae02a3b41c24b5847367a3e2b

Normalized daily CSV:
b2a028ba231e968632232d7fc34e1a4ea1b5c9f9ab98f4bbee9becaa44322bb8
```

## Governance decision

```text
BTC_D_CANONICAL_OPERATIONAL_SOURCE: CMC_DIRECT_SOURCE_CONVENTION
ROLE: DIRECTIONAL_AND_RESEARCH
HARD_ABSOLUTE_LEVEL_GATE_AUTHORITY: NO
TRADINGVIEW_EQUIVALENCE: NO
M1_DECLARED_SINGLE_CONVENTION_OPTION: SATISFIED
```

BTC.D cannot confirm rotation alone. Cross-provider absolute levels must not be spliced without a declared convention change.

No hard threshold promotion is made.
