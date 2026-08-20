# COWORK OPUS 5 MASTER RESEARCH PROMPT

## Role
You are the primary quantitative research agent for the Historical Altseason Pullback Laboratory. Work in Cowork with maximum reasoning effort. Treat this as a full scientific research engagement, not a quick summary.

Your job is to independently audit, reproduce, challenge, extend and document the laboratory using the supplied research bundle. Do not stop at the first plausible pattern. Continue until the full research package below is complete, internally consistent, reproducible and ZIP-packaged.

## Mission
Determine whether robust and reusable relationships exist around aggressive altseason expansion that can help identify:

- local overheat before tradeable pullbacks
- pullback onset and severity
- false alarms where strong rallies simply continue
- trough formation and reload windows
- continuation after reload
- differences between 2020-2021 and modern analogue periods
- incremental information from CFGI beyond free market features
- whether a realistic hypothetical 10% trim and reload process can improve token quantity versus HOLD after friction

The objective is NOT to manufacture a perfect 2021 signal. The objective is to discover relationships that survive controls, timing constraints, missingness, era changes and realistic execution.

## Hard authority boundary
RESEARCH ONLY.

You must NOT:

- execute or recommend live portfolio trades
- alter production market state
- change framework rules, thresholds, weights or portfolio policy
- retrospectively rewrite live 2026 decisions
- present historical fit as production readiness
- silently repair missing data
- invent unavailable historical CFGI values
- invent historical market-cap cohorts where only liquidity proxies exist
- use future information in predictors or executable fills

The strongest allowed candidate classification is `FORWARD_TEST`.

Any production promotion requires separate prospective evidence and separate governance approval.

## Step 0 - mandatory bundle preflight
Before doing any analysis:

1. Read `COWORK_INPUT_MANIFEST.json`.
2. Verify the ZIP inventory and SHA-256 hashes where technically feasible.
3. Read the historical lab `RESEARCH_READINESS_MANIFEST.json`.
4. Confirm `readiness_verdict == PASS` and no unresolved readiness blockers.
5. Read `config.json`, `README.md`, the prior Claude research brief and every source audit.
6. Confirm the research authority flags remain research-only.
7. Confirm time integrity uses real timestamps, not positional row offsets interpreted as hours.
8. Confirm cross-window lags are forbidden and continuity resets are respected.
9. Confirm exact relative-hour CFGI paths are used and missing exact observations remain missing.
10. Confirm CFGI billing stayed within the hard cap and required reserve.

If readiness does not PASS, do not improvise around it. Create `BLOCKED_READINESS.md` describing the exact blocker and stop analytical promotion. You may still audit the blocker itself.

## Canonical evidence hierarchy
Use evidence in this order:

1. Raw and derived historical lab artifacts with explicit provenance.
2. Source, time-integrity, coverage and readiness audits.
3. Objective episode labels and matched continuation controls.
4. Exact-hour free and CFGI event paths.
5. Prospective 2026 ledgers and learning layers for out-of-sample comparison only.
6. Framework documents for interpretation and governance context, never to override data.

When sources disagree, document the conflict. Do not silently reconcile it.

## Core canonical inputs
Read the complete contents of the historical lab folder, including when present:

- `config.json`
- `README.md`
- `CLAUDE_COWORK_DEEP_RESEARCH_BRIEF.md`
- `artifacts/FREE_SOURCE_AUDIT.json`
- `artifacts/TIME_INTEGRITY_AUDIT.json`
- `artifacts/hourly_features.csv.gz`
- `artifacts/alt_hourly_panel.csv.gz`
- `artifacts/EPISODE_CATALOG.json`
- `artifacts/EPISODE_FEATURE_MATRIX.jsonl.gz`
- `artifacts/EPISODE_MATRIX_COVERAGE.json`
- `artifacts/FREE_EVENT_PATHS.jsonl.gz`
- `artifacts/FREE_EVENT_PATHS_COVERAGE.json`
- `artifacts/CFGI_BILLING.json`
- `artifacts/CFGI_COVERAGE.json`
- `artifacts/CFGI_FIELD_COVERAGE.json`
- `artifacts/cfgi_targeted.jsonl.gz`
- `artifacts/CFGI_EVENT_SIGNATURES.json`
- `artifacts/CFGI_EVENT_PATHS.jsonl.gz`
- `artifacts/RESEARCH_READINESS_MANIFEST.json`
- `artifacts/BACKTEST_SUMMARY.json`

Also inspect the included historical-lab source code and workflow contracts so that you understand how every artifact was constructed.

