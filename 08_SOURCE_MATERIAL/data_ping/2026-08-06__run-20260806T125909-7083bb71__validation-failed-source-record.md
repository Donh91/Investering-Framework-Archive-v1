# Validation-failed DATA PING source record

## Identity

- run_id: `run-20260806T125909-7083bb71`
- snapshot_id: `snap-20260806T125909-f99a7d6f`
- snapshot_utc: `2026-08-06T12:59:09.866Z`
- collector_version: `15.2.0`
- collection_status: `FAIL`
- source_collection_status: `PARTIAL`
- failed_check: `PG-003`
- packet_sha256: `f6807f5d94685ed8082877190e967e47841c67e31019427219a658277ab6f6f4`
- packet_sha256_basis: `CANONICAL_ASCII_JSON_WITH_PACKET_SHA256_NULL`

## Passed controls

- execution order: PASS
- status reconciliation: PASS
- receipt bijection: PASS
- breadth transform: PASS
- settled candle filter: PASS
- freeze invariants: PASS
- freeze_count: 1
- post_freeze_call_count: 0
- 61 argument hashes present
- 61 payload hashes present

## Critical failure

All 61 invocation rows contain null `started_at_utc` and null `completed_at_utc`. The packet reports `invocation_required_timestamp_status: FAIL`, `packet_validation_status: FAIL`, `failed_check_ids: [PG-003]`, and `packet_usable_for_main_thread_ingest: false`.

The stated reason is `STARTED_AT_AND_COMPLETED_AT_NOT_EXPOSED_BY_TOOL_INTERFACE`, but the active production contract requires these timestamps.

## Lineage

The packet compares against predecessor snapshot `snap-20260806T115910Z-140c9d66` at `2026-08-06T11:59:10.108Z`. That snapshot was not accepted as the active bounded owner. The active bounded owner remains:

- run `run-20260806T101439Z-79DYrv6q`
- snapshot `snap-20260806T101439Z-caM8nhgy`
- snapshot_utc `2026-08-06T10:14:39.743Z`

Therefore the supplied packet is both validation-failed and non-owner-linked.

## Additional temporal serialization defect

The 24h/48h return rows contain impossible `window_end_utc` values in 1970:

- BTC: `1970-01-10T10:11:31.663Z`
- ETH: `1970-01-06T05:21:29.099Z`
- ETHBTC: `1970-01-01T00:00:00.181Z`

These rows are quarantined regardless of their numerical return values.

## Diagnostic observations only

- BTCUSDT: `64500.01`
- ETHUSDT: `1903.54`
- ETHBTC: `0.02952`
- BTC OI: `106836.466`
- ETH OI: `2291537.245`
- breadth: 24 advancers, 47 decliners, 18 unchanged, positive share `26.9663%`, equal-weight mean `-0.8022%`
- ETF session 2026-08-05: BTC `+244.4M`, ETH `+60.8M`, reconfirming existing owner but creating no new session
- CFGI: global 47, BTC 57, ETH 64

These observations have no bounded, canonical, A-class, shadow-counter or portfolio authority.

## Engineering owners

- issue #320: PG-003 invocation timestamps and owner re-anchoring
- issue #321: malformed 24h/48h `window_end_utc` serialization
- issue #318 remains open for parser code and fixture verification
