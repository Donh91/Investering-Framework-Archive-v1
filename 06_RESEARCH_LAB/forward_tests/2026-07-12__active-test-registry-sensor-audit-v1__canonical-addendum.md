# Active Test Registry — Sensor Audit v1.1 Addendum

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** active tests / blocker repair / instrumentation  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`, `06_RESEARCH_LAB/audit_summaries/2026-07-12__sensor-survival-timing-placebo-regime-audit-v1__canonical.md`, `06_RESEARCH_LAB/audit_summaries/2026-07-12__marginal-decision-value-and-breadth-truth-program-v1__canonical.md`

No new test is created. This addendum repairs blocker states and instrumentation for existing T3, T4 and T6.

## T3 — Graduated Alt Deployment

```yaml
test_id: GRADUATED_DEPLOYMENT_V1_1
status: FORWARD_ONLY_NOT_PROMOTION_READY
historical_axes_available:
  - CMC_DIRECT_SOURCE_CONVENTION_BTC_D
  - STABLECOIN_DEPLOYMENT_PROXY_HISTORY
  - ETHBTC
  - CMC_HISTORICAL_WEEKLY_FROZEN_UNIVERSE_BREADTH
historical_breadth_result:
  predictive_gate: NOT_SUPPORTED
  descriptive_context: RETAIN_ZERO_WEIGHT
remaining_data_limitations:
  - DAILY_POINT_IN_TIME_ALTCOIN_BREADTH
  - HISTORICAL_30DMA_BREADTH
  - PROSPECTIVE_BREADTH_COMPLETE_DECISION_ROWS
  - ALT_PROXY_WITH_POINT_IN_TIME_UNIVERSE_FOR_DAILY_EXECUTION
  - FAKE_ROTATION_DENSITY_FROZEN_METHOD
valid_source_rows: 0_UNCHANGED
valid_outcome_rows: 0_UNCHANGED
portfolio_authority: ZERO
```

Availability of historical weekly breadth does not create a valid forward row or edge. The historical gatekeeper hypothesis failed; T3 may continue only as prospective falsification under its existing owner.

## T4 — Pullback Edge outcomes and C2 instrumentation

Future eligible Pullback Edge rows under the existing test lineage must preserve:

```yaml
required_fields_add:
  - events_total
  - events_eligible
  - events_excluded
  - exclusion_reason_by_event
  - event_window_definition
  - signal_attribution_method
  - A1_state
  - A2_state
  - A3_state_shadow_only
  - C1_state
  - C2_state
  - D_confirmation_state
  - source_timestamp
  - operational_availability_timestamp
  - framework_acceptance_timestamp
```

C2 receives expanded forward logging as LEAN_WARNING. The latency audit requires event-driven or daily capture. No retrospective audit row is counted as prospective evidence, and no live-authority increase is authorized.

## T6 — Rotation Survival Forward

```yaml
test_id: ROTATION_SURVIVAL_FORWARD
status: FORWARD_ONLY_NOT_PROMOTION_READY
available_axes:
  - ETHBTC
  - CMC_BTC_D
  - STABLECOIN_SUPPLY
  - NORMALIZED_DEX_ACTIVITY
  - PRICE_STRUCTURE
  - CMC_HISTORICAL_WEEKLY_FROZEN_UNIVERSE_BREADTH
breadth_role:
  predictive_gate: ZERO_WEIGHT
  descriptive_participation_confirmation: SHADOW_ALLOWED
remaining_requirements:
  - PROSPECTIVE_BREADTH_COMPLETE_ROWS
  - DAILY_POINT_IN_TIME_BREADTH_IF_DAILY_GATE_IS_TESTED
  - SOURCE_AND_OPERATIONAL_AVAILABILITY_TIMESTAMPS
  - SUFFICIENT_INDEPENDENT_REAL_AND_FAKE_EPISODES
flow_axis_status: AVAILABLE_WITH_REVISION_AND_LATENCY_CONTROLS
forward_rows: 0_UNCHANGED
```

DEX change and DEX/supply ratio remain one activity family, not two independent axes. Legacy alt-phase labels are not a substitute for point-in-time breadth.

## Prospective evidence boundary

```text
operation: READ_ONLY_STATUS_REPAIR
row_type: NOT_A_LEDGER_ROW
row_validity: NOT_APPLICABLE_NO_NEW_ROW
coverage_readiness: FORWARD_ROWS_INSUFFICIENT
edge_or_promotion_status: NO_CHANGE
retrospective_rows_promoted: 0
```
