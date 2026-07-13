# Daily Sensor Pair Discovery Lab — Accepted-Log Fallback Addendum v0.1

**Dato:** 2026-07-13  
**Status:** CANONICAL_ACTIVE_ADDENDUM  
**Parent:** `06_RESEARCH_LAB/forward_tests/2026-07-12__daily-sensor-pair-discovery-lab-v0-1__canonical.md`  
**Protocol owner:** `02_DATA_PING/protocols/2026-07-13__data-ping-accepted-log-fallback-v0-1__canonical.md`  
**Authority boundary:** source resolution only; no change to pair catalog, thresholds, evidence gates, market state or portfolio authority

## Binding change

The source resolution order in the parent owner is replaced by:

```text
1. DIRECT_PROJECT_THREAD
2. ACCEPTED_LOG_RECEIPT
3. THREAD_DERIVED_HANDOFF
4. SOURCE_UNAVAILABLE
```

## Accepted-log eligibility

The lab may use `02_DATA_PING/operational_handoffs/latest_accepted_log_state.json` when direct project-thread access is unavailable, provided:

- `source_status=READY_ACCEPTED_LOG`;
- the acceptance receipt and accepted payload paths both read back;
- run ID, version and source timestamp agree across pointer, receipt and payload;
- the stored SHA-256 validates the normalized accepted packet;
- the payload was made durable before the evaluated outcome horizon closed;
- operational-availability lag is recorded;
- the source is no more than 36 hours old for new forecast rows;
- pair eligibility is determined field by field;
- no missing value is inferred or replaced.

A framework commit or current-state pointer without an acceptance receipt is not enough.

## Bootstrap source

```yaml
accepted_log_id: DATA_PING_V4_20260713T052547Z
source_timestamp: 2026-07-13T05:25:47Z
source_status: READY_ACCEPTED_LOG
receipt_path: 02_DATA_PING/operational_handoffs/accepted_logs/history/2026-07-13T052547Z__data-ping-v4__accepted-log.json
accepted_payload_path: 02_DATA_PING/live_state_handover/2026-07-12__rotation-repair-edge-20260712-01__event-ledger.md
forecast_row_permission: ELIGIBLE_BY_FIELD
retrospective_row_permission: FORBIDDEN
```

The lab may freeze eligible rows from this packet only if no applicable horizon outcome is known at freeze time. Pairs whose required fields are absent remain ineligible.

## Outcome rule

Later accepted-log receipts can supply outcomes for earlier frozen rows when they contain the required actual fields. The lab must not fetch external actuals or treat a later framework interpretation as a substitute for missing observations.

## No authority change

```yaml
pair_catalog_changed: NO
market_logic_changed: NO
thresholds_changed: NO
rule_promotion: NONE
portfolio_authority: ZERO
```
