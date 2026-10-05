# M6 SPAR Comparator Feasibility Method v1

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Status:** FROZEN_BEFORE_FEASIBILITY_REPLAY  
**Authority:** RESEARCH_ONLY / DISCOVERY_ONLY  
**Framework main at freeze:** `675079f2d977a9a121649972cbf28f514537daad`

## Purpose

Decide whether a new prospective SPAR validation identity is worth freezing, and which simple comparator it must beat.

This replay cannot establish incremental edge because the comparator family was not part of SPAR-v1's original preregistration.

## Data boundary

Use only accepted SPAR snapshots at or after both:
- original SPAR preregistration;
- adapter-v2 cutover.

No pre-cutover rows.

Use the existing SPAR input adapter and existing 24/72/168h outcome matcher without modifying them.

## Event identities

All event identities use the existing sign-only transitions. No fitted thresholds.

### TARGET_STRICT_P3

A strict temporal successor to SPAR-P3:

1. transition i: BTC resilience AND breadth deterioration;
2. transition j must be later than i, never the same transition;
3. j may be either of the next two transitions;
4. transition j: ETH relative weakness;
5. event timestamp = snapshot after transition j;
6. 72h cooldown.

This is discovery-only on old rows. If used prospectively later, it requires a new experiment identity.

### PRIMARY_COMPARATOR_ETH_WEAKNESS

Any ETH relative weakness transition:
- event timestamp = snapshot after that transition;
- 72h cooldown.

Reason chosen before replay:
ETH weakness is the terminal condition of TARGET_STRICT_P3. This comparator asks whether the preceding BTC-resilience + breadth-deterioration sequence adds information beyond merely observing ETH/BTC weaken.

### SECONDARY_COMPARATOR_BREADTH

Any breadth deterioration transition with 72h cooldown.

### PRECURSOR_ONLY

BTC resilience AND breadth deterioration on the same transition, 72h cooldown.

This tests whether waiting for later ETH weakness changes the observed outcome profile.

### REFERENCE_V1_P3

Existing SPAR-v1 P3 as currently implemented, including its known possibility of same-transition satisfaction.

This is reference only, not a candidate for confirmatory reuse.

## Frozen outcomes

Primary feasibility horizon:
- 72h

Primary metrics:
- BTC MAE
- BTC terminal return

Secondary:
- BTC MFE
- ETH MAE/MFE/terminal
- ETHBTC terminal
- 168h BTC/ETH terminal and MFE as premature-exit context

No composite score.

## Diagnostics

For each event identity report:
- event count;
- matured counts;
- non-overlapping 72h and 168h counts;
- event timestamps;
- median frozen outcomes;
- overlap counts between target and comparators.

## Interpretation

This is not a statistical test.

It answers only:
- is strict P3 sufficiently frequent for future validation?
- does it show a materially different descriptive profile from ETH weakness alone?
- is a new prospective identity worth the calendar cost?

## Decision rule

A new strict-P3 prospective identity is **not automatically justified** by a more negative historical median.

Proceed to prospective freeze only if:
1. target event frequency is non-trivial;
2. the primary comparator is sufficiently populated;
3. the design can be tested without new paid data;
4. the future claim is explicitly incremental versus the primary comparator;
5. no simpler existing owner already answers the same question.

If the strict target is too rare, preserve SPAR-v1 as descriptive evidence and do not create an underpowered new identity.

No market rule, portfolio rule, threshold change or promotion.
