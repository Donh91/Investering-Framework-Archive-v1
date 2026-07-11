# TechDev Historical Archive Batch 3 - Merged Corpus Source Manifest

**Import date:** 2026-07-11  
**Status:** SOURCE_MANIFEST / BATCH_3_SPLIT_COMPLETE / ANALYSIS_READY  
**Scope:** One merged and compressed 203-page PDF, with one TechDev article per page.

## Provenance and deduplication

```yaml
merged_container_sha256: 68f52fef31bb52a1a2d48cf9c17de65f63bcee080eef23326a8e9eaf539c2ea7
merged_pages_or_articles: 203
standalone_split_pdfs_created: 203
raw_text_records_created: 203
new_unique_source_documents_imported: 73
prior_archive_identity_duplicates: 128
intra_batch_duplicate_aliases: 1
prior_archive_resend_aliases: 1
cumulative_unique_source_documents_accounted_for: 214
outcome_scoring_performed: NO
```

The merged and recompressed container changes binary file structure, so its split-page PDF hashes are not directly comparable with hashes of prior standalone PDFs. SHA-256 was retained for the merged container, every split PDF and every normalized text body. Cross-batch deduplication therefore used source identity, issue/part, publication date, title and normalized extracted text. Duplicate sources were not counted as corroborating evidence.

The exact split-file and normalized-text hashes are preserved in four append-only page-index files:

```text
08_SOURCE_MATERIAL/techdev/batch_3_page_index/2026-07-11__techdev-batch-3-page-index-part-1-of-4.md
08_SOURCE_MATERIAL/techdev/batch_3_page_index/2026-07-11__techdev-batch-3-page-index-part-2-of-4.md
08_SOURCE_MATERIAL/techdev/batch_3_page_index/2026-07-11__techdev-batch-3-page-index-part-3-of-4.md
08_SOURCE_MATERIAL/techdev/batch_3_page_index/2026-07-11__techdev-batch-3-page-index-part-4-of-4.md
```

## Newly imported unique source coverage

```yaml
full_issues: [7, 10, 39]
top_gauge: [5]
topping_signals: [5]
market_updates:
  - 15-18
  - 19_PART_1
  - 19_PART_2
  - 20-21
  - 22_PART_1
  - 22_PART_2
  - 23_PART_1
  - 23_PART_2
  - 24_PART_1
  - 25_PART_1
  - 25_PART_2
  - 26_PART_1
  - 26_PART_2
  - 27_PART_1
  - 27_PART_2
  - 28_PART_1
  - 28_PART_2
  - 32_PART_1
  - 34_PART_1
  - 34_PART_2
  - 35_PART_1
  - 35_PART_2
  - 36-48
  - 50-63
  - 67
  - 69
  - 71
  - 74
  - 77-79
other_sources:
  - UPDATE_ON_MARKET_UPDATE_ISSUE_16
  - NEW_EXPLOSIVE_ALTCOIN_SETUP_2023_12_03
  - QUICK_BITCOIN_UPDATE_DOUBLE_BOTTOM_2024_05_01
  - MICROCAP_MEME_PLAY_2024_05_05
  - BRIEF_BITCOIN_UPDATE_AND_MEME_PLAY_2024_05_07
  - MORE_MEME_OPPORTUNITIES_2024_05_25
  - OFF_WEEK_UPDATE_2024_06_05
  - MARKET_UPDATE_76_PREVIEW_2025_08_03
```

## Combined archive coverage after Batch 3

```yaml
full_issues_1_60: COMPLETE
market_updates_1_95: COMPLETE_WHEN_COMBINED_WITH_PRIOR_ISSUES_81_95_MANIFEST
topping_signals_1_8: COMPLETE
top_gauge_present: [1,2,3,4,5,6,7,8,9,10,11,12,14,17,20,22,23,24,25,26,27]
top_gauge_not_present_in_complete_user_export: [13,15,16,18,19,21]
```

Absence from the complete user export is not treated as proof that an issue was never published. These identifiers remain explicit archive absences and must not be reconstructed from neighboring articles.

## Archive boundary

The 203 standalone PDFs and extracted-text files were produced and verified outside GitHub as the binary archive bundle. GitHub stores permanent source lineage, page-level hashes, deduplication state and analysis governance. Historical ingestion does not change current market state, gates, locks, TechDev weighting or portfolio action.
