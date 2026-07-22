# BTC Range Headroom and Pullback Predictability Audit

**Dato:** 2026-07-22  
**Status:** SHADOW_ONLY / RETROSPECTIVE_CHALLENGER / NOT_REPRODUCED  
**Område:** Research Lab, range skill, pullback protection, rebuy discipline, metric governance  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `05_CYCLE_NAVIGATOR/forward_range_ledger/`, `04_MARKET_LEARNING/range_skill/`, `06_RESEARCH_LAB/forward_tests/`, `01_CORE_FRAMEWORK/governance/`  
**Depends on:** `08_SOURCE_MATERIAL/claude/2026-07-22__claude-btc-range-pullback-17-experiment-summary__source-note.md`, `05_CYCLE_NAVIGATOR/protocols/2026-07-08__forward-range-ledger-protocol-v0-1__canonical.md`, `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`, `01_CORE_FRAMEWORK/governance/2026-07-22__sensor-relationship-and-incremental-value-standard__canonical.md`

---

## 1. Governance verdict

```yaml
research_value: HIGH_FOR_NEGATIVE_FINDINGS
new_truth_layer_value: LOW_WITHOUT_REPRODUCTION
reproducibility: INSUFFICIENT
canonical_promotion: NO
FRLP_method_change: NO
FRLP_active_test_closed: NO
new_test_created: NO
new_engine_created: NO
current_caution_flag_activated: NO
market_state_change: NO
rebuy_change: NO
portfolio_action: NO
```

Claude's research is relevant because it challenges two expensive framework ambitions:

- improving weekly range precision through increasingly adaptive constructions;
- predicting pullback bottoms or unusual downside through compact technical features.

The negative findings are directionally valuable. The strong generalisations and live caution claim are not sufficiently reproduced for operational use.

## 2. What is accepted as durable shadow learning

### 2.1 Simple width and tilt refinements did not beat the stated baseline

Within Claude's reported experiment family, the following did not improve the baseline robustly:

- previous-week return tilt of the band centre;
- volatility-term-structure width modulation;
- previous-week range anchoring;
- volume-conditioned width;
- adaptive or asymmetric width;
- general directional skew.

This is useful negative evidence because it discourages immediate complexity expansion.

Accepted bounded inference:

```text
Within the tested prior-close-centred ATR family and reported train/test split,
simple width modulation and linear previous-week-return centre tilt did not add value.
```

Not accepted:

```text
No possible adaptive range method can add value.
```

### 2.2 Zero linear drift tilt is the strongest bounded negative result

The reported centre-shift results are symmetric around zero in both train and test, with zero shift best among the tested values.

Accepted bounded inference:

```text
Do not add a linear centre shift based only on previous-week return
without new prospective evidence.
```

This does not prove that every possible centre model is harmful. It rejects one clearly defined and tempting family of adjustments.

### 2.3 Pullback-conditioned bottom-catching failed in the reported construction

The unconditional upside lifts disappeared when the signal was conditioned on BTC already being at least 10 percent below its 60-day high.

Accepted bounded inference:

```text
The tested momentum and extension features did not provide a useful rebuy edge
inside Claude's defined pullback state.
```

This supports the framework's existing preference for confirmation, persistence and loss-aware deployment over retrospective bottom selection.

It does not prove that every rebuy method is impossible.

### 2.4 Distribution can invalidate an attractive hit-rate

The reported volatility-compression example is methodologically important:

```text
Binary lift looked favourable.
Median forward upside was small.
Median forward drawdown was large.
```

This reinforces an existing framework principle: a signal must be judged by the loss and payoff distribution, not by hit-rate or classification lift alone.

Future signal reports should expose, where applicable:

- sample size;
- base rate;
- hit rate or lift;
- median forward return;
- median favourable excursion;
- median adverse excursion or drawdown;
- tail loss;
- opportunity cost;
- implementation cost;
- regime split;
- confidence interval or uncertainty estimate.

This is archived as a shadow reinforcement of existing outcome and incremental-value governance, not as a new standalone canonical rule.

## 3. Claims that require narrowing

### 3.1 The 0.624 oracle is not a universal ceiling

Claude calls the perfect-width oracle a ceiling for range prediction.

That conclusion is too broad unless the oracle definition is fully specified.

