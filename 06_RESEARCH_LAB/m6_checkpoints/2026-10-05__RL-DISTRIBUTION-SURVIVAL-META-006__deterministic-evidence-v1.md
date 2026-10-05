# M6 Deterministic Evidence Checkpoint v1

**Mission:** `RL-DISTRIBUTION-SURVIVAL-META-006`  
**Date:** 2026-10-05  
**Status:** INTERIM_DETERMINISTIC_EVIDENCE  
**Authority:** RESEARCH_ONLY  
**Framework main:** `7a9d5ca0411f11a2b4774578537cec6c1fcb1f88`

## Current question

Can existing framework machinery add useful distribution / pullback warning lead time while avoiding premature exits?

This checkpoint does not define an exit rule.

## Evidence owner map

| Owner | Current state | M6 use |
|---|---|---|
| SPAR-v1 | Fresh zero-cost replay complete | Descriptive sequence/lead-time discovery |
| SPAR fragility | BLOCKED, placebo/regime methods not prospectively frozen | No inferential claim |
| T4 Pullback Edge | One historical-as-was event has 24h/72h maturity | Concrete false-exit / warning-not-sell case |
| T5 FNP_CUMULATIVE | Outcome/evaluator rows not ready | Cannot quantify cumulative false-negative/false-exit cost yet |
| T6 Rotation Survival | 15 prospective natural rows, zero eligible first cross | Instrumentation healthy, exit-side outcome not yet available |
| Action Compass protection calibration | 238 source outcomes, 0 eligible typed rows | Prospective collection only |
| ETF Absorption/Transmission | Queued behind SPAR fragility + verified adapter | Not runnable now |
| Shared decision-distribution ledger | Append-only owner exists but current state does not contain T4 maturity | Archive completeness needs audit |

## 1. SPAR fresh replay

A fresh run of the existing sequential research queue completed successfully on 2026-10-05 with zero paid calls.

Current identity remains:
`DESCRIPTIVE_SEQUENCE_OUTCOME_ASSOCIATION_ONLY`

No incremental value versus single-sensor states is established.

Prospective-only summary:

### P1
72h:
- n=11
- BTC median return +0.51%
- BTC median MAE -1.47%
- BTC median MFE +1.43%
- ETH median return +1.73%

168h:
- BTC median return +1.49%
- ETH median return +1.36%

### P2
72h:
- n=11
- BTC median return -1.04%
- BTC median MAE -1.40%
- BTC median MFE +0.60%
- ETH median return +0.62%

168h:
- BTC median return +1.66%
- ETH median return +1.49%

### P3
72h:
- n=15
- BTC median return -0.50%
- BTC median MAE -1.29%
- BTC median MFE +1.29%
- ETH median return -0.21%
- ETH median MAE -1.57%
- ETH median MFE +1.15%

168h:
- n=13
- BTC median return +1.69%
- ETH median return +2.04%

Interpretation boundary:
The P2/P3 short-horizon weakness followed by positive 7d medians is consistent with a potential warning-versus-premature-exit tradeoff. It is not evidence of an exit edge because no prospective placebo, regime split or single-sensor comparator is frozen.

## 2. T4 historical-as-was falsification case

Event:
`PULLBACK_EDGE_20260708_01`

Canonical warning anchor:
- 2026-07-08T14:03:00Z
- BTC 61,784.48

72h matured outcome:
- horizon high 64,692.83
- horizon low 61,544.56
- horizon close 64,248.00
- maximum additional drawdown after warning -0.3883%
- maximum rebound +4.7073%
- terminal 72h return +3.9873%
- time to low 1h22m

Framework event judgment:
- market stress detection: `PARTIALLY_SUPPORTED_SHORT_LIVED_STRESS`
- tactical trim execution 24h/72h: `NOT_SUPPORTED`
- downgrade logic: supported
- close logic: supported
- no active trim
- no portfolio action change

This is direct evidence against treating a warning as an automatic sell.

