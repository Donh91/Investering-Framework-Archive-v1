# DATA PING Deep-Capture Escalation Protocol v1

**Date:** 2026-07-28 22:35 CEST  
**Status:** CANONICAL_OPERATIONAL  
**Area:** DATA PING supplemental collection / weekly reconciliation / event-driven evidence recovery  
**Primary owner:** `02_DATA_PING/`  
**Request ledger:** `02_DATA_PING/operational_handoffs/deep_capture_request_ledger_v1.json`  
**Authority boundary:** data-request generation, source completion and research evidence only. This protocol has no authority to change market state, thresholds, gates, experiment outcomes, permissions, portfolio actions or final holdout status.

## 1. Purpose

The normal DATA PING remains the bounded deterministic collector.

This protocol allows the main framework to ask the user for a targeted Custom GPT collection prompt when the normal packet does not contain enough historical depth, event resolution or source detail for reliable calibration.

It creates two complementary capture lanes:

1. `WEEKLY_DEEP_CAPTURE`
2. `EVENT_DRIVEN_DEEP_CAPTURE`

The goal is not more data for its own sake. The goal is to preserve the exact rows required to:

- reconcile the week's accepted DATA PINGs;
- fill bounded gaps without reconstructing values;
- mature registered experiments;
- preserve point-in-time event paths;
- evaluate threshold rejection, acceptance and persistence;
- calibrate Full, Reduced and Minimal shadow profiles;
- distinguish source failure from market behavior;
- support later research without hindsight rewriting.

## 2. Role separation

```yaml
Custom_GPT:
  role: NON_BINDING_DATA_COLLECTOR
  may:
    - retrieve_requested_rows
    - preserve_source_timestamps
    - compute_explicitly_requested_deterministic_features
    - package_large_raw_outputs_with_manifest_and_hashes
  may_not:
    - interpret_framework_state
    - grant_rotation_rebuy_or_entry_permission
    - rescore_closed_experiments
    - recommend_portfolio_action

ChatGPT_Main_Framework:
  role: REQUEST_DESIGN_RECONCILIATION_AND_GOVERNANCE
  owns:
    - trigger_adjudication
    - copy_ready_prompt_generation
    - duplication_control
    - source_authority_check
    - experiment_relevance
    - GitHub_archiving
    - canonical_effect_decision
```

## 3. Weekly deep-capture rule

### 3.1 Due condition

Evaluate once per ISO week after the final settled Sunday/Copenhagen session is available and before the full Master Monday synthesis.

A weekly request is due when one or more of the following is true:

- the week's accepted DATA PINGs do not form a complete settled weekly path;
- verified BTC or ETH weekly high, low or close is missing;
- direct settled ETH/BTC weekly structure is incomplete;
- an active experiment requires rows not retained by the ordinary packets;
- source revisions, missing rows or incompatible methods prevent weekly reconciliation;
- event windows need higher-resolution rows for later outcome analysis;
- the weekly data-gate owner explicitly marks a blocking or conditional gap.

Do not issue a second weekly request when an equivalent complete package already exists for the same ISO week and source-method combination.

### 3.2 Default weekly scope

Request only the data not already preserved.

Preferred bounded structure:

```yaml
full_week:
  hourly_rows:
    - BTCUSDT
    - ETHUSDT
    - ETHBTC
  settled_daily_rows:
    settlement_timezone: Europe/Copenhagen
  verified_weekly_OHLC:
    - BTC
    - ETH
    - direct_ETHBTC_close

material_event_windows_only:
  five_minute_rows: REQUIRED_WHEN_EVENT_EXISTS
  one_minute_rows: ONLY_AROUND_PRECISE_TRIGGER_OR_DISLOCATION

supporting_layers_when_missing_or_material:
  - spot_taker_share
  - funding
  - open_interest
  - basis
  - cross_venue_parity
  - breadth_rows_and_membership_hash
  - ETF_settled_rows_and_revision_state
  - CFGI_snapshots
  - macro_release_rows
```

