# GitHub Archive Sync + Backup v1.4

**Date:** 2026-07-11  
**Status:** CANONICAL_AUTOMATION_PATCH  
**Automation:** `GitHub Archive Sync + Backup`  
**Schedule:** Monday 11:15 Europe/Copenhagen

## Purpose

Combine weekly material archive triage with repository safety, a four-week backup timer and an independent vault snapshot.

## Active repositories

```text
Framework source:
Donh91/Investering-Framework-Archive-v1

Cycle Navigator:
Donh91/Cycle-navigator-

Research / experiments:
Donh91/Eksperimenter-framework-

Independent vault:
Donh91/Investering-Framework-Vault
```

## Weekly counter

```text
1/4 -> validate archive and vault, archive material changes
2/4 -> validate archive and vault, archive material changes
3/4 -> validate archive and vault, archive material changes
4/4 -> normal archive sync + internal safepoint + canonical vault snapshot + receipt + reset
```

The state file is:

```text
00_ARCHIVE_CONTROL/backup_rotation_state.json
```

The file may be advanced once per ISO week only.

## 4/4 backup algorithm

1. Read the repository safety policy, activation contract, state and vault registry.
2. Resolve and freeze source `main` SHA.
3. Create `backup-safepoint/YYYY-MM-DD-cycle-full-backup` from the same SHA.
4. Read the canonical index from the frozen SHA.
5. Build the copy set from:
   - mandatory registry paths
   - all current index addenda
   - every path explicitly referenced by the canonical index
   - all current latest-pointer files
   - active manifests and ledgers referenced by those anchors
6. Copy every source file to:

```text
Donh91/Investering-Framework-Vault
snapshots/YYYY-MM-DD/source-tree/<original source path>
```

7. Record source blob SHA, destination write receipt and read-back status for every path.
8. Write manifest and JSON receipt.
9. Update `latest/backup-status.json` in the vault.
10. Update source backup state.
11. Reset next position to 1/4 only after a final receipt exists.

## Pass states

```text
PASS_CANONICAL_SNAPSHOT
PARTIAL_CANONICAL_SNAPSHOT
FAIL
```

`PASS_CANONICAL_SNAPSHOT` requires every mandatory registry path and every path explicitly referenced by the frozen canonical index.

## Honest product label

The connector snapshot is a canonical disaster-recovery snapshot.

It is not a complete Git mirror and may not be labelled as such.

```text
FULL_GIT_MIRROR_STATUS: NOT_CONFIGURED
```

## High-impact override

Any approved high-impact repository task must trigger the same safepoint and vault snapshot process before the task begins, regardless of timer position.

## Safety rules

- no repository deletion
- no force push
- no history rewrite
- no backup deletion
- no bulk deletion without exact manifest and explicit user approval
- no snapshot replacement
- no vault use as working repository
- no success claim without exact receipts and read-back validation

## Required weekly output

```text
GITHUB ARCHIVE SYNC + BACKUP v1.4
week:
source_main_sha:
repos_checked:
archive_status:
repository_safety_status:
backup_timer: X/4
external_vault_status:
canonical_snapshot_pipeline:
full_git_mirror_status:
last_canonical_snapshot:
next_canonical_snapshot_due:
high_impact_override_status:
run_status:
```

At 4/4 add:

```text
safepoint_branch:
snapshot_root:
manifest_path:
receipt_path:
paths_expected:
paths_verified:
paths_unresolved:
backup_result:
counter_reset_status:
```
