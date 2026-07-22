# Public Repo Methods Closed-Lab Audit

**Dato:** 2026-07-22  
**Status:** SHADOW_ONLY  
**Område:** Research Lab, sensor relations, sequence survival, simplification  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `01_CORE_FRAMEWORK/governance/`, `06_RESEARCH_LAB/forward_tests/`  
**Authority:** No market-state, gate, portfolio, release or production authority

## Purpose

This audit tested mathematical ideas extracted from public repositories as isolated challenger methods against a bounded historical BTC/ETH dataset.

The purpose was not to install public plugins or create new engines.

The purpose was to determine which methods can improve understanding of the existing machinery, especially:

- sensor redundancy;
- nonlinear dependence;
- unique versus synergistic information;
- regime and relationship drift;
- sequence duration and failure hazard;
- change points;
- historical analogs;
- tail dependence;
- framework compression.

## Closed-room controls

- No write to active DATA PING runtime.
- No change to canonical market state.
- No change to gates, rebuy, deployment or portfolio action.
- No external plugin was installed into the framework.
- No public repo code was made authoritative.
- All tests were local exploratory implementations.
- Results are historical diagnostics, not forward-test proof.
- New-engine freeze remains fully respected.

## Data scope and limitations

Historical overlap:

- BTC and ETH daily OHLCV
- 2016-03-10 through 2024-03-24
- 2,886 aligned daily rows
- 20 transparent derived sensor proxies
- 124 relative-strength sequence episodes

Critical limitation:

The available BTC source ended in March 2024, so the primary relationship tests do not cover the full ETF-era from 2024-2026.

Therefore:

- no tested coefficient is promoted;
- no numeric threshold becomes canonical;
- no historical result is treated as current ETF-era proof.

## Methods tested

Ideas were extracted from:

- IDTxl, information dynamics, transfer entropy and PID concepts;
- Tigramite, lagged and regime-dependent causal inference;
- lifelines, survival and hazard analysis;
- ruptures, offline change-point detection;
- River, online concept-drift detection;
- BOCD, Bayesian online change-point concepts;
- statsmodels, dynamic factors and state-space methods;
- dcor, nonlinear distance dependence;
- STUMPY, sequence motifs and historical analogs;
- PyCWT, horizon-specific coherence;
- pyvinecopulib, tail-dependence concepts;
- tick, Hawkes event cascades.

## Test findings

### 1. Sensor compression produced strong learning

Across 20 derived sensor proxies:

- 6 principal components explained 82.96% of variance.
- 8 principal components explained 90.47% of variance.

The dominant latent groups resembled:

1. ETH/relative momentum and transmission;
2. BTC momentum and drawdown;
3. volatility and correlation structure;
4. range/volume stress.

Interpretation:

A material part of apparent multi-sensor confirmation can be repeated observation of the same underlying factor.

This supports simplification audits.

It does not prove that 20 real framework sensors can be reduced to six, because the test used derived proxies rather than the full canonical sensor ledger.

### 2. Linear correlation materially missed nonlinear dependence

Example:

- ETH/BTC 20-day momentum versus ETH/BTC 14-day volatility
- Spearman correlation: approximately 0.10
- Distance correlation: approximately 0.41
- estimate stable across eight subsamples, standard deviation approximately 0.02

The relationship was U-shaped:

- strongly negative momentum was associated with high volatility;
- near-zero momentum was associated with lower volatility;
- strongly positive momentum was also associated with high volatility.

Interpretation:

Low linear correlation does not establish independence or unique sensor value.

This is the strongest methodological finding in the audit.

### 3. Sequence duration was more informative than the initial signal alone

Using a transparent ETH/BTC relative-strength proxy:

- 124 completed episodes were observed;
- 72.6% lasted at least 2 days;
- 61.3% lasted at least 3 days;
- 47.6% lasted at least 5 days;
- 37.9% lasted at least 7 days;
- 8.1% lasted at least 14 days.

Interpretation:

The state label alone was insufficient.

