# CLAUDE COWORK DEEP RESEARCH BRIEF

## Mission
Perform an independent, extremely detailed research audit and challenger analysis of the Historical Altseason Pullback Laboratory after the free bootstrap and targeted CFGI enrichment artifacts exist. The objective is not to invent a perfect 2021 signal. The objective is to discover robust, reusable relationships that may help identify local overheat, pullback onset, trough/reload conditions and continuation during an aggressive altseason while explicitly measuring false trims and comparing every hypothetical active strategy against HOLD.

## Hard authority boundary
- RESEARCH ONLY.
- No portfolio execution.
- No automatic rule, threshold, weight or regime changes.
- No retrospective reclassification of live 2026 decisions.
- Any proposed production use requires separate governance review and forward validation.

## Canonical inputs
Read all files under `06_RESEARCH_LAB/historical_altseason_pullback_v1/` and specifically require, when present:
- `config.json`
- `artifacts/FREE_SOURCE_AUDIT.json`
- `artifacts/hourly_features.csv.gz`
- `artifacts/EPISODE_CATALOG.json`
- `artifacts/EPISODE_FEATURE_MATRIX.jsonl.gz`
- `artifacts/BACKTEST_SUMMARY.json`
- `artifacts/CFGI_BILLING.json`
- `artifacts/CFGI_COVERAGE.json`
- `artifacts/cfgi_targeted.jsonl.gz`
- `artifacts/CFGI_EVENT_SIGNATURES.json`

Also read the prospective 2026 learning layers where useful for out-of-sample comparison:
- Entry Signal Ledger
- Adaptive Pullback Learning / trim-reload ledger
- hourly market sequence archive
- breadth_rich archive
- direct ETHBTC persistence evidence

## Research questions
### RQ1 - What actually changes first before tradeable altcoin pullbacks?
For every objective pullback episode, calculate feature paths at T-72h, -48h, -24h, -12h, -6h, -3h, top, trigger, trough, trough+3h, +6h, +12h and recovery. Determine lead-lag ordering rather than only correlations.

### RQ2 - Which signals distinguish a genuine pullback precursor from a strong rally that simply continues?
Use continuation controls and matched non-pullback periods. Report sensitivity, specificity, precision, false positive rate, false negative rate and lead time. Never evaluate pullback episodes alone.

### RQ3 - Does breadth deterioration lead price, coincide with price, or lag it?
Analyse equal-weight return, median return, 1h/6h/24h breadth, dispersion, active constituent count, volume/trade activity and taker-buy share. Test breadth slope and acceleration, not only level.

### RQ4 - What does ETH leadership / ETHBTC do around local tops and reloads?
Measure ETH minus BTC relative return and direct ETHBTC trajectory. Test whether loss of ETH leadership, ETHBTC momentum deceleration or persistence failure adds information beyond breadth.

### RQ5 - Which CFGI dimensions contain incremental information?
Do not reduce CFGI to the headline score. Separately analyse MARKET/BTC/ETH for: score, price, volatility, volume, impulse, technical, social, dominance, trends, whales and orders. Evaluate levels, 6h and 24h changes, acceleration, cross-symbol spreads and divergence against price/breadth. Rank fields by incremental value after free market features are known.

### RQ6 - Are useful signatures absolute-threshold based or percentile/regime-relative?
Compare fixed thresholds with rolling percentile, z-score, acceleration and sequence/order representations. Prefer regime-relative formulations when equally predictive because history need only rhyme, not repeat.

### RQ7 - Can a realistic 10% trim/reload strategy beat HOLD?
Use next-observable-candle execution, configured roundtrip friction, no hindsight fills and no use of future information. Compare:
A. HOLD
B. Perfect-hindsight ceiling, top-to-trough only as an upper bound
C. Machine-realistic trim/reload
Report extra token quantity on the traded slice and whole-portfolio uplift, missed upside, false-trim cost, MAE/MFE and opportunity loss when price never returns below trim price.

