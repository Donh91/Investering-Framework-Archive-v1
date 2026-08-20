# Mandatory Cowork Opus 5 Research Protocol Addendum

This protocol is mandatory together with `COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md`.

## Hypothesis provenance
Classify every tested relationship as `PRE_SPECIFIED`, `EXPLORATORY`, or `POST_HOC_DISCOVERY`. Preserve an origin receipt. Exploratory and post-hoc results are never confirmatory historical validation.

## Effective sample size and power
Hourly rows are not independent evidence. The primary inferential unit is the independent episode or matched episode-control unit. For every major result report unique events, controls, era counts, clustering assumptions, event-level/bootstrap uncertainty and power as `INADEQUATE`, `LOW`, `MODERATE`, or `ADEQUATE`. Underpowered findings remain descriptive.

## Research degrees of freedom
Create `RESEARCH_DEGREES_OF_FREEDOM.json` covering every meaningful event-window, transformation, lag, threshold, interaction, sequence, model, hyperparameter, control-match, missingness, friction, execution-delay, universe and era choice. Mark each frozen, pre-specified, exploratory or outcome-informed.

## Multiplicity
Define coherent hypothesis families. Report total hypotheses and transformations attempted, uncorrected and FDR-corrected results, survivors, and whether conclusions change after correction. Sharp success among many nearby failed specifications is fragile.

## Top-candidate destruction tournament
After freezing the strongest 3-5 candidates, actively try to destroy them. At minimum, where supportable:

- remove best episode
- full leave-one-episode-out
- remove strongest euphoric 2021 subperiod
- era split and modern analogue replication
- matched-control perturbation
- defensible event-definition perturbation
- timestamp-shift and pseudo-event placebos
- feature-family ablation
- universe sensitivity
- remove highest and lowest liquidity-proxy cohorts
- missingness stress
- friction at base, 1.5x and 2x
- execution delays +1h, +3h, +6h and +12h
- threshold-neighborhood stability
- valid permutation tests

Output `TOP_CANDIDATE_DESTRUCTION_TOURNAMENT.json` and `.md`. Classify each `DESTROYED`, `FRAGILE`, `MIXED`, `ROBUST_WITH_LIMITATIONS`, or `ROBUST`.

Once the tournament begins, failed candidates may not be redefined to rescue them. Any changed definition becomes a new `POST_HOC_DISCOVERY` candidate with no inherited validation credit.

## Placebo and temporal falsification
Key precursors must be tested on pseudo-events, shifted event times, relevant reversed/post-event windows, and matched strong-rally periods without pullbacks. Determine whether a candidate has temporal directionality or merely detects volatility/euphoria.

## Stability surfaces
Do not headline a single optimized lag, threshold or window. Report the best point, median and worst defensible neighboring performance, sign stability and ranking stability. Prefer broad plateaus over sharp optima.

## Incremental information
CFGI and other added feature families must beat simpler free-feature baselines on robust out-of-sample or leave-one-episode-out decision quality, calibration, precision/recall, lead time and economic trim/reload performance after friction. Descriptive interest alone is not incremental edge.

## Economic significance
Final candidates must be evaluated versus HOLD and naive baselines after friction, delayed execution, false-trim opportunity cost, missed-rebound cost and time out of market. Statistical significance alone is insufficient.

## Final evidence ladder
Create `FINAL_EVIDENCE_LADDER.json` and `.md`. Each final candidate receives PASS/FAIL/UNDERPOWERED/NOT_TESTABLE on:

1. data integrity
2. event-level sample adequacy
3. matched-control discrimination
4. temporal directionality
5. multiplicity correction
6. leave-one-episode-out stability
7. era replication
8. placebo survival
9. parameter-neighborhood stability
10. economic significance after friction
11. incremental information beyond simpler baselines
12. prospective 2026 support

## Anti-narrative requirement
Every headline conclusion must state strongest supporting evidence, strongest counterexample, strongest alternative explanation, prospective falsifier and what remains unknown.

## Final verdict classes
Separate findings into `ROBUST_FINDING`, `PROMISING_BUT_UNDERPOWERED`, `EXPLORATORY_ONLY`, `CONTRADICTED`, and `NOT_TESTABLE`.

## Additional mandatory final-ZIP outputs
- `RESEARCH_DEGREES_OF_FREEDOM.json`
- `HYPOTHESIS_PROVENANCE_LEDGER.jsonl`
- `EFFECTIVE_SAMPLE_SIZE_AND_POWER.md`
- `MULTIPLE_TESTING_AUDIT.json`
- `PLACEBO_AND_TEMPORAL_FALSIFICATION.md`
- `PARAMETER_STABILITY_SURFACES/`
- `TOP_CANDIDATE_DESTRUCTION_TOURNAMENT.json`
- `TOP_CANDIDATE_DESTRUCTION_TOURNAMENT.md`
- `FINAL_EVIDENCE_LADDER.json`
- `FINAL_EVIDENCE_LADDER.md`

Null results and failed hypotheses are mandatory outputs. If compute/time limits prevent completion, emit `INCOMPLETE_RESEARCH.md`; never silently omit required work.

Historical findings remain capped at `FORWARD_TEST`. No live execution, production state mutation or automatic rule promotion is authorized.