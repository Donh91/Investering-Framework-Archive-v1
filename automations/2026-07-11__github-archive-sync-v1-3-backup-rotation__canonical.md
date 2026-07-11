# GitHub Archive Sync v1.3 - Repository Safety and Backup Rotation

**Date:** 2026-07-11  
**Status:** ACTIVE_AUTOMATION_SPEC  
**Automation:** `GitHub Archive Sync + Backup`  
**Schedule:** Monday 11:15 Europe/Copenhagen

## Upgrade summary

The existing weekly GitHub Archive Sync now also owns repository safety checks and a four-week backup counter.

## Locked cycle

```text
1/4 - weekly material archive sync
2/4 - weekly material archive sync
3/4 - weekly material archive sync
4/4 - weekly material archive sync plus full backup cycle
```

At 4/4 the automation must:

1. Resolve the current canonical `main` commit.
2. Create a dated internal safepoint branch from the exact commit.
3. Verify the safepoint.
4. Attempt and verify an independent vault backup when the vault is configured.
5. Record exact receipts.
6. Reset the next weekly position to 1/4 only after verification.

## High-impact override

The backup timer never blocks an immediate safepoint.

A high-impact repository change forces a safepoint before work begins, including bulk deletion, top-level movement, canonical index/governance replacement, workflow/security changes or broad namespace migration.

## State file

```text
00_ARCHIVE_CONTROL/backup_rotation_state.json
```

The state file is updated once per successful scheduled ISO-week run. Retries must not double-increment.

## Required output

```text
REPOSITORY_SAFETY_STATUS:
BACKUP_TIMER: X/4
INTERNAL_SAFEPOINT_STATUS:
EXTERNAL_VAULT_STATUS:
LAST_FULL_BACKUP:
NEXT_FULL_BACKUP_DUE:
HIGH_IMPACT_CHANGE_DETECTED:
DELETION_MANIFEST_STATUS:
```

At 4/4:

```text
SOURCE_MAIN_SHA:
SAFEPOINT_BRANCH:
SAFEPOINT_SHA:
EXTERNAL_VAULT_RECEIPT:
BACKUP_RESULT: PASS / PARTIAL_INTERNAL_ONLY / FAIL
COUNTER_RESET_STATUS:
```

## Initial receipt

```text
initial_safepoint: backup-safepoint/2026-07-11-initial-safety-freeze
source_commit: 8aad34fcc0302f61f1282128f4c943433e6d8429
result: VERIFIED_CREATED
next_timer: 1/4
external_vault: NOT_CONFIGURED
```

## Limitation

The automation can create internal safepoints immediately. Independent disaster recovery remains incomplete until a separate private non-fork vault and its minimum-scope backup credential are configured.
