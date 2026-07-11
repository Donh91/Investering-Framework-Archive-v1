# TechDev Claim and Revision Ledger - Batch 3 Corpus Sync Addendum

**Date:** 2026-07-11  
**Status:** OPERATIONAL_APPEND_ONLY / BATCH_3_SOURCE_AND_CLAIM_INDEX_COMPLETE  
**Parent ledger:** `06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claim-ledger__operational.md`

## Current source accounting

```yaml
unique_source_documents_accounted_for: 213
batch_3_merged_article_pages: 203
batch_3_unique_normalized_page_contents: 202
batch_3_new_unique_sources: 72
batch_3_prior_archive_identity_duplicates: 128
batch_3_source_identity_repairs: 1
batch_3_intra_batch_exact_duplicate_aliases: 1
batch_3_prior_resend_aliases: 1
exact_binary_duplicate_copies_ignored_before_batch_3: 72
new_batch_3_source_backed_claim_rows: 71
source_backed_claim_rows: 257
historical_topping_signal_snapshot_rows: 8
valid_outcome_rows: 0
scored_rows: 0
source_import_status: BATCH_3_COMPLETE
batch_3_claim_extraction_status: FIRST_PASS_APPEND_COMPLETE_TDH_187_TO_TDH_257
scoring_status: BLOCKED_PENDING_VERIFIED_ACTUALS_AND_FROZEN_OUTCOME_METHOD
```

## New source anchors

```text
08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-archive-batch-3-merged-corpus__source-manifest.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-complete-corpus-analysis-readiness-batch-3__operational.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-historical-claims-batch-3__source-backed-extraction-v0-5.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-topping-signals-update-5__historical-extraction-addendum.md
```

## Dedupe correction

Top Gauge Issue #5 is an identity repair for the previously imported generic `TechDev Newsletter Substack.pdf` source. It is not a new unique source. The final Batch 3 new-source count is 72 and the cumulative source count is 213.

## Ledger boundary

The 72 newly imported source documents do not imply 72 claim rows. The non-analytical delay notice on merged page 95 is preserved in the source manifest but does not create a claim row. Batch 3 adds 71 decision-relevant source-backed navigation rows.

```text
SOURCE_DOCUMENT_COUNT_IS_NOT_CLAIM_ROW_COUNT
SOURCE_ROW_IS_NOT_OUTCOME_ROW
REVISED_CLAIM_DOES_NOT_REPAIR_ORIGINAL_CLAIM
AUTHOR_REPORTED_BACKTEST_IS_NOT_VERIFIED_PERFORMANCE
HISTORICAL_IMPORT_CHANGES_LIVE_WEIGHT: NO
```

## Next ledger action

Use the complete corpus for deeper chronological revision-chain extraction and, only after a separate scoring-method freeze, attach verified actuals and score roadmap, timing, range, trade and action impact separately. Do not rewrite the 257 source-backed rows.