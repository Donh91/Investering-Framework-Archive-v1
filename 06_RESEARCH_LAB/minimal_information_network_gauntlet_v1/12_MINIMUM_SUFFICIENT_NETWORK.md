# Minimum Sufficient Network

Authority: `RESEARCH_ONLY_NON_CANONICAL`.

There is **no proven globally minimum sufficient network**. The answer is task-dependent.

Rotation-only candidate:
`ETHBTC_PERSISTENCE + BREADTH_SURVIVAL + BTCD_PATH_RECLAIM`
Status: `PROSPECTIVE_TEST_JUSTIFIED`.

Full-objective sparse candidate:
`ETHBTC_PERSISTENCE + BREADTH_SURVIVAL + BTCD_PATH_RECLAIM + ETF_FLOW_QUALITY + LEVERAGE_LIQUIDATION_RECLAIM`
Status: `PREFERRED_PROSPECTIVE_CANDIDATE`.

| Model | n | FP | FN | Lead-time | Opportunity cost | Drawdown avoided | Regime robustness | Incremental value | Complexity | Verdict |
|---|---:|---:|---:|---|---|---|---|---|---:|---|
| ETHBTC only | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | LOW-MEDIUM | baseline | 1 | BASELINE |
| Breadth only | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | MEDIUM | baseline | 1 | BASELINE |
| BTC.D only | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | MEDIUM | baseline | 1 | BASELINE |
| Best pair | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | 2 | TEST_REQUIRED |
| SIMPLE_3 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | MEDIUM-HIGH for rotation | HYPOTHESIS | 3 | PROSPECTIVE_TEST_JUSTIFIED |
| SIMPLE_3 + ETF | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | HIGH post-ETF candidate | FUNCTIONALLY_DISTINCT | 4 | PROSPECTIVE_TEST_JUSTIFIED |
| SIMPLE_3 + ETF + leverage/reclaim | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | HIGH candidate | FUNCTIONALLY_DISTINCT | 5 | PREFERRED_FULL_OBJECTIVE_TEST |
| Full Shadow Stack | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | UNPROVEN_AFTER_DEPENDENCE | HIGH | TEST_REQUIRED |

## Pareto front
No scalar score. Frontier A: ETHBTC+Breadth for earliest screening. Frontier B: SIMPLE_3 for rotation robustness. Frontier C: SIMPLE_3+ETF for ETF-era regime coverage. Frontier D: SIMPLE_3+ETF+leverage/reclaim for full-objective timing + regime. Full Stack joins if reproducible incremental value survives dependence controls.

## Non-inferiority sensitivity
Strict: no material loss in FP, FN, lead-time, regime/function coverage, result `NO_MINIMAL_WINNER` because shared-row metrics are unavailable.
Moderate: one minor degradation may be accepted for material complexity reduction without losing a distinct failure mode, result 4-5 family sparse candidate preferred for testing.
Relaxed: near-equivalence allowed for narrow task with context delegated, result SIMPLE_3 acceptable as rotation-only candidate, not whole-framework minimum.