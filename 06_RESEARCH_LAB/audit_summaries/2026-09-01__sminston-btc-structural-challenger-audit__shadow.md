# Sminston BTC Structural Challenger Audit

**Date:** 2026-09-01  
**Status:** `SHADOW_ONLY / EXTERNAL_INDICATOR_AUDIT / MODIFY_EXISTING_TEST_RECOMMENDED / NO_MARKET_AUTHORITY`  
**Parent test:** `GATE_BTC_PARTIAL_FT_1`  
**Source:** `https://www.sminstonwith.com/chart` and publicly documented Sminston With formulas/pages  
**Authority:** zero portfolio, market-state, threshold, weight, rebuy, rotation or deployment authority

## 1. Executive verdict

Sminston With is relevant to the framework, but not as a new engine, independent vote or altcoin/rotation signal.

The only family with a sufficiently clear problem-to-solution fit is the public, reproducible Bitcoin price-versus-time structural valuation family. It is a plausible challenger to the framework's known BTC offensive false-negative problem: delayed BTC re-entry or permission after major stress while ecosystem confirmation remains weak.

The correct governance disposition is:

```text
GOVERNANCE_VERDICT: MODIFY_EXISTING_TEST
PARENT_TEST: GATE_BTC_PARTIAL_FT_1
NEW_TEST: NO
NEW_ENGINE: NO
LIVE_WEIGHT_CHANGE: NONE
CANONICAL_MARKET_RULE_CHANGE: NONE
MARKET_STATE_CHANGE: NONE
PORTFOLIO_ACTION: NONE
VALID_FORWARD_ROW_CREATED: NO
ROW_CREATION_STATUS: BLOCKED_LEDGER_CONTRACT_INCOMPLETE
```

The source passed the relevance gate. It did not pass the decision-authority gate.

## 2. Frozen research proposition

Test this proposition prospectively, without changing live framework logic:

> Does a preregistered, reproducible BTC price/time structural valuation residual add incremental value to the existing BTC-partial versus WAIT question by reducing genuine BTC false negatives or false permissions after controlling for simple trend and the framework's existing BTC state?

The objective is not to prove Sminston's worldview or forecast BTC fair value.

The objective is to test whether one narrow, reproducible information family changes BTC-specific decisions often enough, and correctly enough, to justify its complexity.

## 3. Source audit

The public chart suite contains multiple families: power law, statistical/quantitative, macro, on-chain and technical. Several of the most interesting proprietary constructions, including Decay Channel, Regression Ensemble, Power Law Quantiles, Cu/Au residual, PMI residual and MODEM, expose interpretation but not enough public implementation detail to claim exact framework reproduction.

Therefore no reconstructed output may be called the original Sminston model unless exact executable lineage is later recovered.

Required label for any reconstruction:

```text
RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_SMINSTON
```

The public formulas currently suitable for deterministic reconstruction include:

```text
Public 5% quantile example:
price_q05 = 2.952e-18 * days_since_2009_01_03 ^ 5.8837

Public OLS example:
log10(price_ols) = -16.378 + 5.650 * log10(days_since_2009_01_03)
```

These formulas are treated as source-backed public specifications, not as validated trading rules.

## 4. Family-by-family disposition

### A. BTC structural valuation - KEEP AS T2 SHADOW CHALLENGER

Candidate features:

```text
Q05_DISTANCE = ln(BTC_PRICE / Q05_MODEL_PRICE)
OLS_RESIDUAL = ln(BTC_PRICE / OLS_MODEL_PRICE)
```

Primary candidate should be `Q05_DISTANCE`, because the proposed use case is stress / structural cheapness context rather than mean-value prediction.

Q05 and OLS must not receive separate confirmation votes. They are correlated transformations of the same price/time family.

Disposition:

```text
SHADOW_CANDIDATE_REPAIR
PARENT: GATE_BTC_PARTIAL_FT_1
LIVE_WEIGHT: ZERO
```

### B. Cu/Au residual, PMI residual and MODEM - AUDIT / SOURCE CONTEXT ONLY

These are conceptually relevant but overlap current macro architecture. The framework already owns a point-in-time-safe Copper/Gold research lane and has already found that a simple Copper/Gold deterioration-to-terminal-distribution rule is not stable enough for authority.

