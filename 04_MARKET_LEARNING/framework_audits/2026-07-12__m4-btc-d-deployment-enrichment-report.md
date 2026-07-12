# M4 Rotation Survival — BTC.D + Deployment Enrichment

**Date:** 2026-07-12  
**Status:** RESEARCH_RESULT_NO_PROMOTION

## Scope

All 18 M4 gate attempts were enriched with:

- CMC BTC.D at cross;
- 5-day BTC.D change;
- +0.75pp dominance reclaim within ten days;
- TOTAL stablecoin supply/activity state;
- 30-day deployment intensity and trailing-365-day percentile;
- selected-chain DEX/supply breadth;
- +7/+14-day deployment state.

The three nested REAL_CANDIDATE rows are one July 2025 episode, not three independent successes. Attempt-level rows were aggregated into independent episodes.

## Episode map

| Episode | Attempts | Outcome | Main context |
|---|---:|---|---|
| Feb–Mar 2025 | 3 | FAKE | strong deployment, but BTC.D reclaim occurred |
| Jul 2025 | 3 | REAL | falling BTC.D, no reclaim, expanding deployment |
| Feb 2026 | 3 | FAKE | parking/mixed deployment and later BTC.D reclaim |
| Mar–Apr 2026 | 3 | FAKE | extremely low intensity / broad contraction |
| May–Jun 2026 | 4 | FAKE | activity without supply growth; low intensity |
| Jun–Jul 2026 | 2 | UNRESOLVED | mixed/contraction context; remains open |

## Highest-value counterexample

The February–March 2025 fake episode had:

- predominantly `EXPANDING_DEPLOYMENT`;
- median 30-day intensity percentile 77.53;
- median selected-chain positive ratio breadth 80%;
- a +0.75pp BTC.D reclaim within ten days.

Therefore:

```text
EXPANDING_DEPLOYMENT ALONE != REAL ROTATION
```

This falsifies a simple stablecoin/DEX confirmation rule.

## Exploratory joint survival signature

The single real episode combined:

1. BTC.D falling across all nested gate crossings;
2. no +0.75pp BTC.D reclaim within ten days;
3. expanding deployment context.

The signature appears in 1/1 real episode and 0/4 resolved fake episodes.

Because there is only one real episode and the signature was identified in the same sample, status is strictly:

```text
SHADOW_ONLY_FORWARD_FALSIFICATION
AUTHORITY: ZERO
```

## Sensor-role upgrade

- ETH/BTC gate = repair attempt;
- stablecoin deployment = transmission-quality context;
- BTC.D reclaim = survival veto/failure context;
- breadth = still-missing independent confirmation;
- price structure = confirmation and exit-side protection.

This role split is cleaner than asking any single sensor to confirm altseason.

## Unresolved episode

The June–July 2026 episode remains `UNRESOLVED`. Its derived fields may be logged, but it must not be assigned a REAL/FAKE outcome retrospectively.

## Final status

```text
M4_BTC_D_ENRICHMENT: COMPLETE
M4_DEPLOYMENT_ENRICHMENT: COMPLETE
M4_EPISODE_DEDUPLICATION: COMPLETE
M4_FULL_MULTI_GATE_REPLAY: PARTIAL
BLOCKER: HISTORICAL BREADTH SERIES
RULE_PROMOTION: NONE
```