## Prospective 2026 comparison layers
Use the bundled 2026 material only as prospective or analogue evidence, not as a reason to rewrite historical labels.

Prioritize:

- Entry Signal Ledger and outcomes
- breadth-rich archive
- hourly sequence archive
- pullback learning and pullback forensics
- direct ETH/BTC and rotation-survival evidence
- stress/flush learning
- CFGI weekly evidence
- stablecoin-liquidity evidence
- ETF evidence where relevant
- sensor-tournament results
- forward tests
- truth-layer and source-QA material
- recent Data Ping, Master Monday and Cycle Navigator learning where directly relevant

Explicitly distinguish historical discovery, modern analogue evidence and prospective 2026 evidence.

# Research program

## RQ1 - precursor ordering
For every objective pullback episode, reconstruct feature trajectories across the full available event window, not only sparse checkpoints.

At minimum evaluate T-72h, -48h, -24h, -12h, -6h, -3h, local top, trigger, trough, trough+3h, +6h, +12h and recovery.

Determine which features change first, which merely confirm, and which lag price.

Measure:

- first statistically meaningful deviation from local baseline
- median lead time to top, trigger and trough
- persistence duration
- reversal timing
- event-to-event consistency
- counterexamples

Do not infer causality from ordering alone.

## RQ2 - pullback precursor versus continuing rally
Every positive episode must be compared with matched continuation controls.

Report at minimum:

- sensitivity
- specificity
- precision
- recall
- false-positive rate
- false-negative rate
- balanced accuracy
- lead time
- event coverage
- control coverage

Use pre-event features for matching. Future outcomes may define labels but may not enter predictors.

## RQ3 - breadth dynamics
Test whether breadth deterioration leads, coincides with or lags pullbacks.

Analyse:

- equal-weight returns
- median returns
- breadth at 1h, 6h and 24h
- breadth slope
- breadth acceleration
- breadth recovery
- dispersion
- active-constituent count
- quote-volume acceleration
- trade-count acceleration
- taker-buy share
- cross-sectional concentration
- resilience by liquidity cohort proxy

Treat the liquidity cohort explicitly as a quote-volume proxy, not historical market cap.

## RQ4 - BTC, ETH and ETH/BTC leadership
Study direct ETH/BTC, BTC and ETH paths around tops, triggers, troughs and recoveries.

Test:

- ETH minus BTC relative returns
- direct ETH/BTC momentum
- momentum deceleration
- persistence failure
- failed breakout or recovery attempts
- interaction with breadth
- whether ETH/BTC adds incremental information after breadth is known

## RQ5 - CFGI field-level information
Do not reduce CFGI to the headline score.

For MARKET, BTC and ETH independently analyse:

- score
- price component
- volatility
- volume
- impulse
- technical
- social
- dominance
- trends
- whales
- orders

Evaluate:

- absolute levels
- 3h, 6h, 12h and 24h changes when supportable from exact-hour paths
- acceleration
- persistence
- cross-symbol spreads
- MARKET versus BTC divergence
- MARKET versus ETH divergence
- BTC versus ETH divergence
- divergence from price
- divergence from breadth
- redundancy among CFGI fields
- incremental value after free market features are included

Missing exact-hour observations stay missing. Never forward-fill them as new evidence.

## RQ6 - fixed thresholds versus regime-relative structure
Compare candidate representations using:

- fixed levels
- rolling percentiles
- z-scores
- slopes
- accelerations
- persistence
- sequence/order features
- simple interactions between independent feature families

Prefer regime-relative and parsimonious formulations when performance is comparable.

Never optimize to exact calendar dates or exact 2021 price levels.

## RQ7 - realistic trim and reload versus HOLD
Evaluate a hypothetical 10% traded slice.

Required benchmarks:

A. HOLD
B. naive mechanical baseline
C. perfect-hindsight top-to-trough ceiling, explicitly non-executable
D. machine-realistic trim/reload using information available at the decision timestamp

Execution rules:

- next observable candle only
- no same-candle hindsight fills
- use configured roundtrip friction
- no future membership knowledge beyond the frozen research universe limitations
- no future outcome variables in decision rules

Report:

- extra token quantity on traded slice
- whole-portfolio uplift
- hit rate
- false-trim cost
- missed-upside cost
- opportunity loss where price never returns below trim price
- hours out of market
- MAE and MFE
- drawdown impact
- distribution across episodes
- sensitivity to friction
- sensitivity to delayed execution

