# TechDev Issue #99 Archive and PDF Ingestion Test Receipt

**Date:** 2026-08-02  
**Status:** IMPLEMENTED_PENDING_PR_GATES  
**Scope:** source archive, supplemented capture, revision tracking, Gem Score rerun, sector chart extraction and PDF ingestion regression

## Inputs

```yaml
pdf_file_id: file_00000000822482469090f42b9c71da5a
pdf_sha256: 1e3c1f97c71ff8c5a05508076a852d94f3eb1079606f980bf73590aa6ee78a3a
sector_chart_file_id: file_000000004d5c81f498a14eff3f6574fc
sector_chart_sha256: 2746f9c583e53aa3301d864e8b8b73b1aeb3ad6e9fd611fde1669d9d276ff86a
supplementary_tail_sha256: 3362899e1135a9d857b50b78f33379b82942cbc14872047362d816bb6ac7e89f
```

## Materialized archive

```text
08_SOURCE_MATERIAL/techdev/2026-08-02__techdev-market-update-99__source-manifest.md
08_SOURCE_MATERIAL/techdev/issue_99/FILE_LIBRARY_SOURCE_POINTER.md
08_SOURCE_MATERIAL/techdev/issue_99/TECHDEV_ISSUE_99_SUPPLEMENTARY_TAIL.txt
08_SOURCE_MATERIAL/techdev/issue_99/TECHDEV_ISSUE_99_SECTOR_CHART_POINTER.md
08_SOURCE_MATERIAL/techdev/issue_99/TECHDEV_ISSUE_99_SECTOR_LEADERSHIP.csv
06_RESEARCH_LAB/forward_tests/2026-08-02__techdev-issue-99-revision-and-rerun__operational.md
06_RESEARCH_LAB/forward_tests/techdev_issue_98/TECHDEV_ISSUE_99_REVISION_ROWS.csv
06_RESEARCH_LAB/forward_tests/techdev_issue_98/TECHDEV_ISSUE_99_GEM_SCORE_RERUN.csv
research/pdf_ingestion/TECHDEV_ISSUE_99_INGESTION_TEST_v1.json
00_ARCHIVE_CONTROL/2026-08-02__index-addendum-techdev-market-update-99-source-and-calibration.md
```

## Explicit source boundary

The uploaded PDF was independently preflighted in the ChatGPT runtime and passed PDF magic, render, encryption and native-text checks. It is a single unusually tall page and ends during the UAI card. The missing article tail and sector chart were supplied separately and are preserved with their own lineage.

The ChatGPT attachment binary cannot be passed directly into the repository workflow by the available GitHub connector. Therefore the GitHub PDF test is a real pinned-parser regression using the workflow's deterministic native-text PDF, while the exact Issue #99 binary has a separate local preflight receipt. This distinction must remain visible.

## Governance

```yaml
new_engine: false
new_test: false
framework_state_change: false
model_weight_change: false
broad_rotation_permission: false
portfolio_action: none
techdev_execution_authority: zero
```

Final workflow IDs, artifact digest, readback status, PR number and merge commit are appended before merge or in the final activation receipt.