Exact premium Sminston macro formulas, vintage handling and historical input lineage are not sufficiently recoverable from the public site for canonical ingestion.

Disposition:

```text
SOURCE_CONTEXT_ONLY
INDEPENDENT_VOTE: NO
MACRO_WEIGHT_CHANGE: NO
```

### C. CVDD, MVRV and LTH loss - RETAIN AS REDUNDANT VALIDATION

These can improve human interpretation of bottom quality, but they overlap existing on-chain/stress/bottom-quality information and do not currently justify another independent vote.

Disposition:

```text
REDUNDANT_VALIDATION
LIVE_WEIGHT: ZERO
```

### D. Upper-tail Decay Channel - HIGH RESEARCH INTEREST, WRONG OWNER FOR T2

The asymmetry between lower structural support and decaying upper extremes is aligned with existing upper-tail fragility and expansion-decay learning.

However, the objective is top/exit risk, not BTC partial re-entry. It must not be smuggled into T2. Exact premium implementation is also not publicly reproducible.

Disposition:

```text
SOURCE_CONTEXT_ONLY
FUTURE_OWNER: EXISTING_EXIT_OR_TOP_RESEARCH_ONLY_IF_SPEC_RECOVERED
NEW_TEST: NO
```

### E. Standard technical charts - REJECT NEW WEIGHT

RSI, MACD, moving averages, Pi Cycle, Fibonacci, Golden/Death Cross, Bull Market Support Band and similar standard charts add insufficient unique information relative to the current stack.

Disposition:

```text
REJECT_NEW_WEIGHT
```

## 5. Quantitative sanity check - not a backtest

Using the public formulas and the 2026-08-31 date:

```text
days_since_genesis: approximately 6449
public_q05_model: approximately USD 76.6k
public_ols_model: approximately USD 139.8k
BTC_close/reference: approximately USD 79k
BTC_vs_q05: approximately +3%
BTC_vs_ols: approximately -44%
```

Interpretation:

BTC is currently close to the public 5% structural quantile, while far below the public OLS centreline.

This is potentially useful as a structural-stress / structural-cheapness observation.

It is not a bottom confirmation and not a buy signal.

Illustrative stress-date sanity checks show why no hard floor is authorized:

```text
2018-12 stress: BTC remained materially above the reconstructed q05
2020-03 stress: BTC traded only modestly above the reconstructed q05
2022-11 stress: BTC traded materially below the reconstructed q05
2026-08/09 current: BTC is close to the reconstructed q05
```

The relationship is therefore zone-like, not an exact floor. A rule such as `BUY_IF_PRICE_WITHIN_X_PERCENT_OF_Q05` is explicitly NOT authorized and must not be invented retrospectively.

## 6. Why T2 is the correct owner

Current framework evidence already identifies a narrower weakness on BTC than on alts: the framework is not a bottom-sniffing model and can pay confirmation cost during rapid BTC recoveries. The active BTC Partial versus WAIT test already asks whether partial BTC permission improves opportunity-cost-adjusted outcome without unacceptable drawdown.

The Sminston structural family therefore does not justify a new test ID. It is a candidate challenger inside the existing unresolved BTC-partial question.

This preserves the framework rule that new external ideas must prove marginal decision value rather than increase signal count.

## 7. Preregistered challenger design

Candidate identity:

```text
candidate_id: SMINSTON_BTC_STRUCTURAL_CHALLENGER_V0_1
representation: RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_SMINSTON
parent_test: GATE_BTC_PARTIAL_FT_1
authority: ZERO
```

### Inputs to freeze before outcome use

- BTC close source and exact daily settlement convention
- genesis/time origin
- exact public q05 formula version
- exact public OLS formula version if retained
- calculation precision
- missing-data behavior
- formula/source retrieval timestamp and hash where feasible
- plausible specification-equivalence set before outcomes are inspected

### Specification-dispersion requirement

The candidate must survive plausible specification perturbations. If reasonable time-origin, quantile or fit definitions materially reverse the decision implication, the family receives zero live weight.

Do not choose the specification that best explains known bottoms.

