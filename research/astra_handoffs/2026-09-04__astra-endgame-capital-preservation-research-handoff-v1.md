# ASTRA Handoff — Endgame Capital Preservation Research v1

**Prepared:** 2026-09-04  
**Priority:** CRITICAL / ENDGAME  
**Authority:** RESEARCH_ONLY / NO_AUTOMATIC_PROMOTION / NO_PORTFOLIO_EXECUTION  
**Mission owner:** existing Cycle Compass Exit / Distribution Research Program  
**Extension:** Endgame Capital Preservation Priority v1

## Mission for Astra

The central problem is not to predict an exact crypto-cycle top. It is to improve the framework's ability to preserve terminal cycle wealth by distinguishing:

1. healthy late-cycle/parabolic continuation;
2. temporary pullback/deleveraging;
3. failed rotation or temporary breadth deterioration;
4. genuine distribution;
5. a sufficiently confirmed exit regime.

The two costly errors must be optimized jointly:

- **premature exit** — missing the final parabolic/altseason upside;
- **late exit** — surrendering a large share of accumulated gains during distribution/regime break.

Astra must explicitly model the trade-off between these errors rather than optimize warning hit-rate alone.

## First instruction: inspect before building

Before proposing new sensors, Astra should map all existing framework owners, shadow lanes, exit-warning calibration, Action Compass phases/warnings, T5/FNP, T6/rotation survival, Hourly, CFGI, breadth, ETH/BTC persistence, BTC.D, derivatives, pullback forensics, stablecoin/liquidity, ETF flows and relevant holder/cycle context.

Do not duplicate an existing owner. Do not silently convert a research proxy into canonical authority.

The native E0-E7 Exit Ladder is currently `OWNER_BLOCKED`; Astra should treat this as an architectural constraint and either design a valid prospective owner/lifecycle proposal or recommend keeping it blocked.

## Research questions Astra must answer

### A. Premature exit
- After each candidate late-cycle warning, how much BTC/ETH/alt upside remained over frozen 24h, 72h, 7d, 14d and 30d horizons?
- How often did warning evidence re-accelerate or invalidate?
- Which evidence family best distinguished a normal pullback from actual distribution?
- Did requiring persistence reduce false exits enough to justify the delay?

### B. Late exit
- How much drawdown followed each warning and each one-stage-later confirmation?
- What was the cost of waiting for stronger confirmation?
- At what stage did additional confirmation stop improving false-positive protection and start creating unacceptable drawdown delay?

### C. Stage calibration
Evaluate a reversible research ladder such as:

`R0_NO_ENDGAME_EVIDENCE -> R1_ENDGAME_WATCH -> R2_ENDGAME_CAUTION -> R3_DISTRIBUTION_CANDIDATE -> R4_EXIT_CONFIRMATION_PENDING -> R5_EXIT_REGIME_CONFIRMED`

with `RESET_INVALIDATED` available from warning/candidate stages.

This is research vocabulary only. Astra must not assign execution authority.

### D. Incremental information
For every candidate family, determine whether it adds information beyond price/trend and existing sensors:
- breadth level, decay and persistence;
- relative breadth versus BTC and ETH;
- ETH/BTC direction/persistence;
- BTC dominance and rotation/deployment context;
- funding, OI, long/short, taker flow and liquidations;
- options/volatility/skew where historical quality supports it;
- CFGI trajectory, acceleration and divergence;
- stablecoin supply/deployment;
- ETF absorption;
- holder/on-chain distribution context;
- macro/cross-asset context;
- cycle/technical context such as TechDev/CryptoCon only as challengers/context unless independently reproducible.

A sensor that merely restates price extension or euphoria should not count as independent confirmation.

## Historical research design Astra should challenge and improve

Astra is explicitly invited to propose historical backtests that were previously impractical, but must respect small-cycle sample size and point-in-time availability.

Candidate methods to assess:

