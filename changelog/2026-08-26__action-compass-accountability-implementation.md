# Action Compass accountability implementation

**Date:** 2026-08-26
**Status:** PROPOSED_OPERATIONAL_IMPLEMENTATION

## Delivered

- one deterministic, immutable receipt per fresh Action Compass interpretation;
- exact input-packet hash, canonical-commit binding and activation ancestry;
- separate Lane-3 state, warning and action fields;
- bounded data-quality and rationale tags, with private and portfolio shape rejection;
- replay deduplication with `DUPLICATE_NOOP` and no new observation;
- no historical chat backfill before the activation marker reaches `main`;
- separate immutable 24H, 7D, 30D, 90D and 180D continuous outcome sidecars;
- daily maturation through the existing Framework Learning Operations writer;
- deterministic discovery priority for Action Compass outcomes in the existing Adaptive Decision Miss auditor.

## Continuous outcome boundary

The sidecars measure terminal return, drawdown, upside, time to trough, time to recovery and a normalized full-exit versus one-unit-hold counterfactual on the existing public BTC and ETH observer series. They do not claim portfolio performance and contain no `HIT`, `MISS`, new market label, threshold or automatic action.

## Authority

```text
new engine: NO
new test ID: NO
new market score: NO
new market threshold: NO
automatic portfolio execution: NO
automatic promotion: NO
historical chat backfill: NO
Round 3 analysis or scoring: OFF
```