### T4 archive completeness gap

The owner scheduled a 7d maturity row for 2026-07-15T14:03:00Z.

Current-main search has not located the matured 7d row.

Do not infer or recompute it into historical-as-was evidence without a separately labelled reconstruction.

## 3. T6 prospective rotation survival

15 natural observations currently exist from 2026-09-14 through 2026-10-05.

All currently report:
`NO_ELIGIBLE_FIRST_CROSS`

Registered ETHBTC level:
`0.0300`

The trigger requires:
`prior ETHBTC < 0.0300 <= current ETHBTC`

Instrumentation began while ETHBTC was already above 0.0300.

Therefore it correctly does not fabricate a first cross.

Consequences:
- no active sequence;
- no delay cost;
- no failure outcome;
- no exit-side outcome.

This is healthy right-censoring, not test failure.

## 4. Action Compass prospective exit calibration

Latest report:
- generated 2026-10-05T07:12:24Z
- source outcome count: 238
- eligible series rows: 0
- warning rows: 0
- state: `COLLECTING_PROSPECTIVE_TYPED_ROWS`

Exclusions are dominated by pre-decision-integrity schema/policy and non-machine projection sources.

Correct action:
wait for typed prospective rows.

Do not backfill historical prose.

## 5. Strongest evidence against a useful exit engine so far

T4 shows a real warning that would have been costly to convert into an immediate trim.

SPAR currently shows that candidate stress sequences can have short-horizon weakness but positive 7d outcomes.

Together these support a critical design requirement:

**Warning quality and sell timing must be scored separately.**

A useful distribution system must prove that staged risk reduction improves the joint frontier of:
- drawdown avoided;
- upside retained;
- false exits;
- re-entry opportunity.

## 6. Strongest evidence that research is worth continuing

The framework now has:
- point-in-time prospective SPAR events;
- explicit MAE/MFE outcomes;
- a real historical warning event with measured false-exit cost;
- prospective typed protection calibration;
- prospective T6 instrumentation;
- a pre-existing canonical research program that already defines the correct loss function.

The problem is no longer conceptual design.

The bottleneck is enough clean, comparable episodes plus frozen controls.

## 7. Current no-hindsight next actions

### RUN NOW / already run
1. SPAR deterministic base replay - completed fresh.
2. M6 evidence-owner reconciliation - this checkpoint.

### FREEZE NEXT
3. New prospective SPAR inferential identity:
   - freeze placebo timestamp universe and exclusions;
   - freeze regime definitions and minimum support;
   - freeze primary claim hierarchy / multiplicity;
   - freeze single-sensor comparator;
   - strict P3 temporal sequence under a new identity.
   Old events remain discovery/descriptive only.

### WAIT FOR NATURAL MATURITY
4. T6 first-cross sequence.
5. Action Compass typed warning rows.
6. T5 FNP source/evaluator rows.

### AUDIT / REPAIR EVIDENCE COMPLETENESS
7. Locate or formally mark missing T4 7d maturity.
8. Reconcile T4 maturity with shared decision-distribution ledger.

### BLOCKED
9. ETF absorption/transmission until SPAR fragility + adapter gate.
10. Any live exit rule or portfolio automation.

## 8. Question for GPT-6.1 Sol

Perform bounded scientific/economic falsification only.

Do not invent new signals.

Assess:
1. Is the current evidence sufficient to justify continuing Distribution Survival research?
2. Does any existing result support a live sell/trim rule? Expected answer must be evidence-based, not assumed.
3. What does T4 imply about false-exit cost?
4. What does SPAR imply, and what can it not imply?
5. Is the proposed next step, freeze a new prospective SPAR inferential identity, the cheapest decisive falsifier?
6. Should any other existing owner be prioritized first?
7. What is the smallest decision frontier M6 should evaluate when clean episodes mature?

Return `selected_live_rules=[]`.

No market rule.
No portfolio action.
No threshold change.
No canonical promotion.
