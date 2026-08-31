# T2 Sminston BTC Challenger v0.1 - Preregistration

**Date:** 2026-08-31  
**Status:** SHADOW_TESTING / T2_REPAIR  
**Parent test:** `GATE_BTC_PARTIAL_FT_1`  
**Secondary attribution:** `FNP_CUMULATIVE`  
**Authority:** RESEARCH_ONLY / NO_PORTFOLIO_AUTHORITY  
**Candidate:** `SMINSTON_BTC_CHALLENGER_V0_1`

## 1. Problem statement

The current framework has documented defensive value, but BTC-specific offensive permission remains under-tested. A candidate that appears attractive only because it explains historical Bitcoin cycles is not enough. The candidate must create prospective decision divergence against the existing BTC-only baseline and improve outcome quality after false-permission cost, drawdown, opportunity cost, source dependency and complexity are counted.

This preregistration directly repairs T2. It does not create a new engine or a new test ID.

## 2. Primary question

> Does a source-frozen Sminston BTC-only package improve partial BTC permission versus canonical WAIT, without ecosystem inputs, by recovering meaningful BTC opportunity cost while keeping false-permission and drawdown cost acceptable?

Secondary question:

> Does Sminston upper-tail information add measurable trim value in the cumulative FNP ledger without causing premature BTC trims?

## 3. Hard isolation rule

The challenger may use only BTC-specific or macro-relative Sminston inputs.

Forbidden inputs:

- ETH/BTC
- breadth
- BTC dominance
- altcoin prices
- stablecoin deployment
- altcoin rotation state
- narrative or social signals

This isolation is deliberate. The test asks whether Sminston adds incremental BTC-only information, not whether it can restate the full framework.

## 4. Candidate families

### Family A - Structural valuation

Target inputs:

- q05 power-law quantile
- q10 power-law quantile
- OLS residual
- Decay Channel position / oscillator

Publicly reproducible at registration:

- q05 formula only

Publicly data-blocked at registration:

- q10 exact formula
- exact OLS residual series
- Decay Channel position / oscillator

#### A1 preregistered q05 shadow permission

Define:

`q05_distance = BTC_close / q05_value - 1`

Shadow permission:

- `BTC_PARTIAL_10` if `q05_distance <= +0.05`
- `WAIT` otherwise

The +5% proximity band is an Investering Research Lab operational threshold, not a Sminston threshold. It is frozen before forward outcomes exist.

q05 coefficients must be captured with each eligible source snapshot because Sminston states that the quantile model is refit over time. Today's coefficients may never be applied backward as if they had existed historically.

### Family B - BTC bottom quality

Target inputs:

- CVDD ratio
- MVRV Z-score
- LTH supply in loss

Preregistered component conditions:

1. `MVRV_Z_BOTTOM = TRUE` if author-reported MVRV Z-score `<= 0.10`.
2. `CVDD_PROXIMITY = TRUE` if BTC price / author-reported CVDD `<= 1.10`.
3. `LTH_LOSS_STRESS = TRUE` if point-in-time expanding percentile of LTH supply in loss is `>= 90th percentile`, calculated only with observations available through the row timestamp.

Family B shadow permission:

- `BTC_PARTIAL_10` if at least 2 of 3 conditions are TRUE
- `WAIT` otherwise

The MVRV 0.10 region follows the author's published interpretation. The CVDD 1.10 proximity band and 90th-percentile LTH rule are Research Lab operational thresholds frozen before outcomes.

### Family C - Macro-relative mispricing

Target inputs:

- Copper/Gold versus detrended BTC residual
- ISM PMI versus detrended BTC residual
- MODEM

Status at registration: `DATA_BLOCKED_AUTHOR_DERIVED`.

No proxy may be labelled as Sminston MODEM, Cu/Au residual or PMI residual. Family C gets no vote until exact point-in-time source values and interpretable semantics can be frozen. A future proxy arm, if ever justified, must be explicitly named `PROXY` and separately preregistered before outcomes.

### Full package

`SMINSTON_FULL_PACKAGE` is not eligible for a decision row at registration because Family C and part of Family A are data-blocked. No single public metric may impersonate the full package.

## 5. Benchmark and action semantics

Canonical benchmark:

- `WAIT`: 0% BTC, 100% stable, 0% alts

Experimental action when a family grants permission:

- `BTC_PARTIAL_10`: 10% BTC, 90% stable, 0% alts

This reuses the existing T2 allocation semantics. It does not resurrect retired BTC price gates.

