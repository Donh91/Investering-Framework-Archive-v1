# Changelog - TechDev Historical Archive Batch 3 Merged Corpus Ingestion

**Date:** 2026-07-11  
**Status:** COMPLETED_SOURCE_SPLIT_AND_ARCHIVE_SYNC

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
6. Classified prior identities, aliases, resend aliases and new unique sources.
7. Created a frozen Batch 3 source manifest and four page-level hash indexes.
8. Imported the missing Topping Signals Update #5 snapshot without outcome scoring.
9. Created analysis-readiness and continuation-handoff controls.
10. Synced Claim Ledger, Active Test Registry, Archive Candidate Queue and CANONICAL_INDEX through append-only addenda.

## Result

```yaml
batch_3_article_pages: 203
new_unique_sources: 73
prior_archive_identity_duplicates: 128
intra_batch_duplicate_aliases: 1
prior_archive_resend_aliases: 1
cumulative_unique_sources: 214
source_backed_claim_rows: 186_EXISTING
historical_topping_signal_snapshots: 8
outcome_rows: 0
scored_rows: 0
```

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

No outcomes were scored. No historical claim was retroactively repaired. No current market state, gate, lock, TechDev weighting or portfolio action was changed. The next research phase is append-only claim and revision extraction for the 73 new unique sources.