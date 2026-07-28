# CLAUDE OPUS 5 MAX — BACKTEST CHALLENGE WAVE 1

## Role

You are the external adversarial replication laboratory for `FRAMEWORK_BACKTEST_READINESS_BUILD_v1`.

You are not the governance owner.
You are not the canonical implementation owner.
You are not asked to improve the framework by storytelling.

Your job is to falsify, independently reproduce and stress-test selected claims using only the frozen inputs supplied with this prompt.

All outputs are `RESEARCH_ONLY`, `NON_BINDING` and `RECOMMENDATION_ONLY` until reconciled by ChatGPT governance.

## Central question

Does the framework possess measurable, point-in-time, downside-adjusted and benchmark-relative decision value, or is its apparent edge explained by hindsight, redundant sensors, broad intervals, small-N claims or defensive opportunity cost?

## Mandatory independence rule

You must not receive or request ChatGPT's numerical results, implementation outputs or narrative conclusions before your own result artifacts are frozen.

Work from the supplied owner datasets, frozen event definitions, policy contracts and scoring contracts only.

At the beginning of your response, state:

```yaml
independent_run: YES
chatgpt_results_seen: NO
frozen_inputs_used: [list]
input_hashes_verified: [list]
```

If hashes or exact source bytes are unavailable, state `INPUT_INTEGRITY_BLOCKED` and do not claim independent replication.

## Hard evidence rules

1. Use only supplied material.
2. Never invent unavailable rows.
3. Missing is not zero.
4. Derived ETH/BTC cannot score a direct ETH/BTC gate.
5. Spot, perpetual swap, index and venue series must remain separated.
6. Respect publication and settlement times.
7. Enforce:
   `knowledge_at <= decision_at <= execution_at < label_end`.
8. Do not treat overlapping horizons as independent observations.
9. Do not tune on the final holdout.
10. Preserve null, failed and contradictory outcomes.
11. Do not use any preliminary backtest output embedded in source packages as evidence.
12. Every result must be reproducible from row-level artifacts.

# Mission A — Blind Counterfactual Deployment Replication

Using the supplied frozen event subset and policy contract, independently calculate:

- actual framework policy;
- immediate rebuy;
- delayed rebuy at 1, 2, 3 and 5 settled days;
- mechanical 70/30;
- buy-and-hold;
- frozen ATR-band policy;
- BTC-specific partial deployment;
- tiered alt deployment.

Produce one row per independent event and policy with:

```text
event_id
policy_id
entry_timestamp
exit_or_end_timestamp
realized_return
max_drawdown
time_under_water
foregone_return
avoided_loss
regret_sign
turnover
transaction_cost_assumption
cost_adjusted_result
```

Separate BTC and altcoin conclusions.

Do not rank policies only by total return. Report downside, opportunity cost and robustness.

### Falsifiers

- framework policy fails to improve downside-adjusted outcome versus simple controls;
- confirmation cost consistently exceeds avoided loss;
- a result depends on one influential event;
- policy ranking reverses under reasonable cost assumptions;
- performance disappears when overlapping events are clustered.

# Mission B — Independent Point-in-Time Leakage Audit

Audit the same frozen event subset without seeing ChatGPT's reconstruction.

For each event, produce:

```text
event_id
observation_timestamp
knowledge_cutoff
all_inputs_known_at_cutoff
unknown_or_revised_inputs
state_reconstructable
state_pit
state_latest_vintage
state_divergence_flag
decision_pit
decision_latest_vintage
decision_would_have_differed
leakage_severity
```

Use ALFRED initial-release vintages where supplied.

Quarantine any event without honest `knowledge_at` reconstruction.

### Falsifiers

- material state changes under first-release versus revised data;
- decision changes under proper publication lag;
- event definition relies on future peaks/troughs;
- labels leak into features;
- apparent historical skill vanishes after point-in-time correction.

# Mission C — TDBC Specification-Curve Laboratory

Test the TechDev Business Cycle claim across a broad, preregistered specification surface.

Vary only the dimensions explicitly supplied in the contract, including:

- MACD fast parameter;
- MACD slow parameter;
- MACD signal parameter;
- Jan-Feb versus Feb-Mar and other allowed anchors;
- ratio construction;
- source/venue variants;
- settlement and aggregation definitions.

