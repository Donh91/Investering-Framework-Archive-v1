# Open Questions Register — Sensor Audit v1.1 Addendum

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** unresolved evidence gaps / next actions  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Depends on:** `01_CORE_FRAMEWORK/governance/2026-07-10__open-questions-register-v1-2__canonical.md`, `06_RESEARCH_LAB/audit_summaries/2026-07-12__marginal-decision-value-and-breadth-truth-program-v1__canonical.md`

## Updated questions

### OQ-PULLBACK — reproducible role and evaluation

```yaml
status: OPEN_NEEDS_PROSPECTIVE_ROWS
question: Does C2 retain usable warning value in prospectively frozen pullback events when A is urgency and D is confirmation/veto?
new_evidence:
  - C-family beat frequency-matched timing placebo historically
  - event topology is not one deterministic A-to-C-to-D sequence
  - one added operational-delay day reduced non-negative usable C lead from 88.9% to 44.4%
next_action: capture C2 event-driven or daily with source, operational-availability and framework-acceptance timestamps
owner: GOVERNANCE_RESEARCH_LAB
```

### OQ-ROTATION — prospective multi-axis decision value

```yaml
status: OPEN_FORWARD_ONLY_NOT_PROMOTION_READY
question: Do ETHBTC, price structure, BTC.D survival, liquidity/activity and descriptive point-in-time breadth reduce fake rotation enough to justify delay prospectively?
resolved_historical_inputs:
  - BTC_D_HISTORY
  - STABLECOIN_DEPLOYMENT_HISTORY
  - WEEKLY_FROZEN_UNIVERSE_ALTCOIN_BREADTH
historical_result:
  breadth_predictive_gate: NOT_SUPPORTED
  breadth_descriptive_context: RETAIN_ZERO_WEIGHT
remaining_requirements:
  - PROSPECTIVE_BREADTH_COMPLETE_DECISION_ROWS
  - SUFFICIENT_INDEPENDENT_REAL_AND_FAKE_EPISODES
  - DAILY_POINT_IN_TIME_BREADTH_IF_DAILY_GATE_IS_TESTED
  - HISTORICAL_30DMA_BREADTH_REMAINS_DATA_MISSING
owner: RESEARCH_LAB
```

### OQ-BREADTH-CADENCE — descriptive breadth cadence

```yaml
status: OPEN_FORWARD_INSTRUMENTATION
question: What reporting cadence preserves breadth as participation context without turning stale weekly data into a daily gate?
known:
  - weekly historical truth is available
  - forward correlations are near zero
  - high breadth can be a late-state observation
next_action: log point-in-time forward snapshots; keep zero predictive and action weight
owner: DATA_PING_RESEARCH_LAB
```

### OQ-B1-REPRO — 21 versus 22 B1 fires

```yaml
status: OPEN_MEDIUM
question: Which exact warm-up, eligibility or date-boundary rule explains the frozen 21-fire series versus direct 22-fire recomputation?
additional_date: 2025-03-04
next_action: independent source-backed reproduction without threshold changes
owner: RESEARCH_LAB_TRUTH_LAYER
```

### OQ-STABLE-LATENCY — operational availability

```yaml
status: OPEN_FORWARD_ONLY
question: Can stablecoin availability or activity context survive actual source latency and revision handling prospectively?
historical_findings:
  - one additional delay day changed expanding-deployment return from +17.54% to -4.98%
  - supply-growth-plus-activity did not behave as a reliable risk-on state
next_action: log source and operational availability timestamps; no standalone strategy promotion
owner: DATA_PING_RESEARCH_LAB
```