Elapsed duration and survival are first-class information.

Caveat:

The exact percentages are definition-dependent and must not become framework thresholds.

### 4. Conditional combinations were more useful than isolated confirmations

At sequence start, a pair combining:

- BTC 20-day momentum;
- ETH relative participation proxy;

achieved temporal cross-validation AUC around 0.72 for seven-day sequence survival.

The isolated inputs achieved approximately 0.67 and 0.66.

However, performance weakened in the 2022-2024 subperiod.

Interpretation:

Some sensor pairs provide synergistic value, but the relationship is regime-dependent.

This supports interaction testing.

It does not support a new signal.

### 5. Change-point methods identified real structural transitions, but were feature-sensitive

A multivariate segmentation test repeatedly found breaks near major market transitions, including:

- March 2020;
- April/July/November 2021;
- late 2022 / early 2023.

However, the exact dates changed materially when the feature family changed.

Interpretation:

Change-point detection is useful as a diagnostic challenger.

A single global breakpoint must not become canonical state authority.

The safer construction is consensus across independent sensor families.

### 6. Online drift alarms were useful but tuning-sensitive

Page-Hinkley-style alarms recurred near several major shifts across multiple thresholds.

The number of alarms and exact timing varied with tuning.

Interpretation:

Online drift belongs in source QA, relationship monitoring or shadow diagnostics.

It must not directly change regime, gates or portfolio action.

### 7. Transfer entropy and causal direction remained weak and unstable

Exploratory discrete transfer-entropy estimates were small.

Some relations appeared statistically unusual in one era and disappeared or reversed in another.

Interpretation:

Lead-lag and causal methods may become valuable with richer canonical data and stronger controls.

They are not ready for permanent operational use.

### 8. Tail dependence confirmed downside asymmetry

Empirical BTC/ETH joint dependence was materially stronger in the downside tail than the upside tail:

- approximate 5% downside dependence: 0.59;
- approximate 95% upside dependence: 0.35.

Interpretation:

Ordinary correlation can understate asymmetric joint stress.

This confirms existing Stress/Flush logic.

It does not justify a new tail-risk engine.

### 9. Historical analog matching failed the baseline test

A multivariate sequence-analogue test inspired by matrix profiles produced:

- analogue MAE: approximately 0.064;
- expanding historical-mean MAE: approximately 0.044;
- analogue sign accuracy: 44.6%;
- baseline sign accuracy: 48.2%.

Interpretation:

Pattern similarity did not create forecasting edge in this test.

Historical analog matching is rejected as a decision layer.

It may remain a descriptive research tool only.

### 10. Frequency analysis added little in this sample

BTC/ETH dependence remained broadly similar across tested daily, weekly and monthly horizons.

Interpretation:

Wavelet or frequency-domain methods may be useful for macro-lag research, but this test did not purchase permanent framework complexity.

### 11. Hawkes/event-cascade methods were data-blocked

Daily rows cannot validly estimate event excitation among liquidations, alerts, order-book events or intraday flows.

Interpretation:

No result was fabricated.

Hawkes research remains ineligible until timestamped event ledgers exist.

## Ranked learning value

1. Nonlinear dependence plus incremental-value audit
2. Sequence survival and hazard framing
3. Factor compression and redundancy mapping
4. Family-consensus change-point diagnostics
5. Tail-dependence confirmation
6. Regime-dependent causal research
7. Online drift diagnostics
8. Frequency-domain analysis
9. Historical analog matching
10. Hawkes, data-blocked

## Final verdict

No public repo should be installed as a new framework engine.

The permanent value is a methodology standard:

Before any sensor receives independent confirmation weight, it must be tested for:

1. linear dependence;
2. nonlinear dependence;
3. incremental out-of-sample value;
4. synergy and interaction value;
5. regime stability;
6. change-point sensitivity;
7. sequence-survival relevance;
8. complexity cost.

The only permanent implementation from this audit is a governance and simplification rule.

All numerical outputs remain historical shadow evidence.
