# DATA PING validation-failed source record — run-3d5187ccaeeea087

- snapshot: `snap-e4fcc29d6ec597cb`
- snapshot_utc: `2026-08-07T08:42:59.283786Z`
- collector: `15.3.1`
- source attachment SHA-256: `7ddc3c16911ee08e6a52ef62b3b2acbf3af27c7ea4fbc755cf25ca97f55eda86`
- collector packet SHA-256: `a45fd402b2fa4d355645073f4fc00431db7ecb051e607d3fb0afe3aa612cb44c`
- collection_status: `FAIL`
- packet usable for main-thread ingest: `false`

## Validation

Failed checks: `INV-006`, `PG-003`, `PG-004`, `PG-005`, `ORC-001`, `ORC-002`, `ORC-003`, `ORC-004`.

Execution order, receipt bijection, status reconciliation and terminal freeze passed, but incremental commit, group barrier and hash integrity failed. Payload hashes were not incrementally committed before subsequent source calls. Invocation start/completion timestamps were absent and represented only as sequence order.

## Source-health snapshot

Core actions: 60 attempted. Status counts: 53 PASS, 4 PARTIAL, 3 FAIL. Optional: 1 UNAVAILABLE.

PUBLIC_WEB failed: Farside BTC/ETH latest totals were visible as 2026-08-06 BTC `+137.6M` and ETH `+92.1M`, but dash-vs-zero semantics were not preserved, while CFGI GLOBAL/BTC/ETH parsing failed. These ETF values are diagnostic only from this failed packet and do not advance ETF ownership.

## Diagnostic market fields only

- BTCUSDT: `64484.93`
- ETHUSDT: `1906.49`
- ETHBTC: `0.02957`
- BTC OI: `104909.178`
- ETH OI: `2292478.456`
- breadth: 19 advancers / 51 decliners / 19 unchanged, 89 included, advance ratio `0.2134831461`, equal-weight mean `-0.5101123596%`
- BTC latest futures taker ratio: `1.0432`
- ETH latest futures taker ratio: `0.9735`
- BTC global long/short: `1.2492`
- ETH global long/short: `2.0609`

Relative to the then-active bounded owner (`64602 / 1903.02 / 0.02946 / BTC OI 107010.162 / ETH OI 2295968.773`), the failed packet was approximately BTC `-0.181%`, ETH `+0.182%`, ETHBTC `+0.373%`, BTC OI `-1.963%`, ETH OI `-0.152%`. These are diagnostics only.

## Authority

`VALIDATION_FAILED_NON_DECISION_OBSERVATION`. No bounded, canonical, ETF-owner, experiment-counter or portfolio pointer may advance from this packet.
