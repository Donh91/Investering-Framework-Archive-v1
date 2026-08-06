# DATA PING Source Record — Validation Failed

```yaml
run_id: run-20260805T232345Z-6f82
snapshot_id: snap-20260805T232345Z-a91c
snapshot_utc: 2026-08-05T23:23:45.183Z
collector_version: 15.2.0
collector_status: FAIL
source_collection_status: PARTIAL
classification: VALIDATION_FAILED_NON_DECISION_OBSERVATION
packet_usable_for_main_thread_ingest: false
failed_check_id: INV-006
failure: INVOCATION_ARGUMENT_AND_PAYLOAD_HASHES_NOT_CAPTURED
packet_sha256: null
```

## Execution facts

- 60 of 60 core actions were attempted.
- Source collection produced 57 PASS, 2 PARTIAL and 1 STALE core results.
- Execution order, source-status reconciliation, breadth transform, settled-candle filtering and freeze invariants passed.
- Invocation-receipt integrity and terminal packet validation failed.
- Every receipt carried null `arguments_sha256` and null `payload_sha256`.
- No canonical packet hash was calculated before terminal freeze.

## Diagnostic observations only

```yaml
BTCUSDT: 64669.99
ETHUSDT: 1910.21
ETHBTC: 0.02953
BTC_final_open_interest: 107318.324
ETH_final_open_interest: 2316237.995
BTC_current_funding: 0.00006354
ETH_current_funding: 0.00002220
```

Versus the latest valid bounded owner `run-e841c63ea8e04a028918`:

```yaml
BTC_change_pct: -0.4648310041
ETH_change_pct: -0.4876092041
ETHBTC_change_pct: -0.0676818951
BTC_open_interest_change_pct: -0.2759088666
ETH_open_interest_change_pct: -1.4559025303
```

These deltas are retained as diagnostic source context only. They are not accepted state transitions because the packet failed its critical integrity contract.

## Other reported candidates

```yaml
ETF_session: 2026-08-05
BTC_ETF_candidate_usd_m: 2.8
ETH_ETF_candidate_usd_m: 0.0
ETF_owner_permission: NO_PACKET_VALIDATION_FAILED
breadth_advancers: 32
breadth_decliners: 38
breadth_unchanged: 19
breadth_positive_share: 0.3595505618
breadth_membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
breadth_gate_permission: NO
stablecoin_global_total: null
```

The zero ETH ETF value must not be interpreted as economic zero outside this failed packet lane. It is an unaccepted candidate until reproduced by a valid owner packet or direct owner ledger.

## Authority treatment

- latest bounded pointer: unchanged;
- canonical predecessor: unchanged;
- ETF owner ledger: unchanged;
- market state: unchanged;
- portfolio action: none;
- A-class and shadow counters: unchanged.
