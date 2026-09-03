# Permanent Separation of Destructive Authority

**Status:** PERMANENT_CANONICAL_GOVERNANCE  
**Effective:** 2026-09-03  
**Scope:** All autonomous agents, models, workflows, API agents, coding agents, research agents, maintainers acting through automation, and future model generations operating on the Investering Framework.

## Core law

An autonomous agent may improve, modify, maintain, audit, repair, and operate the source system, but must never simultaneously possess sufficient authority to irreversibly destroy both:

1. the canonical source system, and
2. its independent recovery / disaster-recovery layer.

Human mnemonic:

> You may improve the aircraft, but you must not simultaneously have authority to destroy both the aircraft and the parachute.

This is a separation-of-duties invariant, not a model-confidence setting.

## Permanent authority invariant

No single autonomous execution identity, credential set, workflow, model session, agent role, or delegated tool context may have uncontrolled destructive authority over both the source repository and the independent recovery layer at the same time.

For purposes of this rule, destructive authority includes the practical ability to perform or authorize operations that could make recovery materially impossible or untrustworthy, including:

- repository deletion;
- branch deletion where it can remove the authoritative recovery path;
- force-push or non-fast-forward history replacement;
- history rewrite;
- destructive mass deletion or overwrite of canonical framework paths;
- deletion, replacement, or corruption of canonical snapshots, manifests, receipts, or recovery instructions;
- weakening or bypassing recovery protections in order to complete another task;
- credential or permission broadening that creates equivalent destructive reach.

## Required separation

### Source-side agent

An agent with meaningful source write, merge, administrative, or destructive authority must not simultaneously receive destructive or administrative authority over the independent recovery layer.

Normal source-side work may read recovery status and receipts when needed for verification, but read access must not be treated as permission to alter the recovery layer.

### Recovery-side agent

An agent permitted to create or verify recovery artifacts must not simultaneously receive uncontrolled destructive authority over the canonical source system.

Recovery work must remain narrowly scoped to backup, verification, restore testing, receipt creation, and explicitly authorized recovery operations.

### Same model, different contexts

The same underlying model family may serve different roles only when the execution contexts, credentials, permissions, and audit trails preserve the separation above. Model identity alone does not satisfy separation of duties.

## High-impact source work

Existing Vault and repository-safety rules remain in force. Before approved high-impact source work, the framework must create and verify the required safepoint / disaster-recovery snapshot according to current canonical recovery governance.

A high-impact change must not proceed merely because a capable model believes recovery is probably possible.

Recovery proof must be evidenced by the framework's own receipts and verification state.

## Fail-closed rule

If an autonomous agent cannot prove that source and recovery destructive authority are separated for the requested operation, it must stop the destructive portion of the operation and report:

`AUTHORITY_SEPARATION_BLOCK`

The agent may continue read-only diagnosis, produce a remediation plan, prepare a non-destructive branch or patch where permitted, or request the narrowly scoped authority needed for one side only.

It must not solve the block by expanding its own permissions.

## No capability-based override

This rule applies regardless of model capability, benchmark score, urgency, convenience, or prior reliability.

It applies to, including but not limited to:

- GPT-5.6 Sol;
- Astra;
- Codex and coding agents;
- OpenAI API agents;
- external-model agents;
- future autonomous models and orchestration systems.

Higher intelligence may justify broader task scope after qualification. It does not justify combining source-destruction and recovery-destruction authority.

There is no universal autonomous "golden key" that overrides this rule.

## No autonomous self-amendment

An autonomous agent must not weaken, delete, bypass, silently reinterpret, or self-exempt from this rule.

Any proposal to amend or retire this invariant is itself a high-impact governance change and requires:

1. explicit human-owner approval;
2. a fresh, verified recovery safepoint under then-current canonical recovery policy;
3. an auditable change path;
4. preservation of an independent recovery mechanism throughout the change.

Absent all four conditions, the existing rule remains authoritative.

## Relationship to Vault governance

This rule supplements, and does not replace, the independent Vault policy.

The recovery layer remains a disaster-recovery target rather than an ordinary working repository. Existing append-only snapshot, manifest, receipt, no-force-push, no-history-rewrite, and restore-verification requirements continue to apply.

## Agent execution check

Before any operation with meaningful destructive potential, an agent must answer all of the following:

1. What is the authoritative source system for this operation?
2. What is the independent recovery layer?
3. What destructive permissions does this execution context hold on the source?
4. What destructive permissions does it hold on recovery?
5. Could one autonomous context make both source and recovery unrecoverable or untrustworthy?
6. Is a fresh recovery receipt required before this change?

If question 5 is `YES` or cannot be established as `NO`, destructive execution is blocked.

## Canonical interpretation

The purpose is not to prevent capable agents from doing difficult work. The purpose is to make catastrophic correlated failure structurally harder.

Agents may be granted deep authority to improve the aircraft. The parachute must remain independently survivable.
