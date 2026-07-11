# TechDev Complete Corpus Claim and Revision Ledger v1

**Date:** 2026-07-11  
**Status:** SOURCE_BACKED / APPEND_ONLY / COMPLETE_AVAILABLE_CORPUS  
**Authority:** Historical research and calibration only  
**Outcome authority:** Separate Wave 1 outcome file under the frozen scoring protocol

## Purpose

This file is the consolidated navigation and governance layer for the complete available TechDev corpus. It does not replace the source manifests or the 257 source-backed claim rows. It binds them into one audit-ready ledger and preserves original claims and later revisions side by side.

## Corpus accounting

```yaml
unique_source_documents_accounted_for: 213
source_backed_claim_rows: 257
historical_topping_signal_snapshots: 8
full_issues_1_60: COMPLETE
market_updates_1_95: COMPLETE
topping_signals_1_8: COMPLETE
top_gauge_export_absences: [13, 15, 16, 18, 19, 21]
outcome_rows_before_wave_1: 0
```

The six Top Gauge absences are explicit source gaps. They are not reconstructed and are not treated as proof that the issues were never published.

## Authoritative row chain

```text
TDH_001-TDH_048
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-historical-claims-and-revisions-2021-2025__source-backed-extraction-v0-3.md

TDH_049-TDH_114
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-historical-claims-and-revisions-batch-2__source-backed-extraction-v0-4.md

Issue #81-#95 rows and addendum
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-81-95__source-backed-extraction-v0-1.md
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-87-88-90__source-backed-addendum-v0-2.md

TDH_187-TDH_257
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-historical-claims-batch-3__source-backed-extraction-v0-5.md
```

The numbering gap between earlier extractions and TDH_187 reflects the already imported later-issue rows. No IDs are reused.

## Claim classes

Each decision-relevant claim remains in one primary class:

```text
ROADMAP
TIMING_WINDOW
PRICE_TARGET_OR_RANGE
ROTATION
TOPPING_SIGNAL
TRADE
TRADE_POLICY
MODEL_DEFINITION
INVALIDATION
REVISION
SECTOR_OR_ASSET_SELECTION
FRAMEWORK_ACTION_IMPACT
```

Roadmap, timing, range, trade and framework-action impact are never blended into a single score.

## Major revision episodes

| Episode | Original position | Later revision | Ledger treatment |
|---|---|---|---|
| 2021-2022 final impulse | 233K and late-2021 or early-2022 top, then 140-230K | 180K alternate map, then 170-230K around September 2022 | Original windows remain scored separately. Later targets do not repair earlier misses. |
| 2022 bottoming | 29-35K highest-probability bottom | 15-20K bottom region after deeper decline, FTX framed as possible final spring | Both ranges remain. First range is not relabeled as the final bottom. |
| Cycle model | Four-year and prior-cycle analogs | Elliott-wave degree, 3x time dilation, cross-market denominators, liquidity and business cycle | Model changes are separate revision rows, not evidence that the prior model succeeded. |
| Swing system | Long-term hold and macro exit | 60/40 portfolio, RSI/MACD system, rule corrections, profit-taking patch and discretionary overrides | Author-reported backtests remain unverified. Mechanical and discretionary outcomes remain separate. |
| Alt rotation | BTC.D decline and ETH/BTC reversal expected to unlock alt outperformance | Repeated timing extensions, new confirmation lines and new cycle analogs | Directional thesis and timing quality are scored separately. |
| 2024 topping signals | Top Gauge possibly triggered, then called triggered | Later classified uncertain if the dividing line held | Provisional, mechanical and discretionary states remain distinct. |
| 2025 targets | 160-180K in Q1/Q2, then Aug/Sep, then 180-200K in 2025 and about 300K in 2026 | Trunk-up recalibration and a slower business-cycle timeline | Expired 2025 windows remain scored. Open 2026 windows remain open until maturity. |
| 2026 final correction | One final leg toward 52-57K with BITI and ETHD setups | Later issues report outcomes and re-entry changes | Original entries, stops and targets remain the scoring anchors. |

## Binding lineage rules

```text
SILENT_REPLACEMENT_OF_ORIGINAL_CLAIM: FORBIDDEN
REVISION_RETROACTIVELY_REPAIRS_ORIGINAL: NO
WINDOW_EXTENSION_WITHOUT_NEW_ROW: FORBIDDEN
MODEL_REPLACEMENT_SCORES_AS_ORIGINAL_MODEL: NO
SOURCE_ROW_EQUALS_OUTCOME_ROW: NO
AUTHOR_REPORTED_BACKTEST_EQUALS_VERIFIED_RESULT: NO
MECHANICAL_SIGNAL_EQUALS_ANALYST_OVERRIDE: NO
```

## Completion assessment

The complete available source corpus is sufficiently organized for category-specific historical analysis. The ledger is complete as an audit and navigation layer for decision-relevant claims. It is not an assertion that every sentence, every minor alt target or every intraday branch has been promoted into a separate row.

Exhaustive project-specific altcoin scoring remains a separate lower-priority lane because it requires verified historical prices, supply-adjusted market-cap conventions and token redenomination handling for each asset.