A full week of one-minute rows is forbidden unless a registered test explicitly requires it and the response budget is addressed by file packaging.

## 4. Event-driven deep-capture rule

### 4.1 Trigger principle

Issue a targeted request when an accepted DATA PING, a registered experiment or a verified catalyst reveals a material event whose path cannot be reconstructed reliably from normal packet summaries.

One directly registered experiment trigger is sufficient.

Otherwise require either:

- one severe trigger; or
- two independent material triggers in the same event window.

### 4.2 Default trigger matrix

Registry-specific thresholds override these defaults.

```yaml
PRICE_DISPLACEMENT:
  material:
    - absolute_move_4h_gte_3pct
    - absolute_move_24h_gte_5pct
    - registered_level_breach_or_failed_reclaim
  severe:
    - absolute_move_4h_gte_5pct
    - liquidation_or_gap_event_with_missing_intraday_path

ETHBTC_THRESHOLD:
  material:
    - touch_cross_or_settled_close_at_0_0275
    - touch_cross_or_settled_close_at_0_0300
    - two_or_more_rejections_without_settled_acceptance
    - first_settled_acceptance_or_failed_retest
  severe:
    - registered_gate_changes_settled_state

BREADTH:
  material:
    - advance_ratio_change_gte_15_percentage_points_between_accepted_pings
    - advance_ratio_below_15pct
    - advance_ratio_above_50pct
    - price_strength_with_breadth_deterioration
  severe:
    - breadth_regime_flip_with_membership_and_hash_available

DERIVATIVES:
  material:
    - open_interest_change_4h_gte_5pct
    - open_interest_change_24h_gte_10pct
    - funding_sign_flip_with_price_displacement
    - owner_challenger_basis_or_mark_deviation_beyond_registered_tolerance
    - sustained_taker_imbalance_relevant_to_active_event
  severe:
    - leverage_unwind_or_liquidation_event_with_cross_venue_confirmation

ETF_FLOW:
  material:
    - absolute_single_asset_settled_flow_gte_250m_usd
    - combined_absolute_settled_flow_gte_500m_usd
    - BTC_ETH_sign_divergence_for_two_settled_sessions
    - source_revision_gte_50m_usd
  severe:
    - issuer_or_methodology_change_affecting_series_comparability

SOURCE_INTEGRITY:
  material:
    - owner_challenger_parity_failure
    - two_or_more_core_source_groups_unavailable
    - revision_or_cache_behavior_changes_current_evidence
    - missing_row_rendered_as_numeric_zero
  severe:
    - owner_source_lineage_or_settlement_semantics_uncertain

EXPERIMENT_MATURITY:
  material:
    - maturity_due_within_6h_and_required_rows_missing
    - trigger_closeout_or_supersession_needs_exact_path
    - post_window_design_question_needs_non_rescoring_evidence
  severe:
    - valid_A_class_receipt_cannot_be_completed_without_prompt_recovery

CATALYST_CONFOUND:
  material:
    - scheduled_primary_source_event_within_24h_and_active_market_experiment
    - unscheduled_regulatory_protocol_or_market_structure_event
  severe:
    - catalyst_changes_source_availability_or_market_microstructure
```

These thresholds create a data-request review. They are not trading signals, market permissions or automatic framework changes.

## 5. Copy-ready prompt contract

When a request is due, the main framework must notify the user and provide exactly one copy-ready Custom GPT prompt.

The prompt must include:

```yaml
request_id: DCR-YYYYMMDD-<type>-<sequence>
request_type: WEEKLY_DEEP_CAPTURE | EVENT_DRIVEN_DEEP_CAPTURE
trigger_reason:
reference_run_ids:
reference_snapshot_times:
exact_window_start_utc:
exact_window_end_utc:
settlement_timezones:
required_instruments_and_series:
required_row_granularity:
required_methods_or_owner_sources:
required_source_timestamps:
required_hashes_and_row_counts:
known_complete_fields_to_omit:
missing_fields_only:
output_packaging:
main_framework_ingest_boundary:
```