1. **Frozen event studies** around historical late-cycle warning candidates.
2. **Leave-one-cycle-out evaluation** so thresholds/models are not evaluated on the same cycle used for fitting.
3. **Matched bull-phase controls** to quantify false-warning rates during ordinary bullish volatility.
4. **Lead-time distributions** instead of single top dates.
5. **Maximum favorable excursion / maximum adverse excursion** after each warning stage.
6. **Survival/invalidation analysis**: probability a warning survives 24h/72h/7d versus reverts.
7. **Sensor ablation / incremental-value tests** to identify correlated duplicates.
8. **Staged-action counterfactuals** using frozen policies defined before outcomes, not hindsight-selected exits.
9. **Cross-cycle robustness** with explicit uncertainty from the tiny number of independent macro cycles.
10. **Within-cycle episode tests** for blow-off, false-breakdown, deleveraging and re-acceleration episodes, kept separate from independent-cycle claims.

Astra should reject any backtest that reconstructs unavailable historical inputs and then labels them as genuinely point-in-time evidence.

## Data acquisition plan

### Use archive first
Inventory the existing GitHub archive before requesting external spend. Identify exactly which missing histories materially constrain endgame testing.

### CFGI
The user is willing to purchase/use additional CFGI API capacity if a large historical pull has clear marginal research value.

Before requesting extra CFGI usage, Astra should specify:
- exact symbols/series/components needed;
- historical date range;
- temporal resolution;
- expected row count/call count/token or API consumption if knowable;
- exact hypothesis that the additional data can test;
- why current archived CFGI is insufficient;
- how the result could change or falsify the framework.

Do not collect a large CFGI dataset merely because it is available.

### Other histories
Astra may recommend additional historical sources for prices, dominance, breadth, derivatives, stablecoins, ETF, options or on-chain holder behavior only when source authority, continuity, licensing and point-in-time semantics can be defended.

## Required scoring framework

Astra should recommend a scorecard that keeps these separate:

- state-classification accuracy;
- premature-exit cost / missed upside;
- late-exit cost / drawdown surrendered;
- warning lead time;
- invalidation/recovery quality;
- confidence calibration;
- data/provenance quality;
- incremental value versus a simple price/trend baseline;
- robustness across cycles/episodes.

Do not optimize a single metric such as top-date accuracy.

## Historical baseline challenger

Every complex endgame model must be compared with simple challengers, for example:
- price/trend only;
- price + breadth;
- price + ETH/BTC;
- simple staged reduction policy;
- current framework warning vocabulary without new sensors.

If the complex system does not beat simple challengers on terminal-wealth trade-off and false-exit cost out of sample, Astra should recommend simplification.

## Prospective implementation target

After historical research, the preferred implementation path is:

1. freeze a research contract;
2. run zero-weight prospective observations;
3. timestamp every stage transition and invalidation;
4. mature outcomes at pre-registered horizons;
5. score false-exit and late-exit costs;
6. review in Master Monday / Monthly AI Learning Council;
7. only then propose governance promotion if evidence is sufficient.

No autonomous threshold optimization or self-promotion.

## Astra deliverables

Astra should return:

1. **Archive map** — what already exists and what should not be duplicated.
2. **Gap matrix** — missing histories, provenance weaknesses and true blockers.
3. **Historical research plan** — ranked by expected information gain.
4. **Backtest design** — with anti-hindsight and out-of-sample safeguards.
5. **Data request manifest** — especially any CFGI bulk pull, with cost/value justification.
6. **False-exit vs late-exit scorecard design**.
7. **Proposed prospective owner/lifecycle** for a staged endgame ladder, or an explicit recommendation to leave E0-E7 blocked.
8. **Implementation plan** — smallest safe GitHub changes first.
9. **Adversarial report** — strongest case the proposed system would still exit too early; strongest case it would exit too late.
10. **STOP/GO decision** for each proposed sensor/model based on incremental value.

## Non-negotiable success definition

The system should not merely warn that a top is near. It should become better at answering:

> Is the expected benefit of waiting for more upside now smaller than the expected capital-preservation benefit of acting, given the current evidence and uncertainty?

while retaining the ability to reverse a warning when the market re-accelerates.

The end goal is not to sell the exact top. The end goal is to leave the cycle with the maximum realistically retainable wealth while avoiding both false hope and premature fear.