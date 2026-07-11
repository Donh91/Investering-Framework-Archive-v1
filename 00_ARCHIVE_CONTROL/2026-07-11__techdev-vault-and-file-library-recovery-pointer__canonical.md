# TechDev Vault and File Library Recovery Pointer

**Date:** 2026-07-11  
**Status:** CANONICAL_RECOVERY_POINTER / ACTIVE  
**Scope:** Future-agent discovery and disaster recovery for the complete available TechDev corpus

## Recovery topology

```text
PRIMARY ARCHIVE
Donh91/Investering-Framework-Archive-v1
= manifests, hashes, claims, revisions, scoring, benchmarks and governance

PRIVATE VAULT
Donh91/Investering-Framework-Vault
= immutable source identity, recovery instructions and receipts

CHATGPT FILE LIBRARY
smallpdf - 11 jul. 2026 - 092311-komprimeret.pdf
= original merged 203-page paid source artifact
```

## Original source identity

```yaml
title: smallpdf - 11 jul. 2026 - 092311-komprimeret.pdf
file_library_id_at_ingestion: file_00000000be7871f5a4f46cc40f6f96d5
size_bytes: 46384809
sha256: 68f52fef31bb52a1a2d48cf9c17de65f63bcee080eef23326a8e9eaf539c2ea7
pages_articles: 203
```

## Vault paths

```text
README.md
techdev/batch_3/RECOVERY_MANIFEST.md
techdev/batch_3/FILE_LIBRARY_SOURCE_POINTER.md
techdev/CANONICAL_RESEARCH_POINTER.md
receipts/2026-07-11__techdev-corpus-recovery-receipt.json
```

## Primary archive paths

```text
08_SOURCE_MATERIAL/techdev/2026-07-11__techdev-historical-archive-batch-3-merged-corpus__source-manifest.md
08_SOURCE_MATERIAL/techdev/batch_3_page_index/2026-07-11__techdev-batch-3-page-index-part-1-of-4.md
08_SOURCE_MATERIAL/techdev/batch_3_page_index/2026-07-11__techdev-batch-3-page-index-part-2-of-4.md
08_SOURCE_MATERIAL/techdev/batch_3_page_index/2026-07-11__techdev-batch-3-page-index-part-3-of-4.md
08_SOURCE_MATERIAL/techdev/batch_3_page_index/2026-07-11__techdev-batch-3-page-index-part-4-of-4.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-complete-corpus-claim-and-revision-ledger-v1__source-backed.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-claim-revision-graph-v1__operational.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-complete-corpus-red-team-audit-v1__operational.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-counterfactual-benchmark-package-v1__scored.md
06_RESEARCH_LAB/forward_tests/2026-07-11__techdev-forward-calibration-ledger-v1__operational.md
01_CORE_FRAMEWORK/governance/2026-07-11__techdev-operational-weighting-v1__canonical.md
```

## Future-agent procedure

1. Read `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md` first.
2. Read this pointer.
3. Read the Vault recovery manifest and receipt.
4. Search the user's File Library by the exact source title when full original article text or charts are required.
5. Verify the recovered file against the recorded SHA-256 before relying on it.
6. Use the page-level source manifest to identify the correct article.
7. Preserve original claims and revisions separately, and never score a duplicate as corroboration.

## Boundary

The GitHub connector available during this operation could not directly transfer the 63.8 MB paid binary split-PDF package. This is recorded transparently in the Vault receipt. The original merged PDF remains in the user's File Library, while all agent-relevant lineage and research are stored in GitHub.

Historical recovery does not alter current market state, gates, locks, rotation permission or portfolio action.
