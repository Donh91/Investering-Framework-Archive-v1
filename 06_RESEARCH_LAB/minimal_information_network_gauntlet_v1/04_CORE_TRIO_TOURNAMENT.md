# Core Trio Tournament

Authority: `RESEARCH_ONLY_NON_CANONICAL`.

Required comparators: ETHBTC only, breadth only, BTC.D only, all three pairwise combinations, SIMPLE_3, SIMPLE_3+ETF, SIMPLE_3+stablecoin, SIMPLE_3+leverage/reset, SIMPLE_3+CFGI, best sparse discovered without outcome-tuned thresholds, full available Shadow Stack, and current stack where historically fair.

A numerically fair head-to-head confusion matrix does not exist in the frozen repository for these exact definitions. FP, FN, calibration and median lead-time are therefore `UNAVAILABLE`, and missing larger-stack metrics are never counted as a SIMPLE_3 win.

| Model | Distinct information | Main blind spot | Classification |
|---|---|---|---|
| ETHBTC only | relative leadership | fake spikes, participation | BASELINE |
| Breadth only | participation survival | may confirm late | BASELINE |
| BTC.D only | concentration/reclaim | no participation view | BASELINE |
| ETHBTC + Breadth | leadership + participation | concentration reclaim | SPARSE CANDIDATE |
| ETHBTC + BTC.D | leadership + concentration | broad survival | SPARSE CANDIDATE |
| Breadth + BTC.D | participation + concentration | early ETH lead | SPARSE CANDIDATE |
| SIMPLE_3 | three rotation families | ETF absorption, stress timing | STRONG ROTATION CANDIDATE |
| SIMPLE_3 + ETF | adds ETF-era hidden deterioration | stress/reload timing | STRONG REGIME CANDIDATE |
| SIMPLE_3 + leverage/reset | adds timing/exhaustion | ETF absorption | STRONG TIMING CANDIDATE |
| SIMPLE_3 + ETF + leverage/reset | rotation + ETF regime + timing | deployment quality | PREFERRED FULL-OBJECTIVE TEST |
| Full Shadow Stack | broadest named coverage | high dependence/complexity | INCREMENTAL_EDGE_UNPROVEN |

A larger stack wins if it reproducibly lowers FP/FN, improves lead-time without material error inflation, or catches a distinct failure regime on shared timestamp-clean rows after dependence and catalyst controls. Complexity is a cost, not a veto.