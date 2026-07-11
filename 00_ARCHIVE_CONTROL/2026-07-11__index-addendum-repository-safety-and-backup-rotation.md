# Index Addendum - Repository Safety and Backup Rotation

**Date:** 2026-07-11  
**Status:** CANONICAL_INDEX_ADDENDUM

Read these files as permanent repository-governance anchors:

```text
01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md
00_ARCHIVE_CONTROL/backup_rotation_state.json
```

## Binding rules

- Four-week backup cycle is active.
- `GitHub Archive Sync` owns the weekly counter.
- Week sequence is `1/4`, `2/4`, `3/4`, `4/4`.
- At `4/4`, create and verify a dated internal safepoint branch.
- At `4/4`, perform an independent external vault backup when the vault is configured.
- An internal branch is a safepoint, not a complete independent backup.
- High-impact changes trigger an immediate safepoint regardless of timer position.
- Repository deletion, canonical branch deletion, force push and history rewrite are forbidden.
- Bulk deletion requires an exact manifest, safepoint and explicit user approval.

## Current state

```text
Initial safepoint:
backup-safepoint/2026-07-11-initial-safety-freeze

Source commit:
8aad34fcc0302f61f1282128f4c943433e6d8429

Next weekly timer position:
1/4

External vault:
NOT_CONFIGURED
```

Any agent performing GitHub work must read the canonical policy before destructive, structural or repository-wide changes.