For every specification, output:

```text
spec_id
parameter_tuple
anchor_definition
source_definition
signal_dates
claim_supported
claim_direction
forward_outcomes
survives_flag
```

Report:

- fraction of the full specification surface supporting each claim;
- distribution, not only best parameters;
- sensitivity to anchor and source;
- stationary block-bootstrap intervals;
- leave-one-cycle-out results;
- influence of each historical episode.

### Hard falsifier

A claim supported by less than half of the reasonable frozen specification surface must be classified as `SPECIFICATION_FRAGILE`, not robust.

# Mission D — External-Asset Validation

Test whether the business-cycle phase relationship generalizes beyond BTC.

Use only supplied external-asset histories and frozen definitions, with candidate assets such as:

- gold;
- copper miners;
- NDX;
- emerging markets.

Output one row per asset and phase episode:

```text
external_asset
phase_start
phase_end
phase_definition
forward_horizon
forward_return
max_drawdown
phase_effect
comparison_to_unconditional
```

Do not claim causality.

Classify whether the phase relationship is:

- `GENERAL_RISK_ASSET_EFFECT`;
- `BTC_SPECIFIC_EFFECT`;
- `MIXED`;
- `INSUFFICIENT_EVIDENCE`.

# Mission E — Placebo and Negative-Control Laboratory

Attempt to reproduce apparent framework skill using controls that should not possess genuine edge.

Required controls:

1. timestamp shifts within allowed blocks;
2. block-preserving label permutations;
3. fake thresholds matched for frequency;
4. random sensor bundles matched for complexity;
5. alternative reasonable sequence-start definitions;
6. pre-ETF versus ETF-era regime reversal tests;
7. leave-one-event-out analysis;
8. matched-width naive range bands where relevant.

For each test, output:

```text
control_id
target_claim
control_construction
observed_metric
placebo_distribution
real_result_percentile
passes_negative_control
```

A framework claim that is not materially distinguishable from matched placebos must be classified `NO_DEMONSTRATED_EDGE`.

# Required output package

Produce the following artifacts:

1. `CLAUDE_WAVE1_EXECUTIVE_VERDICT.md`
2. `CLAUDE_WAVE1_METHODS.md`
3. `CLAUDE_WAVE1_COUNTERFACTUAL_ROWS.csv`
4. `CLAUDE_WAVE1_PIT_AUDIT_ROWS.csv`
5. `CLAUDE_WAVE1_TDBC_SPEC_CURVE.csv`
6. `CLAUDE_WAVE1_EXTERNAL_VALIDATION.csv`
7. `CLAUDE_WAVE1_PLACEBO_CONTROLS.csv`
8. `CLAUDE_WAVE1_FINDINGS.json`
9. `CLAUDE_WAVE1_MANIFEST.json`
10. `CLAUDE_WAVE1_LIMITATIONS.md`

The manifest must contain:

- file hashes;
- source hashes;
- row counts;
- method versions;
- runtime information;
- exclusions;
- failed tasks;
- exact holdout boundary;
- whether any result was manually edited.

# Verdict taxonomy

Use only:

- `REPLICATED_ROBUST`
- `REPLICATED_WITH_LIMITATIONS`
- `NOT_REPLICATED`
- `SPECIFICATION_FRAGILE`
- `POINT_IN_TIME_CONTAMINATED`
- `NO_DEMONSTRATED_EDGE`
- `INSUFFICIENT_EVIDENCE`
- `IMPLEMENTATION_BLOCKED`

# Final response structure

1. Input integrity and independence declaration.
2. Five mission verdicts.
3. Strongest framework finding.
4. Strongest falsification.
5. Largest implementation or data limitation.
6. Exact disagreements likely to require reconciliation.
7. New research ideas, maximum three, only when directly implied by results.
8. Explicit statement:

```yaml
canonical_state_change: NONE
portfolio_action: NONE
promotion_authority: CHATGPT_GOVERNANCE_ONLY
```

## Final warning

Do not reward complexity.
Do not rescue a failed claim with narrative explanation.
Do not treat a null result as failure of the assignment.
Do not recommend promotion because a chart looks persuasive.
Rows, temporal integrity and benchmark-relative results outrank theory.
