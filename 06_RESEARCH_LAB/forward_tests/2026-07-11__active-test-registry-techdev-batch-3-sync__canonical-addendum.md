# Active Test Registry - TechDev Batch 3 Sync Addendum

**Date:** 2026-07-11  
**Status:** CANONICAL_ADDENDUM / BATCH_3_COMPLETE  
**Parent registry:** `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`

## T7 replacement state

```yaml
test_id: TECHDEV_CLAIM_LEDGER
status: ACTIVE_SOURCE_CORPUS_AND_BATCH_3_CLAIM_INDEX_COMPLETE
question: How accurate are TechDev roadmap, timing, range and trade claims when scored separately?
source_scope:
  historical_paid_archive_batches: [BATCH_1, BATCH_2, BATCH_3_MERGED_CORPUS]
  full_issues: 1_TO_60_COMPLETE
  market_updates: 1_TO_95_COMPLETE
  topping_signals: 1_TO_8_COMPLETE
  top_gauge_export_absences: [13,15,16,18,19,21]
source_documents_accounted_for: 213
batch_3_new_unique_sources: 72
batch_3_source_identity_repairs: 1
rows_total: 257_SOURCE_BACKED_CLAIM_ROWS_PLUS_8_HISTORICAL_SIGNAL_SNAPSHOTS
valid_source_rows: 257_UNSCORED
valid_outcome_rows: 0
scored_rows: 0
benchmark: CATEGORY_SPECIFIC_SIMPLE_TIME_RANGE_AND_ACTION_BASELINES
blocked_by:
  - VERIFIED_ACTUALS_METHOD_NOT_FROZEN
  - CATEGORY_SCORING_METHOD_NOT_FROZEN
next_review: SCORING_PROTOCOL_FREEZE_OR_NEW_SOURCE_BATCH
promotion_condition: Enough original-source rows and verified outcomes for category-specific calibration
kill_condition: None for archive continuity; reduce framework weight if calibrated results are poor
owner: RESEARCH_LAB
source_manifest: 08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-archive-batch-3-merged-corpus__source-manifest.md
batch_3_claim_index: 06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-historical-claims-batch-3__source-backed-extraction-v0-5.md
continuation_handoff: 00_ARCHIVE_CONTROL/2026-07-11__techdev-historical-archive-continuation-handoff-batch-3.md
```

## T7 rules retained

```text
Roadmap, timing, range, trade and framework-action impact remain separate.
Original claims and later revisions remain side by side.
Historical source ingestion does not change live gates or portfolio action.
Invalidation drift, analogy flexibility and correlated confluence remain metadata, not scores.
Author-reported backtests remain unverified until independently reproduced.
Mechanical signals and discretionary overrides remain separate.
Source completeness does not imply outcome evidence.
Top Gauge Issue #5 is a source-identity repair, not a new unique document.
```