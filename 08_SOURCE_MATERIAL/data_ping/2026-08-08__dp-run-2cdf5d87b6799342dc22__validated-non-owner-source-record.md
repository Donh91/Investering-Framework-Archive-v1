# DATA PING source record — validated non-owner 15.3.3

```yaml
run_id: dp-run-2cdf5d87b6799342dc22
snapshot_id: dp-snap-9c852e388d2e604e4d91
snapshot_utc: 2026-08-07T22:37:36.388Z
collector_version: 15.3.3
collector_release_authority: 15.3.3
contract: DATA_PING_RUN_FIRST_STATELESS_v1
contract_version: 15.1.1
packet_sha256: e789f6edabbcc9510ad67406098cfdfe72b1f072b30fc3e0192621e7ee2f14e5
packet_bytes: 68422
validator_method: DATA_PING_PACKET_VALIDATOR_v3
validator_checks: 69
validator_failed_checks: 0
collection_status: PARTIAL
owner_grade: false
predecessor_available: false
framework_interpretation: DEFERRED_TO_MAIN_FRAMEWORK
```

## Runtime / audit evidence

- 60/60 core actions attempted.
- 1/1 optional action resolved.
- 61 logical receipts, 65 physical source invocations.
- execution order PASS.
- BINANCE_FINAL 11-action suffix PASS.
- freeze count 1, post-freeze source calls 0.
- all 69 validator checks PASS, including MTH-001, PG-003, INV-006, INV-007, ORD and freeze families.
- packet is main-thread ingestible as evidence but not owner-grade because no accepted predecessor is present.
- invocation timestamps remain sequence-only / upper-bound-oriented rather than full per-call wall-clock timestamps; this is accepted by validator v3 but does not independently satisfy the older issue #320 acceptance text.

## Direct market

- BTCUSDT final: 64892.32
- ETHUSDT final: 1914.84
- ETHBTC final: 0.02951
- BTC final OI: 106930.378
- ETH final OI: 2279702.705
- Binance basis: BTC -4.4853 bps; ETH -5.7216 bps
- OKX basis: BTC -4.3435 bps; ETH -7.2036 bps

## Same-universe breadth

Method `COINGECKO_TOP100_FILTERED_v3`, filter `BREADTH_FILTER_TOP100_EXCLUSIONS_v1`, membership hash `db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739`:

- included 89
- advancers 35
- decliners 36
- unchanged 18
- positive share 39.32584270%
- median 0.0%
- equal-weight mean -0.22471910%

This is directly comparable to the active bounded owner's same membership hash, but remains diagnostic rather than an official v1.1 breadth score.

## Flow / leverage

Spot taker buy share:

- BTC 1h 39.91%, 4h 53.57%, 12h 48.68%
- ETH 1h 52.11%, 4h 42.69%, 12h 49.46%
- ETHBTC 1h 62.38%, 4h 57.29%, 12h 53.21%

Futures taker ratio:

- BTC 1.1572
- ETH 1.4482

Global account long/short:

- BTC 1.0995
- ETH 2.0665

OI changes from exact anchors:

- BTC 1h -0.0332%, 4h -0.4310%, 24h +1.4035%
- ETH 1h -0.1368%, 4h -0.3508%, 24h -0.4437%

## ETHBTC threshold

- direct 0.02951
- 1.6333% below 0.0300
- 7.3091% above 0.0275
- no 0.0300 confirmation supplied.

## ETF 2026-08-06

BTC +137.6M and ETH +92.1M are reproduced again with zero dashes and exact local tie-out. This is corroboration only; the standing targeted two-retrieval owner contract remains incomplete.

## Source gaps

- stablecoin global total unavailable after registered fallbacks
- optional total DeFi TVL unavailable
- realized volatility partial due insufficient settled observations
- GeckoTerminal partial due low-reserve anomalies

No canonical or portfolio effect is claimed by the source.