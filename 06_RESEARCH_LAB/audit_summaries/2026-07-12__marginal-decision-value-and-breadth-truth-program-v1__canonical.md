# Marginal Decision Value & Breadth Truth Program v1

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Evidence class:** CANONICAL_RESEARCH_EVIDENCE  
**Område:** marginal sensor value / frozen-universe breadth / latency / stablecoin role inversion  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `01_CORE_FRAMEWORK/governance/`, `04_MARKET_LEARNING/truth_layer/`, `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `06_RESEARCH_LAB/audit_summaries/2026-07-12__sensor-survival-timing-placebo-regime-audit-v1__canonical.md`, `04_MARKET_LEARNING/full_backtests/2026-07-12__full-sensor-simulation-backtest-v1__canonical.md`  
**Program package SHA-256:** `84d1614e5fdeb2477853fe980f588450e099a9b9ea852bb13a141f1e640481ca`  
**Frozen breadth source artifact SHA-256:** `5664e81a38161486d21fa01116a5ee9f88ec60a1f9ce36bc9da003b9a4a2050c`  
**GitHub Actions source run:** `Donh91/Eksperimenter-framework-` run `29200348955`, artifact `8262211530`, conclusion `success`  
**Extractor/parser merge receipts:** `e123c2aa3e5e0df7bdb7fa935be4525af15eb3f7`, `7f338cfbac1da29682fea9bb5772e47fb4af421a`

## Frozen proposition

Test whether point-in-time correct altcoin breadth, BTC.D and stablecoin activity add marginal forward decision value beyond simpler price/regime baselines, after accounting for survivorship bias, latency, redundancy and regime transportability.

## Executive verdict

```text
FROZEN_UNIVERSE_BREADTH_TRUTH_LAYER: COMPLETE
SOURCE_VALIDATION: PASS_184_OF_184_WEEKLY_SNAPSHOTS
FROZEN_UNIVERSE_ROWS: 18,400
INTERPOLATION: NONE
CURRENT_CONSTITUENT_BACKFILL_USED_AS_TRUTH: NO

BREADTH_PREDICTIVE_GATE: NOT_SUPPORTED
BREADTH_DESCRIPTIVE_ROLE: RETAIN_ZERO_WEIGHT
BREADTH_STANDALONE_ACTION_AUTHORITY: ZERO

BTC.D_PREDICTIVE_WEIGHT: ZERO
BTC.D_SURVIVAL_RECLAIM_CONTEXT: RETAIN_SHADOW

STABLECOIN_STANDALONE_PREDICTION: NOT_SUPPORTED
STABLECOIN_AVAILABILITY_AND_ONE_ACTIVITY_AXIS: RETAIN_CONTEXT

C2_FORWARD_EVIDENCE_EXPANSION: YES
C2_LIVE_AUTHORITY_INCREASE: NO
A3: QUARANTINE_ZERO_WEIGHT
D: CONFIRMATION_OR_VETO

