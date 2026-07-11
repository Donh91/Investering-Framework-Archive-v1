# External Vault Activation and Snapshot Contract v1.1

**Date:** 2026-07-11  
**Status:** PERMANENT_CANONICAL_GOVERNANCE  
**Scope:** `Donh91/Investering-Framework-Vault` and the four-week GitHub backup rotation  
**Depends on:** Repository Safety and Backup Policy v1.0

## 1. Activation verdict

The independent private repository below is verified and active:

```text
Donh91/Investering-Framework-Vault
```

Verified properties:

- private repository
- independent repository, not a fork
- ChatGPT GitHub connector can read and write
- vault policy and append-only folder layout initialized
- dated receipt and latest-status pointer initialized

The external vault is therefore no longer `NOT_CONFIGURED`.

Current state:

```text
EXTERNAL_VAULT_STATUS: CONFIGURED_WRITABLE
CANONICAL_SNAPSHOT_PIPELINE: ARMED
FULL_GIT_MIRROR_STATUS: NOT_CONFIGURED
```

## 2. Two backup products must remain separate

### A. Canonical disaster-recovery snapshot

This is the active automated product available through the current GitHub connector.

It independently preserves the current recoverable framework brain, including:

- canonical index and all current addenda
- archive routing and repository safety governance
- current framework architecture and active engines
- active DATA PING protocols, runtime registry and open event ledgers
- current weekly-operation pointers and lineage controls
- current Cycle Navigator template and publication governance
- active Research Lab registries and accountability ledgers
- current source manifests required to reconstruct the archive
- every file explicitly referenced by the frozen canonical index

Destination:

```text
snapshots/YYYY-MM-DD/source-tree/<original path>
manifests/YYYY-MM-DD__snapshot-manifest.md
receipts/YYYY-MM-DD__backup-receipt.json
latest/backup-status.json
```

### B. Full Git mirror

A full Git mirror means every required branch, tag and reachable historical object.

The current connector cannot honestly guarantee this product.

Therefore:

```text
FULL_GIT_MIRROR_STATUS: NOT_CONFIGURED
```

No automation may describe a canonical snapshot as a complete Git mirror.

## 3. Four-week execution contract

The existing weekly archive automation owns the cycle:

```text
1/4 = validate source, vault, registry and last receipt
2/4 = validate source, vault, registry and last receipt
3/4 = validate source, vault, registry and last receipt
4/4 = freeze source SHA, create internal safepoint, write and verify dated vault snapshot, issue receipt, reset counter
```

The counter may increment only once per ISO week.

A retry in the same ISO week must not increment it again.

The counter resets only after the internal safepoint exists and the external backup attempt has a final receipt.

If the canonical snapshot is partial, reset may occur only when the receipt preserves the exact unresolved-path list and the result is reported as `PARTIAL_CANONICAL_SNAPSHOT`, never `PASS`.

## 4. Frozen-source rule

Every 4/4 backup must first resolve and freeze the source `main` commit SHA.

All source files must be fetched from that frozen SHA, not from a moving `main` branch.

This prevents a snapshot from mixing multiple repository states.

## 5. Registry and discovery

Primary registry:

```text
00_ARCHIVE_CONTROL/vault_backup_registry.json
```

Mandatory discovery order:

1. canonical index
2. all current index addenda
3. archive map and routing
4. backup state and vault registry
5. all paths explicitly referenced by the canonical index
6. current latest-pointer files
7. current manifests and operational ledgers referenced by those anchors

## 6. Verification standard

For every copied path, record:

- source path
- source commit SHA
- source blob SHA when available
- destination path
- destination write receipt or commit SHA
- read-back result
- verification status

Pass rule:

```text
PASS_CANONICAL_SNAPSHOT
```

requires every mandatory registry path and every path explicitly referenced by the frozen canonical index to be present and verified.

Any missing or unverifiable path produces:

```text
PARTIAL_CANONICAL_SNAPSHOT
```

with an exact unresolved-path list.

## 7. High-impact override

Before approved high-impact work, run an out-of-cycle backup sequence regardless of the weekly counter:

1. freeze current source SHA
2. create internal safepoint
3. write canonical vault snapshot
4. verify receipt
5. only then begin the high-impact task

High-impact definitions remain those in Repository Safety and Backup Policy v1.0.

## 8. Vault immutability

The vault is append-only for agents and automations.

Forbidden:

- normal framework development inside the vault
- replacing or deleting prior snapshot roots
- replacing or deleting prior receipts or manifests
- force push
- history rewrite
- deleting the vault
- claiming success without read-back verification

## 9. Initial activation receipts

```text
vault initialization commit:
c580b1b38cb743f284bdc152ca1c3a32c7205c56

vault policy commit:
49d29977dbd53363b8de432ef3dc50085e47f807

connectivity receipt commit:
50f1350f4e3e5e4ed7fe235f3de3c948762992b9

connectivity receipt path:
receipts/2026-07-11__vault-connectivity-receipt.json
```

The activation receipt proves independent read/write capability. It does not claim that a complete dated canonical snapshot has already been executed.

## 10. Required automation output

Every weekly archive sync must report:

```text
BACKUP_TIMER: X/4
EXTERNAL_VAULT_STATUS: CONFIGURED_WRITABLE / DEGRADED / UNAVAILABLE
CANONICAL_SNAPSHOT_PIPELINE: ARMED / RUNNING / PASS / PARTIAL / FAIL
FULL_GIT_MIRROR_STATUS: NOT_CONFIGURED unless independently verified
LAST_CANONICAL_SNAPSHOT:
NEXT_CANONICAL_SNAPSHOT_DUE:
HIGH_IMPACT_OVERRIDE_STATUS:
```

At 4/4 it must additionally report exact source SHA, safepoint branch, snapshot root, manifest path, receipt path, verified count, unresolved count and final backup result.
