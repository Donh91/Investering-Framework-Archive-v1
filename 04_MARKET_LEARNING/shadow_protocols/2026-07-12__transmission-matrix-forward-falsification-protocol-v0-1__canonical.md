# Transmission Matrix Forward Falsification Protocol v0.1

**Date:** 2026-07-12  
**Status:** CANONICAL_SHADOW_PROTOCOL  
**Weight:** 0  
**Action authority:** 0

## Purpose

Prospectively test the separate transmission axes after the historical simulation rejected standalone and simple joint prediction claims.

## Axes

1. **Dominance survival** — CMC BTC.D five-day direction and B1 reclaim state.
2. **Liquidity availability** — TOTAL stablecoin supply change.
3. **Realized activity** — TOTAL DEX-volume change and DEX/supply ratio.
4. **Chain activity breadth** — share of Ethereum, Solana, BSC, Base and Arbitrum with positive seven-day ratio change.
5. **Altcoin participation breadth** — separately sourced frozen-universe breadth; `DATA_MISSING` until available.
6. **Price survival** — ETH/BTC and relevant market structure.

## Frozen source semantics

```text
BTC.D provider: CoinMarketCap
BTC.D convention: CMC_DIRECT_SOURCE_CONVENTION
stablecoin proxy: STABLECOIN_DEPLOYMENT_PROXY
```

Do not call DEX/supply velocity. Do not substitute stablecoin chain breadth for altcoin market breadth.

## Candidate state labels

```text
FALLING_EXPANDING_NO_RECENT_RECLAIM
FALLING_EXPANDING_RECENT_RECLAIM
FALLING_NONEXPANDING
RISING_OR_FLAT_EXPANDING
RISING_OR_FLAT_NONEXPANDING
DATA_MISSING
```

These labels are descriptive, not trade signals.

## Row timing

Create at most one row per complete UTC day or one weekly frozen row when daily collection is unavailable.

At row creation:

- freeze source timestamps and values;
- leave all outcome fields blank;
- set 7d, 14d and 30d evaluation due dates;
- record exact CMC and DeFiLlama source status;
- record altcoin breadth as `DATA_MISSING` rather than inferred.

## Outcome evaluation

When a horizon closes, append:

- ETH/BTC return;
- maximum favorable excursion;
- maximum adverse excursion;
- BTC return as context;
- whether BTC.D reclaim occurred after the row;
- breadth outcome if source-backed.

Never overwrite the frozen input row. Outcome rows must reference the original `transmission_row_id`.

## Promotion gate

No promotion discussion before all are met:

- at least 60 resolved weekly rows or 180 resolved daily rows;
- at least two materially different regimes;
- at least 20 observations in the candidate state under review;
- positive median and positive-rate improvement at two horizons;
- stability after 10/25-bps implementation costs;
- no dependence on fewer than five extreme return days;
- altcoin breadth available for the claimed rotation interpretation.

Passing the gate only permits governance review.

## Current prior

Historical evidence sets the prior to:

```text
standalone deployment prediction: NOT_SUPPORTED
single-episode joint signature: NOT_GENERALIZED
forward test: CONTINUE
```

No market call. No portfolio action. No automatic rule ratification.
