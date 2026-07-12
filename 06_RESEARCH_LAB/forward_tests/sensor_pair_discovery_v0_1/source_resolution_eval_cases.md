# DATA PING Source Resolution Evaluation Cases v0.1

These synthetic cases validate selection logic only. They are not market rows and do not count as prospective evidence.

## Case 1 — Higher used version beats newer timestamp in older version

```yaml
threads:
  - title: DATA PING_V3
    latest_complete_analysis: 2026-07-12T20:00:00+02:00
  - title: DATA PING_V4
    latest_complete_analysis: 2026-07-12T18:00:00+02:00
expected_selected_version: 4
expected_selected_thread: DATA PING_V4
reason: HIGHEST_VERSION_ACTUALLY_USED_WINS
```

## Case 2 — Empty higher version is ignored

```yaml
threads:
  - title: DATA PING_V4
    latest_complete_analysis: 2026-07-12T18:00:00+02:00
  - title: DATA PING_V5
    latest_complete_analysis: null
expected_selected_version: 4
reason: UNUSED_HIGHER_VERSION_DOES_NOT_ACTIVATE
```

## Case 3 — Latest complete analysis wins within same version

```yaml
threads:
  - title: DATA PING_V4 A
    latest_complete_analysis: 2026-07-12T17:00:00+02:00
  - title: DATA PING_V4 B
    latest_complete_analysis: 2026-07-12T19:00:00+02:00
expected_selected_thread: DATA PING_V4 B
reason: LATEST_COMPLETE_ANALYSIS_TIMESTAMP_WITHIN_VERSION
```

## Case 4 — Casual message does not replace source

```yaml
thread: DATA PING_V4
complete_analysis_timestamp: 2026-07-12T19:00:00+02:00
later_message_timestamp: 2026-07-12T19:10:00+02:00
later_message_type: CASUAL_QUESTION
expected_source_timestamp: 2026-07-12T19:00:00+02:00
reason: LATEST_COMPLETE_ANALYSIS_NOT_LATEST_MESSAGE
```

## Case 5 — Same timestamp, different hash blocks pointer update

```yaml
version: 4
source_timestamp: 2026-07-12T19:00:00+02:00
hashes:
  - abc123
  - def456
expected_status: SOURCE_CONFLICT
expected_pointer_update: NO
```

## Case 6 — Direct access unavailable, valid fallback

```yaml
direct_project_thread_access: UNAVAILABLE
handoff_status: READY_THREAD_DERIVED
handoff_age_hours: 12
source_hash_present: true
expected_resolution: THREAD_DERIVED_HANDOFF
```

## Case 7 — Direct access unavailable, stale fallback

```yaml
direct_project_thread_access: UNAVAILABLE
handoff_status: READY_THREAD_DERIVED
handoff_age_hours: 40
max_valid_age_hours: 36
expected_resolution: SOURCE_UNAVAILABLE
expected_forecast_rows: 0
```

## Case 8 — Missing pair field is local, not global

```yaml
source_valid: true
P01_required_fields: complete
P03_required_fields: missing_open_interest
expected:
  P01: ELIGIBLE
  P03: INELIGIBLE_MISSING_SENSOR
  global_run: PARTIAL_WITH_ELIGIBLE_ROWS_ALLOWED
```

## Pass contract

All eight expected outcomes must be preserved by the daily task and any future implementation. A failure in source resolution blocks affected rows and must never be repaired by independent market-data fetching.