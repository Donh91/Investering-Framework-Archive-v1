# S4 Hybrid Zero-Weight Shadow Logging Protocol v0.1

**Date:** 2026-07-11  
**Status:** ACTIVE_SHADOW  
**Authority:** ZERO_WEIGHT / NO_EXECUTION_AUTHORITY

**Operational review:** 2026-08-26 - Exit Ladder `RETIRED_UNIMPLEMENTED`, zero valid rows

## 1. Percentile Gate Log

Purpose: compare fixed ETH/BTC gates with cycle-normalized gates.

Default shadow calculations:
- rolling window: 365 settled daily closes
- `ratio_percentile`
- repair candidate: percentile > p60
- rotation candidate: percentile > p80

These thresholds are Fable design hypotheses, not active rules.

Log every eligible fixed-gate cross in parallel with:
- fixed gate
- ratio percentile
- 365d distribution coverage
- hold days
- 14/30/60d outcomes
- fake-fast / fake-standard / slow-bleed / real-candidate label

Kill:
- after at least 10 resolved crosses, if percentile gates do not beat fixed gates on pre-registered fake-rate/retention metrics, reject or redesign.

## 2. Exit Ladder E0-E7 - retired unimplemented

Historical design purpose: instrument the framework's exit-side blind spot.

The following states are retained for provenance only. They are not current framework vocabulary:
- E0 NEUTRAL
- E1 PRE_ALT_PREP
- E2 ALT_ACTIVE_MONITOR
- E3 PROFIT_READINESS
- E4 DISTRIBUTION_WARNING
- E5 EXIT_RISK_ESCALATION
- E6 TERMINAL_ALERT
- E7 POST_TOP_PROTECTION

Current disposition:

```yaml
exit_ladder_owner_status: RETIRED_UNIMPLEMENTED
valid_rows: 0
row_production: PERMANENTLY_OFF_UNLESS_EXPLICITLY_REACTIVATED
current_decision_vocabulary: THREE_HORIZON_ACTION_COMPASS_v1_1
historical_scaffold_preserved: true
```

No E-state may be emitted, inferred, populated, scored or mapped from current Action Compass state, warning or action fields. Any future reactivation would require a new explicit canonical owner, prospective producer, complete transition and falsifier specification, row lifecycle, validator, Active Test Registry repair and separate governance approval. The retired design receives no grandfathered authority.

### 2.1 Current operational block

```yaml
exit_ladder_owner_status: RETIRED_UNIMPLEMENTED
valid_rows: 0
row_production: OFF
retirement_reasons:
  - NATIVE_E0_E7_OUTPUT_NEVER_IMPLEMENTED
  - TRANSITION_CONDITIONS_AND_FALSIFIERS_NEVER_FROZEN
  - PRODUCER_AND_EMISSION_BINDING_NEVER_DEFINED
  - ROW_LIFECYCLE_NEVER_FROZEN
  - ACTIVE_TEST_OWNER_ABSENT
  - THREE_HORIZON_ACTION_COMPASS_NOW_SOLE_CURRENT_DECISION_VOCABULARY
```

The existing CSV remains a header-only historical scaffold. It must not be populated.

The Three-Horizon Action Compass is an output and decision-translation
contract, not an E0-E7 evaluator. Its Lane-3 state and optional warning
vocabulary must not be mapped directly to E4, E5 or E6 and counted as ladder
transitions. In particular:

- `warning: NONE` is not a warning event;
- a direct E0 to E4, E5 or E6 row would violate the no-level-skipping rule;
- one compass emission must not be retrospectively expanded into 30, 90 and
  180 day evidence without a frozen row-lifecycle contract;
- no row may be routed to FNP without an actual frozen decision divergence;
- no row may be routed to Rotation Survival merely because that schema has an
  `exit_side_outcome` field.

The separate prospective dual-run already records `TRIM_EXIT_STATE` as
`NATIVE_OUTPUT_UNAVAILABLE_FOR_PROSPECTIVE_COUNTERFACTUAL` in:

`04_MARKET_LEARNING/backtests/framework_backtest_readiness_build_v1/prospective_dual_run_v2/r1_evidence_validity_repair/R1_08_PRIMARY_LANE_VALIDITY_SUMMARY.md`

This section closes the blocked owner review by retirement. It creates no state,
threshold, warning, test, score or portfolio authority.

## 3. Challenger Log

Purpose: score a contemporaneous alternative against the official framework.

Requirements:
- same data cutoff
- same source quality
- frozen before the outcome
- no post-hoc parameter changes
- explicit kill criteria at birth
- challenger never alters official output

## 4. Promotion boundary

No component can move beyond shadow unless:
- minimum frozen sample is met
- benchmark is beaten
- performance survives regime stratification
- placebo/ablation checks do not falsify it
- governance ratifies the change