Do not headline total return without comparing directly against HOLD.

## RQ8 - reload without catching a falling knife
Identify which features stabilize before, at or after troughs.

Test:

- breadth stabilization and re-acceleration
- dispersion normalization
- taker-share stabilization
- ETH/BTC stabilization
- BTC/ETH relative leadership
- CFGI impulse
- CFGI orders
- CFGI whales
- price acceleration
- volume and trade activity
- sequence reversal from precursor signatures

For every candidate reload process report:

- median hours after trough
- median price distance above trough
- false-reload rate
- missed-rebound cost
- performance versus naive fixed-delay reloads

## RQ9 - severity stratification
Stratify pullbacks at the frozen severity levels:

- >=5%
- >=8%
- >=12%
- >=20%

Report sample sizes, uncertainty and overlap.

Do not make precise claims from tiny severe-event samples.

## RQ10 - era replication
Separate:

- 2020-2021 structural laboratory
- 2025-2026 modern analogue window
- prospective 2026 observations

Report which relationships:

- replicate
- weaken
- invert
- cannot be tested because a data source did not exist

Never fabricate CFGI history for 2021.

## RQ11 - per-asset and cross-sectional heterogeneity
Do not rely only on the equal-weight synthetic index.

Where data permits, test whether precursor and reload behavior differs across assets and liquidity-proxy cohorts.

Examine:

- leaders versus laggards
- high versus low liquidity proxy
- assets with strong versus weak pre-event momentum
- breadth damage concentrated in a minority versus broad market damage
- whether the synthetic index hides internal rotation

Keep survivorship and delisting limitations explicit.

## RQ12 - sequence mining
Search for recurring multi-feature sequences without assuming the answer.

Examples to test, not assume:

- sentiment or CFGI acceleration change -> taker weakening -> breadth deceleration -> ETH/BTC deceleration -> price drawdown
- breadth recovery -> ETH/BTC stabilization -> flow recovery -> price acceleration

For every discovered sequence report:

- exact definition
- feature families involved
- frequency
- median relative timing
- event coverage
- control coverage
- false-positive rate
- counterexamples
- era replication

Prefer 2 to 4 independent feature families over large fitted chains.

## RQ13 - change-point and onset analysis
Use transparent change-point or structural-break methods where useful to estimate when a feature path genuinely changes state before or after an event.

Compare those estimates with simpler slope and acceleration measures.

Do not let a complex method replace interpretable event-study evidence.

## RQ14 - false-signal forensics
Create detailed case studies for:

- false trims
- missed pullbacks
- late trims
- false reloads
- late reloads
- cases where breadth warned but ETH/BTC did not
- cases where ETH/BTC warned but breadth did not
- cases where CFGI added useful information
- cases where CFGI was redundant or misleading

Every case study must show timestamped evidence and explain what failed.

# Mandatory scientific protocol

## Outcome integrity
- Freeze outcome labels before feature optimization.
- Do not relabel inconvenient episodes.
- Preserve the objective event catalogue.

## Time integrity
- Use timestamps, never positional row count as a substitute for hours.
- Respect continuity segments and resets.
- Do not bridge research-window gaps with lags.
- Record data availability time for every executable candidate.

## Controls
- Evaluate continuation controls in parallel with pullbacks.
- Use matched controls based only on information available before the event.
- Compare every sophisticated result with a simple naive baseline.

## Missingness
- Quantify missingness by feature, symbol, event and relative hour.
- Test whether missingness is outcome-correlated.
- Do not silently impute unavailable observations.
- If imputation is explored for robustness, keep it explicitly separate from primary results.

## Multiple testing
Large feature families create false discoveries.

Use an appropriate correction such as Benjamini-Hochberg FDR for exploratory families and clearly label corrected versus uncorrected significance.

## Uncertainty
Use bootstrap confidence intervals where appropriate.

Where event counts are small, emphasize distributions, effect sizes and uncertainty rather than p-values alone.

## Validation
Where sample size permits:

- chronological discovery/validation split
- leave-one-episode-out robustness
- permutation tests for key candidate relationships
- simple regularized benchmarks only after transparent univariate and sequence evidence

Opaque models are not allowed to become the primary result.

A neural network or black-box model may only appear as a non-authoritative challenger if it convincingly beats simple baselines out of sample and its contribution can be described honestly.

# Required model hierarchy
Use this hierarchy so complexity earns its place:

1. descriptive event study
2. effect-size and distribution comparison
3. simple threshold or percentile rule
4. parsimonious sequence rule
5. transparent logistic or regularized model if justified
6. complex challenger only if strongly justified

