# Phase 0 Historical Shadow Simulation Report

Final verdict: **PASS_TO_PHASE1**

Authority: research-only shadow evaluation. No live Master Monday, Cycle Navigator, canonical market state, threshold, model weight or portfolio authority is changed.

## Result

W33-W37 all passed the four scientific hard gates:

- zero future-market leakage;
- zero retrospective forecast creation;
- zero silent canonical promotion;
- zero duplicate-evidence inflation.

Weekly process-quality scores:

- W33: 17/20
- W34: 17/20
- W35: 19/20
- W36: 20/20
- W37: 20/20

Median: 19/20. Minimum: 17/20.

## Most important design correction discovered during simulation

Historical replay needs two cutoffs, not one:

1. **Market evidence cutoff** freezes factual evidence.
2. **Processing cutoff** may be later and allows adjudication/learning/specialist processing of the already-frozen inputs.

A processing artifact created after the market cutoff is admissible only when its complete inputs are provably bound to evidence available at or before the market cutoff. Otherwise it is `NOT_EVALUABLE`.

This is required to test the desired future Monday ordering without allowing Monday-morning hindsight leakage.

## W33

The historical learning stack predates durable Unified Experimental Adjudication snapshots. The correct simulation behavior is therefore to avoid reconstructing later learning state.

Result: no justified change to the original interpretation. This is a useful clean no-op and demonstrates that the consultation layer can abstain.

## W34

A later same-Monday adjudication artifact exists, but the Phase 0 evidence record cannot prove that its entire factual input set was bound only to the earlier W34 frozen market cutoff.

Result: artifact excluded. The simulation identifies a methodology/infrastructure requirement instead: post-freeze learning jobs intended for Master Monday must publish exact input manifests.

## W35

A prior durable adjudication snapshot was available. It showed extensive semantic duplicate suppression and predominantly incubating/inconclusive research rather than independent directional confirmation.

Result: the original weak/fragile weekly interpretation remains reasonable, but the consultation layer improves uncertainty calibration by preventing raw populations of similar DOWN candidates from being mistaken for independent evidence.

## W36

The pre-cutoff adjudication state contained an ETH range family with `MATURED_SUPPORTED` evidence and five matured outcomes, alongside multiple BTC range candidates and duplicate directional candidates.

Result: Range Lab context materially improves the explanation of the original unresolved volatile transition. It supports a research-level consolidation/range interpretation without allowing a forecast-skill or canonical phase claim.

## W37

The original weekly machine package reported experiment-registry evidence as unavailable. However, fresh pre-cutoff experiment lifecycle evidence existed before the W37 Master Monday package and contained multiple matured-supported range candidates, while scientific admission separately controlled semantic duplication.

Result: this is the strongest Phase 0 value case. A provenance-valid consultation pointer would have strengthened the consolidation/range rationale while preserving the exact scientific firewall. It would not have promoted a range forecast or changed portfolio authority.

## What Phase 0 proved

The new architecture adds most value through:

- durable cross-week memory;
- semantic duplicate control;
- contradiction handling;
- explicit abstention when historical learning cannot be proven;
- range-family context;
- identification of useful information that exists but is not consumed by Master Monday;
- clear separation between weekly analysis context and future methodology improvement.

The simulation does **not** establish forecast skill and does not attempt to score the system by later price correctness.

## Required Phase 1 behavior

Phase 1 should be live parallel shadow only.

The Framework Learning Supervisor and Consultation Gate may run against the current weekly chain, but their outputs must be recorded separately and may not alter live Master Monday or Cycle Navigator.

Phase 1 should test:

- same-week provenance and freshness;
- real compute cost;
- specialist routing frequency;
- consultation usefulness;
- accepted versus rejected advice;
- false-positive opportunity detection;
- whether exact input manifests eliminate the W34 ambiguity;
- whether experiment-learning integration eliminates the W37 information-loss defect.

Only after live parallel-shadow evidence is satisfactory should consultation be allowed to influence Master Monday text or interpretation.

## Final decision

`PASS_TO_PHASE1`

No live activation is included in this Phase 0 branch.