### Baselines

The challenger must be compared against:

1. full WAIT
2. existing BTC_PARTIAL action/state
3. simple BTC price/trend baseline
4. existing framework BTC state without Sminston-derived structural features

### Outcome fields

Reuse the T2 outcome vocabulary:

- return
- maximum adverse excursion
- maximum favorable excursion
- drawdown
- opportunity cost
- false-permission cost
- actual decision divergence

No custom success metric should be invented merely to make the challenger win.

## 8. Promotion conditions

Promotion cannot occur from historical visual fit.

Minimum evidence logic:

```text
- repeated valid decision-divergence rows
- superior opportunity-cost-adjusted outcome versus T2 baselines
- no unacceptable increase in false-permission drawdown
- incremental value remains after existing BTC state and simple trend
- result survives plausible specification set
- result is not concentrated in one hindsight-selected bottom
- result remains useful across relevant regimes
- complexity and source fragility remain low enough to justify retention
```

Any future authority change must use the existing stronger governance path. This audit itself authorizes none.

## 9. Kill criteria at birth

Kill or archive the challenger if any of the following occurs:

```text
K1: no meaningful T2 decision divergence
K2: no incremental value after existing BTC state and simple trend
K3: simple baseline equals or beats the challenger after costs
K4: result disappears or reverses under plausible specification variants
K5: improvement exists only around retrospectively selected bottoms
K6: false-permission drawdown materially increases
K7: source/formula lineage becomes ambiguous or changes silently
K8: reconstructed implementation drifts too far from the public source claim
K9: added maintenance/governance cost exceeds measured benefit
```

A null or negative result is a successful research outcome. It must be preserved rather than replaced by repeated parameter retuning.

## 10. Evidence and ledger boundary

The canonical Active Test Registry has T2 active and needing rows, but the canonical owner folder examined for this audit did not expose a dedicated complete T2 ledger/schema/validator contract sufficient for safe row creation under the Prospective Evidence Ledger rules.

Therefore:

```text
LEDGER_CONTRACT_STATUS: INCOMPLETE_FOR_THIS_CHALLENGER
VALID_FORWARD_ROW_CREATED: NO
PSEUDO_ROW_CREATED: NO
OUTCOME_SCORE_CREATED: NO
```

Do not invent a ledger path, schema, scorer, duplicate key or maturity rule merely to claim activation.

The correct next engineering step, if T2's owner contract is later resolved, is to add this challenger as a bounded T2 feature/counterfactual, not as a new test or engine.

## 11. Current operational interpretation

The reconstructed public q05 proximity is interesting because it says BTC is near a very low percentile of Sminston's long-run price/age distribution.

The correct wording is:

```text
STRUCTURAL_STRESS_OR_CHEAPNESS_CONTEXT: ELEVATED
BOTTOM_CONFIRMED: NO
BUY_SIGNAL: NO
BTC_PARTIAL_PERMISSION_CHANGE: NO
```

Current framework action remains governed by existing owners.

## 12. Final disposition

```text
SMINSTON_SOURCE_RELEVANCE: HIGH
WHOLE_SUITE_INTEGRATION: REJECT
BTC_STRUCTURAL_VALUATION_CHALLENGER: ACCEPT_TO_SHADOW_T2_REPAIR
MACRO_RESIDUAL_FAMILY: AUDIT_ONLY_ZERO_WEIGHT
ONCHAIN_BOTTOM_FAMILY: REDUNDANT_VALIDATION_ZERO_WEIGHT
UPPER_TAIL_DECAY: RESEARCH_CONTEXT_WRONG_T2_OBJECTIVE
STANDARD_TECHNICALS: REJECT_NEW_WEIGHT
NEW_TEST: NO
NEW_ENGINE: NO
LIVE_WEIGHT: ZERO
PORTFOLIO_AUTHORITY: ZERO
```

The durable conclusion is narrow:

> Sminston is worth keeping as an external BTC research challenger. The public structural valuation family is worth testing inside the existing BTC Partial versus WAIT question because it targets a documented BTC false-negative weakness. Nothing in this audit proves a new signal, bottom call, threshold, market state or portfolio action.
