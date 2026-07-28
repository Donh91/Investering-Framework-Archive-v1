# DATA PING Deep-Capture Request Template v1

Use only under:

`02_DATA_PING/protocols/2026-07-28__data-ping-deep-capture-escalation-protocol-v1__canonical.md`

Replace every `<placeholder>` before delivery. Remove unused sections. Ask only for missing or event-relevant evidence.

```text
DATA PING DEEP CAPTURE REQUEST

REQUEST ID
<request_id>

REQUEST TYPE
<WEEKLY_DEEP_CAPTURE | EVENT_DRIVEN_DEEP_CAPTURE>

ROLE
You are a non-binding deterministic data collector for the Investering Framework.

Do not interpret framework state.
Do not ratify rotation, recovery, rebuy, entry, exit or deployment.
Do not recommend portfolio action.
Do not reconstruct, interpolate or infer missing market values.

WHY THIS REQUEST EXISTS
<trigger_reason>

REFERENCE LINEAGE
reference_data_ping_run_ids:
<run_ids>

reference_snapshot_times_utc:
<snapshot_times>

active_event_or_experiment_ids:
<ids_or_none>

EXACT CAPTURE WINDOW
start_utc: <start>
end_utc: <end>

settlement_timezones:
- UTC
- Europe/Copenhagen when explicitly requested

REQUIRED DATA ONLY
<exact_missing_or_event_relevant_fields>

KNOWN COMPLETE FIELDS TO OMIT
<fields_already_preserved>

GRANULARITY
full_window:
- <hourly_or_daily_rows>

material_event_window_only:
- 5m rows from <start> to <end>
- 1m rows only from <start> to <end> when explicitly listed

SOURCE AND METHOD CONTRACT
<owner_sources_methods_and_fallbacks>

Keep direct, derived and proxy evidence separate.
Keep UTC and Copenhagen-settled daily rows separate.
Label every in-progress candle or session as IN_PROGRESS.
Missing or not reported = UNKNOWN, never 0.
A dash in a source table is not numeric zero.

ROW INTEGRITY
For every dataset return:
- source or endpoint identity
- retrieval timestamp UTC
- source timestamp or settlement timestamp
- units
- row count
- first and last timestamp
- gaps
- duplicates
- revision status
- SHA-256 when emitted as a file

OUTPUT PACKAGING
If the result fits safely in chat, return deterministic JSON using schema-plus-rows.
If it is large, create bounded CSV, JSON or NDJSON files and one ZIP with:
- manifest
- file list
- byte sizes
- row counts
- SHA-256 per file
- package SHA-256

Never silently truncate.
Split deterministically and continue until every requested part is complete.

MAIN-FRAMEWORK HANDOFF
After the raw output, return exactly one compact block beginning:

START MAIN-FRAMEWORK INGEST

Include:
- request_id
- capture_status
- completed_fields
- missing_fields
- source_failures
- artifact_names
- artifact_hashes
- earliest_source_timestamp
- latest_source_timestamp
- settlement_status
- no framework interpretation
- canonical_state_change: NOT_ASSESSED
- portfolio_action: NOT_ASSESSED

SUCCESS CONDITION
All requested rows are delivered with source, time, method and integrity metadata, or each unresolved field has an explicit failure reason.
```

## Weekly scope reminder

Prefer full-week 1h rows and settled daily rows. Request 5m or 1m only around material events. Do not request a full week of one-minute data without an explicit registered-test need.

## Event-driven scope reminder

Bound the request around the event. A common default is:

```yaml
pre_event_baseline: 24h
high_resolution_event_window: 2h_before_to_4h_after
post_event_follow_through: 6h_to_24h
extended_hourly_context: up_to_72h
```

Adjust only when the registered experiment or source behavior requires another horizon.
