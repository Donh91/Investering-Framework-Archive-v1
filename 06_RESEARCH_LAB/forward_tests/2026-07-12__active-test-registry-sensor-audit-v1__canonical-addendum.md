# Active Test Registry — Sensor Audit v1 Addendum

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** active tests / blocker repair / instrumentation  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`, `06_RESEARCH_LAB/audit_summaries/2026-07-12__sensor-survival-timing-placebo-regime-audit-v1__canonical.md`

No new test is created. This addendum repairs blocker states and instrumentation for existing T3, T4 and T6.

## T3 — Graduated Alt Deployment

```yaml
test_id: GRADUATED_DEPLOYMENT_V1_1
status: PARTIALLY_UNBLOCKED_BREADTH_BLOCKED
newly_available_fields:
  - CMC_DIRECT_SOURCE_CONVENTION_BTC_D
  - STABLECOIN_DEPLOYMENT_PROXY_HISTORY
  - ETHBTC
remaining_primary_blocker:
  - FROZEN_UNIVERSE_ALTCOIN_BREADTH
secondary_required_fields:
  - ALT_PROXY_WITH_POINT_IN_TIME_UNIVERSE
  - FAKE_ROTATION_DENSITY_FROZEN_METHOD
valid_source_rows: 0_UNCHANGED
valid_outcome_rows: 0_UNCHANGED
portfolio_authority: ZERO
```

Availability of data fields does not create a valid row or edge.

## T4 — Pullback Edge outcomes and C2 instrumentation

Future eligible Pullback Edge rows under the existing test lineage must add:

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

C2 receives expanded forward logging as LEAN_WARNING. No retrospective audit row is counted as prospective evidence.

## T6 — Rotation Survival Forward

```yaml
test_id: ROTATION_SURVIVAL_FORWARD
status: QUEUED_BREADTH_BLOCKED
available_axes:
  - ETHBTC
  - CMC_BTC_D
  - STABLECOIN_SUPPLY
  - NORMALIZED_DEX_ACTIVITY
  - PRICE_STRUCTURE
remaining_primary_blocker:
  - FROZEN_UNIVERSE_ALTCOIN_BREADTH
flow_axis_status: AVAILABLE_WITH_REVISION_AND_LATENCY_CONTROLS
forward_rows: 0_UNCHANGED
```

DEX change and DEX/supply ratio are one activity family, not two independent axes.

## Prospective evidence boundary

```text
row_validity: NOT_APPLICABLE_NO_NEW_ROW
coverage_readiness: BLOCKED_BY_BREADTH
edge_or_promotion_status: NO_CHANGE
retrospective_rows_promoted: 0
```
