# Phase 0 Historical Shadow Simulation Specification v1

Status: DRAFT_SHADOW_ONLY
Authority: research / learning evaluation only
Live Master Monday influence: NONE
Canonical market authority: NONE
Portfolio authority: NONE

## Objective

Evaluate whether the proposed Framework Intelligence & Learning Loop adds material analytical value to Master Monday without hindsight leakage, duplicate evidence inflation, scientific contamination, unnecessary complexity, or unbounded compute.

## Historical windows

Evaluate ISO weeks W33, W34, W35, W36 and W37 of 2026.

## Dual-cutoff rule

Each simulated week has two distinct cutoffs:

1. `market_evidence_cutoff_utc` — freezes the market/research evidence set. No new market observation, outcome, candidate firing, daily capture, ETF observation, macro observation, price movement or other factual evidence after this timestamp may influence the simulated weekly interpretation.
2. `processing_cutoff_utc` — allows later deterministic or agentic processing of the already-frozen eligible inputs so the proposed future Monday ordering can be tested. A processing artifact created after the market cutoff is eligible only if its complete material input set is provably bound to evidence at or before the market cutoff and it introduces no post-cutoff factual evidence.

If that input binding cannot be proven, the later processing artifact is `NOT_EVALUABLE` for that historical simulation.

Later realized outcomes may be attached only after the simulated decision is frozen and only in a separate outcome-audit appendix.

## Required evidence classes

Every consumed item MUST be classified as one of:

- NOW_CURRENT_AT_MARKET_CUTOFF
- RETROSPECTIVE_DESCRIPTIVE
- LEGACY_RESEARCH_CONTEXT
- PRE_PREREGISTRATION_PROSPECTIVE
- PROSPECTIVE_SHADOW
- CONFIRMATORY_ELIGIBLE
- PROCESSING_ONLY_POST_MARKET_CUTOFF
- OUTCOME_ONLY_POST_DECISION

`PROCESSING_ONLY_POST_MARKET_CUTOFF` may influence the simulation only when its inputs are hash/time-bound to the frozen evidence set. `OUTCOME_ONLY_POST_DECISION` MUST NOT enter the simulated decision.

## Required simulation chain

For each week:

1. Resolve the original frozen weekly market evidence and original Master Monday delivery artifact.
2. Set the market evidence cutoff from the frozen point-in-time chain, not from later outcomes.
3. Resolve candidate/adjudication/learning artifacts available for a hypothetical later Monday processing window.
4. Prove that any post-market-cutoff processing artifact is bound only to frozen eligible inputs; otherwise exclude it.
5. Reconstruct duplicate-adjusted hypothesis-family memory from eligible evidence.
6. Build a Range Lab state from eligible range evidence.
7. Build a contradiction state separating horizon, regime, evidence-class and source-quality conflicts.
8. Run a Master Monday Consultation Gate with bounded questions only.
9. Produce a consultation-augmented shadow interpretation.
10. Compare the shadow interpretation with the original Master Monday using process-quality metrics, not future price correctness.
11. After the simulated decision is frozen, attach later outcomes only for a separate outcome-audit appendix.

## Point-in-time firewall

Forbidden:

- reading a later-week learning state and pretending it existed earlier;
- using new post-cutoff market observations merely because a processing job ran later Monday;
- reconstructing a forecast after observing its outcome;
- changing thresholds to improve historical fit;
- treating semantic duplicates as independent support;
- counting repeated LLM commentary as new evidence;
- promoting retrospective descriptive evidence to prospective skill;
- changing the original historical Master Monday output.

When provenance is ambiguous, classify `NOT_EVALUABLE` rather than infer.

## Consultation Gate

The simulated Master Monday may ask only bounded questions whose factual inputs are eligible at the market cutoff, for example:

- Has this sequence appeared in prior eligible evidence?
- Is current ETHBTC strength supported by breadth/transmission history?
- Does leverage materially conflict with the current rotation interpretation?
- Is a current range candidate consistent with accumulated eligible range evidence?
- Did any hypothesis family materially strengthen, weaken, become unsupported or remain unresolved since the prior week?
- Is there evidence that an existing interpretation method deserves a future method-improvement candidate?

Possible consultation outputs:

- NO_MATERIAL_LEARNING
- WEEKLY_ANALYSIS_CONTEXT
- CONTRADICTION_CONTEXT
- RANGE_CONTEXT
- METHOD_IMPROVEMENT_CANDIDATE
- EXPERIMENT_ONLY
- NOT_EVALUABLE

The consultation gate has no authority to modify canonical rules, thresholds, model weights, phase state or portfolio action.

## Specialist simulation roles

Where evidence exists, emulate bounded specialist roles:

- Sequence & Regime Analyst
- Range Lab Analyst
- Rotation Analyst
- Leverage & Microstructure Analyst
- Liquidity & Macro Analyst
- Experiment Family Analyst
- Contradiction Analyst
- Accountability Analyst
- Information Utilization Analyst
- Methodology Auditor

Specialist conclusions are interpretations, not independent evidence events.

## Scoring dimensions

Each week receives 0-2 points per dimension:

1. Evidence completeness
2. Point-in-time integrity
3. Duplicate/correlation control
4. Contradiction awareness
5. Use of prior learning
6. Regime-transfer discipline
7. Scientific-firewall discipline
8. Decision usefulness
9. Explanation compression
10. Compute/complexity discipline

Maximum: 20 points per week.

Mandatory hard gates:

- ZERO FUTURE_MARKET_LEAKAGE
- ZERO RETROSPECTIVE_FORECAST_CREATION
- ZERO SILENT_CANONICAL_PROMOTION
- ZERO DUPLICATE_EVIDENCE_INFLATION

Any hard-gate failure makes the week's result FAIL regardless of score.

## Acceptance threshold

Phase 0 may progress to live parallel shadow only if:

- all five weeks pass all hard gates;
- median weekly score >= 16/20;
- no week scores below 14/20;
- at least three of five weeks show material analytical improvement over the original weekly process OR explicitly demonstrate that no additional consultation was useful;
- no unbounded compute path is identified;
- all proposed methodology improvements remain proposal-only.

Otherwise status is NEEDS_FIX and Phase 1 is blocked.

## Outputs

Expected research-only outputs:

- `research/framework_intelligence/phase0/W33.json`
- `research/framework_intelligence/phase0/W34.json`
- `research/framework_intelligence/phase0/W35.json`
- `research/framework_intelligence/phase0/W36.json`
- `research/framework_intelligence/phase0/W37.json`
- `research/framework_intelligence/phase0/PHASE0_SUMMARY.json`
- `research/framework_intelligence/phase0/PHASE0_REPORT.md`

No output from Phase 0 may be consumed by live Master Monday, Cycle Navigator, canonical market state or portfolio logic.

## Decision states

Final Phase 0 verdict MUST be exactly one of:

- PASS_TO_PHASE1
- NEEDS_FIX
- FAIL_SCIENTIFIC_INTEGRITY

## Operating principle

Test whether the framework can use more of what it already knew at the historical market cutoff without becoming more confident than the evidence justified.
