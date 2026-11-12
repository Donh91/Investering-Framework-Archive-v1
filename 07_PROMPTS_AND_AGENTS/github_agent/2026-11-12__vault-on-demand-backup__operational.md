# Vault On-Demand Backup: Prompt-to-Verified-Recovery Runbook v0.1

**Dato:** 2026-11-12  
**Status:** OPERATIONAL_CANDIDATE · RUN_87_SNAPSHOT_AND_RESTORE_VERIFIED · INDEPENDENT_CUTOVER_NOT_ATTESTED  
**Område:** Source/Vault recovery, on-demand GitHub execution, agent handover  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Depends on:** `AGENTS.md`, `.agents/skills/archive-governance/SKILL.md`, `01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md`, `01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md`

> **Evidence boundary:** The original Vault workflow run #87 completed SUCCESS on 2026-11-12. Native snapshot job and immutable receipt verify a frozen Archive SHA, 319,373 paths with zero unresolved, remote readback PASS and restore-drill PASS. This demonstrates recoverability of that frozen revision, **not** a current-main backup, complete Git mirror, production recovery cutover authorization or independent destructive-custody attestation. No governance or runtime permissions change is authorized by this document.

## User invocation

One concise owner prompt is enough:

> Lav en ny Vault-backup af frameworkets aktuelle Archive main. Brug den eksisterende godkendte backupmekanisme, ingen dubleret kørsel, verificer kilde-SHA, snapshot, manifest og restore/readback, og rapportér dokumenteret PASS eller præcis blokering.

A second useful prompt is: `Kontroller Vault-backup #<run id>, færdiggør evidensen og arkiver kun PASS, hvis alle gates består.`

## Repositories and authority

- **Source/control plane:** `Donh91/Investering-Framework-Archive-v1`, canonical `main`.
- **Independent backup destination:** private `Donh91/Investering-Framework-Vault`, not a substitute for source `main`.
- **Restricted data plane:** `Donh91/secrets` remains separate; never copy restricted source payloads/credentials to public Archive or issue comments.
- **Credential plane:** existing GitHub Actions Secrets or separately approved short-lived credentials. Never ask owner to paste a token into chat or commit secrets.
- **Known on-demand Vault workflow, subject to fresh source verification:** `Donh91/Investering-Framework-Vault/.github/workflows/vault-canonical-recovery.yml`, manual `workflow_dispatch`.
- **Product scope:** `CANONICAL_SNAPSHOT` only when the actual receipt proves it. `FULL_GIT_MIRROR` is NOT established by the mere existence of this workflow.

This runbook never authorizes source/Vault deletion, force pushes, history rewrite, branch/ruleset/credential changes or weakening the permanent separation of destructive authority.

## Execution, strict order

