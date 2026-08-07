# DATA PING source record — dp_20260807_failure_5d98c4b14617

```yaml
snapshot_id: dp_20260807_failure_5d98c4b14617
snapshot_utc: 2026-08-07T18:50:30.119182Z
collector_version: 15.3.1
collection_status: FAIL
validator_pass: false
packet_sha256: 9c7bacc9a3090cb1d9c1ce8763f755a05f233804391d0c6833c72c96ab0720ea
planned_core_actions: 60
attempted_core_actions: 60
planned_optional_actions: 1
attempted_optional_actions: 1
receipt_count: 61
freeze_count: 1
post_freeze_call_count: 0
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
```

## Load-bearing failure evidence

- incremental_commit_status: FAIL
- group_barrier_status: FAIL
- blocking_failure_count: 6
- all invocation started/completed timestamps absent; precision only `SEQUENCE_ONLY`
- all payload hashes absent with basis `NOT_RETAINED_COMPLETE_RESULT`
- PUBLIC_WEB and COINGECKO group transforms failed
- Farside BTC/ETH latest settled rows unresolved/partial
- breadth dedupe/exclusions/membership hash unavailable
- comparison unavailable: `NO_ELIGIBLE_SAME_THREAD_PREDECESSOR`
- packet is explicitly `packet_usable_for_main_thread_ingest=false`

## Diagnostic-only market fields

- BTCUSDT 64740.49
- ETHUSDT 1908.77
- ETHBTC 0.02948
- BTC OI 107182.271
- ETH OI 2285652.417
- CFGI global 51 Neutral; BTC 54 Neutral; ETH 61 Greed

No market authority is assigned to these values.

## Runtime chronology concern

This run used collector 15.3.1 at 2026-08-07T18:50Z after collector 15.3.2 had already produced a later-runtime recovery run earlier the same day (`dp-run-7ddda892cbb35d79ad53`, snapshot 2026-08-07T10:47:45.292410Z). Re-execution on an older collector reintroduced failure classes already observed in 15.3.1. This is treated as potential stale-runtime/version-selection drift and requires an explicit active-version guard.
