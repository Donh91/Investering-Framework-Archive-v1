# Separation of Destructive Authority v1

**Date:** 2026-09-04  
**Status:** PERMANENT_CANONICAL_SAFETY_INVARIANT  
**Scope:** All autonomous and semi-autonomous agents, models, workflows, service accounts, delegated credentials, automation principals, and future agent systems operating on the Investment Framework or its recovery systems.

## Permanent principle

> An agent may improve the aircraft, but it must never simultaneously hold the ability to destroy both the aircraft and the parachute.

Operationally:

> No autonomous or semi-autonomous principal may simultaneously hold sufficient destructive authority to irreversibly damage, delete, rewrite, or render unrecoverable both the canonical source system and its independent recovery layer.

This is a permanent architecture invariant. It is not a trust score, model-quality judgment, or temporary onboarding restriction.

## Required separation

The framework must preserve separation between:

1. **SOURCE AUTHORITY** - authority to change the canonical working framework, code, workflows, registries, configuration, or repository state.
2. **RECOVERY AUTHORITY** - authority to destroy, overwrite, rewrite, delete, invalidate, or disable the independent Vault, immutable snapshots, recovery manifests, restore receipts, mirrors, or equivalent disaster-recovery assets.

A principal may be highly trusted in one domain without receiving destructive authority in the other.

Read access to recovery status, receipts, manifests, and restore evidence is allowed when needed for verification. Narrow append-only backup writing may also be allowed when technically and procedurally constrained. Neither is equivalent to destructive recovery authority.

## Destructive authority includes

Examples include, but are not limited to:

- force-push or history rewrite;
- branch or repository deletion;
- deletion or replacement of immutable snapshots, manifests, or receipts;
- mass deletion, mass overwrite, destructive migration, or unrecoverable namespace rewrite;
- changing permissions, rules, credentials, retention, or safeguards in a way that creates equivalent destructive capability;
- disabling the recovery path, backup automation, restore evidence, or independent recovery repository;
- deleting or invalidating both source safepoints and independent recovery copies.

## Fail-closed rule

If a task appears to require one autonomous principal to obtain destructive authority over both source and recovery:

```text
STOP
FAIL_CLOSED
DO_NOT_BROADEN_PERMISSIONS
DO_NOT_DISABLE_SAFEGUARDS
ESCALATE_TO_SEPARATE_AUTHORITY
```

The task must be split across separate principals or require explicit human-controlled execution with independent recovery proof.

## High-impact work

Before high-impact source work, the existing safepoint and disaster-recovery policy remains binding. A fresh verified recovery point must exist when required by the active backup/DR contract.

No agent may treat its own capability, benchmark performance, seniority, prior success, qualification status, or future "golden key" status as justification for bypassing this rule.

## Self-protection

This invariant must not be silently weakened, removed, bypassed, or superseded by:

- an agent prompt;
- a workflow-local instruction;
- a model migration;
- an automation optimization;
- a convenience exception;
- an agent's own proposal or self-assessment.

Agents may propose stronger controls or clarifications, but may not autonomously weaken this invariant.

Any future replacement must be explicitly authorized by the repository owner, name this policy directly, preserve equal or stronger separation of destructive authority, and be introduced through the framework's controlled governance path with recovery protection in place.

## Precedence

Where lower-level prompts, agent instructions, workflow configuration, or convenience procedures conflict with this policy, this policy wins on destructive-authority separation.

Existing stricter Vault immutability, backup, safepoint, branch, or recovery rules remain fully in force.

## Agent mnemonic

```text
IMPROVE THE AIRCRAFT.
PROTECT THE PARACHUTE.
NEVER HOLD BOTH DESTRUCTIVE KEYS.
```
