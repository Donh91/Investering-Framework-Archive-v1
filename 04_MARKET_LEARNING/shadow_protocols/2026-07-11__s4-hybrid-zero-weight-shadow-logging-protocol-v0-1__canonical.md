# S4 Hybrid Zero-Weight Shadow Logging Protocol v0.1

**Date:** 2026-07-11  
**Status:** ACTIVE_SHADOW  
**Authority:** ZERO_WEIGHT / NO_EXECUTION_AUTHORITY

**Operational review:** 2026-08-26 - `OWNER_BLOCKED`, zero valid Exit Ladder rows

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

## 2. Exit Ladder E0–E7 Log

Purpose: instrument the framework's exit-side blind spot.

States:
- E0 NEUTRAL
- E1 PRE_ALT_PREP
- E2 ALT_ACTIVE_MONITOR
- E3 PROFIT_READINESS
- E4 DISTRIBUTION_WARNING
- E5 EXIT_RISK_ESCALATION
- E6 TERMINAL_ALERT
- E7 POST_TOP_PROTECTION

Rules:
- all states are walk-forward and zero weight
- E1–E4 contain no trade-size or sell instruction
- no state may skip a level
- every transition needs an explicit falsifier
- only governance may approve action language
- minimum eight forward rows per material state before any authority discussion

### 2.1 Current operational block

```yaml
exit_ladder_owner_status: OWNER_BLOCKED
valid_rows: 0
row_production: OFF
blockers:
  - NATIVE_E0_E7_OUTPUT_UNAVAILABLE
  - TRANSITION_CONDITIONS_AND_FALSIFIERS_UNFROZEN
  - PRODUCER_AND_EMISSION_BINDING_UNDEFINED
  - ROW_LIFECYCLE_FOR_MULTIPLE_OUTCOME_HORIZONS_UNFROZEN
  - ACTIVE_TEST_OWNER_ABSENT
```

The existing CSV remains a header-only scaffold. It must not be populated until
all blockers above are resolved in one prospective, causally timestamped owner
contract with a producer and validator.

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

This section makes the same missing native output explicit at the Exit Ladder
owner. It creates no state, threshold, warning, test, score or portfolio
authority. The next valid action is an owner-level governance review that
either freezes a native E0-E7 producer and complete ledger lifecycle or retires
the scaffold.

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
