# TechDev Category Outcome Calibration + BTC.D B1 Reconciliation v1

**Dato:** 2026-07-13  
**Status:** CANONICAL_RESEARCH_EVIDENCE  
**Område:** TechDev claim outcomes / revision cost / BTC.D reproducibility / research cooldown  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Depends on:** TechDev Claim and Revision Ledger; Batch 1-3 claim extractions; Full Sensor Backtest; Sensor Survival Audit; Marginal Decision Value & Breadth Truth Program  
**Research package SHA-256:** `f9d747c0b472a18b023ee07bf5dcf47e5a5a1156eb1ab1e6a6fed6f3f8369845`

## Pre-run health check

```yaml
health_status: READY_WITH_MASTER_MONDAY_ARCHIVE_LAG
active_data_ping: V4
latest_accepted_log_id: DATA_PING_V4_20260713T052547Z
latest_accepted_state: NEAR_PRESENT
latest_accepted_alert: TRIGGERED
latest_verified_week: 2026-W28
latest_verified_btc_range: 61306.84_TO_64700.00
latest_verified_eth_range: 1713.44_TO_1833.40
latest_durable_master_monday: 2026-W28_2026-07-06
master_monday_note: automation ran on 2026-07-13 but no newer durable GitHub pointer was found
recent_repairs_read:
  - daily sensor pair lab v0.1
  - automatic DATA PING thread handoff
  - accepted-log fallback
  - verified W28 range repair
new_engine_freeze: ACTIVE_THROUGH_2026-08-09
```

The Master Monday archive lag was treated as a missing durable source, not reconstructed from memory. The research proceeded from current canonical governance, latest accepted DATA PING V4 state and verified actuals.

## Scope and evidence boundary

```text
unique TechDev source documents: 213
source-backed claim rows in corpus: 257
historical topping snapshots: 8
high-decision-value anchor rows evaluated: 50
outcome-eligible anchor rows: 44
full-corpus exhaustive scoring claimed: NO
retrospective rows promoted as forward evidence: 0
```

This is a category-specific Phase I calibration of a pre-declared anchor cohort. It does not imply that all 257 source rows are scored. Vague, future, source-blocked or instrument-data-blocked claims remain `NOT_DUE`, `NOT_EVALUABLE` or `SOURCE_BLOCKED`.

## TechDev verdict

```text
TECHDEV_MACRO_COMPASS: RETAIN_CONTEXT
TECHDEV_EXACT_TIMING: WEAK_AND_REVISION_DEPENDENT
TECHDEV_LONG_RANGE_PRICE_TARGETS: NOT_SUPPORTED_IN_ANCHOR_COHORT
TECHDEV_NEAR_TERM_CONDITIONAL_GATES: MIXED_TO_USEFUL
TECHDEV_2026_FINAL_BOTTOM_REVISION: STRONGLY_SUPPORTED_PROVISIONALLY
TECHDEV_REVISION_VALUE: REAL
TECHDEV_REVISION_COST: MATERIAL
TECHDEV_STANDALONE_EXECUTION_AUTHORITY: ZERO
TECHDEV_ROTATION_AUTHORITY: SHADOW_ONLY
FRAMEWORK_WEIGHT_CHANGE: NONE_AUTOMATIC
```

### Category learning

- **Roadmap:** useful as broad scenario context when probabilistic; weak when converted to exact multi-year price paths.
- **Timing:** weakest recurring lane. Several windows were early or extended. Issue #95 is a strong recent exception.
- **Price range / price-and-time:** long-range targets underperformed; revised short-horizon termination zones were materially better.
- **Conditional gates:** several explicit downside or reclaim gates were decision-useful even when the surrounding narrative failed.
- **Trade:** independently blocked where Issue #90 or complete ETF series were missing. Later author-reported stop-outs remain source context, not verified performance.
- **Revision:** later revisions often improved the map, but may not repair original scores and must carry delay, adverse-move and invalidation-drift cost.
- **Framework action impact:** remains not evaluable because point-in-time framework actions influenced by each claim are not exhaustively backfilled.

## Revision-value bonus experiment

The bonus proposition was:

> TechDev may add more value through adaptive revision than through first-call precision.

Verdict:

```text
SUPPORTED_AS_GOVERNANCE_INTERPRETATION
NOT_A_PERFORMANCE_EDGE
```

Five anchor chains showed that later revisions improved the final map in four cases, but with material costs. The 2021-2022 cycle-top chain remained wrong despite repeated revisions. The 2022 bottom range became accurate only after the low. The 2025-2026 BTC and ETH chains improved substantially after missed relief targets and timing extensions. The April 2026 breakdown call was roughly four weeks early before later confirmation became useful.

Future TechDev reviews must therefore preserve two channels:

```text
FIRST_CALL_INFORMATION
REVISION_INFORMATION_AND_COST
```

A correct later revision may be useful, but it may not increase the original claim score.

## BTC.D B1 21-vs-22 reconciliation

The discrepancy is resolved:

```text
canonical B1 fire count: 22
extra valid date: 2025-03-04
root cause of 21-row simulation: evaluation frame was truncated at 2025-03-01 before five-day warm-up eligibility was applied
source conflict: NO
implementation artifact: YES
```

The 2025-03-04 condition used BTC.D from 2025-02-27, which existed before the signal. It contains no look-ahead. The correct implementation computes lagged features on available pre-window history and then filters the evaluation period.

At 10 days:

```text
21 fires: mean +2.050%, median +2.740%, negative rate 28.6%
22 fires: mean +1.786%, median +2.576%, negative rate 31.8%
```

The conclusion remains unchanged:

```text
B1_EARLY_WARNING_WEIGHT: 0
B1_MECHANICAL_TRIM_WEIGHT: 0
B1_SURVIVAL_RECLAIM_CONTEXT: RETAIN_SHADOW
```

## 4-8 week evidence-production period

```text
earliest major-audit review: 2026-08-10
hard-stop evidence review: 2026-09-07
new broad sensor engine: FORBIDDEN
large parameter sweep: FORBIDDEN
```

Existing owners continue to collect C2, Sensor Pair Lab, M3, Rotation Survival, Graduated Deployment, FRLP and TechDev claim/revision rows. A major decision-value audit may run after 2026-08-10 only if at least three independent event windows exist and at least two lanes have reached their existing governance-review threshold. Otherwise wait until 2026-09-07 and run an evidence-sufficiency review rather than forcing an edge conclusion.

## Machine-readable owners

```text
06_RESEARCH_LAB/audit_summaries/techdev_calibration_v1/TECHDEV_ANCHOR_CLAIM_OUTCOME_ROWS.csv
06_RESEARCH_LAB/audit_summaries/techdev_calibration_v1/TECHDEV_CATEGORY_OUTCOME_SUMMARY.csv
06_RESEARCH_LAB/audit_summaries/techdev_calibration_v1/TECHDEV_REVISION_VALUE_AND_COST.csv
06_RESEARCH_LAB/audit_summaries/techdev_calibration_v1/B1_21_VS_22_METRIC_COMPARISON.csv
06_RESEARCH_LAB/audit_summaries/techdev_calibration_v1/HEALTH_CHECK.json
```

No market call. No portfolio action. No rule promotion. No TechDev weight change from this research alone.
