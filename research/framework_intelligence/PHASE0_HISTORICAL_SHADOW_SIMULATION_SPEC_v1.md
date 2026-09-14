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

Each week MUST be reconstructed using a strict point-in-time cutoff. Evidence created after the historical Master Monday decision cutoff for that week is forbidden for that week's simulation, except when explicitly used in a later outcome-audit stage that is separately labelled and never fed back into the simulated decision.

## Required evidence classes

Every consumed item MUST be classified as one of:

- NOW_CURRENT_AT_CUTOFF
- RETROSPECTIVE_DESCRIPTIVE
- LEGACY_RESEARCH_CONTEXT
- PRE_PREREGISTRATION_PROSPECTIVE
- PROSPECTIVE_SHADOW
- CONFIRMATORY_ELIGIBLE
- OUTCOME_ONLY_POST_CUTOFF

OUTCOME_ONLY_POST_CUTOFF evidence MUST NOT enter the simulated Master Monday decision.

## Required simulation chain

For each week:

1. Resolve the exact original Master Monday evidence cutoff and original delivery artifact.
2. Resolve only artifacts that existed at or before that cutoff.
3. Reconstruct a duplicate-adjusted hypothesis-family memory from eligible evidence.
4. Build a Range Lab state from eligible range candidates/outcomes available at the cutoff.
5. Build a contradiction state separating horizon, regime, evidence-class and source-quality conflicts.
6. Run a Master Monday Consultation Gate with bounded questions only.
7. Produce a consultation-augmented shadow interpretation.
8. Compare the shadow interpretation with the original Master Monday using process-quality metrics, not future price correctness.
9. After the simulated decision is frozen, attach later outcomes only for an outcome-audit appendix.

## Point-in-time firewall

Forbidden:

- reading a later-week learning state and pretending it existed earlier;
- reconstructing a forecast after observing its outcome;
- changing thresholds to improve historical fit;
- treating semantic duplicates as independent support;
- counting repeated LLM commentary as new evidence;
- promoting retrospective descriptive evidence to prospective skill;
- changing the original historical Master Monday output.

## Consultation Gate

The simulated Master Monday may ask only bounded questions whose inputs are already eligible at the cutoff, for example:

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

The Phase 0 simulation should emulate bounded specialist roles where evidence exists:

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

- ZERO FUTURE LEAKAGE
- ZERO RETROSPECTIVE FORECAST CREATION
- ZERO SILENT CANONICAL PROMOTION
- ZERO DUPLICATE-EVIDENCE INFLATION

Any hard-gate failure makes the week's result FAIL regardless of score.

## Acceptance threshold

Phase 0 may progress to live parallel shadow only if:

- all five weeks pass all hard gates;
- median weekly score >= 16/20;
- no week scores below 14/20;
- at least three of five weeks show material analytical improvement over the original weekly process OR explicitly demonstrate that no additional consultation was useful;
- the simulation identifies no unbounded compute path;
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

The simulation is designed to test whether the framework can use more of what it already knows without becoming more confident than its evidence justifies.
