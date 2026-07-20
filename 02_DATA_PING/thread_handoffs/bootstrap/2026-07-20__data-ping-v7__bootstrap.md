# DATA PING V7 Bootstrap

**Status:** `PREPARED_NOT_ACTIVE`  
**Authority:** continuity and source-contract loading only  
**Activation:** first complete V7 packet reviewed and accepted by ChatGPT/Main Framework  
**Current active source:** `DATA PING_V6`

## Startup instruction

Read in this exact order:

```text
1. 02_DATA_PING/thread_handoffs/latest_thread_handover_state.json
2. 02_DATA_PING/thread_handoffs/checkpoints/2026-07-20__data-ping-v6__recovery-checkpoint.md
3. 02_DATA_PING/version_governance/2026-07-19__data-ping-v6-raw-collector-contract-v1__canonical.md
4. 02_DATA_PING/thread_handoffs/history/2026-07-19__data-ping-v5-to-v6__handover.md
5. 02_DATA_PING/operational_handoffs/latest_decision_context_state.json
6. 02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
7. the accepted payload, receipt, supplement and active registry referenced by those pointers
8. 02_DATA_PING/operational_handoffs/latest_validation_only_observation_state.json
9. the validation-only supplement referenced by that pointer
10. 03_WEEKLY_OPERATIONS/master_monday/latest_master_monday.json
11. the W30 run receipt and all paths declared by the Master Monday pointer
12. the first complete packet posted in DATA PING_V7
```

Do not reconstruct missing fields, source hashes, predecessor IDs, cohorts or market values from memory. Do not infer state from this bootstrap.

## Active source rule

```text
Highest numbered DATA PING version containing an actual complete Main-Framework-accepted packet wins.
```

Until a complete V7 packet is accepted:

```yaml
active_source_version: V6
V7_status: PREPARED_NOT_ACTIVE
latest_canonical_accepted_log_id: DATA_PING_V6_20260719T200033Z
latest_settled_closeout_id: MASTER_MONDAY_CLOSEOUT_W30_20260720T054959Z
latest_validation_only_snapshot_id: DATA_PING_V6_RAW_20260720T081747Z
latest_validation_only_canonical_acceptance: false
market_state_change_from_bootstrap: NO
gate_or_threshold_change_from_bootstrap: NO
portfolio_action_from_bootstrap: NONE
```

An empty V7 thread, greeting, bootstrap receipt, schema-only test, format test or validation-only packet does not supersede V6.

## Packet interface

Use the active raw collector interface until an explicit later canonical contract changes it:

```text
DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
```

Exact output envelope:

```text
DATA_PING_MAIN_THREAD_INGEST_BEGIN
{one valid JSON object with exactly 11 top-level fields}
DATA_PING_MAIN_THREAD_INGEST_END
IGNORE FOR MAIN-FRAMEWORK INGEST
PACKET_SHA256: <hash or NOT_GENERATED>
```

Exact top-level fields:

```text
packet
meta
quality
source_health
observations
source_ledgers
deterministic_source_aggregates
readiness
missing
artifacts
authority
```

No progress messages, duplicate human summary, giant raw sidecars or unrequested ZIPs.

## Collector role

The successor supplies verified source observations and reproducible source ledgers only. Main Framework owns:

```text
CLV and range position
retention
runtime gates and falsifiers
Stage-1 and FNP decisions
recovery and rotation interpretation
permissions and portfolio action
canonical acceptance
```

The collector has zero authority to ratify state, close events, change thresholds, open deployment or recommend portfolio action.

## Source and lineage requirements

The first complete V7 packet must identify:

```yaml
canonical_predecessor_id: DATA_PING_V6_20260719T200033Z
collector_predecessor_id: latest directly verified V6 collector packet or EXPLICIT_UNRESOLVED
```

It must not point back to V5 as canonical predecessor. If collector lineage cannot be verified, report the exact gap instead of choosing an older packet.

Required rules:

```yaml
weekly_candle_basis: BINANCE_CEST_DAILY_SOURCE_ROWS
rolling_24h_weekly_substitution: FORBIDDEN
etf_primary: FARSIDE
secondary_etf_values: SEPARATE_PROVISIONAL_ONLY
weekend_etf: NO_SESSION_WEEKEND
spot_taker_scope: VENUE_SPECIFIC_NOT_MARKET_WIDE_CVD
futures_scope: VENUE_SPECIFIC_NOT_MARKET_WIDE
membership_hash_for_dynamic_breadth: REQUIRED
breadth_sample_change_status: NOT_COMPARABLE_SAMPLE_CHANGED
fixed_risk35_reconstruction: FORBIDDEN
market_wide_cvd_substitution: FORBIDDEN
```

## Accepted-log integrity warning

```yaml
current_v6_accepted_payload_sha256: NOT_GENERATED
current_v6_accepted_payload_commit_sha: NOT_RECORDED
accepted_log_fallback_contract_status: PARTIAL
reconstruction_allowed: false
```

The missing V6 receipt fields must remain explicit. Do not create a replacement hash from a later copy and describe it as contemporaneous proof.

A future V7 canonical acceptance transaction should record the source timestamp, exact receipt and payload paths, commit SHA, deterministic SHA-256, data quality, field coverage, missing fields and branch/main read-back status before advancing the accepted-log pointer.

## Fixed breadth gap

```yaml
FIXED_RISK35_v1_canonical_identity: UNKNOWN
reconstruction_from_current_top50_or_top100: FORBIDDEN
historical_weekly_breadth: AVAILABLE
daily_historical_breadth: DATA_MISSING
historical_30DMA_breadth: DATA_MISSING
dynamic_breadth_role: SHADOW_DESCRIPTIVE_ONLY
breadth_predictive_permission: ZERO
```

This gap does not block raw collection or settled weekly closeout, but it blocks claims requiring the original fixed cohort.

## Required acknowledgement

Before the first complete V7 packet, return only:

```text
DATA_PING_THREAD_BOOTSTRAP
handover_status: PASS / PARTIAL / FAIL
loaded_handover_id: DATA_PING_THREAD_HANDOVER_V5_TO_V6_20260719T144323Z
loaded_checkpoint_id: DATA_PING_V6_RECOVERY_CHECKPOINT_20260720T104536Z
loaded_contract: DATA_PING_MAIN_THREAD_INGEST_v2_0_RAW
latest_accepted_log_id: DATA_PING_V6_20260719T200033Z
active_source_version: V6
intended_successor_version: V7
active_event_id: ROTATION_REPAIR_EDGE_20260712_01
fixed_risk35_identity_status: UNKNOWN_RECONSTRUCTION_FORBIDDEN
portfolio_action: NONE
ready_for_first_complete_v7_ping: YES / NO
```

This is a continuity receipt, not market analysis.

## First complete V7 packet

The packet must end with:

```yaml
binding: false
canonical_acceptance: false
framework_state_change: false
portfolio_action: false
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
```

Main Framework validates the packet, accepted-log transaction, lineage and read-back before deciding V7 activation. V6 remains active until then.
