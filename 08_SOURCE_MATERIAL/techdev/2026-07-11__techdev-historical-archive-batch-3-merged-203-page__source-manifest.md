# TechDev Historical Archive Batch 3 - Merged 203-Page Source Manifest

**Import date:** 2026-07-11  
**Status:** SOURCE_MANIFEST / BATCH_3_COMPLETE / ANALYSIS_READY  
**Scope:** User-supplied merged TechDev archive containing 203 one-page article artifacts  
**Prior handoff:** `00_ARCHIVE_CONTROL/2026-07-11__techdev-historical-archive-continuation-handoff-batch-2.md`

## Source and split rule

- The merged PDF is a transport container, not one analytical article.
- All 203 pages were split into one-page PDFs and matching UTF-8 text files.
- Every page received a stable source ID, split-PDF SHA-256 and normalized-text SHA-256.
- Exact duplicates and re-sends are aliases only and do not count as corroboration.
- Merging and recompression change standalone PDF bytes, so prior dedupe uses article identity plus normalized text, not the new split-PDF hash alone.
- GitHub stores lineage, hashes, metadata, claims and revision relationships, not the paid binary archive.
- No outcomes were scored and no live framework state was changed.

## Batch accounting

```yaml
merged_pages: 203
unique_normalized_page_contents: 202
prior_manifested_pages_present: 128
new_unique_source_artifacts_imported: 72
source_identity_repairs: 1
exact_duplicate_aliases: 1
republication_aliases: 1
prior_unique_sources_accounted_for: 141
cumulative_unique_source_artifacts_accounted_for: 213
new_source_backed_claim_rows: 71
cumulative_source_backed_claim_rows: 257
valid_outcome_rows: 0
scored_rows: 0
```

## Coverage consequences

```yaml
full_issues: COMPLETE_1_TO_60
market_update: COMPLETE_1_TO_95_ACROSS_BATCHES
topping_signals: COMPLETE_1_TO_8
top_gauge_present: [1,2,3,4,5,6,7,8,9,10,11,12,14,17,20,22,23,24,25,26,27]
top_gauge_remaining_gaps: [13,15,16,18,19,21]
```

## Registry files

```text
08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-archive-batch-3-new-source-registry.tsv
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-historical-claims-batch-3__source-backed-extraction-v0-5.md
04_MARKET_LEARNING/macro_shadow/2026-07-11__techdev-complete-archive-coverage-and-analysis-readiness__calibration-note.md
```

## Alias and repair notes

- Merged page 1 identifies the prior generic `TechDev Newsletter Substack.pdf` artifact as Top Gauge Issue #5. This repairs identity without increasing the unique-source count.
- Merged pages 54 and 72 are exact normalized-text duplicates. Page 72 is an alias only.
- Merged page 143 is a re-send of page 23 with minor wrapper differences. It remains a republication alias and does not add independent evidence.
- The full 203-row registry, split PDFs, extracted text and machine-readable corpus are preserved in the generated Batch 3 archive package.