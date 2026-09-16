# FMZ Quant Strategies - Disaster Recovery Binding

**Date:** 2026-09-14  
**Status:** RECOVERY_BINDING / RESEARCH_ONLY / NO_AUTHORITY  
**Source note:** `08_SOURCE_MATERIAL/external_methods/2026-09-12__herman-fmz-strategy-corpus__source-note.md`

## Purpose

Preserve the externally hosted `fmzquant/strategies` research corpus independently of the upstream GitHub repository so future Research Lab work does not depend on upstream availability.

This binding creates no trading authority, alpha claim, market rule, threshold or portfolio permission.

## Frozen upstream identity

```yaml
source_repository: fmzquant/strategies
source_url: https://github.com/fmzquant/strategies
source_default_branch: master
source_pinned_commit: 7853bb2bf262c4567ac238d3552d97f0e50cb801
source_commit_count_all_refs: 104
source_ref_count: 3
source_file_count_at_pin: 5807
```

## Private disaster-recovery copy

```yaml
vault_repository: Donh91/Investering-Framework-Vault
vault_path: external_sources/fmzquant-strategies/2026-09-14/
receipt: receipts/2026-09-14__fmzquant-strategies-disaster-recovery-receipt.json
manifest: external_sources/fmzquant-strategies/2026-09-14/manifest.json
restore_status: PASS_FULL_GIT_BUNDLE_AND_TREE_RESTORE
archive_result: PASS_DURABLE_PRIVATE_ARCHIVE
```

The private Vault contains both:

1. a complete Git bundle preserving all refs and reachable Git objects from the mirror clone;
2. a frozen source-tree tarball for the pinned commit;
3. repository metadata, branches, tags, issues/PR issue records, pull requests and releases captured separately from Git history;
4. refs, commit log and source-tree listing;
5. SHA-256 checksums and a restore-tested manifest.

## Integrity binding

```yaml
full_git_bundle_bytes: 35371127
full_git_bundle_sha256: 2a06f2ca101ee512f8aab5a37f4023526da64d24d4456c520af94cdd676a2c95
source_tree_archive_bytes: 18803929
source_tree_archive_sha256: f3912ad0097e4ed029970a27b541bd6b2c53b067c02c1c8f9cc392b2ee96fc4a
```

A non-destructive restore drill cloned the archived Git bundle, checked out the pinned commit, matched the source tree identity and passed `git fsck --full --strict` before the Vault receipt was committed.

## Research and licensing boundary

The upstream repository has no repository-wide license declared in the reviewed snapshot. Individual strategy files may contain their own licenses or attribution requirements.

Therefore the private copy is a disaster-recovery and internal research corpus only:

```text
DO NOT REDISTRIBUTE THE MIRRORED CORPUS.
DO NOT TREAT ORIGINAL BACKTEST CLAIMS AS EVIDENCE OF EDGE.
INSPECT FILE-LEVEL LICENSE / ATTRIBUTION BEFORE CODE REUSE.
ROUTE ALL STRATEGY TESTING THROUGH EXISTING RESEARCH LAB GOVERNANCE.
```

## Recovery rule

If the upstream repository becomes unavailable, the private Vault copy is the recovery source. Restore from the Git bundle first, verify its SHA-256 against this binding and the private receipt, then verify the restored pinned commit before any research use.

The source note remains the research interpretation owner. This file is provenance and disaster-recovery navigation only.
