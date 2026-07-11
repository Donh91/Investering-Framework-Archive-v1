# TechDev Claim and Revision Ledger

**Dato:** 2026-07-11  
**Status:** OPERATIONAL_APPEND_ONLY / HISTORICAL_BATCH_2_IMPORTED / CONTINUATION_OPEN  
**Område:** TechDev roadmap / timing / range / trade calibration  
**Primary folder:** `06_RESEARCH_LAB/forward_tests/`  
**Related folders:** `08_SOURCE_MATERIAL/techdev/`, `04_MARKET_LEARNING/macro_shadow/`, `01_CORE_FRAMEWORK/governance/`  
**Depends on:** Active Test Registry; TechDev macro-compass governance

---

## Purpose

TechDev remains a macro compass and roadmap input, not an execution motor.

This ledger separates:

```text
ROADMAP_ACCURACY
TIMING_ACCURACY
RANGE_ACCURACY
TRADE_ACCURACY
FRAMEWORK_ACTION_IMPACT
```

These categories must never be blended into one score.

---

## Current status

```yaml
source_scope:
  historical_paid_archive_batch_1: 2021-11-04_TO_2025-10-13
  historical_paid_archive_batch_2: 2022-03-06_TO_2025-02-09
  later_issue_sequence: ISSUES_81_TO_95
  topping_signal_sequence: UPDATES_1_2_3_4_6_7_8
unique_source_documents_accounted_for: 141
exact_duplicate_upload_copies_ignored: 72
source_backed_claim_rows: 186
historical_topping_signal_snapshot_rows: 7
valid_source_rows: 186_UNSCORED
valid_outcome_rows: 0
scored_rows: 0
source_import_status: BATCH_2_COMPLETE_CONTINUATION_OPEN
scoring_status: BLOCKED_PENDING_VERIFIED_ACTUALS_AND_FROZEN_OUTCOME_METHOD
```

Batch 2 accounting:

```yaml
uploaded_files_in_batch: 98
new_unique_source_documents: 47
duplicate_upload_copies_ignored: 51
new_source_backed_claim_rows: 66
```

Primary source-backed extractions:

```text
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-historical-claims-and-revisions-2021-2025__source-backed-extraction-v0-3.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-historical-claims-and-revisions-batch-2__source-backed-extraction-v0-4.md
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-81-95__source-backed-extraction-v0-1.md
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-87-88-90__source-backed-addendum-v0-2.md
```

Source manifests:

```text
08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-paid-archive-batch-1__source-manifest.md
08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-paid-archive-batch-2__source-manifest.md
08_SOURCE_MATERIAL/techdev/2026-07-10__techdev-issues-81-95__source-manifest.md
08_SOURCE_MATERIAL/techdev/2026-07-10__techdev-topping-signals-updates-1-8__source-manifest.md
```

Historical calibration:

```text
04_MARKET_LEARNING/macro_shadow/2026-07-11__techdev-historical-revision-and-governance-patterns__calibration-note.md
04_MARKET_LEARNING/macro_shadow/2026-07-11__techdev-historical-revision-patterns-batch-2__calibration-note.md
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-topping-signals-updates-1-8__historical-extraction-v0-1.md
```

Continuation control:

```text
00_ARCHIVE_CONTROL/2026-07-11__techdev-historical-archive-continuation-handoff-batch-2.md
```

Issue #90 directly anchors the original BITI and ETHD setups. Later issues preserve outcome and re-entry reports without replacing the original setup.

---

## Required claim row

```yaml
claim_id:
issue_number_or_source_id:
issue_date:
source_path:
source_status:
asset:
claim_type:
  ROADMAP
  TIMING_WINDOW
  PRICE_RANGE
  TRADE
  TRADE_POLICY
  SECTOR
  MODEL_DEFINITION
  INVALIDATION
  REVISION
original_claim_verbatim_or_precise_paraphrase:
target_low:
target_high:
time_window_start:
time_window_end:
invalidation:
position_or_trade_if_any:
framework_action_impact_at_time:
revision_ids:
revision_type:
  PARAMETER_UPDATE
  TIMING_UPDATE
  MODEL_REPLACEMENT
  INVALIDATION_RECLASSIFICATION
  THESIS_REVERSAL
model_family:
analogy_family:
time_dilation_assumption:
original_invalidation:
later_invalidation_change:
confidence_language_raw:
correlated_confluence_family:
audit_flags:
  INVALIDATION_DRIFT_FLAG
  ANALOG_FLEXIBILITY_FLAG
  CORRELATED_CONFLUENCE_FLAG
  UNVERIFIED_BACKTEST_CLAIM
final_outcome:
timing_error_days:
range_error_pct:
trade_return_pct:
roadmap_result:
  SUPPORTED
  PARTIAL
  NOT_SUPPORTED
  NOT_EVALUABLE
scoring_eligibility:
notes:
```

The additional historical fields are ledger metadata and lineage controls, not new engines.

---

## Revision rule

Original claims and later revisions must remain side by side.

