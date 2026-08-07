# DATA PING validation-failed source record

```yaml
run_id: dprun_32c45bcac4df4fa4
collector_version: 15.3.1
contract: DATA_PING_RUN_FIRST_STATELESS_v1
collection_status: FAIL
snapshot_id: null
snapshot_utc: null
retrieval_time_upper_bound_utc: 2026-08-06T23:15:58.678008Z
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
classification: VALIDATION_FAILED_ORCHESTRATION_INTERRUPTED_NON_DECISION
```

## Supplied artifacts

- `packet(1).json`
  - uploaded byte size: `12010`
  - uploaded-file SHA-256: `4d8978d0426d25e6bd7cf5dba3fd315dabe6059127fd6d8f6808e7e25985caa9`
  - packet-declared canonical SHA-256: `6a822acf3c5c068b88b41c3126bfc479205446f431fee43e72f899cb918b6691`
- `validation_report.json`
  - uploaded byte size: `7073`
  - uploaded-file SHA-256: `ca466eaff3656f14af2c53c36d3f43dfb8a1e6847511c171b0336c43abb26747`
  - validator payload SHA-256: `235a468e2fbbd8bf2d23fe5bd5ea33aeb4ab86163a53a3d4e69b9bac66e6d055`

The uploaded-file SHA values are byte hashes of the conversation attachments. The packet-declared hash uses the collector's declared canonical packet hashing basis and is retained separately rather than conflated with the attachment-byte hash.

## Execution facts

```yaml
planned_core_actions: 60
attempted_core_actions: 1
planned_optional_actions: 1
attempted_optional_actions: 0
resolved_source_invocations: 2
receipt_count: 2
freeze_count: 0
execution_interrupted: true
interruption_reason: INCREMENTAL_COMMIT_AND_UNREGISTERED_SOURCE_CALL_VIOLATION
packet_usable_for_main_thread_ingest: false
```

The first registered action was `FARSIDE_BTC_DIRECT_ALL_DATA`. Its initial page response was incomplete for the registered action. Before that invocation was incrementally committed, a second source call opened the page continuation. That continuation had no registered action/method mapping and was recorded as `UNREGISTERED_FARSIDE_BTC_CONTINUATION` / `UNREGISTERED_METHOD`. The runtime then stopped fail-closed.

## Partial Farside BTC evidence — QA only

The continuation exposed a 2026-08-06 BTC ETF row with:

```yaml
displayed_total_usd_m: 29.2
local_sum_usd_m: 29.2
tieout: true
dash_unknown_fund_cells: 8
zero_fund_cells: 1
MSBT_usd_m: 14.9
GBTC_usd_m: 7.5
BTC_usd_m: 6.8
ARKB_usd_m: 0.0
normalized_row_sha256: 0ddcde02a22c0e9e2c9d2e4652864aa6764260767a7ef94cc9eef5eef9c46fe0
row_usable: false
market_use_status: FAIL
authorized_for_market_use: false
```

This is preserved as partial-publication/finality evidence only. It must not update the ETF owner ledger and must not be treated as a revision of any later complete 2026-08-06 row.

## Durable learning

A displayed Total can exactly tie to the sum of currently numeric issuer cells while most issuer cells are still dashes/unknown. Therefore exact Total tie-out alone is insufficient for ETF owner finality. Owner-grade rows require complete target-cell publication in addition to repeated stable retrievals, session identity, header-resolved Total and full audit evidence.

## Authority effect

```yaml
bounded_pointer_advanced: false
canonical_state_change: NONE
portfolio_effect: NONE
market_interpretation_authorized: false
```
