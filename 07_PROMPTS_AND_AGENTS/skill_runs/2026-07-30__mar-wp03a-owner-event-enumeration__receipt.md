# MAR-WP03A Owner Event Enumeration — Receipt

- Date: 2026-07-30
- Parent issue: #209
- Work issue: #227
- Branch: `agent/mar-wp03a-owner-event-enumeration-v1`
- Scope: development window only

## Result

One independent owner-source event was enumerated under the frozen WP03 contracts:

`MAR_ETHBTC_0300_20260728T150000Z_C01`

Direct settled Binance ETHBTC hourly rows show acceptance above 0.0300 at 15:00 and 16:00 UTC on 2026-07-28, followed by a settled close below the threshold at 17:00 UTC. The event is therefore assigned the preregistered label `FAILED_PERSISTENCE`.

Eight subsequent hourly crossings/observations were assigned to the same overlap cluster and are not independent observations.

## Lineage

The event is `OWNER_PARTIAL`, not fully replayable, because the scoped owner artifact does not provide all frozen pre-event checkpoints at -72h, -24h and -4h.

Blocked families remain explicit:

- BTC/ETH settled range breaks: missing complete boundary/price owner join;
- breadth displacement/divergence: missing complete machine materialization with identical membership-hash parity;
- ETF reversals: row-level publication/retrieval availability unresolved from WP02C.

## Scientific boundary

- Forward returns calculated: NO
- Hit rates calculated: NO
- Economic ranking: NO
- Parameter search: NO
- Final holdout accessed: NO
- Framework promotion: NONE
- Portfolio effect: NONE

## Validation

A deterministic structural validator is included. No GitHub Actions execution is claimed unless a workflow run is separately observed.
