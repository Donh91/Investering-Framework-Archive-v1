# Active Test Registry - TechDev Batch 3 Sync Addendum

**Date:** 2026-07-11  
**Status:** CANONICAL_ADDENDUM  
**Parent registry:** `06_RESEARCH_LAB/forward_tests/2026-07-10__active-test-registry__canonical.md`

## T7 replacement state

```yaml
test_id: TECHDEV_CLAIM_LEDGER
status: ACTIVE_SOURCE_CORPUS_COMPLETE_BATCH_3_CLAIM_EXTRACTION_PENDING
question: How accurate are TechDev roadmap, timing, range and trade claims when scored separately?
source_scope:
  historical_paid_archive_batches: [BATCH_1, BATCH_2, BATCH_3_MERGED_CORPUS]
  full_issues: 1_TO_60_COMPLETE
  market_updates: 1_TO_95_COMPLETE
  topping_signals: 1_TO_8_COMPLETE
  top_gauge_export_absences: [13,15,16,18,19,21]
source_documents_accounted_for: 214
batch_3_new_unique_sources: 73
rows_total: 186_SOURCE_BACKED_CLAIM_ROWS_PLUS_8_HISTORICAL_SIGNAL_SNAPSHOTS
valid_source_rows: 186_EXISTING_UNSCORED
valid_outcome_rows: 0
scored_rows: 0
benchmark: CATEGORY_SPECIFIC_SIMPLE_TIME_RANGE_AND_ACTION_BASELINES
blocked_by:
  - BATCH_3_CLAIM_EXTRACTION_NOT_YET_APPENDED
  - VERIFIED_ACTUALS_METHOD_NOT_FROZEN
  - CATEGORY_SCORING_METHOD_NOT_FROZEN
next_review: AFTER_BATCH_3_CLAIM_EXTRACTION_OR_SCORING_PROTOCOL_FREEZE
promotion_condition: Enough original-source rows and verified outcomes for category-specific calibration
kill_condition: None for archive continuity; reduce framework weight if calibrated results are poor
owner: RESEARCH_LAB
source_manifest: 08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-archive-batch-3-merged-corpus__source-manifest.md
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
```