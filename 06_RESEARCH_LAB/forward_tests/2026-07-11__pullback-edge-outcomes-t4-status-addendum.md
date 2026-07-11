# T4 Pullback Edge Outcomes — Status Addendum

**Date:** 2026-07-11  
**Test:** `PULLBACK_EDGE_20260708_01_OUTCOMES`  
**Status:** EVENT_CLOSED / 7D_FOLLOWUP_PENDING  
**Supersedes for T4 status fields only:** the prior T4 block in `2026-07-10__active-test-registry__canonical.md`

```yaml
test_id: PULLBACK_EDGE_20260708_01_OUTCOMES
status: ACTIVE_EVENT_CLOSED_7D_FOLLOWUP
question: Did the edge detector provide market-stress value and/or tactical trim execution value?
rows_total:
  matured_market_horizon_rows: 2
  framework_event_close_rows: 1
valid_source_rows: 2_MATURED_MARKET_OUTCOMES
valid_outcome_rows: 2_MATURED_HORIZONS
framework_judgment_rows: 1_EVENT_CLOSE
benchmark: NO_TRIM_HOLD_CORE
current_results:
  market_stress_detection: PARTIALLY_SUPPORTED_SHORT_LIVED_STRESS
  tactical_trim_execution_24h_72h: NOT_SUPPORTED
  downgrade_logic: SUPPORTED
  close_logic: SUPPORTED
blocked_by:
  - 7D_NOT_YET_MATURED
  - FINAL_ACTION_COUNTERFACTUAL_RECONCILIATION
next_review: 2026-07-15T14:03:00Z_OR_FIRST_VERIFIABLE_RUN_AFTER
promotion_condition: repeated event-level value across multiple valid events
kill_condition: retire or redesign if stress warnings repeatedly provide no incremental decision value
owner: DATA_PING_GOVERNANCE
```

The closed event must not be reopened by the 7D row. A later qualifying deterioration requires a new event ID.