1. **Resolve current authority.** Read `AGENTS.md`, the two permanent backup governance owners and `00_ARCHIVE_CONTROL/vault_backup_registry.json`; resolve the current *actual* source `main` SHA and scope, not cached issue text. Check the current Vault run inventory before dispatch. If an equivalent backup is in progress, **observe, do not trigger a duplicate**.
2. **Access preflight.** Check the intended private Vault. A GitHub App or connector `404 NOT_FOUND` alone is **not** proof of deletion or rename. Before proposing repo recreation or access expansion, try the *already-authorized, owner-signed-in* GitHub browser/profile, if available. Read Vault metadata and existing workflow from there. If no authorized access, report `VAULT_ACCESS_UNVERIFIED`; never make Vault public or create a second repo/identity.
3. **Separation gate.** Check whether the effective principal/credential could destroy source and recovery. If both destructive authorities coexist or are unknown for a high-impact operation, stop with the named policy reason. Read-only status/receipt inspection and tightly constrained append-only writing are different from destructive authority, but broader credentials must be called out as an enforcement gap.
4. **Freeze source and internal safepoint.** Resolve exact current Archive `main` SHA. Create a date-stamped `backup-safepoint/YYYY-MM-DD-short-purpose` from that exact SHA **when policy requires or owner approves**; independently compare against the frozen SHA (`identical`, 0 ahead, 0 behind). Do not use this branch as a task workspace. Record it as `INTERNAL_ONLY`, never as independent recovery.
5. **One authorized workflow dispatch.** Confirm the existing Vault workflow is correct and its inputs/default branch do not change permissions, delete history, overwrite dated snapshots or expose private values. Owner's on-demand request authorizes one run of the existing approved mechanism, **not** a modified replacement. Use the Vault GitHub Actions UI only when authenticated access is available and the connector has no legitimate dispatch action. Record run ID/URL and dispatch timestamp. Do not use repeated clicks, repeated billable runs or duplicate retries.
6. **Track real jobs.** Observe `snapshot` plus conditional `validate_recovery_pr`, `verify_archive_receipt`, `publish_archive_receipt` from original GitHub run/job/step state. A skipped job is neither automatic success nor failure: understand the actual workflow condition and require any mandated verification through other authenticated evidence. Treat stalled or in-progress jobs as `PENDING`, not `PASS`. Read failing native steps, do not infer from green UI badges alone.
7. **Bind the right commit.** The GitHub Actions run commit in *Vault* is the workflow's own HEAD, **not necessarily** the source Archive SHA copied. Explicitly distinguish `vault_workflow_head_sha`, `source_archive_frozen_sha`, `internal_safepoint_sha`, `snapshot_vault_commit_sha` and `receipt_vault_commit_sha`. Require a receipt that proves the frozen source really is the intended Archive version.
8. **Inspect immutable output.** Verify the run's *actual* dated `snapshots/<date>/source-tree/`, `manifests/<date>__snapshot-manifest.md`, `receipts/<date>__backup-receipt.json`, `receipts/<date>__restore-drill-receipt.json` when included, and `latest/backup-status.json`. These are **contractual patterns**, not proof that files exist for a particular run. Confirm mandatory indexed paths, paths expected/verified/unresolved, destination readback against frozen source blob/digest, actual recovery/restore test and pointer lineage. A restored older snapshot is NOT current source coverage.
9. **Report exact product.** `PASS_CANONICAL_SNAPSHOT` only when native completion, required paths, source SHA, manifest, receipt and recovery readback agree. Use `PARTIAL_CANONICAL_SNAPSHOT` when bounded unresolved paths are listed, `FAIL` on definitive failure, `PENDING` while running and `UNVERIFIED` when access/proof is absent. Never say `FULL_GIT_MIRROR` without branch/tag/history proof. A newer Archive `main` after the frozen SHA requires a clearly labeled post-backup delta, not a retroactive claim.
10. **Archive learning with real evidence.** Once (and only once) the run meets the success gate, update the current Archive operating owner through an isolated `agent/task-YYYYMMDD-...` branch and governed PR, link the exact run/receipt and finalize this runbook as an observed operational method. Preserve the existing S1 and archive ownership; do not create a second supervisor, workflow, schedule, agent identity or permanent private-data backdoor.

## Run #87: verification outcome (2026-11-12, source-frozen backup)

The workflow **completed SUCCESS** after 31m59s, with `snapshot` PASSED in 30m06s and `publish_archive_receipt` PASSED in 1m46s. `validate_recovery_pr` and `verify_archive_receipt` were SKIPPED by workflow conditions: they are not independently claimed as PASSED.