```text
SILENT_REPLACEMENT_OF_ORIGINAL_CLAIM: FORBIDDEN
LATEST_REVISION_ERASES_PRIOR_ERROR: NO
TIME_WINDOW_EXTENSION_WITHOUT_NEW_ROW: FORBIDDEN
MODEL_REPLACEMENT_SCORES_AS_ORIGINAL_MODEL: NO
DISCRETIONARY_OVERRIDE_SCORES_AS_MECHANICAL_SIGNAL: NO
AUTHOR_REPORTED_BACKTEST_COUNTS_AS_VERIFIED_OUTCOME: NO
```

A revised target may be useful, but it does not retroactively improve the original claim.

---

## Historical governance flags

```text
INVALIDATION_DRIFT_FLAG:
  use when an original failure condition is later weakened, reframed or removed.

ANALOG_FLEXIBILITY_FLAG:
  use when the comparison family or mapped cycle position changes while the directional thesis survives.

CORRELATED_CONFLUENCE_FLAG:
  use when multiple indicators may describe the same underlying factor and should not be counted as independent confirmations.

UNVERIFIED_BACKTEST_CLAIM:
  use when a source reports backtest performance that has not been independently reproduced from frozen data and rules.
```

Flags are descriptive metadata. They do not score a claim by themselves.

---

## Source-status rule

```text
SOURCE_BACKED_CLAIM:
  may_be_imported: YES
  may_be_scored_without_actuals: NO

LATER_ISSUE_DESCRIPTION_OF_ORIGINAL:
  may_be_preserved: YES
  may_replace_original_source: NO
  scoring_status: BLOCKED_FOR_ORIGINAL_CLAIM_ACCURACY

MISSING_SEQUENCE_ISSUE:
  may_be_reconstructed: NO
  continuation_status: SOURCE_NEEDED
```

---

## Weighting rule

```yaml
macro_readiness_weight: MEDIUM_HIGH
exact_timing_weight: MEDIUM_LOW_UNTIL_SCORED
standalone_execution_weight: ZERO
rotation_authority: SHADOW_ONLY
sector_selection: WATCHLIST_INPUT
```

Historical source ingestion does not change live gates, current state, rebuy locks or portfolio action.

---

## Historical boundaries

The paid archive and the 2024 Topping Signals sequence are preserved as historical calibration, not active doctrine.

```text
MECHANICAL_SIGNAL_STATUS and ANALYST_OVERRIDE must remain separate.
A discretionary trigger call may not be represented as a threshold hit.
A later downgrade may not erase an earlier call.
A new analogy may not count as validation of an older analogy.
A later model may not repair an earlier timing or target score.
No framework weight change before a separate outcome pass.
Confirmation quality and action timeliness must be scored separately.
Correlated confluence must be grouped by sensor family.
```

---

## Batch 2 revision chains

```text
SPRING_2022:
  reaccumulation and early-impulse claims
  → repeated support failures
  → 35K reassessment gates
  → 30Ks-bottom error acknowledgement after LUNA
  → strategy redesign and lower invalidation

MECHANICAL_SYSTEM:
  pure hold and one exit
  → 60 percent hold / 40 percent swing
  → 2D RSI+MACD system
  → immediate rule repairs
  → Transition Buy exit flaw
  → 50 percent take profit at plus 15 percent
  → later discretionary overrides

MACRO_MODEL:
  halving and cycle symmetry
  → Elliott-wave degree and 3x time dilation
  → log-log parabola and non-USD denominators
  → cross-market confluence
  → CN10Y/DXY global-liquidity cycle

TARGET_METHOD:
  price-only Fibonacci targets
  → market-cap-aware targets where supply inflation matters
  → relative-strength classification where young charts are ambiguous
```

---

## Weekly summary

```yaml
unique_source_documents_accounted_for: 141
historical_batch_1_documents: 72
historical_batch_2_documents: 47
later_issue_81_95_documents: 15
topping_signal_documents: 7
source_backed_claim_rows: 186
historical_signal_snapshot_rows: 7
roadmap_rows_scored: 0
timing_rows_scored: 0
range_rows_scored: 0
trade_rows_scored: 0
revisions_logged: SOURCE_CHAINS_FROZEN_THROUGH_BATCH_2
framework_actions_influenced: NOT_BACKFILLED
calibration_change_recommended: GOVERNANCE_HYGIENE_ONLY_NO_LIVE_WEIGHT_CHANGE
```

## Next review

1. Continue source ingestion from the Batch 2 handoff without rewriting prior batches.
2. Import missing chronological issues when supplied; do not infer them.
3. Freeze verified actual-data and category-specific outcome methodology before scoring.
4. Score roadmap, timing, range, trades and framework impact separately.
5. Group correlated confluence by sensor family.
6. Preserve original confidence language, invalidations and model family.
7. Import Topping Signals Update #5 if supplied.
8. Independently reproduce any mechanical backtest before treating it as evidence.
9. Do not alter TechDev's framework weight from source extraction alone.