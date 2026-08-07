# Audit receipt — DATA PING run-3d5187ccaeeea087

- collector: 15.3.1
- snapshot: snap-e4fcc29d6ec597cb
- snapshot UTC: 2026-08-07T08:42:59.283786Z
- attachment SHA-256: 7ddc3c16911ee08e6a52ef62b3b2acbf3af27c7ea4fbc755cf25ca97f55eda86
- collector packet SHA-256: a45fd402b2fa4d355645073f4fc00431db7ecb051e607d3fb0afe3aa612cb44c
- validator: FAIL
- failed checks: INV-006, PG-003, PG-004, PG-005, ORC-001, ORC-002, ORC-003, ORC-004
- freeze count: 1
- post-freeze calls: 0
- main-thread ingest: NO
- bounded owner advancement: NO
- canonical change: NONE
- portfolio effect: NONE

Archive classification: `VALIDATION_FAILED_NON_DECISION_OBSERVATION`.

Chronology note: this run occurred after the near-valid 15.3.1 MTH-001-only failure and represents a temporary regression of incremental commit/timing/group-barrier integrity. The later 15.3.2 run at 10:47Z recovered those critical runtime properties but still did not become owner because predecessor/lineage and complete method authority remained unresolved.