RULE_PROMOTION: NONE
PORTFOLIO_ACTION: NONE
```

## 1. Frozen-universe breadth truth layer

The program recovered 184 weekly CoinMarketCap historical snapshots from 2023-01-01 through 2026-07-05. For each date, the ranked universe was frozen at that date before excluding BTC, ETH, exact stablecoins, wrapped/LST assets and fixed-NAV commodity proxies. The top 100 remaining assets form the point-in-time universe.

```text
snapshots_expected: 184
snapshots_passed: 184
raw_ranked_assets_per_snapshot: 200
frozen_eligible_assets_per_snapshot: 100
frozen_universe_rows: 18,400
daily_breadth: DATA_MISSING
historical_30DMA_breadth: DATA_MISSING
```

Weekly breadth is not daily breadth. Four-week snapshot comparisons are not a fabricated daily 30-day moving-average series.

## 2. Survivorship-bias finding

Only 45% of the first 2023 universe overlapped with the latest 2026 universe. Median overlap with the latest universe was 62%, and median one-week Jaccard turnover was 5.83%.

Using the latest constituents retrospectively produced sign-changing distortion:

```text
mean_positive_7d_bias_pp: -0.17
p05_positive_7d_bias_pp: -4.99
p95_positive_7d_bias_pp: +4.64
max_absolute_positive_7d_bias_pp: 14.31
```

The small average is cancellation, not safety. Current constituents are invalid historical breadth truth.

## 3. Marginal predictive value

Adding the full frozen-breadth family to the price baseline worsened forward ETH/BTC magnitude prediction:

| Horizon | Median MAE deterioration | 95% moving-block interval |
|---:|---:|---:|
| 7d | +0.84 percentage point | +0.36 to +1.33 |
| 14d | +1.08 percentage points | +0.29 to +1.95 |
| 28d | +3.74 percentage points | +2.19 to +5.18 |

Across top-20, top-50 and top-100 universes, four predeclared feature families and three horizons, none of 36 magnitude tests produced robust improvement. No universe/feature variant produced robust Brier or decision-accuracy improvement.

Breadth therefore fails as an entry permission, hard gatekeeper or standalone rotation predictor in this sample.

## 4. Breadth is descriptive state information

Breadth was meaningfully related to contemporaneous participation:

```text
positive_7d_breadth vs contemporaneous_ETHBTC_7d: Spearman +0.378
positive_28d_breadth vs contemporaneous_ETHBTC_28d: Spearman +0.401
```

Forward correlations were near zero. The predeclared saturated state, at least 80% positive over seven days, had contemporaneous ETH/BTC median +1.83% but subsequent medians of -1.61%, -3.62% and -5.61% at 7, 14 and 28 days.

This does not authorize a contrarian rule. It supports only the narrower statement that very high breadth can be a late-state or exhaustion observation rather than early permission.

## 5. Rotation episodes

The one resolved real M4 rotation episode began with 94% positive breadth, while one fake episode began with 87%. Among five resolved episodes, an initial breadth print of at least 80% had 100% recall and 50% precision, with only one real event.

```text
M4_REAL_EPISODES: 1
BREADTH_GATE_GENERALIZATION: NOT_SUPPORTED
```

## 6. BTC.D and stablecoin marginal value

BTC.D remained negative as a predictive feature. At 30 days, adding BTC.D worsened MAE by approximately 0.63 percentage point with a positive block-bootstrap interval. Its retained job is survival/reclaim and post-stress context.

Stablecoin information showed a small 7–14 day point-estimate improvement, strongest near 14 days, but its interval crossed zero and the prior latency/regime audit remains binding. It keeps zero standalone authority.

The four predeclared availability/activity states did not behave as reliable risk-on signals. `SUPPLY_GROWTH_WITHOUT_ACTIVITY` was least negative, not bullish. Activity may describe churn, intensity or late transmission.

## 7. TRIAD sequence and latency

The event topology did not support one deterministic A→C→D sequence. Severe events appeared under multiple paths, including no prior signal, A only, A→C and A→C→D.

The durable role separation remains:

```text
A1/A2: URGENCY_ONLY
A3: QUARANTINE_ZERO_EXECUTION_WEIGHT
C1/C2: LEAN_WARNING
D: CONFIRMATION_OR_VETO
```

C remains the warning family worth expanded prospective evidence, but usable lead decays rapidly:

| Added operational delay | Events with non-negative usable lead |
|---:|---:|
| 0d | 88.9% |
| 1d | 44.4% |
| 2d | 44.4% |
| 3d | 33.3% |

C2 must be logged event-driven or daily with source, operational-availability and framework-acceptance timestamps. This is instrumentation, not authority promotion.

## 8. Active-test consequence

The prior blocker label `HISTORICAL_BREADTH_MISSING` is obsolete.

```text
HISTORICAL_WEEKLY_FROZEN_BREADTH: AVAILABLE
DAILY_HISTORICAL_BREADTH: DATA_MISSING
HISTORICAL_30DMA_BREADTH: DATA_MISSING
BREADTH_PREDICTIVE_GATE: NOT_SUPPORTED
BREADTH_ROLE: DESCRIPTIVE_CONFIRMATION_ZERO_WEIGHT
```

T3 and T6 are no longer blocked by absence of all historical breadth. They remain forward-only and not promotion-ready because historical gatekeeper value was negative, prospective breadth-complete decision rows are insufficient, and M4 has only one resolved real episode.

## 9. Final decision matrix

```text
PRICE_STRUCTURE: RETAIN_CONFIRMATION_BASELINE
C2: EXPAND_PROSPECTIVE_ROWS_NO_AUTHORITY_INCREASE
A3: QUARANTINE_ZERO_WEIGHT
D: CONFIRMATION_OR_VETO
BTC.D: SHADOW_SURVIVAL_RECLAIM_CONTEXT
STABLECOIN_SUPPLY: LIQUIDITY_AVAILABILITY_CONTEXT
NORMALIZED_DEX_ACTIVITY: ONE_ACTIVITY_CONTEXT_AXIS
FROZEN_BREADTH: DESCRIPTIVE_PARTICIPATION_CONFIRMATION_ZERO_WEIGHT
LEGACY_ALT_PHASE_LABEL: REJECT_AS_BREADTH_SUBSTITUTE
```

## Evidence and authority boundary

The program is retrospective canonical research evidence. It modifies evidence classifications, blocker labels and forward instrumentation. It creates no market call, portfolio action, live threshold, new engine, new score, automatic rule promotion or prospective evidence row.

```text
RETROSPECTIVE_ROWS_PROMOTED: 0
PROSPECTIVE_ROWS_APPENDED: 0
ROW_VALIDITY: NOT_APPLICABLE_NO_NEW_ROW
COVERAGE_READINESS: FORWARD_ROWS_INSUFFICIENT
EDGE_OR_PROMOTION_STATUS: NO_CHANGE
```

## Machine-readable archive

Primary root:

```text
06_RESEARCH_LAB/audit_summaries/marginal_decision_breadth_v1/
```

The complete external research package and raw breadth artifact are identified by their SHA-256 values above. The repository stores the durable machine-readable outputs, source validation, reproducibility bundle and exact execution receipts needed for later agents to recover and rerun the work.
