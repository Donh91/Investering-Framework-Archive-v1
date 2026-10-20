# Shared Row Tournament activation-readiness review — 2026-10-05

**Status:** READY_FOR_CURRENT_GATE_VALIDATION / NOT_ACTIVATED  
**Authority:** RESEARCH_ONLY / NON_CANONICAL  
**Base main:** `5720bb9a21ae9a6e47198a6c973dd2a6c2cb34aa`  
**Purpose:** trigger the existing Shared Row Tournament Research Gate on current code and record source-readiness evidence.  
**This file does not activate collection.**

## Frozen activation contract

The existing P0 repair requires, before any new future floor:

1. merged P0 implementation and negative controls;
2. one complete post-repair 168-hour direct ETH/BTC window;
3. one complete immutable dated breadth owner bundle;
4. three chronological settled CMC BTC.D prints;
5. all bound source availability after the implementation boundary;
6. a separate future floor later than the complete first-row source set.

Implementation boundary:
`2026-08-23T08:18:29Z`

Containment sentinel remains active at this review.

## Current-source readiness reproduced from main

### ETH/BTC

Direct daily hourly files inspected:
2026-09-28 through 2026-10-05.

At common information cutoff after 2026-10-05T14:00:00Z, the latest legal direct window contains:

- 168 unique timestamps;
- start 2026-09-28T14:00:00Z;
- end 2026-10-05T13:00:00Z;
- exact 167-hour span;
- zero duplicate timestamps;
- zero one-hour continuity gaps;
- zero non-PASS spot rows;
- all `source_window_end_utc` values no later than the cutoff;
- all source availability well after the P0 implementation boundary.

Mechanical source gate:
`SATISFIED_ON_CURRENT_MAIN`

### Breadth

Dated owner bundle:
`03_DAILY_CAPTURE_LOGS/breadth_rich/2026/10/2026-10-05/`

Contains:
- owner_snapshot.json
- receipt.json
- artifact_manifest.json
- raw_source_payload.json

Owner:
- contract `C5E_TOP100_BREADTH_OWNER_v1_2`
- method `TOP100_FILTERED_STABLE_EXCLUSION_RICH_BREADTH_v1_2`
- provider `COINGECKO_MARKET_CAP`
- retrieval/freeze `2026-10-05T12:17:44.779378Z`
- 100 constituents
- frozen membership hash present

Receipt:
- status PASS
- aggregate replay PASS
- run ID agrees with owner
- membership hash agrees with owner
- constituent count = 100

Manifest:
- `C5E_ARTIFACT_MANIFEST_v1`
- run ID agrees with owner/receipt
- binds required immutable bundle members.

Mechanical source gate:
`SATISFIED_ON_CURRENT_MAIN`

### BTC.D

Source:
`03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv`

Latest settled rows available before the common Oct-05 cutoff include:
- 2026-10-02
- 2026-10-03
- 2026-10-04

Rows are:
- provider CoinMarketCap;
- source symbol CMC_GLOBAL_METRICS_BTC_DOMINANCE;
- UTC settled;
- SETTLED_COMPLETE_DATE;
- data_quality PASS;
- source_status PUBLIC_SOURCE_BACKED;
- source verification timestamp 2026-10-05T12:34:53Z.

Mechanical source gate:
`SATISFIED_ON_CURRENT_MAIN`

## P0 implementation / review lineage

PR #519 merged at:
`f7de1f0b92278d3d887077d40d61fc453fc9e084`

PR validation declared:
- validate_core_prospective_freeze: 8 production-shaped tests;
- validate_next_action_controller: 12 checks;
- materializer fail-closed while quarantined;
- independent adversarial sentinel dry-run PASS.

Two automated review findings were later addressed on current main:

1. frozen row provenance is now recomputed and verified before outcome maturation;
2. weekly and relevance consumers now share the integrity filter for repaired rows / valid divergences.

This review does not treat old PR prose as sufficient current proof. The purpose of this PR is to rerun the existing gate on the current tree.

## Required PR gate result

The existing workflow:
`.github/workflows/shared-row-tournament-research-gate.yml`

must pass on this PR.

It runs:
- Python compile
- tournament contract validation
- `validate_core_prospective_freeze.py`
- `validate_next_action_controller.py`
- evidence-controller status
- maturation
- weekly tournament
- relevance
- monitor
- dry-run next-action controller.

## Activation decision boundary

Even if the PR gate passes:

`COLLECTION_STATE_CHANGE = NOT_IN_THIS_PR`

`NEW_FUTURE_FLOOR = NOT_IN_THIS_PR`

A separate ChatGPT activation adjudication must choose a genuinely future floor after this complete source set and must never backdate rows.

No market threshold changes.
No model-weight changes.
No portfolio authority.
No canonical market-state effect.
