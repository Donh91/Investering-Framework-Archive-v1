# Canonical Research Synthesis — CMC BTC.D + DeFiLlama Completion

**Date:** 2026-07-12  
**Status:** CANONICAL_RESEARCH_EVIDENCE  
**Authority:** Research/governance only; no market call, portfolio action or rule promotion.

## Completion verdict

```text
TRADINGVIEW_EXPORT_PATH: USER_ACCESS_BLOCKED_BY_PAYMENT
BTC_D_CMC_DIRECT_SERIES: READY_WITH_ONE_PRESERVED_SOURCE_GAP
TRADINGVIEW_CRYPTOCAP_EQUIVALENCE: NO
STABLECOIN_HISTORY: READY_SHADOW_RESEARCH
M1_CMC_B_LEG: COMPLETE
M1_STRICT_3_LEG_HYPOTHESIS: NOT_SUPPORTED_IN_SAMPLE
M4_BTC_D_AND_DEPLOYMENT_ENRICHMENT: COMPLETE
M4_FULL_REPLAY: PARTIAL_HISTORICAL_BREADTH_MISSING
```

## BTC.D source governance

The unavailable TradingView route is replaced with an audit-clean CoinMarketCap direct-source series:

- period: 2023-01-01 through 2026-07-11;
- 1,287 numeric daily rows;
- 99.922360% calendar coverage;
- one preserved provider gap on 2023-01-05;
- no interpolation, carry-forward or proxy insertion;
- zero numeric revision across two retrievals;
- source convention: `CMC_DIRECT_SOURCE_CONVENTION`.

CoinMarketCap defines dominance as BTC market capitalization divided by the total market capitalization of cryptoassets it tracks, including tokens and stablecoins. This is not silently relabelled as TradingView `CRYPTOCAP:BTC.D`.

Canonical role:

```text
DIRECTIONAL_AND_RESEARCH
HARD_ABSOLUTE_LEVEL_GATE_AUTHORITY: NO
```

## Stablecoin deployment history

The DeFiLlama artifact contains 5,532 matched daily rows: 922 per entity for TOTAL, Ethereum, Solana, BSC, Base and Arbitrum from 2024-01-01 through 2026-07-10.

The layer is decomposed into:

```text
LIQUIDITY AVAILABILITY AXIS = stablecoin supply impulse
REALIZED ACTIVITY AXIS     = DEX activity relative to supply
```

`DEX volume / stablecoin supply` remains `STABLECOIN_DEPLOYMENT_PROXY`. It is not velocity, net inflow, exchange reserves or proof of capital direction.

## M1 result

The pre-registered B1 rule was run unchanged:

```text
BTC.D(t) - BTC.D(t-5 calendar days) >= +0.75 percentage point
rising-edge fires only
```

Results:

- 22 fires;
- 5/9 Wave events detected before/at C5;
- 1/4 >=Storm events detected before/at C12;
- two false alarms;
- strict A+B+C 5-day cluster: 1/4 >=Storm recall;
- A+C 5-day cluster: 4/4 >=Storm recall.

Adding B1 reduced early-warning recall. The strict three-leg core hypothesis is not supported under the declared CMC convention in this sample.

A ±30/60/90-day placebo-shift attack frequently scored better than the actual B1 dates. This forbids post-hoc threshold loosening and reinforces anti-overfit governance.

## M4 result

All 18 M4 attempts were enriched and nested gates were aggregated into six independent episodes:

```text
REAL: 1
FAKE: 4
UNRESOLVED: 1
```

The February–March 2025 fake episode had strong deployment context but a +0.75pp BTC.D reclaim within ten days. Therefore expanding deployment alone is not sufficient.

The single real July 2025 episode combined:

1. falling BTC.D across all nested crossings;
2. no +0.75pp dominance reclaim within ten days;
3. expanding deployment.

This signature separated 1/1 real from 0/4 fake episodes in-sample. Because there is only one real episode and the signature was identified in the same sample, status is strictly:

```text
SHADOW_ONLY_FORWARD_FALSIFICATION
AUTHORITY: ZERO
```

## Cleaner transmission architecture

- ETH/BTC gate = repair attempt;
- stablecoin deployment = transmission-quality context;
- BTC.D reclaim = survival veto/failure context;
- breadth = missing independent confirmation;
- price structure = confirmation and exit-side protection.

No sensor is allowed to confirm rotation alone.

## Data-integrity warning

The M1 PDF reports 151 warning fires, while the supplied row CSV contains 81 warning rows. The B1 series is directly reproducible, but A/C/D combinations are reproducible only against the 81-row export. Exact recreation of the original aggregate requires the generating script or full daily signal matrix.

## Forward research order

1. preserve CMC as the declared BTC.D convention;
2. log dominance survival and deployment axes prospectively;
3. add breadth without current-constituent historical backfill;
4. resolve M4 rows only at frozen horizons;
5. run M2 only after these source-backed labels mature;
6. continue M3 prospective collection.

No market call. No portfolio action. No rule ratification.
