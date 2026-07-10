# TechDev Issues #81–#95 — Source Manifest

**Import date:** 2026-07-10  
**Status:** SOURCE_MANIFEST / COMPLETE_SEQUENCE  
**Scope:** Original user-uploaded TechDev newsletter PDFs used for source-backed claim extraction  
**Related ledger:** `06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claim-ledger__operational.md`

## Source rule

- One selected uploaded PDF is the lineage anchor for each imported issue.
- Duplicate uploads of the same issue are not counted as additional sources.
- The PDFs are source material, not framework doctrine.
- Claim extraction uses precise paraphrases; it does not reproduce the newsletters.
- No claim is scored in this import.
- Original claims and later revisions remain side by side.

## Imported issues

| Issue | Issue date | Selected uploaded artifact | SHA-256 | Import status |
|---:|---|---|---|---|
| #81 | 2025-11-03 | `TechDev Newsletter - Market Update Issue #81.pdf` | `1b17bf189514baf1d2dc494ffee1b0a7596a3f65a68dbf9de3b9f17c91c8eec2` | SOURCE_BACKED_IMPORTED |
| #82 | 2025-11-17 | `TechDev Newsletter - Market Update Issue #82.pdf` | `05ff60ecdc6e8b1c608024dd9012c61c62e7dffb5124075d60a60fb2b7732d81` | SOURCE_BACKED_IMPORTED |
| #83 | 2025-11-30 | `TechDev Newsletter - Market Update Issue #83(1).pdf` | `c3a1e662184b8e31255d7bf351e3d331edecc519bddbfd97c97f8a9fc6e63e75` | SOURCE_BACKED_IMPORTED |
| #84 | 2025-12-15 | `TechDev Newsletter - Market Update Issue #84(2).pdf` | `be3f16a3887d0d6cd33c372dec6ebdbad6adbbf8c366cf2eca48ee41f5a0f92f` | SOURCE_BACKED_IMPORTED |
| #85 | 2025-12-28 | `TechDev Newsletter - Market Update Issue #85(2).pdf` | `01f74ac02b3a26d63487faaf08db65b4b2bc6ab26935663c4d626a0288526c3f` | SOURCE_BACKED_IMPORTED |
| #86 | 2026-01-12 | `TechDev Newsletter - Market Update Issue #86(1).pdf` | `2d42039532d08cd4421800a1c5115fa5de2a5a2a4c7e50dbcdfba6f8c4fda9e0` | SOURCE_BACKED_IMPORTED |
| #87 | 2026-02-02 | `TechDev Newsletter - Market Update Issue #87.pdf` | `a898a4cc9759e7c771ac765098da722c406cba829a1daba90c034c0f37be36ab` | SOURCE_BACKED_IMPORTED |
| #88 | 2026-02-19 | `TechDev Newsletter - Market Update Issue #88.pdf` | `4eef7647d88109dbd1c4212139b0f2fa83bce40455e7e58a59b2441a9e00cd10` | SOURCE_BACKED_IMPORTED |
| #89 | 2026-03-02 | `TechDev Newsletter - Market Update Issue #89(2).pdf` | `4833b9c6be2ee701c9abbc352a3019346188b6a0fff682d719afa930af27e100` | SOURCE_BACKED_IMPORTED |
| #90 | 2026-03-15 | `TechDev Newsletter - Market Update Issue #90.pdf` | `d05c4fd0fa8cf3bc612c357198b10507fa29cfc5abda73d8d693412aec66a080` | SOURCE_BACKED_IMPORTED |
| #91 | 2026-03-29 | `TechDev Newsletter - Market Update Issue #91(1).pdf` | `0383155fe6415c774ff330019435db8148ebb30a914a013b00cf7ec88fb6ab57` | SOURCE_BACKED_IMPORTED |
| #92 | 2026-04-12 | `TechDev Newsletter - Market Update Issue #92(1).pdf` | `8e245ed9b2e58ade0007d8d55a064f315c5db8150fb1fdb813d1db87eb808e2b` | SOURCE_BACKED_IMPORTED |
| #93 | 2026-04-27 | `TechDev Newsletter - Market Update Issue #93.pdf` | `524fae81bd56580949665786886d1fe483d3917ab17b579b7d763eaf3193abd5` | SOURCE_BACKED_IMPORTED |
| #94 | 2026-05-17 | `TechDev Newsletter - Market Update Issue #94(1).pdf` | `098fbe46f005b00c842b8f96b788c0d3b761d833d7e142bde3e1e60a5e3eefbe` | SOURCE_BACKED_IMPORTED |
| #95 | 2026-05-31 | `TechDev Newsletter - Market Update Issue #95(1).pdf` | `aff5ae2d5bfea654c9cc9a1a4cdbb65dd568e882b89b77949ad4cf668105a387` | SOURCE_BACKED_IMPORTED |

## Coverage

```yaml
sequence_start: 81
sequence_end: 95
issues_expected: 15
issues_imported: 15
issues_missing: 0
missing_issue_numbers: []
source_backed_claim_rows_extracted: 72
historical_signal_snapshot_rows_separate: 7
scoring_performed: NO
outcomes_filled: NO
```

## Extraction files

```text
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-81-95__source-backed-extraction-v0-1.md
06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claims-issues-87-88-90__source-backed-addendum-v0-2.md
```

## Lineage repair completed

Issue #90 now provides the original source for the BITI and ETHD trade setups later discussed in Issues #91 and #92.

```text
TD90_BITI_001 → TD91_BITI_001 → TD92_BITI_001
TD90_ETHD_001 → TD91_ETHD_001 → TD92_ETHD_001 → TD93_ETHD_001
```

The later outcome and re-entry reports do not erase or improve the original Issue #90 setup retroactively.
