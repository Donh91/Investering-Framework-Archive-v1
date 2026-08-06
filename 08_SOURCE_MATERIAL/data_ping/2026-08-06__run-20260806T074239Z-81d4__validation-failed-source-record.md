# DATA PING Validation-Failed Source Record

```yaml
run_id: run-20260806T074239Z-81d4
snapshot_id: snap-20260806T074239Z-42af
snapshot_utc: 2026-08-06T07:42:39.000Z
collector_version: 15.2.0
collector_status: FAIL
source_collection_status: PARTIAL
classification: VALIDATION_FAILED_NON_DECISION_OBSERVATION
failed_check_id: INV-006
packet_usable_for_main_thread_ingest: false
```

## Execution and integrity

```yaml
planned_core_actions: 60
attempted_core_actions: 60
core_pass: 57
core_partial: 2
core_stale: 1
execution_order_status: PASS
status_reconciliation: PASS
breadth_transform_status: PASS
settled_candle_filter_status: PASS
freeze_invariants_status: PASS
invocation_receipt_integrity: FAIL
arguments_sha256_present: 0_of_61
payload_sha256_present: 0_of_61
packet_sha256: null
```

The source-collection layer produced broad observations, but the packet failed the mandatory cryptographic invocation-to-receipt integrity gate. No market, ETF, breadth, predecessor or portfolio owner may be advanced from this run.

## Diagnostic observations only

```yaml
BTCUSDT: 64867.68
ETHUSDT: 1910.53
ETHBTC: 0.02946
BTC_open_interest: 106609.234
ETH_open_interest: 2282083.486
```

Change versus latest valid bounded owner `run-e841c63ea8e04a028918`:

```yaml
BTC_change_pct: -0.160561
ETH_change_pct: -0.470939
ETHBTC_change_pct: -0.304569
BTC_open_interest_change_pct: -0.934821
ETH_open_interest_change_pct: -2.909002
```

Diagnostic structure is consistent with a modest price pullback and material deleveraging, especially in ETH. It has no state authority because the packet failed validation.

## Unaccepted ETF candidates

```yaml
session: 2026-08-05
BTC_candidate_usd_m: 244.4
ETH_candidate_usd_m: 60.8
owner_permission: NO
```

The preceding validation-failed packet reported BTC `+2.8M` and ETH `0.0M` for the same session. The large discrepancy may reflect publication timing, table finalization or parsing, but neither packet can adjudicate it because both failed `INV-006`.

Latest valid ETF owner remains the 2026-08-04 session:

```yaml
BTC_usd_m: 211.5
ETH_usd_m: 53.1
```

## Diagnostic breadth

```yaml
method: COINGECKO_TOP100_FILTERED_v3
filter: BREADTH_FILTER_TOP100_EXCLUSIONS_v1
included: 89
advancers: 45
decliners: 41
unchanged: 3
positive_share: 0.505617977528
equal_weight_mean_return_24h_pct: -0.284453185810
membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
scoring_owner: BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1
scored_gate_permission: NOT_AUTHORIZED
```

The raw advancer share crossed 50%, but the equal-weight mean was negative and the method is incompatible with the locked v1.1 owner. Validation failure independently blocks all gate use.

## Required handling

- Preserve as QA and engineering evidence only.
- Do not replace latest valid bounded owner.
- Do not update canonical predecessor.
- Do not update ETF owner.
- Do not increment A-class or shadow counters.
- Keep GitHub issue #317 open.
- Require a fresh full rerun after hash-integrity remediation.
