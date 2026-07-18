# DATA PING V6 Bootstrap

**Status:** `PREPARED_NOT_ACTIVE`  
**Authority:** continuity only  
**Activation:** first complete V6 DATA PING reviewed and accepted by Main Framework

## Startup instruction

Read in this exact order:

```text
1. 02_DATA_PING/thread_handoffs/latest_thread_handover_state.json
2. 02_DATA_PING/thread_handoffs/checkpoints/2026-07-18__data-ping-v5__recovery-checkpoint.md
3. 02_DATA_PING/operational_handoffs/latest_decision_context_state.json
4. 02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
5. the accepted payload and receipt referenced by that pointer
6. the active event registry referenced by the accepted-log pointer
7. 02_DATA_PING/decision_value/prospective_events/ROTATION_REPAIR_EDGE_20260712_01.json
8. the first complete packet posted in DATA PING_V6
```

Do not reconstruct missing fields from memory. Do not infer market values from this bootstrap.

## Active source rule

```text
Highest numbered DATA PING version containing an actual complete accepted packet wins.
```

Until a complete V6 packet is accepted:

```yaml
active_source_version: V5
V6_status: PREPARED_NOT_ACTIVE
canonical_predecessor: READ_FROM_LATEST_ACCEPTED_LOG_STATE
market_state_change_from_bootstrap: NO
portfolio_action_from_bootstrap: NONE
```

An empty V6 thread, a greeting or this acknowledgement does not supersede V5.

## Current packet interface

Use:

```text
DATA_PING_MAIN_THREAD_INGEST_v1_1
```

The compact packet must contain exactly these 11 top-level fields:

```text
packet
meta
quality
source_health
observations
deterministic_derived
experimental_shadow
collector_interpretation_nonbinding
missing
artifacts
authority
```

No new feature, engine, score or redesign is permitted merely because the thread version changes.

## Current known continuity limitations

```yaml
FIXED_RISK35_v1_authoritative_membership: MISSING
independent_artifact_parity: PENDING
```

The original 35-member cohort must not be regenerated from a current Top50 or Top100 list. Dynamic breadth remains shadow-only.

## Authority rules

```yaml
collector_authority: NONE
canonical_acceptance_owner: MAIN_FRAMEWORK_CHATGPT
framework_interpretation: DEFERRED
automatic_recovery_or_rotation_conclusion: NOT_COMPUTED_BY_DATA_PING
portfolio_action: NONE
```

Pending is never zero. Partial candles are not closes. Partial ETF sessions are not completed sessions. Venue-specific derivatives or spot-taker data are not market-wide CVD or market-wide OI.

## Required acknowledgement

Return only a compact continuity receipt before the first V6 packet:

```text
DATA_PING_THREAD_BOOTSTRAP
handover_status: PASS / PARTIAL / FAIL
loaded_checkpoint_id: DATA_PING_V5_RECOVERY_CHECKPOINT_20260718T120000Z
latest_accepted_log_id: <resolved from pointer>
active_source_version: V5
intended_successor_version: V6
active_event_id: ROTATION_REPAIR_EDGE_20260712_01
fixed_risk35_status: MISSING_UNTIL_VERIFIED_ARTIFACT
portfolio_action: NONE
ready_for_first_complete_v6_ping: YES / NO
```

This acknowledgement is not a market analysis and changes no state.
