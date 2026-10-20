# Pons Early-Buyer Precursor Integration v1 — 2026-10-06

Status: MERGED / RESEARCH_ONLY / FORWARD_EVIDENCE_PENDING

Merged PR: #1522
Merge commit: `32a7b204cbd91eb8efb1f8e76300c73297bd93f9`

Existing owners:
- #1419 Conviction Wallet Intelligence
- #1018 prospective G2/G3 shadow harness
- `06_RESEARCH_LAB/alpha_lab/2026-10-02__wallet-precursor-execution-fidelity-prospective-experiment-v1__prereg.md`

No new scanner, scorer, ledger, scheduler, alert path or trading authority was created.

## What was added

The existing Clean G3 wallet-quality primitive is now reusable across explicitly admitted buyer-graph contracts while the original Pump/Solana wrapper remains backward compatible.

Pons/Robinhood has a dedicated adapter:
- input: immutable `MAL_PONS_CURVE_CAPTURE_CASE_V1`
- input: immutable `MAL_PONS_EARLY_BUYER_COHORT_FREEZE_V1`
- graph: `MEME_ALPHA_PONS_EARLY_BUYER_GRAPH_v1`
- cohort semantics: CurveBuy token recipient, not automatically tx initiator
- fixed feature cutoff: first 5 minutes after launch
- signal availability: latest of case freeze, cohort freeze and prospective-credit time
- launch-time action credit: false

Wallet quality remains:
- chain local
- venue local
- role local
- based only on outcomes matured by cutoff
- future reputation/outcomes forbidden
- cross-chain skill import forbidden

Wallet Alpha registry state is admitted only when its review timestamp is at or before the buyer-graph cutoff.

Entity treatment remains conservative:
- SAME_FUNDER does not collapse identity
- BUNDLE_LINK does not collapse identity
- only STRONG_CONTROLLER evidence collapses addresses

Research precursor states:
- UNKNOWN
- WATCH
- MULTI_ENTITY_CONVERGENCE

`TIME_SENSITIVE_PRECURSOR` is deliberately not emitted by this adapter. It requires separate lead-time evidence.

A wallet counts toward convergence only if BOTH are true:
1. locally matured Pons/Robinhood history satisfies the existing minimum-history rule; and
2. its point-in-time Wallet Alpha state is REPEATABLE_EDGE_CANDIDATE or REPEATABLE_EDGE_SUPPORTED.

## Exact-head gates

PASS:
- Meme Alpha Clean G3 Core Gate
- Meme Alpha Runtime Gate
- API Agent Gateway Gate
- Data Architecture Gate
- Continuity Learning Gate
- Storage Health Gate
- Automation Production Health Gate
- Full Architecture 1-7 Gate
- Owner-Bound Daily Director Manual

The first architecture pass exposed an unrelated existing unsafe main-writer in `.github/workflows/edge001-t2-registry.yml`. The smallest governance repair was included:
- removed push-triggered main writing
- pinned manual execution to main
- moved to framework-main-writer queue
- added safe rebase/retry/main-readback behavior

No EDGE-001 research logic changed.

## Pons forward runtime

Durable Pons capture has independently established its real forward boundary:
- activation_utc: `2026-10-06T21:36:02Z`
- next runtime: PASS at `2026-10-06T21:41:43Z`
- no errors
- no post-activation eligible launch yet

Current capture state:
`ACTIVE_WAIT_FIRST_ELIGIBLE_CASE`

Do not loosen selection rules or grant pre-activation credit.

## Next scientific step

Before Robinhood wallet activity/funding data may become canonical precursor evidence, prove bounded historical coverage/completeness through the existing Blockscout runtime owner.

Missing or truncated wallet history must remain UNKNOWN, never inactivity.

Current edge state:
`CAPABILITY_MERGED / PROSPECTIVE_EDGE_NOT_YET_PROVEN`.
