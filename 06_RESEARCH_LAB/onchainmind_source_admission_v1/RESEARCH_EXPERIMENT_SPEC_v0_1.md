# Research Experiment Specification v0.1

**Status:** WORK_PREP / SHADOW_ONLY  
**Date:** 2026-09-01  
**Authority:** zero live weight, threshold, gate, portfolio, execution or canonical market-state authority.

## Objective

Determine whether newly accessible public/on-chain data adds **incremental, reproducible information** to the existing framework. The objective is not to find attractive historical charts and not to maximize backtest fit.

## Experiment A — Compact on-chain incremental value

Candidate axes are deliberately compressed:

1. **Holder valuation:** choose one of MVRV or STH-MVRV as the primary representation.
2. **Realized behavior:** SOPR.
3. **Old-coin spending:** VDD or one equivalent dormancy-family representative.

Do not count multiple members of a family as independent confirmations.

### Baseline ladder

Every candidate must be evaluated over identical timestamps against:

1. simple BTC price/trend baseline;
2. existing framework BTC state available at that timestamp;
3. the candidate's simpler component family where applicable;
4. matched non-trigger / non-extreme periods;
5. timestamp-shift placebo where economically sensible.

### Horizons

Predeclare and report all:

- 7D
- 14D
- 28D

No horizon may be selected after outcomes are observed.

### Evaluation

Work should inspect the current Research Lab / T2 outcome conventions and reuse compatible return, MAE, MFE, drawdown, opportunity-cost and false-permission measures where possible. Do **not** create a new active test solely for this experiment.

Use expanding or walk-forward evaluation. Feature transforms must use only trailing information. If a rolling percentile/z-score is used, its lookback and minimum history must be frozen before outcome review.

Report:

- row count and missingness;
- exact source refs and hashes;
- train/test chronology;
- pooled and regime-partition results;
- baseline result;
- candidate result;
- delta versus baseline;
- sensitivity to plausible, predeclared representations;
- negative results.

### Promotion ceiling

A retrospective improvement may justify continued shadow observation only. Live authority requires separate prospective evidence under current governance.

## Experiment B — URPD topology

First objective is a point-in-time **source observation dataset**, not a predictive test.

Before any feature is frozen, Work must establish:

- exact snapshot date semantics;
- retrieval time;
- BTC price/settlement source;
- price-bin definition and whether bins change over time;
- pctSupply / btcSupply semantics;
- retention depth;
- provider revision behavior;
- data storage rights.

Candidate topology features may include:

- supply near spot share;
- nearest dense cost-basis shelf distance;
- nearest sparse/vacuum distance;
- above-versus-below spot supply asymmetry;
- distribution concentration/entropy.

These are hypotheses, not approved sensors.

Do not create a forward prediction row merely because a source snapshot exists. Source observations and prediction ledgers are separate.

## Experiment C — Prediction-market expectations

Network collection remains blocked until Work resolves an explicit official source-use/storage contract.

If cleared, predeclare an event taxonomy before collecting outcome-linked markets. Potential categories:

- central-bank decisions;
- inflation/growth releases where a market exists;
- major crypto regulatory/policy events;
- clearly defined ETF/legal events.

Do not cherry-pick markets because they later became important.

Primary question:

> Do changes in event probabilities contain calibrated information beyond scheduled-event data, macro data and contemporaneous crypto price?

No probability level is a trading signal by itself.

## Stop rules

Return `KILL` or `HOLD` rather than forcing a result when:

- exact source semantics are unresolved;
- point-in-time safety cannot be established;
- raw/derived storage rights are not sufficient;
- a proxy materially changes the meaning;
- a simpler baseline matches or beats the candidate;
- the result depends on one hindsight-selected regime/horizon;
- missingness or revisions destroy reproducibility;
- complexity/maintenance cost exceeds incremental value.

Prefer a small exact result to a large synthetic one.
