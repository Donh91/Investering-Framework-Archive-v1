# Execution receipt - DATA PING run_4dd78b1e

```yaml
execution_timestamp_utc: 2026-07-30T14:20:00Z
mode: MAIN_FRAMEWORK_INGEST_BOUNDED_MARKET_AND_SOURCE_QA
result: BOUNDED_OBSERVATION_ACCEPTED_PREDECESSOR_REJECTED_DCR_PREPARED
```

## Decisions

- deduplicated `run_7793a18a...` without a new record;
- accepted `run_4dd78b1e...` as a bounded current-market observation;
- rejected its packet-supplied longitudinal comparison because the declared predecessor was QA-only;
- kept the accepted market predecessor at `snap_0e19c112413d471d8270cad1a18148a7`;
- recognized current breadth at 55.0562%, above both gates but only narrowly above 55%;
- denied rotation because direct ETHBTC owner data is unavailable and the derived ratio is below 0.0300;
- created no A-class receipt and no shadow-run increment;
- prepared `DCR-20260730-EVENT-003` for direct owner recovery and exact breadth-sidecar recovery;
- appended the third live sidecar breach to issue #224 and recurring invalid-predecessor evidence to issue #232.

## Governance

```yaml
rotation: NO_ROTATION
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
A_rows_total: 2
shadow_dual_run_valid_runs: 5
final_holdout_opened: NO
```

## Scope

Additive archive files plus bounded updates to the predecessor pointer, deep-capture ledger and prospective accumulation status. No threshold, sensor weight, forecast score or portfolio authority changed.