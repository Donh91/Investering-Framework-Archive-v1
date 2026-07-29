# STRUCTURAL MARKET BANDS - FUNCTIONAL REPLICATION v0.1

**Status:** RESEARCH_ONLY  
**Effective:** 2026-07-29  
**Framework impact:** None until evidence review  
**Promotion:** Not automatic

## Research question

Can a reproducible, causal proxy for Structural Market Bands improve structural valuation, downside-depth estimation or range placement beyond simpler on-chain and price-based baselines already available to the framework?

The purpose is not to guess or claim reconstruction of a proprietary formula. The purpose is to reproduce the public functional idea and test whether it adds measurable decision value.

## Public functional claim under test

The indicator appears to use UTXO/on-chain information, coin lifespan or age structure, and short-, medium- and long-horizon market-cap dynamics to estimate dynamic structural support and resistance zones.

Unknown and therefore not assumed:

- exact formula
- exact weights
- exact windows
- exact reliability definition
- entity adjustment
- smoothing method
- band construction

## Research principles

- No Core changes
- No Master Monday or RAW changes during research
- Point-in-time and causal calculations only
- Full provenance for every input
- Simple baselines before complex models
- Walk-forward testing before interpretation
- Kill criteria applied before promotion discussion
- Explanatory beauty does not count as edge

## Candidate proxy families

### SMB-A - Cohort Cost-Basis Envelope

Candidate inputs:

- realized price
- short-term holder realized price
- long-term holder realized price
- cohort realized prices
- UTXO realized-price distribution or equivalent
- supply in profit/loss

Hypothesis:

Structural bands may largely represent a reliability-weighted cost-basis envelope across coin-age cohorts.

### SMB-B - Lifespan Pressure Envelope

Candidate inputs:

- dormancy
- coin days destroyed
- spent output age bands
- revived supply
- UTXO age distribution
- cohort survival or hazard-style estimates

Hypothesis:

Structural bands may reflect zones where increasing capital pressure is required to mobilize mature supply.

### SMB-C - Multi-Horizon Capital Structure

Candidate inputs:

- realized-cap momentum
- 30D, 90D and 365D market-cap change
- cohort cost basis
- supply in profit/loss
- age-weighted realized value

Hypothesis:

Structural bands may be a multi-horizon capital-structure envelope combining price location and on-chain capital persistence.

### SMB-D - Minimal Public Baseline

Candidate inputs:

- realized price
- rolling quantiles
- realized volatility
- long-horizon moving or logarithmic bands

Purpose:

Establish whether expensive on-chain complexity adds value over a cheap and reproducible model.

## Required outputs

Each proxy must produce, at minimum:

```text
STRUCTURAL_BAND_STATE:
Below Support / Inside Support / Neutral Corridor / Inside Resistance / Above Resistance

SUPPORT_BAND_LOW
SUPPORT_BAND_HIGH
RESISTANCE_BAND_LOW
RESISTANCE_BAND_HIGH
BAND_PENETRATION: 0-100%
COUNTER_PRESSURE: Weak / Building / Strong
DATA_QUALITY
MODEL_VERSION
```

## Evaluation targets

### Structural floor value

- forward 7D, 14D, 30D and 90D return after support entry
- maximum adverse excursion
- time spent below support
- reclaim probability and time to reclaim
- false-floor rate

### Structural resistance value

- forward return after resistance entry
- maximum favorable excursion before reversal
- breakout survival
- false-resistance rate

### Range placement value

- improvement in 5-7D low placement
- improvement in 5-7D high placement
- containment without excessive width
- breach depth
- calibration against naive volatility bands

### Framework value

Did the proxy improve any of the following beyond existing inputs?

- Pullback Wave Size
- Bottom Cluster Validation
- Vacuum / Mixed / Absorption classification
- downside-depth translation
- structural accumulation context
- capital-protection context

## Baselines

All proxy candidates must compete against:

- realized price
- STH/LTH cost basis
- MVRV-style bands
- CVDD or Delta Cap, when reproducible
- URPD-style zones, when available
- rolling price quantiles
- volatility bands
- horizontal support/resistance
- existing framework range model

## Historical windows

Preferred evaluation windows:

- 2013-2015
- 2017-2019
- 2020-2022
- 2023-2026

The study must report performance by regime, not only pooled results.

## Walk-forward protocol

1. Freeze formulas and parameter grids before holdout evaluation.
2. Use expanding or rolling training windows.
3. Evaluate unseen periods separately.
4. Report sensitivity to reasonable parameter changes.
5. Reject results dependent on one cycle or one narrow parameter choice.
6. Record unavailable or revised data explicitly.

## Data-quality stress tests

The research must test sensitivity to:

- lost coins
- dormant supply
- exchange and custodian consolidation
- change outputs and self-churn
- entity-adjusted versus raw UTXO data
- missing history
- revised provider data
- chain-specific incompatibility

## Forward shadow test

If a proxy survives historical testing, it must complete at least 30 daily rows, preferably 90, before promotion review.

Each row must freeze:

- model state
- bands
- penetration
- expected price path
- expected 3D, 7D and 14D implication
- baseline comparison
- later outcome
- whether it changed the operational translation

## Kill criteria

The research is rejected or frozen if any of the following applies:

1. Inputs cannot be sourced reproducibly.
2. Point-in-time reconstruction is not auditable.
3. Results are concentrated in one cycle.
4. Small parameter changes reverse the conclusion.
5. The proxy does not beat simple baselines after costs of complexity.
6. The proxy only duplicates existing framework sensors.
7. Explanatory fit improves while price/action output worsens.
8. The model requires proprietary data unavailable for ongoing operation.

## Possible verdicts

- REJECT
- EXPLANATORY_ONLY
- SHADOW_CONTEXT
- RANGE_OVERLAY_CANDIDATE
- PROMOTION_REVIEW_REQUIRED

No result may move directly from research to Core.

## Final decision standard

The central test is not whether the proxy draws convincing historical bands.

The central test is whether it improves a frozen, scorerable price or action output relative to simpler baselines and the existing framework.