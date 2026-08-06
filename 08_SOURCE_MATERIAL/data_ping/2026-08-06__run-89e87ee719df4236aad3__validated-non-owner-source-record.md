# DATA PING source record — validated non-owner

- Run ID: `run-89e87ee719df4236aad3`
- Snapshot ID: `snap-0cc3b5c7eb8740269a3b`
- Snapshot UTC: `2026-08-06T16:00:43.486Z`
- Collector: `15.2.0`
- Contract: `DATA_PING_RUN_FIRST_STATELESS_v1`
- Source collection: `PARTIAL`
- Packet validation: `PASS`
- Packet SHA-256: `a02aacc8abc7805bc8195f5dd02ede00545aa254f5dc3279595b18c8376ab566`
- Freeze count: `1`
- Post-freeze calls: `0`
- Delivery: user-supplied inline packet

## Validation shape

All 60 core actions were attempted. The packet reports 57 PASS, 3 PARTIAL and no core FAIL/UNAVAILABLE/STALE rows. Receipt bijection, invocation integrity, execution order, settled-candle filtering, freeze invariants and packet validation all passed. Retrieval timing is encoded as a common UTC base plus per-invocation start offsets and durations and is declared `EXACT_PER_INVOCATION`.

## Lineage

The packet compares against:

- predecessor run: `run-20260806T115910Z-04fa4db6`
- predecessor snapshot: `snap-20260806T115910Z-140c9d66`

That predecessor has not been accepted as the active bounded owner. The active bounded owner at ingest time remains:

- run: `run-20260806T101439Z-79DYrv6q`
- snapshot: `snap-20260806T101439Z-caM8nhgy`
- snapshot UTC: `2026-08-06T10:14:39.743Z`

Therefore this packet is source-valid but lineage-blocked and cannot replace the bounded owner.

## Direct observations

- BTCUSDT: `64638.72`
- ETHUSDT: `1911.52`
- ETHBTC: `0.02956`
- BTC open interest: `106549.743`
- ETH open interest: `2300824.063`
- BTC ETF 2026-08-05: `+244.4M USD`
- ETH ETF 2026-08-05: `+60.8M USD`
- CFGI global: `52 Neutral`
- CFGI BTC: `55 Neutral`
- CFGI ETH: `61 Greed`, source status `PARTIAL` because the page contained an internal score/classification conflict
- VIX: `15.81`

## Breadth

Method: `COINGECKO_TOP100_FILTERED_v3`
Filter: `BREADTH_FILTER_TOP100_EXCLUSIONS_v1`
Membership hash: `db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739`

- Included: `89`
- Advancers: `30`
- Decliners: `45`
- Unchanged: `14`
- Positive share: `33.70786517%`
- Median return: `-0.1%`
- Equal-weight mean: `-0.4393258427%`

The supplied breadth method remains incompatible with the locked scoring owner `BREADTH_FILTER_TOP100_EXCLUSIONS_v1_1`; it is diagnostic only.

## Derived-feature QA limitation

The earlier malformed 1970 `window_end_utc` values are absent from this compact packet. However, the 24h/48h `return_range_rows` now contain only numeric feature values and do not expose row-level source-backed `window_start_utc` and `window_end_utc`. Consequently issue #321 is not yet proven resolved.

## Authority

- Collector interpretation: `DEFERRED_TO_MAIN_FRAMEWORK`
- Main-thread classification: `VALIDATED_NON_OWNER_LINEAGE_BLOCKED_OBSERVATION`
- Bounded owner advancement: `NO`
- Canonical state effect: `NONE`
- Portfolio effect: `NONE`
