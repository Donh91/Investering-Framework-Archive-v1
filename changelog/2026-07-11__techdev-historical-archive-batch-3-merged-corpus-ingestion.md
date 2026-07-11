# Changelog - TechDev Historical Archive Batch 3 Merged Corpus Ingestion

**Date:** 2026-07-11  
**Status:** COMPLETED_SOURCE_SPLIT_ARCHIVE_SYNC_AND_CLAIM_INDEX

## Input

The user supplied one merged, compressed 203-page PDF containing one TechDev article per page.

```yaml
container_sha256: 68f52fef31bb52a1a2d48cf9c17de65f63bcee080eef23326a8e9eaf539c2ea7
pages: 203
```

## Actions completed

1. Parsed all 203 article pages.
2. Split the container into 203 standalone one-page PDFs.
3. Extracted one text record per article.
4. Calculated SHA-256 for the container, every standalone PDF and every normalized text body.
5. Compared source identities against all prior TechDev manifests.
6. Classified prior identities, identity repairs, exact aliases, resend aliases and new unique sources.
7. Created and reconciled the frozen Batch 3 source manifest and four page-level hash indexes.
8. Imported the missing Topping Signals Update #5 snapshot without outcome scoring.
9. Appended 71 source-backed, unscored claim-navigation rows, TDH_187 through TDH_257.
10. Created analysis-readiness and continuation-handoff controls.
11. Synced Claim Ledger, Active Test Registry, Archive Candidate Queue and CANONICAL_INDEX through append-only addenda.
12. Produced a complete local archive package with split PDFs, extracted text, CSV and JSONL manifests, duplicate reports and a machine-readable corpus.

## Result

```yaml
batch_3_article_pages: 203
unique_normalized_page_contents: 202
new_unique_sources: 72
prior_archive_identity_duplicates: 128
source_identity_repairs: 1
intra_batch_exact_duplicate_aliases: 1
prior_archive_resend_aliases: 1
cumulative_unique_sources: 213
new_source_backed_claim_rows: 71
source_backed_claim_rows: 257
historical_topping_signal_snapshots: 8
outcome_rows: 0
scored_rows: 0
```

## Dedupe reconciliation

Top Gauge Issue #5 was found on merged page 1. It identifies the previously imported generic `TechDev Newsletter Substack.pdf` source, so it repairs that source identity rather than increasing the unique-source count. Merged pages 54 and 72 are exact duplicates, and page 143 is a re-send of page 23.

## Coverage result

```text
Full Issues #1-#60: COMPLETE
Market Updates #1-#95: COMPLETE
Topping Signals #1-#8: COMPLETE
Top Gauge absent from complete user export: #13, #15, #16, #18, #19, #21
```

## Verification

Every split PDF was verified as one page, with matching source-page dimensions and matching normalized extracted text. Representative pages from the beginning, middle and end of the corpus were rendered for visual inspection.

## Governance boundary

No outcomes were scored. No historical claim was retroactively repaired. No current market state, gate, lock, TechDev weighting or portfolio action was changed. Complete category-specific performance analysis remains blocked until the scoring protocol and independently verified actual-data conventions are frozen.