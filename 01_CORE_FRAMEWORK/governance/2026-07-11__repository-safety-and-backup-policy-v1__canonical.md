# Repository Safety and Backup Policy v1.0

**Date:** 2026-07-11  
**Status:** PERMANENT_CANONICAL_GOVERNANCE  
**Scope:** All agents, automations, connectors and human maintenance affecting the Investering framework repositories.

## 1. Purpose

Preserve agent usefulness while preventing one mistaken command, cleanup task or agent decision from destroying the framework, rewriting its history or deleting the only usable archive.

The policy applies to:

- `Donh91/Investering-Framework-Archive-v1`
- `Donh91/Cycle-navigator-`
- `Donh91/Eksperimenter-framework-`
- any future independent backup vault

Core principle:

```text
Agents may work freely inside isolated working branches.
Agents may not hold unreviewed irreversible power over canonical history.
```

## 2. Four-week backup rotation

A four-week cycle is selected because the framework changes quickly and a six-week interval creates unnecessary exposure.

The weekly GitHub Archive Sync owns the counter:

```text
Week 1: BACKUP_TIMER 1/4
Week 2: BACKUP_TIMER 2/4
Week 3: BACKUP_TIMER 3/4
Week 4: BACKUP_TIMER 4/4, perform full backup cycle and reset
```

Counter rules:

1. Increment once per successful scheduled weekly archive sync.
2. A retry on the same weekly run must not increment twice.
3. If the archive sync is blocked before repository validation, do not increment.
4. At 4/4, create and verify a dated internal safepoint branch from the current canonical `main` commit.
5. At 4/4, also perform and verify an independent external vault backup when the vault is configured.
6. Reset the next weekly position to 1/4 only after the safepoint is verified.
7. Failure of the external vault must be reported honestly and must not be recorded as a completed external backup.

## 3. Immediate safepoint override

The four-week timer does not limit emergency safepoints.

Before any high-impact operation, create a dated safepoint immediately regardless of timer position.

A high-impact operation includes:

- deleting more than 10 files
- deleting more than 5 percent of repository files
- deleting or moving a top-level directory
- changing `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`
- changing archive routing, precedence or source governance
- replacing more than 25 files in one operation
- changing GitHub workflows, security policy or backup configuration
- repository-wide renames or namespace migrations

Safepoint naming:

```text
backup-safepoint/YYYY-MM-DD-short-purpose
```

Required receipt:

- source branch
- source commit SHA
- created safepoint branch
- timestamp
- intended high-impact operation
- verification result

## 4. Forbidden operations

The following are forbidden for agents and automations unless the user explicitly changes this policy first:

- deleting a repository
- deleting the canonical `main` branch
- force-pushing to canonical or backup branches
- rewriting Git history
- `git push --mirror` against a destination that is not a dedicated empty backup vault
- `git clean`
- `git reset --hard` as a cleanup method
- bulk checkout or bulk restore that overwrites unreviewed work
- deleting backup branches
- modifying branch protection, rulesets, repository permissions or backup credentials
- deleting the external vault
- deleting both source and backup copies in the same operation

No agent may silently reinterpret a destructive operation as routine cleanup.

## 5. Deletion gate

Normal file retirement remains allowed, but it must be auditable.

### Low impact

Up to 10 individual files, below 5 percent of repository contents, no top-level directory and no canonical index or governance deletion.

Requirements:

- work on a task branch
- list every deleted path
- state replacement or retirement reason
- verify no unexpected deletions
- merge through a pull request or other explicit reviewed change record

### High impact

Anything exceeding the low-impact limits.

Requirements:

1. Explicit user approval for the exact deletion or movement manifest.
2. Immediate safepoint before the change.
3. Separate working branch.
4. Pre-change and post-change file-count comparison.
5. Exact deletion, movement and replacement manifest.
6. Pull request with verification results.
7. No force operations.

## 6. Working branch rule

Default branch model:

```text
main
= canonical truth, protected target

agent/task-YYYYMMDD-short-purpose
= isolated agent work

backup-safepoint/YYYY-MM-DD-short-purpose
= recovery anchor, never normal workspace
```

Agents must not use backup branches as working branches.

## 7. Canonical `main` protection target

GitHub settings should enforce:

- pull request required before merge
- direct pushes to `main` blocked
- force pushes blocked
- branch deletion blocked
- rules apply to administrators
- agents and automations are not bypass actors
- security and workflow changes require explicit review

Until these GitHub-side rules are configured, the repository is policy-protected but not fully platform-enforced.

## 8. External backup vault

Required target:

```text
Donh91/Investering-Framework-Vault
```

The vault must be:

- private
- independent, not a fork
- used only for backups and restore tests
- outside normal agent write access where practical
- protected from force pushes and deletion
- configured with the minimum credential necessary for automated backup

A backup stored only as another branch inside the source repository is a safepoint, not a complete disaster-recovery backup.

## 9. Full backup definition

A full external backup is valid only when it preserves:

- all branches required for recovery
- tags
- complete reachable Git history
- the canonical default branch
- a dated backup receipt containing source and destination commit identifiers

A manifest-only copy, selected-file copy or GitHub issue is not a full backup.

## 10. Verification and restore testing

At each 4/4 cycle:

- verify source `main` SHA
- verify internal safepoint points to the same SHA
- verify external vault backup completed when configured
- record exact source and destination identifiers
- record status as `PASS`, `PARTIAL_INTERNAL_ONLY` or `FAIL`

Quarterly:

- perform a non-destructive restore drill into a temporary test location or repository
- verify canonical index readability
- verify representative source, governance, ledger and weekly-operation files
- record restore result
- do not modify production repositories during the drill

## 11. Automation output

Every GitHub Archive Sync must include:

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

At 4/4 it must additionally include:

```text
SOURCE_MAIN_SHA:
SAFEPOINT_BRANCH:
SAFEPOINT_SHA:
EXTERNAL_VAULT_RECEIPT:
BACKUP_RESULT: PASS / PARTIAL_INTERNAL_ONLY / FAIL
COUNTER_RESET_STATUS:
```

## 12. Current implementation state

Initial internal safepoint created:

```text
branch: backup-safepoint/2026-07-11-initial-safety-freeze
source_commit: 8aad34fcc0302f61f1282128f4c943433e6d8429
status: VERIFIED_CREATED
```

External vault:

```text
status: NOT_CONFIGURED
consequence: four-week runs can create internal safepoints, but cannot yet claim independent disaster-recovery backup
```

## 13. Honest limitation

This policy is a guardrail, not an operating-system or GitHub security boundary.

Full protection requires GitHub-side branch rules, an independent vault and a backup credential that normal agents cannot change or delete.
