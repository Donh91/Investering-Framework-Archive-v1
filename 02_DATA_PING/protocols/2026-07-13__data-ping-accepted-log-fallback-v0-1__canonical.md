# DATA PING Accepted-Log Fallback Protocol v0.1

**Dato:** 2026-07-13  
**Status:** CANONICAL_OPERATIONAL  
**Område:** DATA PING source resolution / accepted run receipts / scheduled-agent fallback  
**Primary folder:** `02_DATA_PING/`  
**Authority boundary:** source transport and provenance only; no independent analysis, market call, threshold change, rule promotion or portfolio action

## 1. Purpose

Allow scheduled framework agents to consume the newest accepted DATA PING even when direct cross-thread access is unavailable and the full verbatim thread handoff was not written.

The user continues to work only in ChatGPT DATA PING threads. GitHub remains an invisible backend.

## 2. Source hierarchy

Consumers must resolve sources in this order:

```text
1. DIRECT_PROJECT_THREAD
2. ACCEPTED_LOG_RECEIPT
3. THREAD_DERIVED_HANDOFF
4. SOURCE_UNAVAILABLE
```

### DIRECT_PROJECT_THREAD

Use the latest complete user-supplied DATA PING analysis in the highest numbered version actually used.

### ACCEPTED_LOG_RECEIPT

Use only a durable acceptance receipt that:

- identifies one exact `accepted_log_id` / DATA PING run ID;
- identifies the DATA PING version and source timestamp;
- links to a readable accepted payload or event packet in GitHub;
- records the commit SHA that made the packet durable;
- records a deterministic hash of the normalized accepted payload;
- preserves data-quality and missing-field labels;
- contains only fields present in the accepted DATA PING packet;
- passes read-back and hash validation;
- is no more than 36 hours old for new forecast-row creation.

A bare commit message, prose summary, framework state pointer or run ID without a readable payload is insufficient.

### THREAD_DERIVED_HANDOFF

Use the existing exact thread-derived handoff only when its pointer says `READY_THREAD_DERIVED`, its payload and hash validate, and it is no more than 36 hours old.

## 3. Highest-version resolution

```text
1. Consider only versions containing an actual complete user-supplied DATA PING.
2. Highest numeric version wins.
3. Within that version, latest complete source timestamp wins.
4. An empty newer thread does not supersede an older active version.
5. A casual comment does not become a source packet.
6. An older version cannot replace a valid higher-version pointer.
7. Same-version same-timestamp different-hash packets create SOURCE_CONFLICT.
```

## 4. Acceptance receipt contract

History path:

```text
02_DATA_PING/operational_handoffs/accepted_logs/history/YYYY-MM-DDTHHMMSSZ__data-ping-vN__accepted-log.json
```

Latest pointer:

```text
02_DATA_PING/operational_handoffs/latest_accepted_log_state.json
```

Required receipt fields:

```yaml
contract_version:
accepted_log_id:
data_ping_version:
source_timestamp:
accepted_at:
source_mode: ACCEPTED_LOG_DERIVED
framework_acceptance_status:
accepted_payload_path:
accepted_payload_commit_sha:
accepted_payload_hash_sha256:
data_quality:
field_coverage:
missing_fields:
readback_status:
hash_status:
forecast_row_permission:
notes:
```

`forecast_row_permission` may be `ELIGIBLE_BY_FIELD` only when all source, read-back, hash, causal-timestamp and freshness checks pass. It never means that every sensor pair is eligible.

## 5. DATA PING main-thread responsibility

After receiving and interpreting a complete Custom GPT DATA PING analysis, the active DATA PING thread should:

1. preserve or archive the accepted sensor packet;
2. assign or preserve one stable DATA PING run ID;
3. record the framework acceptance decision separately from the raw sensor state;
4. create and verify an accepted-log receipt;
5. update `latest_accepted_log_state.json` only after successful read-back;
6. return a compact acceptance block to the conversation.

Required conversational block:

```text
DATA_PING_ACCEPTANCE
accepted_log_id: <stable run id>
data_ping_version: <N>
source_timestamp: <UTC timestamp>
framework_acceptance_status: <status>
durable_capture: PASS / FAIL
accepted_payload_path: <GitHub path or DATA_MISSING>
accepted_payload_hash: <sha256 or DATA_MISSING>
sensor_pair_lab_source_status: READY_ACCEPTED_LOG / NOT_READY
```

The block is a receipt, not a second market analysis.

## 6. Field-level eligibility

The Sensor Pair Lab must determine eligibility independently for each pair and horizon.

- Missing data makes only the affected pair/horizon ineligible.
- `DATA_MISSING`, `UNAVAILABLE` and pending fields are never interpreted as negative evidence.
- No value may be inferred from framework prose when the field is absent from the accepted payload.
- Framework acceptance labels may be frozen as controls but cannot substitute for missing component sensors.

## 7. Causal and prospective boundary

An accepted-log packet may create a prospective row only when:

- its source timestamp precedes the lab freeze timestamp;
- no outcome from the requested horizon was known or imported at freeze time;
- operational-availability lag is recorded;
- frozen fields are immutable;
- later outcomes come only from a later valid DATA PING source.

A delayed receipt may still mature prior rows if it provides later actuals, but it may not manufacture a forecast after the outcome is known.

## 8. Current bootstrap receipt

The accepted DATA PING run `DATA_PING_V4_20260713T052547Z` is eligible as the first accepted-log fallback source because its accepted sensor packet was made durable before any 24h, 72h or 7d outcome horizon closed.

The receipt preserves the exact accepted packet from:

```text
02_DATA_PING/live_state_handover/2026-07-12__rotation-repair-edge-20260712-01__event-ledger.md
```

The receipt does not claim that all eight sensor pairs are eligible.

## 9. Safety

Forbidden:

- browsing the web or fetching replacement market data;
- calling the Custom GPT automatically;
- treating a prose summary as a complete packet;
- reconstructing missing source fields;
- creating retrospective forecast rows;
- changing live sensor weights or thresholds;
- automatic rule promotion or portfolio action.

## 10. Current status

```yaml
protocol_version: 0.1
source_hierarchy_active: YES
accepted_log_fallback_active: YES
user_github_action_required: NO
custom_gpt_automatic_invocation: NO
independent_market_data_fetch: FORBIDDEN
rule_promotion: NONE
portfolio_authority: ZERO
```
