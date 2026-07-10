# TechDev Issues #81–#95 — Source Manifest

**Import date:** 2026-07-10  
**Status:** SOURCE_MANIFEST / PARTIAL_SEQUENCE_COMPLETE  
**Scope:** Original user-uploaded TechDev newsletter PDFs used for source-backed claim extraction  
**Related ledger:** `06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claim-ledger__operational.md`

## Source rule

- One selected uploaded PDF is the lineage anchor for each imported issue.
- Duplicate uploads of the same issue are not counted as additional sources.
- The PDFs are source material, not framework doctrine.
- Claim extraction uses precise paraphrases; it does not reproduce the newsletters.
- No claim is scored in this import.
- Missing issues are recorded as missing and must not be reconstructed from later summaries.

## Imported issues

| Issue | Issue date | Selected uploaded artifact | SHA-256 | Import status |
|---:|---|---|---|---|
| #81 | 2025-11-03 | `TechDev Newsletter - Market Update Issue #81.pdf` | `1b17bf189514baf1d2dc494ffee1b0a7596a3f65a68dbf9de3b9f17c91c8eec2` | SOURCE_BACKED_IMPORTED |
| #82 | 2025-11-17 | `TechDev Newsletter - Market Update Issue #82.pdf` | `05ff60ecdc6e8b1c608024dd9012c61c62e7dffb5124075d60a60fb2b7732d81` | SOURCE_BACKED_IMPORTED |
| #83 | 2025-11-30 | `TechDev Newsletter - Market Update Issue #83(1).pdf` | `c3a1e662184b8e31255d7bf351e3d331edecc519bddbfd97c97f8a9fc6e63e75` | SOURCE_BACKED_IMPORTED |
| #84 | 2025-12-15 | `TechDev Newsletter - Market Update Issue #84(2).pdf` | `be3f16a3887d0d6cd33c372dec6ebdbad6adbbf8c366cf2eca48ee41f5a0f92f` | SOURCE_BACKED_IMPORTED |
| #85 | 2025-12-28 | `TechDev Newsletter - Market Update Issue #85(2).pdf` | `01f74ac02b3a26d63487faaf08db65b4b2bc6ab26935663c4d626a0288526c3f` | SOURCE_BACKED_IMPORTED |
| #86 | 2026-01-12 | `TechDev Newsletter - Market Update Issue #86(1).pdf` | `2d42039532d08cd4421800a1c5115fa5de2a5a2a4c7e50dbcdfba6f8c4fda9e0` | SOURCE_BACKED_IMPORTED |
| #89 | 2026-03-02 | `TechDev Newsletter - Market Update Issue #89(2).pdf` | `4833b9c6be2ee701c9abbc352a3019346188b6a0fff682d719afa930af27e100` | SOURCE_BACKED_IMPORTED |
| #91 | 2026-03-29 | `TechDev Newsletter - Market Update Issue #91(1).pdf` | `0383155fe6415c774ff330019435db8148ebb30a914a013b00cf7ec88fb6ab57` | SOURCE_BACKED_IMPORTED |
| #92 | 2026-04-12 | `TechDev Newsletter - Market Update Issue #92(1).pdf` | `8e245ed9b2e58ade0007d8d55a064f315c5db8150fb1fdb813d1db87eb808e2b` | SOURCE_BACKED_IMPORTED |
| #93 | 2026-04-27 | `TechDev Newsletter - Market Update Issue #93.pdf` | `524fae81bd56580949665786886d1fe483d3917ab17b579b7d763eaf3193abd5` | SOURCE_BACKED_IMPORTED |
| #94 | 2026-05-17 | `TechDev Newsletter - Market Update Issue #94(1).pdf` | `098fbe46f005b00c842b8f96b788c0d3b761d833d7e142bde3e1e60a5e3eefbe` | SOURCE_BACKED_IMPORTED |
| #95 | 2026-05-31 | `TechDev Newsletter - Market Update Issue #95(1).pdf` | `aff5ae2d5bfea654c9cc9a1a4cdbb65dd568e882b89b77949ad4cf668105a387` | SOURCE_BACKED_IMPORTED |

## Missing issues in sequence

| Issue | Status | Rule |
|---:|---|---|
| #87 | SOURCE_MISSING | Do not infer original claims from later issues |
| #88 | SOURCE_MISSING | Do not infer original claims from later issues |
| #90 | SOURCE_MISSING_CRITICAL_FOR_TRADE_ORIGINS | Issue #91 may describe outcomes/revisions, but cannot substitute for Issue #90's original trade rows |

## Coverage

```yaml
sequence_start: 81
sequence_end: 95
issues_expected: 15
issues_imported: 12
issues_missing: 3
missing_issue_numbers: [87, 88, 90]
source_backed_claim_rows_extracted: 55
scoring_performed: NO
outcomes_filled: NO
```

## Lineage boundary

For claims whose original trade was introduced in missing Issue #90:

```text
SOURCE_STATUS:
  ISSUE_91_DERIVATIVE_REPORT_AVAILABLE
  ISSUE_90_ORIGINAL_SOURCE_MISSING

SCORING:
  BLOCKED_FOR_ORIGINAL_ENTRY_ACCURACY
```

Later TechDev revisions remain linked to earlier rows without erasing the original claim.