The generated prompt must:

- ask only for missing or event-relevant evidence;
- preserve direct, derived and proxy classifications;
- preserve UTC and Copenhagen-settled rows separately;
- require exact source and retrieval timestamps;
- require row counts, gaps, duplicates and SHA-256 when files are produced;
- label in-progress rows separately from settled rows;
- treat missing as `UNKNOWN`, never zero;
- prohibit interpolation and reconstruction;
- prohibit framework interpretation and portfolio advice;
- split a large request deterministically rather than silently truncating it;
- return a manifest when output is packaged as ZIP, NDJSON, CSV or JSON files;
- include one compact `START MAIN-FRAMEWORK INGEST` summary after the raw artifacts are complete.

## 6. Request ledger

Every issued request must be appended to:

`02_DATA_PING/operational_handoffs/deep_capture_request_ledger_v1.json`

Required fields:

```yaml
request_id:
request_type:
created_at_utc:
iso_week:
trigger_class:
trigger_evidence_ids:
reference_data_ping_runs:
requested_window:
requested_fields:
status: PREPARED | SENT_TO_CUSTOM_GPT | RESPONSE_RECEIVED | VALIDATED | PARTIAL | CANCELLED_DUPLICATE
response_artifact_ids:
validation_result:
resolved_gaps:
unresolved_gaps:
canonical_effect: NONE
portfolio_effect: NONE
```

A prepared prompt is not evidence. A user-confirmed Custom GPT response is not accepted evidence until the main framework validates source, time, method, settlement and duplication.

## 7. Deduplication and event clusters

- Repeated pings inside the same event cluster do not automatically create new requests.
- Extend the existing request window when the event is still open and the requested package has not been delivered.
- Create a new request only when a new settled state, independent event cluster, source failure class or experiment maturity condition appears.
- Weekly and event-driven requests may be combined when their required windows and methods overlap.
- Do not create retrospective A-class rows from a deep-capture response.

## 8. Thread-handover requirement

Every future DATA PING handover must preserve:

- this protocol path and version;
- the current request-ledger path;
- pending or partially fulfilled request IDs;
- the latest completed weekly deep-capture package;
- active event-driven windows;
- any Custom GPT prompt already prepared but not yet sent;
- explicit tasks that must not be duplicated.

A successor thread must check the ledger before issuing a new deep-capture prompt.

## 9. Notification discipline

Notify the user only when:

- a weekly deep-capture prompt is genuinely required;
- an event-driven trigger creates a material evidence gap;
- a pending request needs correction or continuation;
- a completed package materially resolves a source, experiment or design question.

The notification must say why the request is useful and provide the full copy-ready prompt. Do not merely ask the user to obtain “more data.”

## 10. Governance and forbidden behavior

Forbidden:

- expanding the standard DATA PING layout merely to avoid targeted requests;
- using a request trigger as a market signal;
- asking Custom GPT to ratify framework state;
- duplicate full-history collection when owner artifacts already exist;
- silently changing settlement timezone;
- mixing UTC and Copenhagen daily rows;
- treating an incomplete session as settled;
- using current constituents to reconstruct historical breadth;
- converting a deep-capture response into retrospective prospective evidence;
- opening the final holdout;
- automatic threshold, sensor, stack or portfolio changes.

## 11. Current activation state

```yaml
protocol_version: 1
weekly_deep_capture: ACTIVE_ON_GAP_OR_RECONCILIATION_NEED
event_driven_deep_capture: ACTIVE_ON_MATERIAL_TRIGGER
standard_data_ping_layout_change: NONE
user_prompt_delivery: COPY_READY_WHEN_DUE
request_ledger_required: YES
future_thread_handover_required: YES
canonical_market_authority: ZERO
portfolio_authority: ZERO
```