Immutable evidence:
- Original [Vault Actions #87](https://github.com/Donh91/Investering-Framework-Vault/actions/runs/43241155043) and [snapshot job](https://github.com/Donh91/Investering-Framework-Vault/actions/runs/43241155043/job/131261595157).
- Verified [remote-verification JSON receipt](https://github.com/Donh91/Investering-Framework-Vault/blob/8ed85c3a383131d60f39be3e6c5638fde6d0004a/receipts/2026-11-12-run-43241155043-1__remote-verification.json), committed to a Vault **task branch**, not verified merged to Vault main. Git commit `8ed85c3a383131d60f39be3e6c5638fde6d0004a`.
- Frozen source **Archive** `source_sha=bee079d7a755874dc6c71a0292c3d3e86db30531`; Vault workflow execution `d8bf61048dccf32884f50bf6782a09059fead281`; Vault snapshot destination SHA `989d58fb68e743871401e8ae14b4cf63570332b1`; never substitute one for another.
- Manifest SHA-256 `3c0e2b66edaef6ad60207b2bef853fd294cb5666c6b4c9f1942762d692e3b92a`, schema v2, 16 shards; `verified_paths=319373`, `unresolved_paths=[]`.
- `remote_readback=PASS`; `restore_drill=PASS_ALL_FILES_AND_GIT_TREE`; source tree SHA `77ef95d946409b23442b620e60bd492296638a94`.
- Original internal safepoint `backup-safepoint/2026-11-12-manual-vault-request` was verified identical to source `bee079d7...` when created.
- Independently verified Archive `main` subsequently advanced to `47bf787ea8d32c15687a4d7bb68caa71792e5cef`, **36 commits ahead** of the frozen backed-up revision at the time of the follow-up comparison. These later 36 commits are **not covered by this snapshot**; a later backup/delta needs its own source SHA and receipt.
- Receipt says `separation_result=REQUIRES_INDEPENDENT_OWNER_EVIDENCE` and `release_permission=false`. Therefore successful **data restore drill** must never be represented as approval of production cutover, merge or independent source/Vault custody.
- Private repo authenticated browser access succeeded despite GitHub App `404`, a reusable authorization boundary finding, not a reason to broaden access.
- Backup result: **VERIFIED_FROZEN_SOURCE_SNAPSHOT_AND_RESTORE**. `CURRENT_OWNER_VERSION_BACKUP=PENDING_POST_MERGE_DELTA`; `FULL_GIT_MIRROR=NOT_PROVEN`; `INDEPENDENT_CUTOVER_AUTHORIZATION=BLOCKED_PENDING_OWNER_EVIDENCE`.

For any future prompt, execute the same original-owner path, first check for an existing in-progress run, freeze the *then-current* Archive SHA, confirm append-only source/Vault principal separation, dispatch at most once, verify immutable remote receipt and restore, then compare the present Archive main to the frozen source. Never silently infer latest-main coverage from a green historical run.

## Run #88: blocked by a required-path validation failure (2026-11-12)

The existing workflow was manually dispatched once after verifying that run #87 was the latest and no equivalent backup was running. The explicit source was Archive `161063feabc7b44f1248d6ed00f39d1f83dbcd02`, 41 commits ahead of #87's frozen source.

- [Vault Actions #88](https://github.com/Donh91/Investering-Framework-Vault/actions/runs/43293588094) finished **FAILURE**. The [snapshot job](https://github.com/Donh91/Investering-Framework-Vault/actions/runs/43293588094/job/131445884321) failed during “Freeze source and create unique append-only Vault branch” with `Required recovery paths missing: CN-MN-001`. Receipt publication was skipped. This run established no new snapshot or restore evidence.
- At the frozen source, `00_ARCHIVE_CONTROL/CANONICAL_INDEX.md` describes `CN-MN-001` as an editorial identifier. The identifier is absent as a repository-root file path. Review required-path extraction with the source and Vault owners, keeping validation of genuine file references intact.
- Retry only after a reviewed fix demonstrates that the identifier is classified correctly and real missing recovery paths still stop the run. Freeze the then-current source and check for an active or newer verified backup before any retry. Run #87 remains the last verified frozen-source snapshot.

## Mandatory compact receipt to return to owner

```yaml
backup_run_url:
backup_product: CANONICAL_SNAPSHOT | TARGETED_SNAPSHOT | DELTA_SNAPSHOT | FULL_GIT_MIRROR | NONE
vault_workflow_head_sha:
source_archive_frozen_sha:
current_archive_main_sha:
source_safepoint_branch:
source_safepoint_sha:
vault_snapshot_commit_sha:
snapshot_root:
manifest_path:
backup_receipt_path:
restore_receipt_path:
paths_expected:
paths_verified:
paths_unresolved:
native_run_conclusion:
restore_readback_result:
current_version_in_snapshot: YES | NO | PARTIAL | UNKNOWN
post_merge_delta_status: PASS | PENDING | NOT_REQUIRED | UNKNOWN
separation_enforcement: PASS | GAP | BLOCKED | UNVERIFIED
backup_result: PASS_CANONICAL_SNAPSHOT | PARTIAL_CANONICAL_SNAPSHOT | PENDING | FAIL | UNVERIFIED
evidence_urls:
```

## Learning guardrails / negative tests

- App connector says Vault `404`, authenticated owner session reads it: **DO NOT** conclude deleted; distinguish authorization boundary.
- Internal safepoint exists, no external receipt: **DO NOT** label external backup complete.
- Run started or `snapshot` job apparently completed, no manifest/restore receipt: **DO NOT** declare recovery PASS.
- Vault workflow HEAD looks valid but source Archive SHA absent: **DO NOT** claim current Archive was captured.
- Only subset of mandatory paths verified: **PARTIAL**, never full canonical PASS.
- Run hangs: observe exact native step; **do not** trigger a duplicate or silently disable safeguards.
- Request concerns source/control plane: **do not** promise `secrets`, Alpha Lab or other repositories were backed up unless explicitly present in source-bound receipts.
- A prior backup is valid for its frozen SHA, not automatically for later source changes.

## Ownership / release

This is a documentation-only, low-impact procedural candidate. No change to existing backup automation, schedule, release policy, credentials, market authority or GitHub configuration. The original S1 [Archive #1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156) may verify terminal run status and route reviewed documentation through the existing main branch PR process. Do not auto-merge a `PENDING` or overstated success claim.