The reported oracle appears to know the future weekly width while retaining a fixed centre, shape, horizon and Jaccard objective. It can therefore establish only a bounded result:

```text
WIDTH_ONLY_JACCARD_HEADROOM
within a fixed prior-close-centred symmetric interval family.
```

It does not establish a theoretical ceiling for:

- centre prediction;
- probabilistic quantiles;
- asymmetric risk intervals;
- conditional regime models;
- alternative horizons;
- density forecasts;
- breach-cost or Winkler optimisation;
- separate upside and downside tails;
- decision-specific ranges.

The correct archive language is therefore:

```text
Simple width-only Jaccard improvement appears limited in the tested family.
Weekly range prediction as a whole is not proven saturated.
```

### 3.2 Jaccard and containment optimise different objectives

Claude correctly notes that Jaccard and containment can pull in opposite directions.

A narrow band may improve overlap efficiency while increasing breaches. A wider band may improve containment while reducing Jaccard.

FRLP already avoids a one-metric decision by retaining:

- Winkler scores;
- Jaccard;
- containment;
- breach days;
- direction bias;
- width ratio;
- adjustment alpha against DUMB_1.5 and DUMB_2.0.

Therefore Claude's Jaccard result cannot independently justify freezing the official width at ATR14 x 1.50.

### 3.3 Downside was not shown to be universally unpredictable

Claude tested a defined target, feature family, source history and train/test split.

The accepted statement is:

```text
The tested daily technical and flow features did not robustly predict
Claude's volatility-normalised 10-day abnormal downside target.
```

The rejected overgeneralisation is:

```text
Downside cannot be predicted by any method.
```

Unexamined information may include:

- options-implied distributions;
- cross-venue leverage and liquidation structure;
- macro event risk;
- credit and dollar shocks;
- market depth;
- on-chain supply changes;
- ETF transmission;
- state duration and interaction terms;
- richer event-level data.

The research supports humility and reactive protection, not an impossibility theorem.

### 3.4 The 300-parameter maximum is not a formal noise floor

Without the parameter space, selection procedure, dependence among variants and null construction, the stated `0.006` should not be called a universal noise floor.

It is retained as:

```text
CLAUDE_REPORTED_RANDOM_SEARCH_MAXIMUM
```

not as a canonical significance threshold.

## 4. Current low-volatility pullback configuration

Claude reports a current configuration with:

- 180-day volatility percentile near 19 percent;
- ATR7 / ATR14 near 0.929;
- approximately 14.76 percent below the 60-day high;
- a test-period analogue sample of 28 observations;
- median 10-day upside of +1.15 percent;
- median forward drawdown of -13.62 percent.

This is not activated as a caution signal because:

1. the current observations lack source receipts;
2. the pattern was selected within a 17-experiment research sequence;
3. the test sample is only 28;
4. the exact event definition and overlap handling are incomplete;
5. confidence intervals and era sensitivity are absent;
6. no independent reproduction exists;
7. the research itself says classification and rebuy should remain unchanged.

Archive classification:

```text
CURRENT_CAUTION_CONFIGURATION: HYPOTHESIS_CONTEXT_ONLY
LIVE_ALERT: NO
NEW_FORECAST_ROW: NO
RETROSPECTIVE_SCORE: NO
```

## 5. Relationship to active owners

### T1 - FRLP v0.1 Range Forward Ledger

Claude's research is a retrospective challenger input to T1.

It does not replace the forward question:

```text
Does the official CN range or human adjustment beat DUMB_1.5 and DUMB_2.0
on frozen, forward, independently verified rows?
```

Required handling:

```text
T1_STATUS: REMAINS_ACTIVE
ATR_1_50_PROMOTION: NO
HUMAN_ADJUSTMENT_SUSPENSION: NOT_TRIGGERED_BY_THIS_SUMMARY
VALID_FORWARD_ROW_CREATED: NO
```

At the next planned FRLP methodology review, the research may motivate explicit checks of:

- prior-close centred symmetric baseline;
- zero previous-week-return tilt challenger;
- width-only improvement versus DUMB_1.5 and DUMB_2.0;
- Jaccard versus containment trade-off;
- Winkler and breach-cost outcome;
- adjustment alpha after complexity cost.

No historical result may be inserted as a prospective FRLP row.

### T2 - BTC Partial versus WAIT

