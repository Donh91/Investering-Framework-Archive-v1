# Repository Preflight and Data Gate Receipt Repair v1.0

**Dato:** 2026-07-20  
**Status:** OPERATIONAL  
**Område:** GitHub Archive Sync / Master Monday Data Gate / repository access diagnostics  
**Primary folder:** `03_WEEKLY_OPERATIONS/automation_patches/`  
**Depends on:** `01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md`, `01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md`, `03_WEEKLY_OPERATIONS/master_monday/process/2026-07-14__master-monday-durable-handoff-contract-v1__canonical.md`

## 1. Incident being repaired

The first 2026-07-20 `GITHUB ARCHIVE SYNC + BACKUP v1.8` attempt returned a global deferred status after repository access was treated as unavailable.

The later remediation proved that:

- the canonical framework repository was readable and writable;
- the Cycle Navigator and Experiments repositories were accessible;
- archive/governance work could continue;
- only the independent Vault was unavailable in that execution context.

The run therefore mixed two separate facts:

```text
CANONICAL_REPOSITORY_ACCESS
and
EXTERNAL_VAULT_ACCESS
```

A Vault failure must never be generalized into a GitHub-wide failure.

Incident classification:

```text
WRITE_GOVERNANCE_INCIDENT: NONE
DIAGNOSTIC_CLASSIFICATION_ERROR: YES
FINAL_2026-07-20_STATE: PARTIAL_REMEDIATED
```

## 2. Binding repository preflight matrix

Every GitHub-aware weekly operation must test repositories independently.

Required matrix:

| Repository | Role | Required result |
|---|---|---|
| `Donh91/Investering-Framework-Archive-v1` | canonical archive and governance | independent READ and WRITE-CAPABILITY classification |
| `Donh91/Cycle-navigator-` | public-product archive | independent READ classification |
| `Donh91/Eksperimenter-framework-` | experimental evidence | independent READ classification |
| `Donh91/Investering-Framework-Vault` | independent backup product | independent READ/WRITE classification only when backup work is due or validation is required |

Allowed access states per repository:

```text
READ_WRITE
READ_ONLY
UNAVAILABLE
UNKNOWN_AFTER_RETRY
NOT_REQUIRED_THIS_RUN
```

No single repository result may silently determine another repository's status.

## 3. Two-probe rule before global deferral

The canonical repository must fail two non-destructive probes before a run may claim repository-wide deferral:

1. repository metadata or equivalent connector capability probe;
2. read-back of one mandatory canonical path, normally `AGENTS.md` or `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md`.

If the probes disagree, classify:

```text
CANONICAL_REPOSITORY_ACCESS: DEGRADED_RETRY_REQUIRED
```

and retry once before stopping.

`DEFERRED` or `DEFERRED_UNKNOWN` is allowed only when the canonical repository remains unavailable after both probes and the requested archive/governance task cannot be executed safely.

## 4. Vault isolation rule

When the canonical repository is accessible but the Vault is unavailable:

- continue all safe archive, governance, pointer, checkpoint, receipt and read-back work in the canonical repository;
- do not write, replace or probe-create files in the Vault;
- do not increment the four-week backup counter;
- do not claim a canonical snapshot or full Git mirror;
- preserve the prior valid Vault pointer and backup state;
- return a partial status, never global `DEFERRED`.

Required classification:

```text
ARCHIVE_SYNC_STATUS: PASS or PARTIAL
EXTERNAL_VAULT_STATUS: UNAVAILABLE or DEGRADED
CANONICAL_SNAPSHOT_PIPELINE: FAIL or NOT_DUE
FULL_GIT_MIRROR_STATUS: NOT_CONFIGURED
OVERALL_RUN_STATUS: PARTIAL_ARCHIVE_PASS_BACKUP_FAIL_VAULT_UNAVAILABLE
```

If the Vault later becomes accessible, a subsequent run may validate it independently. It must not rewrite prior receipts or pretend the earlier backup succeeded.

## 5. Archive Sync v1.8.1 status rules

The automation must distinguish:

```text
PASS
PARTIAL_ARCHIVE_PASS_BACKUP_FAIL_VAULT_UNAVAILABLE
PARTIAL_REPOSITORY_ACCESS_DEGRADED
DEFERRED_CANONICAL_REPOSITORY_UNAVAILABLE
FAIL_SAFETY
```

A successful remediation after an incorrect initial access diagnosis must report:

```text
write_governance_result: PARTIAL_REMEDIATED
final_repository_state: PASS or PARTIAL
manual_intervention_required: YES
```

It may not report an unqualified clean pass for that run.

## 6. Master Monday Data Gate receipt contract

The Data Gate must maintain exactly one receipt per ISO week at:

```text
03_WEEKLY_OPERATIONS/sunday_closeout/<ISO_WEEK>/master_monday_data_gate_receipt.json
```

Required states:

```text
WAITING_FOR_SOURCE
SOURCE_RECEIVED_VALIDATING
COMPLETED
PARTIAL_SOURCE_MISSING
PARTIAL_RECEIPT_WRITE_FAIL
```

Minimum fields:

```text
iso_week
selected_source_mode
source_packet_id
source_timestamp
source_hash_or_unknown
blocking_missing_fields
non_blocking_unknown_fields
state
created_at
updated_at
completion_timestamp
closeout_commit_or_unknown
receipt_write_status
```

## 7. Receipt timing and duplicate protection

At the first same-week check:

- read the weekly receipt when it exists;
- create `WAITING_FOR_SOURCE` only when source completion is genuinely pending;
- update to `SOURCE_RECEIVED_VALIDATING` before full validation;
- update to `COMPLETED` only after source validation and weekly closeout completion;
- later same-week checks must remain silent after `COMPLETED`.

If the source and closeout are valid but the receipt cannot be written:

- do not discard valid market-source completion;
- allow Master Monday readiness to continue;
- report `PARTIAL_RECEIPT_WRITE_FAIL`;
- preserve any previous valid pointer;
- create no duplicate closeout;
- retry only the receipt transaction, not the market calculation.

## 8. Write-access classification

Read access does not prove write access.

Write capability is verified only by an authorized real transaction on an explicit non-default task branch, never by a placeholder or probe file.

If no write is otherwise due, classify write capability as:

```text
WRITE_CAPABILITY: NOT_EXERCISED_THIS_RUN
```

Do not manufacture a mutation merely to test access.

## 9. Required user-facing diagnostics

Archive Sync must report:

```text
canonical_repo_access:
cycle_navigator_repo_access:
experiments_repo_access:
vault_repo_access:
canonical_repo_probe_1:
canonical_repo_probe_2:
manual_intervention_required:
initial_diagnostic_error:
archive_sync_status:
backup_status:
overall_run_status:
```

Data Gate must report internally or in its receipt:

```text
data_gate_receipt_path:
data_gate_receipt_state:
data_gate_receipt_write_status:
duplicate_closeout_prevented:
```

## 10. Authority boundary

This patch changes only automation diagnostics, durability and receipt handling.

It changes no:

- market state;
- DATA PING acceptance authority;
- gate or threshold;
- forecast;
- score;
- rule promotion;
- portfolio action;
- Vault contents;
- GitHub workflow or permission setting.
