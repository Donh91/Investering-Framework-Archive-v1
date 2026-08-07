# DATA PING SOURCE RECORD — VALIDATION FAILED

- date: 2026-08-07
- run_id: `run_d7acf5a7a58448c3`
- snapshot_id: `snap_99a76d473529f7db`
- snapshot_utc: `2026-08-07T07:43:24.203684Z`
- collector_version: `15.3.1`
- contract: `DATA_PING_RUN_FIRST_STATELESS_v1`
- collection_status: `FAIL`
- packet_sha256: `74f38320772f80a3ea6bfa288e5aaa8fdf4e94d3ccef0b32c427bbe7d22eacf9`
- validator: `DATA_PING_PACKET_VALIDATOR_v3`
- validator_pass: `false`
- failed_check_ids: `[MTH-001]`
- packet_usable_for_main_thread_ingest: `false`

## Execution evidence

The run completed the full planned execution graph:

- 60/60 core actions attempted
- 1/1 optional action attempted
- 61 resolved source invocations
- 61 receipts
- incremental commit PASS
- group transform barriers PASS
- BINANCE_FINAL atomic suffix PASS
- freeze_count 1
- post-freeze source calls 0
- execution_interrupted false

This materially differs from preceding failed run `dprun_32c45bcac4df4fa4`, which stopped after one registered core action.

## Sole blocking defect

The packet executed action `BTC_ETH_CURRENT` using `COINGECKO_SIMPLE_PRICE_v1`, but `method_versions.registered` omitted that method. The validator correctly failed closed with:

`METHOD_VERSION_NOT_REGISTERED:COINGECKO_SIMPLE_PRICE_v1`

Engineering owner: GitHub issue #326.

## Nonblocking source limitations

- BTC ETF latest settled row unresolved in returned Farside page window
- ETH ETF latest settled row unresolved in returned Farside page window
- CFGI ETH classification conflict
- stablecoin global total unresolved
- GeckoTerminal low-reserve anomalies
- realized-volatility windows insufficient history

## Diagnostic-only market evidence

These values are preserved for audit only and have zero owner/canonical authority:

- BTCUSDT final: 64,400.91
- ETHUSDT final: 1,904.20
- ETHBTC final: 0.02957
- BTC open interest: 105,256.847
- ETH open interest: 2,294,281.56
- breadth universe: 89
- advancers / decliners / unchanged: 17 / 51 / 21
- breadth advance ratio: 19.1011%
- equal-weight 24h mean: -0.65056%
- CFGI global / BTC / ETH: 48 / 57 / 60, with ETH classification conflict
- stablecoin global total: null
- ETF owner values: unavailable in this run

## Authority boundary

No bounded pointer advance. No canonical state change. No ETF owner update. No prospective evidence promotion. No portfolio action.