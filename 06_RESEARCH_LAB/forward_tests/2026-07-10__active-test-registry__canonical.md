# Active Test Registry

**Dato:** 2026-07-11  
**Status:** CANONICAL  
**Område:** forward tests / active evidence production  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** GPT-5.6 Fresh Eyes Audit Implementation; Rule and Evidence Registry  
**New-engine freeze:** ACTIVE through 2026-08-09

---

## Registry contract

This is the only active test navigation list during the 30-day engine freeze.

Every test must expose:

```text
test_id
question
status
start_time
required_fields
rows_total
valid_source_rows
valid_outcome_rows
divergence_days
benchmark
blocked_by
next_review
promotion_condition
kill_condition
owner
```

No new test may be added unless it replaces, merges or directly repairs one listed here.

---

## T1 — FRLP v0.1 Range Forward Ledger

```yaml
test_id: FRLP_V0_1
status: ACTIVE_FORWARD_TEST
question: Does the official CN range or human adjustment beat DUMB_1_5 and DUMB_2_0 on forward verified rows?
start: CN_15
required_fields: [frozen_official_range, frozen_dumb_1_5_range, frozen_dumb_2_0_range, independently_verified_actual_high_low, winkler_scores, adjustment_alpha]
rows_total: PENDING_REGISTRY_SYNC
valid_source_rows: PENDING_REGISTRY_SYNC
valid_outcome_rows: PENDING_REGISTRY_SYNC
benchmark: DUMB_1_5_AND_DUMB_2_0
blocked_by: NONE_FOR_NEW_FORWARD_ROWS
next_review: WEEKLY
promotion_condition: sustained baseline outperformance under FRLP rules
kill_condition: apply existing K1_K8; suspend human adjustment if it continues to lose
owner: CYCLE_NAVIGATOR_RESEARCH_LAB
```

## T2 — BTC Partial versus WAIT

```yaml
test_id: GATE_BTC_PARTIAL_FT_1
status: ACTIVE_NEEDS_ROWS
question: Does partial BTC permission improve opportunity-cost-adjusted performance versus full WAIT without unacceptable drawdown?
required_fields: [timestamped_framework_state, WAIT_action, BTC_partial_action, actual_decision_divergence, return, max_adverse_excursion, max_favorable_excursion, drawdown, opportunity_cost, false_permission_cost]
rows_total: 1_INITIALIZATION_ROW
valid_source_rows: 0_AT_AUDIT
valid_outcome_rows: 0_AT_AUDIT
divergence_days: 0_AT_AUDIT
benchmark: WAIT
blocked_by: NONE_FOR_BTC_ONLY_ROWS
next_review: DAILY_ROW_CAPTURE_WEEKLY_REVIEW
promotion_condition: repeated valid divergence with superior risk-adjusted outcome
kill_condition: suspend if no decision divergence during the fixed observation window or if drawdown cost dominates
owner: GOVERNANCE_RESEARCH_LAB
```

## T3 — Graduated Alt Deployment

```yaml
test_id: GRADUATED_DEPLOYMENT_V1_1
status: DATA_BLOCKED
question: Can staged alt deployment reduce false negatives without materially increasing fake-rotation loss?
required_fields: [breadth, BTC_D, ETHBTC, stablecoin_deployment, alt_proxy, fake_rotation_density]
rows_total: 0_VALID
valid_source_rows: 0
valid_outcome_rows: 0
benchmark: WAIT_AND_BTC_ONLY
blocked_by: [INCOMPLETE_BREADTH, INCOMPLETE_BTC_D, INCOMPLETE_DEPLOYMENT]
next_review: WHEN_REQUIRED_FIELDS_EXIST
promotion_condition: valid divergence rows and superior outcome
kill_condition: no pseudo-rows while blocked; suspend if data cannot become production-grade
owner: GOVERNANCE_RESEARCH_LAB
```

## T4 — Pullback Edge Event Outcomes

```yaml
test_id: PULLBACK_EDGE_20260708_01_OUTCOMES
status: ACTIVE
question: Did the edge detector provide market-stress value and/or tactical trim execution value?
required_fields: [framework_approved_anchor, 24H_outcome, 72H_outcome, 7D_outcome, event_close_outcome, action_counterfactual]
rows_total: 1_MATURED_24H_PLUS_EVENT_PATH
valid_source_rows: 1_MATURED_24H
valid_outcome_rows: 1_MATURED_24H
benchmark: NO_TRIM_HOLD_CORE
blocked_by: [72H_NOT_YET_RECONCILED, 7D_NOT_YET_MATURED_OR_RECONCILED, EVENT_CLOSE_PENDING]
next_review: AT_EACH_MATURITY
promotion_condition: main-framework ratification after sufficient maturity
kill_condition: close event and stop collection after formal event close plus final row
owner: DATA_PING_GOVERNANCE
```

## T5 — Cumulative FNP Ledger

```yaml
test_id: FNP_CUMULATIVE
status: ACTIVE_NEEDS_ROWS
question: Which locks are correct restraint and which create genuine missed opportunity?
required_fields: [frozen_horizon, asset_tier, blocked_action, benchmark_action, actual_cost, drawdown_avoided, missed_upside, final_classification]
rows_total: INSUFFICIENT
valid_source_rows: INSUFFICIENT
valid_outcome_rows: INSUFFICIENT
benchmark: WAIT_OR_EXISTING_PERMISSION
blocked_by: ROW_PRODUCTION
next_review: WEEKLY
promotion_condition: repeated source-backed divergence and stable loss function
kill_condition: redesign if horizons are not frozen or classifications are retrospective
owner: GOVERNANCE_RESEARCH_LAB
```

## T6 — Rotation Survival Forward Row

