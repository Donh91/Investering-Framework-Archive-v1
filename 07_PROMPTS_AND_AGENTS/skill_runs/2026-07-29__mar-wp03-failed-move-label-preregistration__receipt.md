# MAR-WP03 Failed-Move Label Preregistration — Receipt

- receipt_id: `MAR-WP03-20260729-001`
- program: `MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1`
- work_package: `MAR-WP03`
- status: `LABELS_AND_WINDOWS_FROZEN_BEFORE_EVENT_ENUMERATION`
- authority: `RESEARCH_CONTROL_ONLY`

## Completed

1. Preregistered direct ETH/BTC threshold-attempt labels for 0.0275 and 0.0300.
2. Preregistered BTC/ETH settled range-break, failed-break and failed-reclaim labels.
3. Preregistered breadth displacement and price/breadth divergence labels with mandatory membership-hash parity.
4. Defined ETF reversal labels but blocked hard enumeration pending row-level availability timestamps.
5. Frozen event windows, persistence checkpoints, outcome horizons and overlap-clustering rules.
6. Enforced one independent event per overlap cluster.
7. Added a strict event-row schema with zero outcome access and zero portfolio authority.
8. Added deterministic structural validation.

## Scientific boundary

- historical event enumeration: `NOT_STARTED`
- event rows created: `0`
- outcomes inspected: `NO`
- economic comparison: `LOCKED`
- parameter search: `NOT_RUN`
- final holdout: `SEALED`
- retrospective event creation: `FORBIDDEN`

## Material design decisions

- Direct gates require direct owner data; derived ratios cannot substitute.
- Settled acceptance, failed acceptance and failed persistence are separate labels.
- Breadth labels require identical universe membership hash across compared snapshots.
- Same-cluster follow-ups are not independent samples.
- Missing owner-source checkpoints are right-censored, not replaced.
- Confounds are recorded prospectively and cannot be filtered post hoc merely because outcomes are inconvenient.

## Gate result

- preregistration integrity: `PASS_FOR_BRANCH_STRUCTURE`
- event enumeration authority: `READY_FOR_BOUNDED_OWNER_LINEAGE_AUDIT`
- economic execution: `NO_GO`

## Next work order

`MAR-WP03A_OWNER_EVENT_ENUMERATION_AND_LINEAGE_AUDIT`

Enumerate only owner-source events in the non-holdout development window, apply the frozen cluster rules, quarantine partial lineage and do not calculate forward returns or economic rankings.
