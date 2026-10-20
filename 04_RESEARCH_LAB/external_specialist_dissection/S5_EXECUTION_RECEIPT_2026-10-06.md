# S5 Execution Receipt - 2026-10-06

Status: BASELINE_MERGED / PROSPECTIVE_GRADING_PENDING / RESEARCH_ONLY
Master issue: #1512
Execution issue: #1514
Merged PR: #1515
Merge commit: c65be9111d0f9091d4f5a6485f15d6a06ce1779e

## What was implemented

A source-agnostic, threshold-free derivatives crowding feature vector using:
- completed-hour price response;
- spot taker imbalance;
- futures taker imbalance;
- OI notional-value change;
- latest known basis;
- latest known funding before cutoff.

Windows:
- 1h
- 4h
- 12h
- 24h

The transformer excludes incomplete current intervals and rejects future funding leakage.

## Compatibility tags

Only descriptive sign-based tags are emitted:
- SPOT_ABSORPTION_SHORT_PRESSURE_COMPATIBLE
- BROAD_RISK_ON_COMPATIBLE
- LEVERAGE_LED_PUMP_COMPATIBLE
- DISTRIBUTION_INTO_LEVERAGED_LONGS_FLOW_COMPATIBLE
- HEALTHY_DELEVERAGING_COMPATIBLE
- BROAD_WEAKNESS_COMPATIBLE

Multiple tags may coexist.

They are not pullback states, warnings or actions.

## Source proof

Frozen BTCUSDT and ETHUSDT Binance public read-only fixtures were captured on 2026-10-06 and replayed offline in CI.

The source is treated as a capability proof, not permanent runtime authority. Historical Framework evidence of Binance Futures HTTP 451 remains binding; future collectors must preserve source health and fallback semantics.

## Gates

Green on PR head before merge:
- Full Architecture 1-7 Gate
- Data Architecture Gate
- Storage Health Gate
- Experiment Lifecycle Gate
- Automation Production Health Gate
- dedicated Research S5 Derivatives Crowding v1 gate

## Scientific boundaries

No threshold was tuned.
No Compass state changed.
No new pullback engine was created.
No SELL/TRIM/alert authority was created.
Existing M6 prospective warning/outcome contracts remain outcome truth.

## What remains

The baseline is technically ready but has not proven edge.

Next evidence:
1. prospectively freeze repeated vectors;
2. join later to existing M6 24h/72h/7d/14d/30d outcomes;
3. compare full vector against simple baselines;
4. only then decide whether liquidation-map or options challengers add incremental value.

Current edge state:
INSUFFICIENT_PROSPECTIVE_EVIDENCE.
