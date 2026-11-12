# Vault On-Demand Backup: Prompt-to-Verified-Recovery Runbook v0.1

**Dato:** 2026-11-12  
**Status:** OPERATIONAL_CANDIDATE · PENDING_RUN_87_FINAL_EVIDENCE  
**Område:** Source/Vault recovery, on-demand GitHub execution, agent handover  
**Primary folder:** `07_PROMPTS_AND_AGENTS/github_agent/`  
**Depends on:** `AGENTS.md`, `.agents/skills/archive-governance/SKILL.md`, `01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md`, `01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md`

> **Evidence boundary:** This is a reproducible procedure, NOT proof that the 2026-11-12 backup finished. The observed run #87 was still `in_progress` at last readback. Only native terminal GitHub evidence, an exact source-bound manifest/receipt and a verified recovery readback can promote the result. No governance or runtime permissions change is authorized by this document.

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

## Run #87: observed, **not promoted** (2026-11-12)

- Owner-requested original run: [Vault Actions #87](https://github.com/Donh91/Investering-Framework-Vault/actions/runs/43241155043).
- Vault workflow HEAD shown: `d8bf61048dccf32884f50bf6782a09059fead281`. **This is not yet an authenticated frozen Archive snapshot SHA.**
- Archive main was `bee079d7a755874dc6c71a0292c3d3e86db30531` when the internal backup branch was created; it subsequently advanced. That safepoint is `backup-safepoint/2026-11-12-manual-vault-request`, compare identical at that point.
- Prioritized access finding: connector returned `404` for private Vault, but the existing authenticated GitHub browser could read Vault and trigger the already-present manual workflow. Do not interpret 404 as proof Vault is gone.
- Last owner-session inspection observed run `IN_PROGRESS` with `snapshot` running for ~14 minutes, freeze/readback step active; validation/receipt jobs not verified terminal. A previous earlier observation had ambiguous job state; latest native state wins.
- Required for promotion: terminal native run/job evidence; snapshot/receipt paths and actual Vault commits; *Archive* frozen SHA; counts/digests; restore/readback `PASS`; source coverage relative to post-run `main`.
- **Current result:** `BACKUP_PENDING_TERMINAL_VERIFICATION`, `EXTERNAL_BACKUP_PASS=FALSE`, `FULL_GIT_MIRROR=NOT_PROVEN`.

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
