# DATA PING source record — dp-run-7ddda892cbb35d79ad53

## Identity
- contract: `DATA_PING_RUN_FIRST_STATELESS_v1`
- collector: `15.3.2`
- run_id: `dp-run-7ddda892cbb35d79ad53`
- snapshot_id: `dp-snap-50a5f320c97b9c262d36`
- snapshot_utc: `2026-08-07T10:47:45.292410Z`
- packet_sha256: `cec694e692e1a0cadc504e6909e451bfc96feaf94edef640b44f22fac964260c`
- uploaded_file_sha256: `e65a6884783f304a4e58fc2fd1834ceb1cc8f77e42c143f1a5d2d569e214ce24`
- uploaded_file_bytes: `77888`

## Runtime / validator
- runtime_completion: `COMPLETE`
- attempted core: `60/60`
- attempted optional: `1/1`
- physical source invocations: `65`
- logical receipts: `61`
- freeze_count: `1`
- post_freeze_call_count: `0`
- validator_pass: `true`
- executed checks: `69`
- passed checks: `68`
- failed/warning checks: `MTH-001 MEDIUM`
- owner_grade declared by packet: `false`
- packet_usable_for_main_thread_ingest declared by packet: `true`
- comparison/predecessor: `NOT_AVAILABLE / NO_ACCEPTED_SAME_THREAD_PREDECESSOR`

## MTH-001 state
The prior exact trigger `COINGECKO_SIMPLE_PRICE_v1` is now present in `method_versions.registered_required.current_price`, so that specific registry omission is repaired. The packet still retains 18 source actions with unresolved/null method IDs and therefore reports `method_compatibility_status: PARTIAL` and `owner_grade: false`.

## Direct market
- BTCUSDT final: `64880.01`
- ETHUSDT final: `1913.23`
- ETHBTC final: `0.02949`
- BTC OI final: `105575.678`
- ETH OI final: `2295032.378`

## ETF observation
Farside 2026-08-06 rows are complete and tie exactly:
- BTC: `+137.6M`, 12 numeric fund cells, dash_count 0, row hash `cb706308261651b9af1d5249f339ebe70a82dd15d102bf965f8b494c2ac5a1cc`
- ETH: `+92.1M`, 10 numeric fund cells, dash_count 0, row hash `38ea6dc3684145caadec59b3c8015f49493747fa7ca7dec41d5bd31bc4239092`

These corroborate the standing 2026-08-06 ETF candidates, but the packet does not satisfy the separate targeted owner-validation contract requiring two independent retrievals >=60 seconds apart with owner-grade finality evidence. ETF owner therefore does not advance from this run.

## Breadth
- membership hash: `db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739`
- included: 89
- advancers: 27
- decliners: 46
- unchanged: 16
- advance ratio: 30.3371%
- median 24h return: -0.1%
- equal-weight mean: -0.03483%

## Flow diagnostics
Spot taker buy share:
- BTC 1h/4h/12h: `47.52% / 47.29% / 45.73%`
- ETH 1h/4h/12h: `23.35% / 33.11% / 39.37%`
- ETHBTC 1h/4h/12h: `44.90% / 48.78% / 56.32%`

Latest futures taker ratios:
- BTC: `1.2779`
- ETH: `1.1210`

Global long/short:
- BTC: `1.1501`
- ETH: `2.0349`

## Classification
`VALIDATED_NON_OWNER_LINEAGE_AND_METHOD_AUTHORITY_PARTIAL_OBSERVATION`

No bounded/canonical/portfolio owner advancement is authorized from this record.