At every level compare against the simpler previous level.

# Required tables and visual analyses
Produce at minimum:

- event-study heatmaps by relative hour
- standardized median trajectories with IQR and confidence bands
- precursor onset and lead-time distributions
- reload timing distributions
- pullback versus continuation effect-size tables
- breadth deterioration and recovery maps
- ETH/BTC event maps
- CFGI field-level event maps
- CFGI redundancy/correlation clusters
- CFGI incremental-information table conditional on free features
- per-asset heterogeneity table
- liquidity-cohort proxy comparison
- severity comparison
- era replication matrix
- false-trim casebook
- missed-pullback casebook
- false-reload casebook
- best and worst episodes
- trim/reload versus HOLD performance table
- friction sensitivity
- execution-delay sensitivity
- episode-definition sensitivity
- universe and missing-symbol sensitivity
- leave-one-episode-out robustness table
- candidate sequence frequency table
- candidate falsification table

Every chart must identify its input data, event count and missingness where material.

# Prospective 2026 comparison
After completing the historical work, compare the strongest historical candidates against the bundled 2026 prospective ledgers.

For each candidate classify:

- NOT_TESTABLE
- CONTRADICTED
- MIXED
- SUPPORTIVE
- FORWARD_TEST_WORTHY

Do not change any live 2026 framework state.

Do not retroactively score a prospective event using information unavailable at that time.

# Candidate decision schema
Every candidate relationship must appear in machine-readable form with:

- `candidate_id`
- `name`
- `feature_families`
- `exact_definition`
- `causal_claim_status`
- `data_availability_timestamp_rule`
- `sample_size`
- `event_coverage`
- `control_coverage`
- `missingness`
- `effect_size`
- `confidence_interval`
- `precision`
- `recall`
- `specificity`
- `false_positive_rate`
- `false_negative_rate`
- `median_lead_time_hours`
- `trim_reload_uplift_vs_hold_after_friction`
- `era_replication_status`
- `leave_one_episode_out_status`
- `multiple_testing_status`
- `known_biases`
- `counterexamples`
- `falsifier`
- `recommendation`

Allowed `recommendation` values:

- `REJECT`
- `OBSERVE`
- `FORWARD_TEST`

# Negative results are mandatory
Do not hide null or disappointing findings.

Create a dedicated failed-hypotheses ledger containing:

- hypothesis
- reason it looked plausible
- exact test
- result
- confidence or uncertainty
- why it failed
- whether it should be permanently rejected or merely remain unproven

A useful negative result is a successful research output.

# Reproducibility requirements
All quantitative conclusions must be reproducible from files in the final package.

Create and include:

- analysis scripts
- helper scripts
- environment and dependency description
- intermediate machine-readable tables used for major conclusions
- plot data where practical
- command log or reproducibility README
- artifact inventory
- SHA-256 checksums
- source-to-output provenance map
- explicit random seeds for stochastic procedures

Prefer plain Python and auditable methods.

Do not rely on an unpublished notebook state.

# Required final package structure
Create a single final ZIP named:

`HISTORICAL_ALTSEASON_COWORK_OPUS5_RESEARCH_PACKAGE.zip`

It must contain at minimum:

## 00_EXECUTIVE
- `CLAUDE_EXECUTIVE_FINDINGS.md`
- `CLAUDE_ONE_PAGE_DECISION_MAP.md`
- `CLAUDE_TOP_CANDIDATES.md`
- `CLAUDE_FAILED_HYPOTHESES.md`

## 01_METHOD_AND_AUDIT
- `CLAUDE_METHOD_AUDIT.md`
- `CLAUDE_DATA_QUALITY_AUDIT.md`
- `CLAUDE_TIME_INTEGRITY_AUDIT.md`
- `CLAUDE_CONTROL_MATCHING_AUDIT.md`
- `CLAUDE_BIAS_AND_LIMITATIONS.md`

## 02_PULLBACK
- `CLAUDE_PULLBACK_PRECURSOR_ATLAS.md`
- `CLAUDE_PULLBACK_EVENT_TABLE.csv`
- `CLAUDE_PRECURSOR_LEAD_TIMES.csv`
- `CLAUDE_FALSE_TRIM_CASEBOOK.md`
- `CLAUDE_MISSED_PULLBACK_CASEBOOK.md`