Portfolio divergence return:

`0.10 * BTC_return_from_frozen_entry_reference`

## 6. Valid-row rule

A row is forward evidence only if all are true:

1. canonical framework state and benchmark action are frozen at or before the same information cutoff,
2. candidate inputs are source-frozen at the same cutoff,
3. candidate action is immutable before outcome maturity,
4. candidate and benchmark actions actually diverge,
5. source lineage and formula/version metadata are retained,
6. no outcome data were available when the row was created.

Initialization, QA, replay and same-action observations are not divergence evidence.

## 7. Episode independence

To reduce serial row inflation:

- create a new candidate episode only on a permission-state transition,
- repeated daily TRUE states inside the same episode do not create new divergence rows,
- after an episode ends, a new independent episode requires at least 7 consecutive UTC closes with the candidate permission FALSE before a new TRUE transition can create another episode.

The 7-day reset is a preregistered anti-autocorrelation heuristic, not a market claim.

## 8. Frozen outcome horizons

For T2 comparability:

- 24H
- 72H
- 7D

Extended research horizons:

- 14D
- 30D

Primary decision-value horizon for slow structural valuation: 30D.  
Primary safety horizon: 7D maximum adverse excursion.

No horizon may be changed after row creation.

Required outcome fields include:

- BTC return
- candidate portfolio return
- MFE
- MAE
- max drawdown
- opportunity cost recovered versus WAIT
- false-permission cost
- correct-restraint classification
- source integrity status

## 9. T5 / FNP upper-tail sidecar

Decay Channel and related upper-tail information are relevant to missed-trim risk, not bottom permission. They must not be mixed into T2 entry scoring.

At registration, the upper-tail sidecar is `DATA_BLOCKED` because exact public point-in-time Decay values and a defensible action threshold are unavailable.

Before the first upper-tail outcome row can exist, a prospective amendment must freeze:

- exact source value and semantics,
- action threshold,
- trim fraction,
- no-trim benchmark,
- 7D / 30D / 90D horizons,
- premature-trim loss function.

No retrospective threshold search is permitted.

## 10. Incremental-value tests

A candidate family cannot graduate merely because it has positive returns.

Required analyses after sufficient forward evidence:

- versus WAIT
- versus existing T2 BTC partial logic
- leave-one-family-out ablation
- overlap / dependence analysis
- complexity-adjusted value
- source-revision sensitivity
- stress versus non-stress episode split

Repeated metrics derived from the same BTC price/time structure count as one information family unless unique incremental value is demonstrated.

## 11. Promotion floor

There is no automatic promotion.

A governance review is not allowed before both conditions are met:

- at least 6 independent eligible divergence episodes,
- at least 180 calendar days from first valid divergence row.

A family must additionally show:

- cumulative opportunity-cost recovered > cumulative false-permission cost,
- positive median 30D decision divergence,
- acceptable 7D MAE versus the benchmark,
- positive unique ablation value,
- no source-lineage or look-ahead violation,
- positive value after complexity tax.

## 12. Kill criteria

Immediate kill or quarantine if:

- future information leaks into a source or formula,
- historical refits are treated as point-in-time values,
- proprietary values cannot be captured reproducibly enough for audit,
- a proxy is presented as the author's metric,
- action thresholds are changed after observing outcomes.

Evidence-based kill after the minimum episode floor if:

- cumulative net decision value is <= 0,
- false-permission cost dominates recovered opportunity cost,
- incremental value disappears after duplicated information is removed,
- the family never creates meaningful decision divergence,
- operational complexity exceeds demonstrated benefit.

A null result is a successful research outcome and means REJECT / DO_NOT_INTEGRATE.

## 13. Historical replay policy

Historical raw BRK/on-chain series may be used for feasibility, mechanism study and hypothesis generation.

They may not promote the candidate.

In particular, the current q05 coefficients may not be applied to 2015, 2018, 2020 or 2022 and scored as if those coefficients were known then. Sminston's quantile model is refit over time, so doing that would create look-ahead leakage.

Historical Sminston model rows are eligible only if a genuine archived point-in-time model snapshot, formula, export or author timestamp can be independently bound to the historical date.

## 14. Decision rule

The candidate survives only if the answer to this question becomes YES from prospective rows:

> Does this candidate make the BTC-only framework measurably better after accounting for false permission, missed upside, drawdown, dependence, source integrity and complexity?

Until then:

`SHADOW_TESTING_ONLY`.