The research supports measuring confirmation-based permission against full WAIT with:

- maximum adverse excursion;
- maximum favourable excursion;
- missed upside;
- false-permission cost;
- opportunity cost.

It does not create a BTC partial permission rule.

### T4 - Pullback Edge Event Outcomes

Claude's negative predictability result suggests that the pullback edge should be evaluated on actual risk-management value, including damage avoided and execution value, rather than requiring perfect advance prediction.

This interpretation is already compatible with T4's question:

```text
Did the edge detector provide market-stress value and/or tactical trim execution value?
```

No T4 outcome is changed by this research.

### T5 - Cumulative FNP Ledger

The failed bottom-catching construction reinforces the need to measure the cost of waiting and confirmation rather than infer that any missed rebound proves the lock was wrong.

No valid FNP row is created because the research lacks a frozen live divergence decision and a matured counterfactual.

### Sensor Relationship and Incremental Value Standard

The research aligns with the existing canonical requirements for:

- simple baselines;
- out-of-sample incremental value;
- regime stability;
- complexity cost;
- rejection when value disappears under conditioning;
- preservation of robust negative findings.

No second canonical methodology file is needed.

## 6. Proposed range-method freeze is rejected for now

Claude recommends:

```text
Symmetric ATR14 x 1.50 around previous weekly close.
No tilt, no adaptivity and no skew.
```

Governance decision:

```text
METHOD_FREEZE: REJECT_PENDING_FORWARD_EVIDENCE
BASELINE_RELEVANCE: ACCEPT
SIMPLIFICATION_DIRECTION: ACCEPT
```

Reasons:

- FRLP already uses DUMB_1.5 and DUMB_2.0 as frozen baselines;
- official ranges are subject to forward Winkler, Jaccard, containment and kill monitoring;
- the Claude result is not independently reproducible;
- its objective is dominated by Jaccard, while FRLP uses multiple loss measures;
- replacing a live prospective test with a retrospective conclusion would weaken governance.

The correct action is to keep the simple ATR baselines prominent and require the official or human-adjusted range to prove incremental value prospectively.

## 7. Reproduction package required for stronger use

A future Claude or local rerun must provide:

```text
1. exact source endpoints, instruments and venue convention;
2. immutable raw daily rows and source hashes;
3. timezone, candle settlement and week definition;
4. complete feature dictionary and formulas;
5. exact target labels and overlap rules;
6. all 17 experiments, not selected summaries;
7. full parameter search space;
8. train/test split frozen before evaluation;
9. walk-forward or expanding validation where appropriate;
10. bootstrap confidence intervals;
11. multiple-testing correction or honest false-discovery treatment;
12. regime and era breakdowns;
13. transaction and delay costs where decision-relevant;
14. median return, MFE, MAE, drawdown and tail-loss distributions;
15. executable code, environment and deterministic checksums;
16. independent rerun with exact-state agreement on core findings.
```

Only then may the research be considered for:

- a valid historical-test table;
- a bounded FRLP methodology review;
- an operational reporting-field update;
- a prospective challenger specification.

## 8. Final conclusion

The strongest learning is negative and useful:

```text
Simple range refinements and tested pullback-conditioned rebuy features
failed to show durable incremental value in Claude's reported setup.
```

The second strongest learning is methodological:

```text
A favourable hit-rate can coexist with an unacceptable payoff and drawdown distribution.
```

The research does not prove that weekly ranges are globally solved, that downside is universally unpredictable, or that ATR14 x 1.50 should replace the active forward process.

The framework should therefore:

- preserve simple ATR baselines;
- resist unproven adaptive range complexity;
- keep FRLP active;
- evaluate pullback tools on realised protection and counterfactual cost;
- evaluate rebuy through confirmation and forward divergence rows;
- require distributional outcome reporting;
- request an executable reproduction package before promotion.

## 9. Authority boundary

```text
CANONICAL_RANGE_CHANGE: NO
ACTIVE_TEST_CHANGE: NO
NEW_ENGINE: NO
NEW_TEST: NO
CURRENT_ALERT: NO
MARKET_STATE_CHANGE: NO
GATE_CHANGE: NO
REBUY_CHANGE: NO
DEPLOYMENT_CHANGE: NO
PORTFOLIO_ACTION: NO
```
