# COWORK OPUS 5 RESEARCH PROTOCOL ADDENDUM

This addendum is mandatory and has equal authority to `COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md`. If there is ambiguity, choose the interpretation that is more conservative scientifically and preserves the research-only boundary.

## 1. Hypothesis provenance classes
Before testing or optimizing any relationship, assign it exactly one provenance class:

- `PRE_SPECIFIED`: explicitly defined by the frozen lab config, prior research brief, prospective framework hypothesis, or master prompt before observing the final research results.
- `EXPLORATORY`: generated during analysis without inspecting the target outcome for optimization, but not pre-specified.
- `POST_HOC_DISCOVERY`: discovered after inspecting outcome-conditioned paths, event outcomes, failures, or repeated model results.

Every candidate table and machine-readable candidate record must contain `hypothesis_provenance_class` and `hypothesis_origin_receipt`.

Never present exploratory or post-hoc evidence as confirmatory. A post-hoc discovery may be `OBSERVE` or `FORWARD_TEST`, never historically validated merely because its in-sample statistics are strong.

## 2. Effective sample size and power gate
Hourly rows are not independent observations. The primary inferential unit is the independent episode or matched episode-control unit.

For every major result report:

- raw hourly observations
- unique events
- unique matched controls
- era counts
- effective inferential sample size
- dependence or clustering assumptions
- whether confidence intervals are event-clustered or episode-bootstrapped
- a qualitative power classification: `INADEQUATE`, `LOW`, `MODERATE`, or `ADEQUATE`

Do not make strong claims from a large number of hourly rows when the number of independent episodes is small.

If a severity bucket or era has too few independent events for reliable inference, report it descriptively and mark it `UNDERPOWERED`, not negative and not confirmed.

## 3. Research degrees-of-freedom ledger
Create `RESEARCH_DEGREES_OF_FREEDOM.json` listing every meaningful researcher choice made after bundle preflight, including:

- event-window choices
- feature transformations
- lag choices
- thresholds and percentile cutoffs
- interaction definitions
- sequence definitions
- model families
- hyperparameters
- control-matching variations
- missingness handling
- friction assumptions
- execution delays
- universe filters
- era boundaries
- multiple-testing families

For each choice state whether it was frozen, pre-specified, exploratory, or outcome-informed. Use this ledger when judging confidence in final candidates.

## 4. Candidate-family multiplicity
Do not apply multiple-testing correction only within convenient small tables. Define coherent feature and hypothesis families before significance testing and report:

- total hypotheses attempted
- total transformations attempted
- uncorrected results
- family-wise FDR-corrected results
- how many candidates survive correction
- whether the headline conclusion changes after correction

A candidate that exists only because many nearby thresholds or lags were tried must be treated as fragile even if one specification is significant.

## 5. Mandatory top-candidate destruction tournament
After ranking the strongest 3-5 candidate relationships, stop optimizing them and actively attempt to destroy each one.

At minimum run, where technically supportable:

1. remove the single best-performing episode
2. leave-one-episode-out across every episode
3. remove the strongest euphoric 2021 subperiod
4. historical era split
5. modern analogue replication
6. matched-control perturbation
7. event-definition perturbation within defensible frozen-neighborhood alternatives
8. timestamp shift/placebo tests
9. random pseudo-event/placebo tests
10. feature-family ablation
11. universe sensitivity
12. remove highest-liquidity proxy cohort
13. remove lowest-liquidity proxy cohort
14. missingness stress
15. friction at base, 1.5x and 2x
16. execution delay at +1h, +3h, +6h and +12h where meaningful
17. threshold-neighborhood stability rather than single optimized cutoffs
18. permutation test of labels or event assignment where statistically valid

Create `TOP_CANDIDATE_DESTRUCTION_TOURNAMENT.json` and a human-readable report.

For each candidate classify robustness as:

- `DESTROYED`
- `FRAGILE`
- `MIXED`
- `ROBUST_WITH_LIMITATIONS`
- `ROBUST`

No candidate may receive `FORWARD_TEST` unless it is at least `ROBUST_WITH_LIMITATIONS`, except where the report explicitly labels it a low-confidence exploratory forward test and explains why.

## 6. Placebo and temporal falsification
A genuine precursor should not work equally well after the event or on arbitrary timestamps.

For key candidates test:

- pseudo-events drawn from non-event periods
- temporally shifted event timestamps
- reversed or post-event feature windows when appropriate
- control periods with similar prior rally strength but no subsequent pullback

Report whether the signal has genuine temporal directionality or merely identifies generic high-volatility regimes.

## 7. Stability surface, not best point
Never headline the best-performing exact threshold, lag, or window alone.

For important candidates produce a local stability surface around plausible neighboring specifications. Prefer broad plateaus to sharp optima. A sharp optimum surrounded by failure is evidence of overfit.

Record:

- best point
- median neighboring performance
- worst defensible neighboring performance
- sign stability
- ranking stability

## 8. Incremental information standard
For CFGI or any additional feature family, require evidence of incremental value over simpler free-feature baselines.

Report:

- free-feature baseline
- added-feature model/rule
- out-of-sample or leave-one-episode-out delta
- calibration change
- precision/recall change
- lead-time change
- economic trim/reload delta after friction

If CFGI is interesting descriptively but does not improve robust decision quality beyond free features, say so explicitly.

## 9. Economic significance before statistical significance
A statistically detectable relationship is not useful if it does not survive realistic execution.

For every candidate that reaches final consideration, report whether it improves versus HOLD and naive baselines after:

- configured friction
- delayed execution
- false-trim opportunity cost
- missed rebound cost
- time out of market

Do not promote a candidate solely because a p-value or effect-size table looks attractive.

## 10. Evidence ladder and final confidence
Every final candidate must receive an evidence-ladder score across:

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

Output `FINAL_EVIDENCE_LADDER.json` with PASS/FAIL/UNDERPOWERED/NOT_TESTABLE per dimension plus explanation.

Historical fit alone can never satisfy the final ladder.

## 11. Anti-narrative requirement
For every headline conclusion include:

- strongest evidence supporting it
- strongest counterexample
- strongest alternative explanation
- what evidence would falsify it prospectively
- what remains unknown

If the data do not justify a strong conclusion, the correct output is uncertainty.

## 12. Frozen-results rule
Once the final top candidates are selected for the destruction tournament, do not revise their definitions in response to failed robustness tests. Failed tests must remain failures. Any revised definition becomes a new `POST_HOC_DISCOVERY` candidate and starts with no validation credit.

## 13. Final research verdict classes
The final executive summary must separate:

- `ROBUST_FINDING`
- `PROMISING_BUT_UNDERPOWERED`
- `EXPLORATORY_ONLY`
- `CONTRADICTED`
- `NOT_TESTABLE`

Do not collapse these into one confidence score.

## 14. Mandatory package outputs added by this protocol
The final ZIP must additionally contain:

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

The final package manifest and SHA-256 inventory must include these files.

## 15. Stop condition
Do not declare the research complete until:

- all mandatory master-prompt outputs exist
- all mandatory addendum outputs exist
- all major quantitative claims have reproducible source tables/code
- null results and failed hypotheses are preserved
- the destruction tournament is complete
- hashes and manifest verify
- no unresolved readiness blocker was bypassed

If compute/time limits prevent completion, return an explicitly incomplete package with `INCOMPLETE_RESEARCH.md`; never silently omit required work.