### RQ8 - How early can we identify reload without catching a falling knife?
Analyse trough and recovery signatures. Test stabilization in breadth, dispersion, taker share, ETHBTC, CFGI impulse/orders/whales and price acceleration. Measure distance from trough and hours after trough for each candidate rule.

### RQ9 - Does behaviour differ by pullback severity?
Stratify at >=5%, >=8%, >=12%, >=20% drawdowns, with sample sizes and uncertainty. Do not claim precision from tiny severe-event samples.

### RQ10 - Does behaviour differ between 2020-2021 and modern analogue windows?
Treat 2020-2021 as the historical structural laboratory and later CFGI-covered periods as enrichment/analogue evidence. Explicitly report where findings fail to replicate across eras.

## Mandatory anti-overfit protocol
1. Outcome-first labels must remain frozen before feature optimisation.
2. Keep pullback and continuation-control datasets separated until evaluation.
3. Split discovery and validation chronologically where sample size permits.
4. Use bootstrap confidence intervals for effect sizes and performance.
5. Correct for multiple comparisons across large CFGI feature families, or explicitly mark exploratory findings.
6. Reject any signal that depends on exact dates, absolute 2021 price levels or impossible-to-know future membership.
7. Flag survivorship bias and constituent-history limitations.
8. Prefer parsimonious sequences of 2-4 independent feature families over large fitted models.
9. No neural network or opaque model unless a simple benchmark is beaten convincingly out of sample.
10. Every candidate must be compared with a naive baseline and HOLD.

## Required analyses
- event-study heatmaps by relative hour
- standardized median feature trajectories with IQR/CI
- precursor lead-time distributions
- recovery/reload lead-time distributions
- pullback vs continuation control effect-size tables
- feature redundancy/correlation clusters
- CFGI incremental-information table conditional on free features
- false-trim case studies
- missed-pullback case studies
- best and worst episodes
- sensitivity analysis to episode definition and friction
- sensitivity to universe membership / missing symbols
- leave-one-episode-out robustness where feasible
- 2026 prospective analogue comparison without changing live policy

## Signal-order research
Explicitly search for recurring sequences, e.g. sentiment/CFGI acceleration change -> taker-flow weakening -> breadth deceleration -> ETHBTC deceleration -> price drawdown, and the reverse around troughs. Do not assume this ordering. Infer it from the data and give frequency, median timing and counterexamples for each discovered sequence.

## Deliverables
Create a self-contained research package with:
1. `CLAUDE_EXECUTIVE_FINDINGS.md`
2. `CLAUDE_METHOD_AUDIT.md`
3. `CLAUDE_PULLBACK_PRECURSOR_ATLAS.md`
4. `CLAUDE_RELOAD_ATLAS.md`
5. `CLAUDE_CFGI_FEATURE_VALUE.md`
6. `CLAUDE_TRIM_VS_HOLD_BACKTEST.md`
7. `CLAUDE_FALSE_SIGNAL_CASEBOOK.md`
8. `CLAUDE_ROBUSTNESS_AND_LIMITATIONS.md`
9. `CLAUDE_2026_FORWARD_TEST_PLAN.md`
10. machine-readable `CLAUDE_FINDINGS.json`

## Machine-readable candidate schema
For every candidate relationship include:
- candidate_id
- feature_families
- exact causal definition
- data availability timestamp rule
- sample size
- event coverage
- control coverage
- effect size
- confidence interval
- precision / recall when applicable
- false-positive rate
- median lead time
- trim/reload uplift vs HOLD after friction
- era replication status
- robustness status
- known biases
- recommendation: REJECT / OBSERVE / FORWARD_TEST

## Final decision standard
A historical relationship is never production-ready by historical performance alone. The strongest allowed recommendation is `FORWARD_TEST`. Promotion requires prospective 2026 evidence and separate owner/governance review.
