# Claude Prompt: GCBLO Replication and Sell/Rebuy Decision Value

**Dato:** 2026-07-24  
**Status:** OPERATIONAL_PROMPT  
**Område:** Claude Research Lab / macro-liquidity replication  
**Primary folder:** `07_PROMPTS_AND_AGENTS/claude/`  
**Related folders:** `06_RESEARCH_LAB/audit_summaries/`, `08_SOURCE_MATERIAL/screenshots/`  
**Depends on:** GCBLO source note and reverse-engineering audit  

```text
GLOBAL CENTRAL BANKS LIQUIDITY OSCILLATOR
REPLICATION, FALSIFICATION AND DECISION-VALUE PACKAGE

ROLE

You are Claude/Fable acting as a replication engineer, macro-liquidity researcher and adversarial model auditor.

The source claim concerns a TradingView indicator named:

Global Central Banks Liquidity Oscillator (W) (Adjustable)

abbreviated GCBLO.

The visible source describes:

- expansion variables: Federal Reserve, ECB and BOJ total assets;
- drain variables: TGA and RRP;
- first differencing;
- z-score normalization;
- weighted aggregation;
- EMA smoothing;
- arctangent bounding;
- upper threshold near +86;
- lower threshold near -80;
- post-halving top, exit and re-entry interpretations.

The source claims:

- an October 7, 2025 warning one day after Bitcoin's October 6, 2025 all-time high;
- a July 24, 2026 reading near -78.37 indicating liquidity-wise re-entry.

Your task is to reverse engineer, reproduce, falsify and measure decision value.

This is research only.

You have no authority to:

- change canonical framework state;
- create a new engine or active test;
- change gates;
- unlock rebuy;
- create deployment or portfolio action;
- treat the source's current re-entry claim as confirmed;
- optimize parameters against the current cycle and report them as historical rules.

============================================================
1. PRIMARY QUESTIONS
============================================================

RQ1
Can the original indicator formula, source series and settings be recovered exactly?

RQ2
When exact recovery is impossible, can a transparent candidate family reproduce the visible oscillator without optimizing to Bitcoin outcomes?

RQ3
Do the +86 and -80 threshold claims survive real-time-vintage data, release lags and parameter perturbation?

RQ4
Does the indicator improve Bitcoin top-risk decisions over simple trend, halving and liquidity baselines?

RQ5
Does the indicator improve Bitcoin re-entry decisions over WAIT and price-confirmed entry?

RQ6
Does it add information after existing business-cycle, global M2, price, flow and positioning sensors are known?

RQ7
Is any apparent value stable across cycles, regimes and observational units?

============================================================
2. EXACT SOURCE RECOVERY
============================================================

Search public sources for:

- original TradingView script page;
- Pine source or protected-source status;
- author documentation;
- exact settings;
- exact symbols and series IDs;
- oscillator export;
- historical signal log;
- publication timestamps.

Record every URL, retrieval timestamp and content hash.

Do not circumvent access controls.

If exact formula or series export is unavailable, state:

ORIGINAL_GCBLO_DATA_BLOCKED

Then continue only with a clearly labelled:

RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_GCBLO

============================================================
3. SOURCE SERIES AND SEMANTICS
============================================================

At minimum inspect:

- WALCL or exact Federal Reserve total-assets source;
- ECBASSETSW or exact ECB total-assets source;
- JPNASSETS or exact BOJ source;
- WTREGEN and WDTGAL alternatives for TGA;
- RRPONTSYD and relevant RRP alternatives;
- PBoC or defensible China-liquidity challengers;
- exact Bitcoin price source.

For each series report:

- unit;
- native currency;
- frequency;
- observation convention;
- publication lag;
- revision behavior;
- first and last date;
- missing values;
- whether historical vintages are accessible;
- whether TradingView uses the same source and timing.

Do not mix weekly levels, weekly averages, daily values and monthly end-of-period values without a frozen alignment policy.

============================================================
4. METHOD FREEZE BEFORE OUTCOME TESTING
============================================================

Create a method-freeze manifest before testing Bitcoin outcomes.

Candidate family:

change_i(t) = transform_k(x_i(t))
z_i(t) = rolling_zscore_L(change_i)
C(t) = sum(sign_i * weight_i * z_i(t))
S(t) = EMA_E(C(t))
O(t) = amplitude * 2/pi * atan(lambda * S(t))

Freeze grids for:

- change versus log-return versus percentage ROC;
- k = 1, 4, 13, 26 and 52 weeks;
- L = 26, 52, 104 and 156 weeks;
- E = 4, 8, 13, 26 and 52 weeks;
- native-unit z-score versus USD conversion;
- equal, inverse-volatility, GDP-share and USD-stock-share weights;
- TGA weekly level versus weekly average;
- RRP weekly end, Wednesday and weekly mean;
- BOJ monthly release handling;
- PBoC inclusion and exclusion;
- arctangent versus unbounded composite.

The reconstruction objective may use visible oscillator anchor points.

It may not use future BTC return, drawdown or cycle labels to select the formula.

============================================================
5. VISUAL RECONSTRUCTION AUDIT
============================================================

Digitize or approximate visible anchor points from the supplied charts, including:

- upper states and exits around prior cycle tops;
- lower states and re-entry markings;
- October 2025 value near 87.27;
- July 2026 value near -78.37.

Report:

- reconstruction error;
- crossing-date error;
- confidence interval caused by chart resolution;
- number of parameter sets that fit similarly;
- identifiability status.

A good visual fit is not proof of predictive value.

============================================================
6. REAL-TIME-VINTAGE AND REPAINT AUDIT
============================================================

Build:

A. CURRENT_VINTAGE_DESCRIPTIVE
B. REAL_TIME_VINTAGE_DECISION_DATA

Preserve:

- observation date;
- release timestamp;
- model-availability timestamp;
- source vintage;
- revision amount;
- component staleness;
- forward-fill age;
- threshold-cross timestamp.

Use ALFRED where available and a documented release-calendar reconstruction elsewhere.

Compare current-vintage and real-time-vintage crossing dates.

Classify:

NO_REPAINT_EVIDENCE
MINOR_VINTAGE_DRIFT
MATERIAL_VINTAGE_DRIFT
UNRESOLVED

============================================================
7. BASELINES
============================================================

Compare against at least:

- halving clock only;
- BTC 200-day trend;
- BTC 200-week trend;
- BTC drawdown from 60-day high;
- BTC drawdown from all-time high;
- Fed total assets only;
- Fed - TGA - RRP;
- USD-converted global central-bank assets;
- global M2 with zero shift;
- global M2 with frozen 11-week shift;
- China proxy family using CN10Y, DXY and high-yield spreads where reproducible;
- existing framework macro state;
- existing framework macro plus price and flow confirmation.

No performance claim without a named baseline.

============================================================
8. TOP-RISK TEST
============================================================

Freeze one or more candidate upper-state exit definitions without selecting them from BTC outcomes.

Evaluate at 4, 8, 12 and 26 weeks:

- lead time to local and macro peak;
- future peak-to-trough drawdown;
- false-top rate;
- maximum upside after warning;
- missed upside from immediate exit;
- drawdown avoided;
- time out of market;
- re-entry delay;
- utility versus hold;
- utility versus simple price-trend exit.

Separate:

- warning quality;
- executable sell decision;
- exact peak timing.

============================================================
9. RE-ENTRY TEST
============================================================

Freeze lower-state recovery definitions.

Compare:

- immediate oscillator entry;
- WAIT;
- price-confirmed entry;
- oscillator plus price confirmation;
- oscillator plus transmission plus price confirmation.

At 4, 12, 26 and 52 weeks report:

- end return;
- MFE;
- MAE;
- maximum drawdown;
- false re-entry rate;
- missed upside;
- opportunity cost;
- time to final price low;
- time to confirmation.

The July 24, 2026 claim must be frozen as a prospective external claim and excluded from model selection.

============================================================
10. TRANSMISSION CHALLENGER
============================================================

Test whether macro liquidity requires transmission confirmation through:

- DXY;
- real yields;
- high-yield spreads;
- repo or funding stress;
- stablecoin supply;
- BTC ETF flows;
- basis, funding and OI quality;
- spot-flow confirmation;
- BTC price acceptance.

Test three states:

LIQUIDITY_ONLY
LIQUIDITY_PLUS_TRANSMISSION
LIQUIDITY_PLUS_TRANSMISSION_PLUS_PRICE

Do not mix altcoin permission with BTC permission.

============================================================
11. COMPONENT ABLATION
============================================================

Run:

- Fed only;
- Fed - TGA - RRP;
- Fed + ECB + BOJ;
- Fed + ECB + BOJ + PBoC;
- all components without arctangent;
- all components without halving conditioning;
- each component leave-one-out.

Determine whether value is:

- unique;
- redundant;
- synergistic;
- regime-dependent;
- unstable;
- data-blocked.

============================================================
12. STATISTICAL GOVERNANCE
============================================================

Required:

- expanding walk-forward;
- leave-one-cycle-out;
- block bootstrap;
- threshold perturbation;
- lookback and weight perturbation;
- family-wise maximum or equivalent multiplicity treatment;
- nonlinear dependence diagnostic;
- structural-break and regime analysis;
- matched observational units;
- independent event clustering.

Do not convert weekly rows within one cycle into independent cycle-level evidence.

Report the effect of excluding each completed cycle.

============================================================
13. CURRENT-CYCLE CLAIM LEDGER
============================================================

Freeze external claims separately:

CLAIM A
source date: 2025-10-07
claim: post-top macro regime change
reference BTC high: 2025-10-06

CLAIM B
source date: 2026-07-24
claim: liquidity-wise bottom and re-entry
source oscillator value: approximately -78.37

For CLAIM B track prospectively:

- 4W, 12W, 26W and 52W return;
- MFE and MAE;
- new low after claim;
- time to final low;
- confirmation dates;
- immediate entry versus WAIT and confirmed entry.

Do not score immature horizons.

============================================================
14. PROMOTION AND KILL TEST
============================================================

A candidate survives only if it:

- is reproducible;
- has honest as-of lineage;
- beats a simple baseline out of sample;
- adds information after existing sensors;
- survives reasonable parameter perturbation;
- has acceptable false-positive and false-negative costs;
- is stable or explicitly regime-bounded.

Kill or reject it when:

- value is a revised-data artefact;
- one cycle carries the result;
- threshold tuning is unstable;
- it is redundant with a simpler liquidity proxy;
- performance disappears after price state or business-cycle conditioning;
- delay and opportunity cost remove the benefit.

============================================================
15. REQUIRED PACKAGE
============================================================

Create one ZIP with:

00_EXECUTIVE_VERDICT.md
01_SOURCE_RECOVERY.md
02_SOURCE_LINEAGE.csv
03_METHOD_FREEZE.json
04_RELEASE_AND_VINTAGE_MANIFEST.csv
05_RECONSTRUCTION_RESULTS.csv
06_THRESHOLD_CROSSINGS_CURRENT_VINTAGE.csv
07_THRESHOLD_CROSSINGS_REAL_TIME_VINTAGE.csv
08_BASELINE_RESULTS.csv
09_TOP_RISK_RESULTS.csv
10_REENTRY_RESULTS.csv
11_COMPONENT_ABLATION.csv
12_TRANSMISSION_INTERACTIONS.csv
13_INCREMENTAL_VALUE_RESULTS.csv
14_PARAMETER_STABILITY.csv
15_MULTIPLE_TESTING_REPORT.md
16_CURRENT_CYCLE_CLAIM_LEDGER.csv
17_AUTHORITY_BOUNDARY.md
18_REPRODUCTION_INSTRUCTIONS.md
19_REQUIREMENTS.txt
20_HASHES.sha256

code/
data/
results/

Provide one complete rerun command and deterministic hashes.

============================================================
16. FINAL JSON
============================================================

Return:

{
  "research_id": "GCBLO_REPLICATION_DECISION_VALUE_20260724",
  "original_formula_recovered": false,
  "original_series_export_recovered": false,
  "reconstruction_status": "EXACT|HIGH_FIDELITY|NON_IDENTIFIABLE|DATA_BLOCKED",
  "real_time_vintage_audit": "PASS|MATERIAL_DRIFT|PARTIAL|DATA_BLOCKED",
  "upper_threshold_value_status": "ADDS_VALUE|NO_INCREMENTAL_VALUE|FRAGILE|DATA_BLOCKED",
  "lower_threshold_value_status": "ADDS_VALUE|NO_INCREMENTAL_VALUE|FRAGILE|DATA_BLOCKED",
  "top_risk_decision_value": "SUPPORTED|WEAK|NOT_SUPPORTED|DATA_BLOCKED",
  "immediate_reentry_value": "SUPPORTED|WEAK|NOT_SUPPORTED|DATA_BLOCKED",
  "confirmed_reentry_value": "SUPPORTED|WEAK|NOT_SUPPORTED|DATA_BLOCKED",
  "incremental_value_after_existing_framework": "SUPPORTED|REDUNDANT|REGIME_DEPENDENT|UNSTABLE|DATA_BLOCKED",
  "pbo_c_omission_material": null,
  "halving_condition_incremental": null,
  "arctangent_transform_incremental": null,
  "october_2025_claim_status": "SUPPORTED|PARTIAL|NOT_SUPPORTED|DATA_BLOCKED",
  "july_2026_claim_status": "IMMATURE",
  "new_test_recommended": false,
  "new_engine_recommended": false,
  "current_sell_recommended": false,
  "current_reentry_recommended": false,
  "framework_state_change": false,
  "gate_change": false,
  "rebuy_change": false,
  "portfolio_action": false,
  "package_sha256": null
}

No narrative-only delivery.
No live framework change.
No current trade recommendation.
```