```yaml
test_id: ROTATION_SURVIVAL_FORWARD
status: QUEUED_DATA_DEPENDENT
question: Does survival across ETHBTC, breadth, BTC_D, deployment and flow outperform first-cross logic?
required_fields: [ETHBTC_hold_days, breadth_state, BTC_D_state, deployment_state, flow_congruence, exit_side_outcome]
rows_total: 0_FORWARD_CONFIRMED
valid_source_rows: 0
valid_outcome_rows: 0
benchmark: FIRST_ETHBTC_CROSS
blocked_by: MULTI_AXIS_DATA_COMPLETENESS
next_review: WHEN_FIELDS_AVAILABLE
promotion_condition: lower fake rate and acceptable delay
kill_condition: kill axes with no incremental value; retire test if data remains unavailable
owner: RESEARCH_LAB
```

## T7 — TechDev Claim and Revision Ledger

```yaml
test_id: TECHDEV_CLAIM_LEDGER
status: ACTIVE_SOURCE_IMPORT_COMPLETE_BATCH_1_CONTINUATION_OPEN
question: How accurate are TechDev roadmap, timing, range and trade claims when scored separately?
source_scope:
  historical_paid_archive_batch_1: 2021-11-04_TO_2025-10-13
  later_issue_sequence: ISSUES_81_TO_95
  topping_signal_sequence: UPDATES_1_2_3_4_6_7_8
source_documents_accounted_for: 94
exact_duplicate_upload_copies_ignored: 21
required_fields: [claim_id, issue_date, original_claim, target, time_window, invalidation, revision, final_outcome, timing_error, range_error, trade_result_if_applicable, framework_action_impact]
rows_total: 120_SOURCE_BACKED_CLAIM_ROWS_PLUS_7_HISTORICAL_SIGNAL_SNAPSHOTS
valid_source_rows: 120_UNSCORED
valid_outcome_rows: 0
scored_rows: 0
benchmark: CATEGORY_SPECIFIC_SIMPLE_TIME_RANGE_AND_ACTION_BASELINES
blocked_by: [VERIFIED_ACTUALS_METHOD_NOT_FROZEN, CATEGORY_SCORING_METHOD_NOT_FROZEN]
next_review: NEW_SOURCE_BATCH_OR_SCORING_PROTOCOL_FREEZE
promotion_condition: enough original-source rows and verified outcomes for category-specific calibration
kill_condition: none for archive continuity; reduce framework weight if calibrated results are poor
owner: RESEARCH_LAB
source_manifest: 08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-paid-archive-batch-1__source-manifest.md
continuation_handoff: 00_ARCHIVE_CONTROL/2026-07-11__techdev-historical-archive-continuation-handoff.md
```

Rules for T7:

```text
Roadmap, timing, range, trade and framework-action impact remain separate.
Original claims and later revisions remain side by side.
Historical source ingestion does not change live gates or portfolio action.
Invalidation drift, analogy flexibility and correlated confluence are metadata flags, not scores.
```

## T8 — Multi-Ping Aggregation Value

```yaml
test_id: MULTI_PING_AGGREGATION_VALUE
status: QUEUED
question: Does 3-4 ping aggregation reduce false flips versus latest ping alone without excessive delay?
required_fields: [latest_ping_state, aggregation_state, eventual_framework_state, false_flip_count, delay_minutes]
rows_total: 0
valid_source_rows: 0
valid_outcome_rows: 0
benchmark: LATEST_PING_ONLY
blocked_by: ROW_INSTRUMENTATION
next_review: AFTER_10_ELIGIBLE_STATE_CHANGES
promotion_condition: meaningful false-flip reduction with acceptable delay
kill_condition: no improvement or unacceptable delay
owner: DATA_PING_RESEARCH_LAB
```

## T9 — Chief Reproducibility

```yaml
test_id: CHIEF_REPRODUCIBILITY
status: QUEUED
question: Does the same ratified framework input produce the same action class across repeated runs/models?
required_fields: [frozen_input_packet, action_class, rationale_tags, run_model, run_time]
rows_total: 0
valid_source_rows: 0
valid_outcome_rows: 0
benchmark: EXACT_MATCH_AND_ALLOWED_VARIANCE
blocked_by: TEST_PACKET_CREATION
next_review: AFTER_10_PACKETS
promotion_condition: stable action class with bounded wording variation
kill_condition: merge Chief into deterministic mapping if reproducibility is poor
owner: GOVERNANCE_RESEARCH_LAB
```

## T10 — Archive Lineage Integrity

```yaml
test_id: ARCHIVE_LINEAGE_INTEGRITY
status: ACTIVE
question: Can every official forecast be traced from source Master Monday through ratification, CN handoff, actual and score?
required_fields: [forecast_id, source_master_monday, ratification_receipt, CN_handoff, verified_actual, score_row]
rows_total: W28_GAP_DETECTED
valid_source_rows: PENDING_REPAIR
valid_outcome_rows: PENDING_REPAIR
benchmark: COMPLETE_LINEAGE
blocked_by: W28_RATIFIED_SOURCE_UNRESOLVED
next_review: IMMEDIATE_AND_WEEKLY
promotion_condition: 100_percent lineage for official scored rows
kill_condition: none; incomplete rows remain unscored
owner: ARCHIVE_MASTER_MONDAY_GOVERNANCE
```

---

## Freeze enforcement

```text
NEW_TEST_WITHOUT_REGISTRY_ENTRY: FORBIDDEN
DATA_BLOCKED_PSEUDO_ROW: FORBIDDEN
SCHEMA_CREATION_COUNTED_AS_VALID_ROW: FORBIDDEN
RETROSPECTIVE_STORY_COUNTED_AS_FORWARD_TEST: FORBIDDEN
SOURCE_ROW_COUNTED_AS_OUTCOME_ROW: FORBIDDEN
```
