# Index Addendum - External Vault Activation

**Date:** 2026-07-11  
**Status:** CANONICAL_INDEX_ADDENDUM

Read these files with the existing repository safety policy:

```text
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md
00_ARCHIVE_CONTROL/backup_rotation_state.json
00_ARCHIVE_CONTROL/vault_backup_registry.json
```

## Active vault

```text
repository: Donh91/Investering-Framework-Vault
visibility: private
independent_not_fork: VERIFIED
connector_read_write: VERIFIED
canonical_snapshot_pipeline: ARMED
full_git_mirror_status: NOT_CONFIGURED
```

## Binding distinction

The active automation produces an independent canonical disaster-recovery snapshot of the recoverable framework brain.

It must not claim complete Git-history mirroring unless branches, tags and reachable historical objects are independently preserved and verified.

## Four-week cycle

```text
1/4 validate
2/4 validate
3/4 validate
4/4 internal safepoint + frozen-SHA canonical vault snapshot + manifest + receipt + reset
```

High-impact changes trigger the same backup sequence immediately, regardless of timer position.

## Current timer

```text
next scheduled position: 1/4
counter owner: GitHub Archive Sync + Backup
```
