# MAR-WP03B Owner History Completion — Receipt

- Date: 2026-07-30
- Parent issue: #209
- Prior work issue: #227
- Branch: `agent/mar-wp03b-owner-history-completion-v1`

## Result

WP03B reviewed the available direct owner history for the materialized ETHBTC 0.0300 event and the blocked event families.

The settled Copenhagen daily owner rows add valid context before and across the event, but they do not satisfy the exact preregistered hourly checkpoints at -72h, -24h and -4h. The event therefore remains `OWNER_PARTIAL`; no daily value was substituted for an hourly checkpoint.

The breadth family is now classified more precisely as retroactively irrecoverable for the DCR-002 event. The accepted audit established that exact predecessor/current constituent snapshots were not retained. Current-universe substitution and retrospective reconstruction remain forbidden. Prospective repair is governed by the Point-in-Time Breadth Sidecar Retention Addendum and issue #224.

BTC/ETH range events remain blocked pending a frozen-boundary plus settled-owner-price join. ETF reversal events remain blocked pending row-level publication and retrieval availability timestamps.

## Scientific boundary

- Forward returns calculated: NO
- Hit rates calculated: NO
- Economic ranking: NO
- Parameter search: NO
- Final holdout accessed: NO
- Framework promotion: NONE
- Portfolio effect: NONE

## Next

Proceed to MAR-WP03C prospective lineage completion and safe descriptive audit. Only newly retained point-in-time evidence may upgrade lineage. No retroactive breadth reconstruction is permitted.