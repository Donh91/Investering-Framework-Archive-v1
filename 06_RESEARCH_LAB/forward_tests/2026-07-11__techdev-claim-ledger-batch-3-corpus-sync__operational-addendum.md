# TechDev Claim and Revision Ledger - Batch 3 Corpus Sync Addendum

**Date:** 2026-07-11  
**Status:** OPERATIONAL_APPEND_ONLY / BATCH_3_SOURCE_CORPUS_IMPORTED / CLAIM_EXTRACTION_PENDING  
**Parent ledger:** `06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claim-ledger__operational.md`

## Current source accounting

```yaml
unique_source_documents_accounted_for: 214
batch_3_merged_article_pages: 203
batch_3_new_unique_sources: 73
batch_3_prior_archive_identity_duplicates: 128
batch_3_intra_batch_duplicate_aliases: 1
batch_3_prior_resend_aliases: 1
exact_binary_duplicate_copies_ignored_before_batch_3: 72
source_backed_claim_rows: 186_EXISTING
historical_topping_signal_snapshot_rows: 8
valid_outcome_rows: 0
scored_rows: 0
source_import_status: BATCH_3_SOURCE_SPLIT_COMPLETE
batch_3_claim_extraction_status: PENDING_APPEND_ONLY_PASS
scoring_status: BLOCKED_PENDING_VERIFIED_ACTUALS_AND_FROZEN_OUTCOME_METHOD
```

## New source anchors

```text
08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-archive-batch-3-merged-corpus__source-manifest.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-complete-corpus-analysis-readiness-batch-3__operational.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-topping-signals-update-5__historical-extraction-addendum.md
```

## Ledger boundary

The 73 newly imported source documents are not automatically 73 claim rows. Source-backed claim extraction must be decision-relevant, append-only and preserve the full chronology of original claims, revisions, invalidations and model changes.

```text
SOURCE_DOCUMENT_COUNT_IS_NOT_CLAIM_ROW_COUNT
SOURCE_ROW_IS_NOT_OUTCOME_ROW
REVISED_CLAIM_DOES_NOT_REPAIR_ORIGINAL_CLAIM
AUTHOR_REPORTED_BACKTEST_IS_NOT_VERIFIED_PERFORMANCE
HISTORICAL_IMPORT_CHANGES_LIVE_WEIGHT: NO
```

## Next ledger action

Create a Batch 3 extraction beginning after the current claim ID sequence. Cover roadmap, timing, ranges, trades, trade policy, model definitions, invalidations and revisions separately. Do not score until the historical outcome protocol is frozen.