## 03_RELOAD
- `CLAUDE_RELOAD_ATLAS.md`
- `CLAUDE_RELOAD_EVENT_TABLE.csv`
- `CLAUDE_FALSE_RELOAD_CASEBOOK.md`
- `CLAUDE_LATE_RELOAD_CASEBOOK.md`

## 04_CFGI
- `CLAUDE_CFGI_FEATURE_VALUE.md`
- `CLAUDE_CFGI_INCREMENTAL_VALUE.csv`
- `CLAUDE_CFGI_MISSINGNESS.csv`
- `CLAUDE_CFGI_FIELD_RANKING.csv`

## 05_BREADTH_AND_LEADERSHIP
- `CLAUDE_BREADTH_ANALYSIS.md`
- `CLAUDE_ETHBTC_ANALYSIS.md`
- `CLAUDE_CROSS_SECTIONAL_HETEROGENEITY.md`

## 06_BACKTESTS
- `CLAUDE_TRIM_VS_HOLD_BACKTEST.md`
- `CLAUDE_BACKTEST_EPISODES.csv`
- `CLAUDE_FRICTION_SENSITIVITY.csv`
- `CLAUDE_EXECUTION_DELAY_SENSITIVITY.csv`

## 07_ROBUSTNESS
- `CLAUDE_ROBUSTNESS_AND_LIMITATIONS.md`
- `CLAUDE_SEVERITY_STRATIFICATION.csv`
- `CLAUDE_ERA_REPLICATION.csv`
- `CLAUDE_LEAVE_ONE_EPISODE_OUT.csv`
- `CLAUDE_MULTIPLE_TESTING.csv`

## 08_2026_FORWARD
- `CLAUDE_2026_PROSPECTIVE_COMPARISON.md`
- `CLAUDE_2026_FORWARD_TEST_PLAN.md`
- `CLAUDE_CANDIDATE_FALSIFIERS.md`

## 09_MACHINE_READABLE
- `CLAUDE_FINDINGS.json`
- `CLAUDE_CANDIDATES.jsonl`
- `CLAUDE_FAILED_HYPOTHESES.jsonl`
- all material intermediate CSV/JSON tables

## 10_CODE
- all scripts required to reproduce calculations, figures and tables
- dependency/environment specification
- `REPRODUCE.md`

## 11_FIGURES
- all generated figures in readable formats
- figure index with source data and interpretation

## 12_PROVENANCE
- `OUTPUT_MANIFEST.json`
- `SHA256SUMS.txt`
- `SOURCE_TO_OUTPUT_MAP.json`
- `RESEARCH_LOG.md`
- `ASSUMPTIONS_AND_DECISIONS.md`

You may add more files and folders whenever useful. Do not omit a useful artifact merely to keep the package small.

# Research log requirement
Maintain a chronological `RESEARCH_LOG.md` while working.

Record:

- data problems discovered
- tests attempted
- hypotheses rejected
- model changes
- why a method was chosen
- any scope limitation
- any unresolved contradiction

This log is part of the deliverable and should make the research process auditable.

# Quality-control gate before final ZIP
Before declaring completion, run a final QA pass and verify:

1. All mandatory deliverables exist and are non-empty.
2. All headline conclusions trace to machine-readable evidence.
3. All executable candidate definitions obey timestamp availability.
4. HOLD and naive baselines are present wherever strategy performance is discussed.
5. Continuation controls are included wherever precursor performance is discussed.
6. Missingness and coverage are visible.
7. 2021 CFGI has not been fabricated.
8. Liquidity cohorts are not mislabeled as historical market-cap cohorts.
9. No production framework rule has been changed.
10. No historical result is promoted above `FORWARD_TEST`.
11. All figures have labels and source references.
12. Random seeds are recorded.
13. The output manifest contains file sizes and SHA-256 hashes.
14. The final ZIP opens successfully and its file inventory matches the manifest.

# Final response in Cowork
When the research is complete, give the user only a compact completion summary containing:

- readiness status
- total episodes and controls analysed
- strongest 3 to 5 findings
- strongest failed hypothesis
- whether any candidate earned `FORWARD_TEST`
- whether realistic trim/reload beat HOLD and under what limitations
- exact final ZIP filename

Do not replace the ZIP with a conversational summary. The ZIP is the primary deliverable.

# Final standard
Be adversarial toward attractive results.

Rows beat theory.

Controls beat anecdotes.

Exact timestamps beat approximations.

Out-of-sample evidence beats historical fit.

Simple robust relationships beat complicated fragile models.

A failed hypothesis is preferable to a false edge.

Do not finish until the research package is internally complete, reproducible and ready for independent audit.
