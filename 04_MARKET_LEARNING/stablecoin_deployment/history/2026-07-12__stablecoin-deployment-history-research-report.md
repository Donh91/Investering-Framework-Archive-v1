# Stablecoin Deployment Proxy — Historical Research Report

**Date:** 2026-07-12  
**Status:** SOURCE_BACKED_SHADOW_RESEARCH

## Data status

```text
HISTORY_READY: YES
AUTHORITY: SHADOW_RESEARCH
VELOCITY_CLAIM: FORBIDDEN
TVL_SUBSTITUTION: NONE
INTERPOLATION: NONE
```

The DeFiLlama artifact contains 5,532 matched daily rows: 922 rows for each of TOTAL, Ethereum, Solana, BSC, Base and Arbitrum from 2024-01-01 through 2026-07-10.

The five named chains represented 62.78% of TOTAL stablecoin supply and 68.01% of TOTAL DEX volume on 2026-07-10. Coverage is broad but not exhaustive.

## Source receipt

```text
Outer artifact ZIP SHA-256:
6591b74a77e762c0037614e9d1cf1f4080f844c63fa9fb0782698f6af07c4c22

Nested 12-JSON raw ZIP SHA-256:
70fdc03d36a4aa1ee6bf1d524999c387999872faea8a5f6e6730030d874cd67c

Raw endpoint files: 12/12 PASS
Normalized rows: 5532
Rows per entity: 922
```

Source endpoints:

- `https://api.llama.fi/stablecoincharts/all`
- `https://api.llama.fi/stablecoincharts/{chain}`
- `https://api.llama.fi/overview/dexs`
- `https://api.llama.fi/overview/dexs/{chain}`

## Measurement architecture

The historical layer is deliberately split into:

1. `stablecoin_supply` — parked or available dollar-like liquidity;
2. `dex_volume` — realized on-chain exchange activity;
3. `daily_dex_to_supply` — same-day activity relative to supply;
4. `deployment_intensity_7d/30d` — rolling DEX volume divided by average supply;
5. `deployment_state_7d` — descriptive sign matrix, not a score.

States:

- `EXPANDING_DEPLOYMENT`: supply up, DEX activity up;
- `PARKING_ACCUMULATION`: supply up, DEX activity flat/down;
- `ACTIVITY_WITHOUT_SUPPLY_GROWTH`: supply flat/down, DEX activity up;
- `BROAD_CONTRACTION`: supply down, DEX activity down;
- `MIXED_TRANSITION`: residual mixed state.

None is a standalone market or deployment confirmation.

## Latest complete snapshot — 2026-07-10

| Entity | Supply 7d | DEX 7d | 30d intensity percentile | Descriptive state |
|---|---:|---:|---:|---|
| TOTAL | -0.31% | +12.50% | 6.30 | ACTIVITY_WITHOUT_SUPPLY_GROWTH |
| Ethereum | -1.26% | +52.75% | 1.64 | ACTIVITY_WITHOUT_SUPPLY_GROWTH |
| Solana | -4.28% | -10.94% | 17.53 | BROAD_CONTRACTION |
| BSC | +1.39% | -11.56% | 0.27 | PARKING_ACCUMULATION |
| Base | -1.57% | +23.20% | 16.71 | ACTIVITY_WITHOUT_SUPPLY_GROWTH |
| Arbitrum | -1.06% | -22.38% | 1.64 | BROAD_CONTRACTION |

This describes a low historical 30-day activity-intensity regime for several entities. It is not a future market call.

## Full-period divergence evidence

2024-01-01 to 2026-07-10:

| Entity | Supply change | DEX change | DEX/supply change |
|---|---:|---:|---:|
| TOTAL | +137.64% | +139.74% | +0.88% |
| Ethereum | +125.82% | +207.15% | +36.01% |
| Solana | +738.81% | +191.86% | -65.21% |
| BSC | +296.00% | +67.97% | -57.58% |
| Base | +2607.38% | +3527.59% | +33.99% |
| Arbitrum | +92.56% | -76.47% | -87.78% |

Supply and activity can diverge radically. Supply growth alone cannot be called deployment.

## Canonical semantics

```text
LIQUIDITY_AVAILABILITY_AXIS = stablecoin supply impulse
REALIZED_ACTIVITY_AXIS      = DEX activity intensity
PROXY_NAME                  = STABLECOIN_DEPLOYMENT_PROXY
VELOCITY                     = DATA_MISSING / NOT_CLAIMED
```

A single stablecoin score is prohibited because it would destroy the distinction between parked liquidity and realized activity.
