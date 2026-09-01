# External Vault / Disaster Recovery Health Audit

Date: 2026-09-01
Recorded at UTC: 2026-09-01T17:31:42Z
Status: `BLOCKED_EXTERNAL_ACCESS`
Source main frozen for audit: `0d09dc3ef7be05b002acf8bd59d324158d45d51b`

## Verdict

The independent disaster-recovery design exists, but current external DR is not operationally green.

The canonical target remains `Donh91/Investering-Framework-Vault`. It was historically initialized and connector read/write access was verified in July 2026. The current GitHub App authority now returns 404 for that repository, and installation `144438405` currently exposes only the Archive, Eksperimenter and restricted `secrets` repositories. The current authority cannot distinguish repository deletion/rename from loss of App repository selection, so no lifecycle claim is inferred from 404 alone.

No external backup, restore test or complete Git mirror is claimed by this audit.

## Current recovery anchor

A fresh internal safepoint was created before this audit state was persisted:

```text
branch: backup-safepoint/2026-09-01-external-vault-dr-recovery
source_sha: 0d09dc3ef7be05b002acf8bd59d324158d45d51b
safepoint_sha: 0d09dc3ef7be05b002acf8bd59d324158d45d51b
compare: IDENTICAL
ahead_by: 0
behind_by: 0
```

This is an internal recovery anchor only. It is not an independent disaster-recovery backup.

## Evidence chronology

### 2026-07-11 - Vault activated

PR #4 established the dedicated private independent target, initialized the append-only snapshot layout and recorded connector read/write access as verified. The contract intentionally separated a canonical disaster-recovery snapshot from a full Git mirror.

### 2026-07-13 - Last preserved green validation

The v1.6 archive run recorded Vault validation PASS and the snapshot pipeline as armed/tested. The backup counter completed 1/4 and advanced its expected position to 2/4.

### 2026-07-20 - Access failure became durable

The v1.8 archive run recorded `Donh91/Investering-Framework-Vault: UNAVAILABLE_404_CURRENT_CONNECTOR_SESSION`. It correctly blocked counter advancement, created no canonical snapshot and made no fallback mirror claim.

### 2026-09-01 - Failure still present

Fresh current probes reproduce the 404. The current GitHub App installation repository set contains exactly:

```text
Donh91/Investering-Framework-Archive-v1
Donh91/Eksperimenter-framework-
Donh91/secrets
```

`Donh91/Investering-Framework-Vault` is absent from that installation repository set.

## Stale control-plane state

`00_ARCHIVE_CONTROL/backup_rotation_state.json` was last updated 2026-07-13 and still contains historical fields such as `CONFIGURED_WRITABLE` and `READ_WRITE_VERIFIED`. Those statements describe the last verified historical state, not current connector reachability.

The same file still records:

```text
last_completed_position: 1
next_position: 2
last_completed_iso_week: 2026-W29
last_verified_canonical_snapshot: null
```

This audit does not rewrite that canonical backup configuration because backup configuration is high-impact governance and the required external target is currently unavailable. Instead, the current failure is preserved in the additive machine receipt:

`research/repository_safety/2026-09-01__external-vault-dr-health-receipt.json`

## Rejected shortcuts

`Donh91/secrets` is not a replacement Vault. Current cross-repository governance assigns it to restricted provider data and explicitly forbids canonical framework decision authority there. Copying the framework brain into that plane would collapse the control/restricted boundary.

`Donh91/Eksperimenter-framework-` is public and non-dedicated, so it is not a compliant private independent backup target.

A `backup-safepoint/*` branch in the source repository remains an internal safepoint, not independent DR.

## Recovery gate

External DR may return to PASS only after all of the following are directly verified:

1. The canonical Vault is accessible to the authorized installation, or a separately governed canonical target replacement is explicitly completed.
2. The target is private, independent and not a fork.
3. Current source `main` is frozen to an exact SHA before copy.
4. A dated append-only canonical snapshot is written from that frozen SHA.
5. Every mandatory seed path and every then-current canonical-index referenced path is read back with matching content or stable digest.
6. A final backup receipt contains exact source and destination identifiers with no unresolved required paths.
7. A non-destructive restore drill verifies representative canonical index, governance, ledger and weekly-operation files.
8. Full Git mirror remains separately classified unless branches, tags and reachable history are independently preserved and verified.

## External boundary action still required

If `Donh91/Investering-Framework-Vault` still exists, the minimal recovery action is to include that repository in GitHub App installation `144438405` with only the repository access needed for the governed snapshot and restore verification.

If the repository no longer exists, recreation or target replacement is a separate governed decision. This audit does not silently substitute another repository and does not modify repository permissions, installation selection or backup credentials.

## Final classification

```text
INTERNAL_SAFEPOINT: PASS
EXTERNAL_VAULT_ACCESS: FAIL
CANONICAL_EXTERNAL_SNAPSHOT: NOT_RUN
RESTORE_DRILL: NOT_RUN
FULL_GIT_MIRROR: NOT_CONFIGURED
BACKUP_ROTATION: BLOCKED_AT_1_OF_4_SINCE_AT_LEAST_2026-07-20
EXTERNAL_DR: BLOCKED_EXTERNAL_ACCESS
EXTERNAL_BACKUP_SUCCESS_CLAIMED: NO
```
