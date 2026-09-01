# External Vault / Disaster Recovery Recovery Record

Date: 2026-09-01  
Status: `PASS_CANONICAL_DR`

## Recovery

The prior `BLOCKED_EXTERNAL_ACCESS` condition was resolved when account-level GitHub App repository access to `Donh91/Investering-Framework-Vault` was restored. The historical failure receipt remains immutable evidence and is not rewritten.

Fresh current-authority verification established that the Vault is private, independent/not-a-fork, readable and writable.

## Frozen source

```text
source repository: Donh91/Investering-Framework-Archive-v1
frozen main SHA: 879b1798856a6e835364a8328025437a7d9f9e62
safepoint: backup-safepoint/2026-09-01-external-vault-canonical-snapshot
safepoint SHA: 879b1798856a6e835364a8328025437a7d9f9e62
```

All source reads for the snapshot were made from the frozen SHA.

## Canonical snapshot proof

Production workflow run `33547532410`, job `99988639071`, completed `SUCCESS`.

The runtime reconstructed the canonical snapshot contract from the frozen `vault_backup_registry.json` plus every explicit path referenced by the frozen `CANONICAL_INDEX.md`.

```text
paths_expected: 78
paths_verified: 78
paths_unresolved: 0
source/destination Git blob equality: PASS 78/78
snapshot root: snapshots/2026-09-01/source-tree/
Vault snapshot commit: 1c4fbd2e62842712f7afb5d6f8fa86be4522b476
Vault final receipt commit: e0706fa60d5dffd640ce4feff4de95b21a59b09f
backup result: PASS_CANONICAL_SNAPSHOT
```

Remote main readback verified the final backup receipt, restore receipt and 78-path manifest after push.

## Restore drill

A non-destructive restore drill read representative files from the committed Vault snapshot and compared exact Git blob identity with the frozen source.

Verified categories included:

- canonical archive index
- repository safety governance
- canonical weekly backbone engine
- current Master Monday pointer
- active forward-test registry
- TechDev source manifest

Result: `PASS_RESTORE_DRILL`, 6/6 representative paths. Production repositories were not modified by the restore drill.

## Product boundary

```text
CANONICAL_DISASTER_RECOVERY_SNAPSHOT: PASS
FULL_GIT_MIRROR: NOT_CONFIGURED
```

The full Git mirror remains a separate backup product. This recovery does not claim preservation of every branch, tag or historical Git object.

## Rotation semantics

This snapshot was an out-of-cycle high-impact override. It therefore does not count as a scheduled weekly backup-counter event.

```text
last_completed_position: 1/4
next_position: 2/4
counter_advanced_by_this_recovery: NO
```

## Cleanup

The temporary one-shot Vault workflow was removed after successful proof. Vault main after cleanup is `80c415fecaefafb28d5b57104c01377ac609edc5`. Dated snapshot, manifests and receipts remain append-only.

## Authority

No market state, portfolio authority, model weight, threshold or canonical market rule was changed.

Current machine pointer:

`research/repository_safety/LATEST_EXTERNAL_DR_HEALTH.json`
